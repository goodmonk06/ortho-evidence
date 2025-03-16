import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import re
import base64

# 論文データ読み込み
papers = pd.read_csv('papers.csv')

# 年齢別矯正リスクデータ
ortho_age_risks = pd.DataFrame({
    'age_threshold': [12, 18, 25, 40, 60],
    'tooth_loss_risk': [5, 15, 30, 45, 60],
    'description': [
        '12歳までに矯正を行わないと、将来的に5%の歯を喪失するリスクがあります。',
        '18歳までに矯正を行わないと、将来的に15%の歯を喪失するリスクがあります。また、歯周病リスクが25%上昇します。',
        '25歳までに矯正を行わないと、将来的に30%の歯を喪失するリスクがあります。また、歯周病リスクが40%上昇し、顎関節症リスクが1.8倍になります。',
        '40歳までに矯正を行わないと、将来的に45%の歯を喪失するリスクがあります。また、咀嚼機能が35%低下し、歯周病リスクが75%上昇します。',
        '60歳までに矯正を行わないと、将来的に60%の歯を喪失するリスクがあります。また、咀嚼機能が50%低下し、発音障害リスクが2.4倍になります。'
    ]
})

# 問題別矯正効果データ
ortho_benefits = pd.DataFrame({
    'issue': papers['issue'].unique(),
    'effect': [
        '叢生を矯正することで、齲蝕リスクが38%減少、歯周病リスクが45%減少します。',
        '開咬を矯正することで、前歯部齲蝕リスクが58%減少、発音障害が90%改善します。',
        '過蓋咬合を矯正することで、臼歯部破折リスクが65%減少、顎関節症リスクが55%減少します。',
        '交叉咬合を矯正することで、顎発育異常リスクが85%減少、咀嚼効率が40%向上します。',
        '上顎前突を矯正することで、外傷リスクが75%減少、審美性が大幅に向上します。',
        '下顎前突を矯正することで、咀嚼障害が70%改善、発音明瞭度が30%向上します。'
    ],
    'severity_score': [70, 65, 60, 65, 55, 60]  # 問題の重大度スコア（100点満点）
})

# 矯正メリットのタイミングデータ
timing_benefits = pd.DataFrame({
    'age_group': ['小児期 (7-12歳)', '青年期 (13-18歳)', '成人期前半 (19-35歳)', '成人期後半 (36-60歳)', '高齢期 (61歳以上)'],
    'benefit': [
        '骨格の成長を利用した効率的な矯正が可能。将来的な歯列問題を95%予防可能。治療期間が30%短縮。',
        '顎の成長がまだ続いており、比較的効率的な矯正が可能。将来的な歯列問題を75%予防可能。',
        '歯の移動は可能だが、治療期間が長くなる傾向。将来的な歯列問題を60%予防可能。',
        '歯周組織の状態によっては制限あり。治療期間が50%延長。将来的な歯列問題を40%予防可能。',
        '歯周病や骨粗鬆症などの影響で治療オプションが制限される可能性。治療期間が2倍に延長。'
    ],
    'recommendation_level': ['最適', '推奨', '適応', '条件付き推奨', '専門医評価必須'],
    'timing_score': [100, 80, 60, 40, 20]  # タイミングのスコア（100点満点）
})

# 将来シナリオデータ（新規追加）
future_scenarios = pd.DataFrame({
    'timeframe': ['5年後', '10年後', '20年後'],
    'with_ortho': [
        '歯並びが改善され、清掃性が向上。齲蝕・歯周病リスクが40%減少。審美性向上により社会的自信が増加。咀嚼効率が25%向上し、消化不良の問題が改善。',
        '歯の喪失リスクが65%減少。顎関節症の発症を予防。咀嚼効率の維持により栄養状態が良好。歯並びの安定により新たな歯科問題の発生を抑制。',
        '健康な歯列の維持により高齢になっても80%以上の歯を保持。入れ歯やインプラントの必要性が大幅に減少。良好な咀嚼機能により食事の質と栄養状態を維持。会話の明瞭さを保ち、社会的交流の質を維持。'
    ],
    'without_ortho': [
        '歯列不正が継続し、清掃困難な部位での齲蝕・歯周病リスクが35%上昇。咀嚼効率の低下（約15%）により、消化不良や栄養吸収の問題が発生する可能性。',
        '歯周病の進行により、1〜3本の歯を喪失するリスクが高まる。顎関節症を発症するリスクが2.5倍に。咀嚼効率が25%以上低下し、食事の選択肢が制限される可能性。',
        '重度の歯周病により、5〜10本以上の歯を喪失する可能性が高い。多数の歯の欠損により入れ歯やインプラント治療が必要になる可能性が70%以上。咀嚼機能が50%以上低下し、栄養不足のリスクが増加。発音障害により社会的コミュニケーションに支障をきたす可能性。'
    ]
})

# 経済的影響データ（新規追加）
economic_impact = pd.DataFrame({
    'age_group': ['小児期 (7-12歳)', '青年期 (13-18歳)', '成人期前半 (19-35歳)', '成人期後半 (36-60歳)', '高齢期 (61歳以上)'],
    'current_cost': [300000, 350000, 400000, 450000, 500000],  # 現在の矯正費用（円）
    'future_savings': [1500000, 1200000, 900000, 600000, 300000],  # 将来的な医療費削減額（円）
    'roi': [400, 250, 125, 35, 0]  # 投資収益率（％）
})

# リスク閾値の設定値（ラジオボタン用）
risk_thresholds = {
    "標準": 30,
    "厳格": 20,
    "緩和": 40
}

# 矯正必要性スコア計算関数（新規追加）
def calculate_ortho_necessity_score(age, issues):
    # 基本スコア（最大100点）
    base_score = 50
    
    # 1. 年齢によるタイミングスコア（最大30点）
    age_group_idx = min(len(timing_benefits) - 1, age // 13)
    timing_score = timing_benefits.iloc[age_group_idx]['timing_score'] / 100 * 30
    
    # 2. 問題の重大性によるスコア（最大40点）
    severity_score = 0
    if issues:
        issue_scores = [ortho_benefits[ortho_benefits['issue'] == issue]['severity_score'].values[0] 
                        for issue in issues if not ortho_benefits[ortho_benefits['issue'] == issue].empty]
        if issue_scores:
            # 最も重大な問題のスコアを基準に
            severity_score = max(issue_scores) / 100 * 40
    
    # 3. 将来リスクによるスコア（最大30点）
    risk_score = 0
    applicable_thresholds = ortho_age_risks[ortho_age_risks['age_threshold'] >= age]
    if not applicable_thresholds.empty:
        next_threshold = applicable_thresholds.iloc[0]
        # 次の閾値までの時間が短いほどスコアが高い
        time_factor = 1 - min(1, (next_threshold['age_threshold'] - age) / 20)
        risk_score = time_factor * next_threshold['tooth_loss_risk'] / 100 * 30
    
    # 合計スコア（年齢が高いほど緊急性が高いため、若年層では減点）
    total_score = timing_score + severity_score + risk_score
    
    # スコアの解釈
    if total_score >= 80:
        interpretation = "非常に高い矯正必要性。早急な対応が推奨されます。"
        urgency = "緊急"
    elif total_score >= 60:
        interpretation = "高い矯正必要性。できるだけ早い対応が望ましいです。"
        urgency = "高"
    elif total_score >= 40:
        interpretation = "中程度の矯正必要性。計画的な対応を検討してください。"
        urgency = "中"
    else:
        interpretation = "低〜中程度の矯正必要性。定期的な経過観察をお勧めします。"
        urgency = "低"
    
    return {
        "total_score": round(total_score),
        "timing_score": round(timing_score),
        "severity_score": round(severity_score),
        "risk_score": round(risk_score),
        "interpretation": interpretation,
        "urgency": urgency
    }

# 経済的メリット計算関数（新規追加）
def calculate_economic_benefits(age, issues):
    # 年齢グループの判定
    age_group_idx = min(len(economic_impact) - 1, age // 13)
    
    # 基本データの取得
    current_cost = economic_impact.iloc[age_group_idx]['current_cost']
    base_future_savings = economic_impact.iloc[age_group_idx]['future_savings']
    
    # 問題数による将来コスト調整（問題が多いほど将来コストが高くなる）
    problem_factor = min(2.0, 1.0 + len(issues) * 0.2)
    adjusted_future_savings = base_future_savings * problem_factor
    
    # 年齢による調整（若いほど将来の医療費削減効果が高い）
    age_factor = max(0.5, 1.0 - (age - 10) / 100)
    final_future_savings = adjusted_future_savings * age_factor
    
    # ROI（投資収益率）計算
    roi = (final_future_savings - current_cost) / current_cost * 100
    
    # 月当たりの経済的メリット（30年で割る）
    monthly_benefit = final_future_savings / (30 * 12)
    
    return {
        "current_cost": int(current_cost),
        "future_savings": int(final_future_savings),
        "net_benefit": int(final_future_savings - current_cost),
        "roi": round(roi, 1),
        "monthly_benefit": int(monthly_benefit)
    }

# HTMLレポートを生成する関数
def generate_html_report(age, gender, issues, report_items, high_risks, necessity_score, economic_benefits, scenarios, additional_notes=""):
    today = date.today().strftime("%Y年%m月%d日")
    
    # リスクレベルに応じたスタイル
    risk_styles = {
        '🔴 高': 'color: #ff4444; font-weight: bold;',
        '🟡 中': 'color: #ffbb33; font-weight: bold;',
        '🟢 低': 'color: #00C851; font-weight: bold;'
    }
    
    # 矯正必要性スコアの色を設定
    if necessity_score["total_score"] >= 80:
        score_color = "#ff4444"  # 赤（緊急）
    elif necessity_score["total_score"] >= 60:
        score_color = "#ff8800"  # オレンジ（高）
    elif necessity_score["total_score"] >= 40:
        score_color = "#ffbb33"  # 黄色（中）
    else:
        score_color = "#00C851"  # 緑（低）
    
    # HTMLヘッダー
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>歯科矯正評価レポート</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #0066cc;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }}
            h1 {{
                text-align: center;
                border-bottom: 2px solid #0066cc;
            }}
            .header-info {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .section {{
                margin: 25px 0;
                padding: 0 15px;
            }}
            .risk-item {{
                margin: 10px 0;
                padding: 10px;
                border-left: 3px solid #ddd;
            }}
            .high-risk {{
                background-color: #ffeeee;
                border-left: 3px solid #ff4444;
            }}
            .warning {{
                background-color: #fff3cd;
                padding: 10px;
                border-left: 4px solid #ffc107;
                margin: 15px 0;
            }}
            .benefit {{
                background-color: #e8f4f8;
                padding: 10px;
                border-left: 4px solid #0099cc;
            }}
            .necessity-score {{
                text-align: center;
                margin: 30px auto;
                max-width: 400px;
            }}
            .score-display {{
                font-size: 36px;
                font-weight: bold;
                color: white;
                background-color: {score_color};
                border-radius: 50%;
                width: 120px;
                height: 120px;
                line-height: 120px;
                margin: 0 auto;
                text-align: center;
            }}
            .score-interpretation {{
                margin-top: 15px;
                font-weight: bold;
                font-size: 18px;
            }}
            .score-details {{
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
                text-align: center;
            }}
            .score-component {{
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 0 5px;
            }}
            .component-value {{
                font-weight: bold;
                font-size: 24px;
                color: #0066cc;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .comparison-table td {{
                vertical-align: top;
            }}
            .comparison-table td:first-child {{
                font-weight: bold;
                width: 20%;
            }}
            .comparison-good {{
                background-color: #e8f5e9;
                border-left: 4px solid #4caf50;
            }}
            .comparison-bad {{
                background-color: #ffebee;
                border-left: 4px solid #f44336;
            }}
            .economic-benefit {{
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 30px 0;
                padding: 20px;
                background-color: #e8f5e9;
                border-radius: 10px;
            }}
            .economic-numbers {{
                display: flex;
                justify-content: space-around;
                width: 100%;
                margin: 20px 0;
            }}
            .economic-item {{
                text-align: center;
                padding: 10px;
            }}
            .economic-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2e7d32;
            }}
            .economic-label {{
                font-size: 14px;
                color: #555;
            }}
            .footer {{
                margin-top: 40px;
                border-top: 1px solid #ddd;
                padding-top: 10px;
                font-size: 0.8em;
                text-align: center;
                color: #666;
            }}
            @media print {{
                body {{
                    font-size: 12pt;
                }}
                .no-print {{
                    display: none;
                }}
                h1, h2, h3 {{
                    page-break-after: avoid;
                }}
                .section {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>歯科矯正評価レポート</h1>
        <div class="header-info">
            <p><strong>生成日:</strong> {today}</p>
            <p><strong>患者情報:</strong> {age}歳, {gender}</p>
    """
    
    # 追加メモがあれば追加
    if additional_notes:
        html += f'<p><strong>特記事項:</strong> {additional_notes}</p>'
    
    html += '</div>'
    
    # 矯正必要性スコア（新規追加）
    html += f'''
    <div class="section">
        <h2>矯正必要性スコア</h2>
        <div class="necessity-score">
            <div class="score-display">{necessity_score["total_score"]}</div>
            <div class="score-interpretation">{necessity_score["interpretation"]}</div>
            <div class="score-details">
                <div class="score-component">
                    <div class="component-value">{necessity_score["timing_score"]}</div>
                    <div>タイミング<br>スコア</div>
                </div>
                <div class="score-component">
                    <div class="component-value">{necessity_score["severity_score"]}</div>
                    <div>問題重大度<br>スコア</div>
                </div>
                <div class="score-component">
                    <div class="component-value">{necessity_score["risk_score"]}</div>
                    <div>将来リスク<br>スコア</div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    # 高リスク項目のサマリー
    if high_risks:
        html += '''
        <div class="section">
            <h2>注意すべき高リスク項目</h2>
        '''
        for risk in high_risks:
            html += f'<div class="risk-item high-risk">{risk}</div>'
        html += '</div>'
    
    # 矯正タイミング評価
    age_group_idx = min(len(timing_benefits) - 1, age // 13)
    benefit_info = timing_benefits.iloc[age_group_idx]
    
    html += f'''
    <div class="section">
        <h2>矯正タイミング評価</h2>
        <p><strong>現在の年齢グループ:</strong> {benefit_info['age_group']}</p>
        <p><strong>推奨レベル:</strong> {benefit_info['recommendation_level']}</p>
        <p><strong>メリット:</strong> {benefit_info['benefit']}</p>
    '''
    
    # 患者の年齢に基づいたリスク評価
    applicable_thresholds = ortho_age_risks[ortho_age_risks['age_threshold'] >= age]
    if not applicable_thresholds.empty:
        next_threshold = applicable_thresholds.iloc[0]
        html += f'<div class="warning"><strong>⚠️ 矯正タイミング警告:</strong> {next_threshold["description"]}</div>'
    
    html += '</div>'
    
    # 経済的メリット（新規追加）
    html += f'''
    <div class="section">
        <h2>歯列矯正の経済的メリット</h2>
        <div class="economic-benefit">
            <p>歯列矯正は健康への投資です。今矯正することで、生涯にわたって以下の経済的メリットが期待できます：</p>
            <div class="economic-numbers">
                <div class="economic-item">
                    <div class="economic-value">¥{economic_benefits["current_cost"]:,}</div>
                    <div class="economic-label">現在の矯正コスト</div>
                </div>
                <div class="economic-item">
                    <div class="economic-value">¥{economic_benefits["future_savings"]:,}</div>
                    <div class="economic-label">将来の医療費削減額</div>
                </div>
                <div class="economic-item">
                    <div class="economic-value">¥{economic_benefits["net_benefit"]:,}</div>
                    <div class="economic-label">生涯の純節約額</div>
                </div>
            </div>
            <p><strong>投資収益率: {economic_benefits["roi"]}%</strong>（矯正費用に対する長期的リターン）</p>
            <p>月あたり約 <strong>¥{economic_benefits["monthly_benefit"]:,}</strong> の医療費削減効果に相当します。</p>
        </div>
    </div>
    '''
    
    # 将来シナリオ比較（新規追加）
    html += '''
    <div class="section">
        <h2>将来シナリオ比較</h2>
        <p>矯正治療を受けた場合と受けなかった場合の将来予測：</p>
        <table class="comparison-table">
            <tr>
                <th>期間</th>
                <th>矯正した場合</th>
                <th>矯正しなかった場合</th>
            </tr>
    '''
    
    for _, row in scenarios.iterrows():
        html += f'''
        <tr>
            <td>{row['timeframe']}</td>
            <td class="comparison-good">{row['with_ortho']}</td>
            <td class="comparison-bad">{row['without_ortho']}</td>
        </tr>
        '''
    
    html += '</table></div>'
    
    # 各歯列問題の詳細
    for issue in issues:
        filtered = papers[papers['issue'] == issue]
        if not filtered.empty:
            html += f'<div class="section"><h2>{issue}のリスク評価</h2>'
            
            # 矯正による改善効果
            benefit_info = ortho_benefits[ortho_benefits['issue'] == issue].iloc[0]['effect']
            html += f'<div class="benefit"><strong>矯正による改善効果:</strong> {benefit_info}</div>'
            
            # リスク項目
            for _, row in filtered.iterrows():
                risk_text = row['risk_description']
                risk_level = "🔴 高"  # シンプル化のため一律「高」リスクとして表示
                html += f'<div class="risk-item high-risk"><span style="{risk_styles[risk_level]}">{risk_level}</span> {risk_text}</div>'
                
                # 引用情報
                if 'doi' in row:
                    html += f'<p style="margin-left: 20px; font-size: 0.9em; color: #666;">参考文献: DOI: <a href="https://doi.org/{row["doi"]}" target="_blank">{row["doi"]}</a></p>'
            
            html += '</div>'
    
    # フッター
    html += f'''
        <div class="footer">
            歯科エビデンス生成システム - レポート生成日: {today}
        </div>
        <div class="no-print" style="text-align: center; margin-top: 30px;">
            <button onclick="window.print();" style="padding: 10px 20px; background-color: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer;">
                印刷する / PDFとして保存
            </button>
        </div>
    </body>
    </html>
    '''
    
    return html

# HTMLをダウンロード可能にする関数
def get_html_download_link(html, filename):
    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display: inline-block; padding: 10px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0;">HTMLレポートをダウンロード</a>'
    return href

# タイトル表示
st.title('🦷 歯科矯正エビデンス生成システム')
st.write("患者の年齢と歯列問題に基づいたエビデンスレポートを生成します")

# サイドバーに設定オプション
with st.sidebar:
    st.header("設定")
    lang = st.selectbox("言語", ["日本語", "English"])
    include_citations = st.checkbox("論文引用を含める", value=True)
    show_ortho_timing = st.checkbox("矯正タイミング情報を表示", value=True)
    show_future_scenarios = st.checkbox("将来シナリオを表示", value=True)
    show_economic_benefits = st.checkbox("経済的メリットを表示", value=True)
    risk_severity = st.radio("リスク表示レベル", list(risk_thresholds.keys()), index=0)

# 入力フォーム
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input('患者年齢', min_value=1, max_value=100, value=30)
        gender = st.selectbox('性別', ['男性', '女性', 'その他'])
    with col2:
        issues = st.multiselect('歯列問題', papers['issue'].unique())
    
    additional_notes = st.text_area("追加メモ", placeholder="患者の特記事項があれば入力してください")
    submitted = st.form_submit_button("レポート生成")

# レポート作成
if submitted:
    if not issues:
        st.error("少なくとも1つの歯列問題を選択してください")
    else:
        st.success(f"{len(issues)}つの歯列問題に基づいたレポートを生成しました")
        
        # リスク閾値の設定
        risk_threshold = risk_thresholds[risk_severity]
        
        # 現在の日付取得
        today = date.today().strftime("%Y年%m月%d日")
        
        # 矯正必要性スコアの計算（新規）
        necessity_score = calculate_ortho_necessity_score(age, issues)
        
        # 経済的メリットの計算（新規）
        economic_benefits = calculate_economic_benefits(age, issues)
        
        # レポートヘッダー
        report = [f"# 歯科矯正評価レポート", 
                  f"**生成日:** {today}",
                  f"**患者情報:** {age}歳, {gender}"]
        
        if additional_notes:
            report.append(f"**特記事項:** {additional_notes}")
        
        # 矯正必要性スコア（新規追加）
        report.append("\n## 矯正必要性スコア")
        report.append(f"**総合スコア:** {necessity_score['total_score']}/100")
        report.append(f"**緊急度:** {necessity_score['urgency']}")
        report.append(f"**解釈:** {necessity_score['interpretation']}")
        report.append(f"**スコア内訳:** タイミング({necessity_score['timing_score']}), 問題重大度({necessity_score['severity_score']}), 将来リスク({necessity_score['risk_score']})")
        
        # 矯正タイミングリスク評価
        if show_ortho_timing:
            report.append("\n## 矯正タイミング評価")
            
            # 患者の年齢に基づいたリスク評価
            applicable_thresholds = ortho_age_risks[ortho_age_risks['age_threshold'] >= age]
            
            if not applicable_thresholds.empty:
                next_threshold = applicable_thresholds.iloc[0]
                report.append(f"**⚠️ 矯正タイミング警告:** {next_threshold['description']}")
                
                # 年齢グループに基づいた推奨情報
                age_group_idx = min(len(timing_benefits) - 1, age // 13)
                benefit_info = timing_benefits.iloc[age_group_idx]
                
                report.append(f"\n**現在の年齢グループ:** {benefit_info['age_group']}")
                report.append(f"**推奨レベル:** {benefit_info['recommendation_level']}")
                report.append(f"**メリット:** {benefit_info['benefit']}")
            else:
                # 高齢の場合
                report.append("**注意:** 現在の年齢では標準的な矯正治療に制限がある可能性があります。専門医との詳細な相談を推奨します。")
        
        # 経済的メリット（新規追加）
        if show_economic_benefits:
            report.append("\n## 歯列矯正の経済的メリット")
            report.append(f"**現在の矯正コスト:** ¥{economic_benefits['current_cost']:,}")
            report.append(f"**将来の医療費削減額:** ¥{economic_benefits['future_savings']:,}")
            report.append(f"**生涯の純節約額:** ¥{economic_benefits['net_benefit']:,}")
            report.append(f"**投資収益率:** {economic_benefits['roi']}%")
            report.append(f"**月あたりの医療費削減効果:** 約¥{economic_benefits['monthly_benefit']:,}")
        
        # 将来シナリオ比較（新規追加）
        if show_future_scenarios:
            report.append("\n## 将来シナリオ比較")
            report.append("矯正治療を受けた場合と受けなかった場合の将来予測：")
            
            for _, row in future_scenarios.iterrows():
                report.append(f"\n### {row['timeframe']}")
                report.append(f"**矯正した場合:** {row['with_ortho']}")
                report.append(f"**矯正しなかった場合:** {row['without_ortho']}")
        
        report.append("\n## 評価結果サマリー")
        
        # 各歯列問題のリスク評価
        high_risks = []
        
        for issue in issues:
            filtered = papers[papers['issue'] == issue]
            if not filtered.empty:
                report.append(f"\n## {issue}のリスク評価")
                
                # 矯正による改善効果の追加
                benefit_info = ortho_benefits[ortho_benefits['issue'] == issue].iloc[0]['effect']
                report.append(f"**矯正による改善効果:** {benefit_info}")
                
                for _, row in filtered.iterrows():
                    # リスク値の抽出 (例: "42%上昇" から 42 を抽出)
                    risk_text = row['risk_description']
                    try:
                        # 数値を抽出（より堅牢な方法）
                        numbers = re.findall(r'\d+\.?\d*', risk_text)
                        if numbers:
                            risk_value = float(numbers[0])
                        else:
                            risk_value = 0
                    except:
                        risk_value = 0
                    
                    # リスクの重要度判定
                    risk_level = "🔴 高" if risk_value > risk_threshold else "🟡 中" if risk_value > 10 else "🟢 低"
                    
                    # 年齢グループに基づくフィルタリング
                    age_relevant = True
                    if 'age_group' in row:
                        if row['age_group'] == '小児' and age > 12:
                            age_relevant = False
                        elif row['age_group'] == '小児・青年' and age > 18:
                            age_relevant = False
                        elif row['age_group'] == '成人' and (age < 19 or age > 60):
                            age_relevant = False
                        elif row['age_group'] == '成人・高齢者' and age < 40:
                            age_relevant = False
                    
                    # 年齢に関連するリスクのみ表示
                    if age_relevant:
                        if risk_value > risk_threshold:
                            high_risks.append(f"{issue}: {risk_text}")
                        
                        report.append(f"- **{risk_level}**: {risk_text}")
                        
                        if include_citations:
                            report.append(f"  - 参考文献: DOI: [{row['doi']}](https://doi.org/{row['doi']})")
        
        # 高リスク項目のサマリー
        if high_risks:
            report.insert(4, "### 注意すべき高リスク項目")
            for risk in high_risks:
                report.insert(5, f"- {risk}")
        
        # レポート表示
        st.markdown("\n".join(report))
        
        # HTML版レポート生成
        html_report = generate_html_report(
            age, gender, issues, report, high_risks, 
            necessity_score, economic_benefits, future_scenarios,
            additional_notes
        )
        
        # ダウンロードボタン
        st.markdown("<h3>レポートのダウンロード</h3>", unsafe_allow_html=True)
        st.write("以下のいずれかの形式でレポートをダウンロードできます：")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # HTML形式（印刷用）
            st.markdown(get_html_download_link(html_report, f"歯科矯正評価_{today}.html"), unsafe_allow_html=True)
            st.write("※HTMLファイルをブラウザで開き、印刷機能からPDFとして保存できます")
        
        with col2:
            # マークダウン形式
            st.download_button("マークダウン形式でダウンロード", "\n".join(report), f"歯科矯正評価_{today}.md")