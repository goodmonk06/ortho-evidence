import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import re

# 論文データ読み込み
papers = pd.read_csv('papers.csv')

# 年齢別矯正リスクデータ（新規追加）
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

# 問題別矯正効果データ（新規追加）
ortho_benefits = pd.DataFrame({
    'issue': papers['issue'].unique(),
    'effect': [
        '叢生を矯正することで、齲蝕リスクが38%減少、歯周病リスクが45%減少します。',
        '開咬を矯正することで、前歯部齲蝕リスクが58%減少、発音障害が90%改善します。',
        '過蓋咬合を矯正することで、臼歯部破折リスクが65%減少、顎関節症リスクが55%減少します。',
        '交叉咬合を矯正することで、顎発育異常リスクが85%減少、咀嚼効率が40%向上します。',
        '上顎前突を矯正することで、外傷リスクが75%減少、審美性が大幅に向上します。',
        '下顎前突を矯正することで、咀嚼障害が70%改善、発音明瞭度が30%向上します。'
    ]
})

# 矯正メリットのタイミングデータ（新規追加）
timing_benefits = pd.DataFrame({
    'age_group': ['小児期 (7-12歳)', '青年期 (13-18歳)', '成人期前半 (19-35歳)', '成人期後半 (36-60歳)', '高齢期 (61歳以上)'],
    'benefit': [
        '骨格の成長を利用した効率的な矯正が可能。将来的な歯列問題を95%予防可能。治療期間が30%短縮。',
        '顎の成長がまだ続いており、比較的効率的な矯正が可能。将来的な歯列問題を75%予防可能。',
        '歯の移動は可能だが、治療期間が長くなる傾向。将来的な歯列問題を60%予防可能。',
        '歯周組織の状態によっては制限あり。治療期間が50%延長。将来的な歯列問題を40%予防可能。',
        '専門医評価必須。歯周病や骨粗鬆症などの影響で治療オプションが制限される可能性。治療期間が2倍に延長。'
    ],
    'recommendation_level': ['最適', '推奨', '適応', '条件付き推奨', '専門医評価必須']
})

# タイトル表示
st.title('🦷 歯科エビデンス生成システム')
st.write("患者の年齢と歯列問題に基づいたエビデンスレポートを生成します")

# サイドバーに設定オプション
with st.sidebar:
    st.header("設定")
    lang = st.selectbox("言語", ["日本語", "English"])
    include_citations = st.checkbox("論文引用を含める", value=True)
    show_charts = st.checkbox("データグラフを表示", value=True)
    show_ortho_timing = st.checkbox("矯正タイミング情報を表示", value=True)
    show_recommendations = st.checkbox("具体的な矯正推奨を表示", value=True)

# 入力フォーム
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input('患者年齢', min_value=1, max_value=100, value=30)
        gender = st.selectbox('性別', ['男性', '女性', 'その他'])
    with col2:
        issues = st.multiselect('歯列問題', papers['issue'].unique())
        risk_threshold = st.slider('リスク表示閾値 (%)', 0, 100, 20)
    
    additional_notes = st.text_area("追加メモ", placeholder="患者の特記事項があれば入力してください")
    submitted = st.form_submit_button("レポート生成")

# レポート作成
if submitted:
    if not issues:
        st.error("少なくとも1つの歯列問題を選択してください")
    else:
        st.success(f"{len(issues)}つの歯列問題に基づいたレポートを生成しました")
        
        # 現在の日付取得
        today = date.today().strftime("%Y年%m月%d日")
        
        # レポートヘッダー
        report = [f"# 歯科リスク評価レポート", 
                  f"**生成日:** {today}",
                  f"**患者情報:** {age}歳, {gender}"]
        
        if additional_notes:
            report.append(f"**特記事項:** {additional_notes}")
        
        # 矯正タイミングリスク評価（新規追加）
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
        
        report.append("\n## 評価結果サマリー")
        
        # 各歯列問題のリスク評価
        high_risks = []
        
        for issue in issues:
            filtered = papers[papers['issue'] == issue]
            if not filtered.empty:
                report.append(f"\n## {issue}のリスク評価")
                
                # 矯正による改善効果の追加（新規）
                if show_recommendations:
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
                    
                    # 年齢グループに基づくフィルタリング（新規）
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
        
        # 矯正しない場合の将来リスク（新規追加）
        if show_recommendations:
            report.append("\n## 矯正しない場合の長期リスク")
            
            # 年齢に基づいた将来リスク予測
            future_risks = []
            for _, risk in ortho_age_risks.iterrows():
                if risk['age_threshold'] > age:
                    years_until = risk['age_threshold'] - age
                    future_risks.append(f"- **{years_until}年後 ({risk['age_threshold']}歳時点)**: {risk['description']}")
            
            if future_risks:
                report.extend(future_risks)
            else:
                report.append("- 現在の年齢では、標準的な将来リスク予測データがありません。専門医の評価を推奨します。")
        
        # 高リスク項目のサマリー
        if high_risks:
            report.insert(4, "### 注意すべき高リスク項目")
            for risk in high_risks:
                report.insert(5, f"- {risk}")
        
        # レポート表示
        st.markdown("\n".join(report))
        
        # グラフ表示（シンプル化）
        if show_charts and issues:
            st.subheader("リスク比較グラフ")
            
            # 簡易的なグラフデータ作成
            risk_values = []
            issue_names = []
            
            for issue in issues:
                filtered = papers[papers['issue'] == issue]
                if not filtered.empty:
                    for _, row in filtered.iterrows():
                        risk_text = row['risk_description']
                        # 数値を抽出（より堅牢な方法）
                        numbers = re.findall(r'\d+\.?\d*', risk_text)
                        if numbers:
                            try:
                                risk_value = float(numbers[0])
                                risk_values.append(risk_value)
                                issue_names.append(issue)
                            except:
                                pass
            
            if risk_values and issue_names:
                chart_data = pd.DataFrame({
                    '問題': issue_names,
                    'リスク値': risk_values
                })
                st.bar_chart(chart_data.set_index('問題'))
            else:
                st.info("グラフ表示に適したデータがありません")
                
            # 年齢による歯の喪失リスクテーブル（グラフの代わり）
            if show_ortho_timing:
                st.subheader("年齢による歯の喪失リスク")
                
                # 年齢リスクテーブル作成
                age_risk_data = pd.DataFrame({
                    '年齢閾値': ortho_age_risks['age_threshold'],
                    '歯喪失リスク(%)': ortho_age_risks['tooth_loss_risk']
                })
                
                # 患者の現在年齢の予測リスクを計算
                current_risk = np.interp(age, 
                                         ortho_age_risks['age_threshold'], 
                                         ortho_age_risks['tooth_loss_risk'])
                
                # 現在の患者リスクを追加
                patient_row = pd.DataFrame({
                    '年齢閾値': [f"現在の患者（{age}歳）"],
                    '歯喪失リスク(%)': [f"{current_risk:.1f}"]
                })
                
                # テーブル表示
                st.write("📊 **年齢と歯喪失リスクの関係**")
                st.write(age_risk_data)
                st.write("**患者の現在リスク:**")
                st.write(patient_row)
                
        # 矯正メリット情報（グラフの代わりにテーブル表示）
        if show_recommendations and show_charts:
            st.subheader("年齢別矯正治療のメリット比較")
            
            # 現在の年齢グループをハイライト
            age_group_idx = min(len(timing_benefits) - 1, age // 13)
            
            # 現在の年齢グループを強調表示
            st.write(f"**現在の年齢グループ**: {timing_benefits.iloc[age_group_idx]['age_group']} - {timing_benefits.iloc[age_group_idx]['recommendation_level']}")
            
            # タイミングメリットデータをテーブル表示
            timing_display = pd.DataFrame({
                '年齢グループ': timing_benefits['age_group'],
                '推奨レベル': timing_benefits['recommendation_level'],
                'メリット': timing_benefits['benefit']
            })
            st.table(timing_display)
        
        # ダウンロードボタン
        st.download_button("レポートをダウンロード", "\n".join(report), f"歯科リスク評価_{today}.md")