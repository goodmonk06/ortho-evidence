import streamlit as st
import pandas as pd
from datetime import date

# 論文データ読み込み
papers = pd.read_csv('papers.csv')

# タイトル表示
st.title('🦷 歯科エビデンス生成システム')
st.write("患者の年齢と歯列問題に基づいたエビデンスレポートを生成します")

# サイドバーに設定オプション
with st.sidebar:
    st.header("設定")
    lang = st.selectbox("言語", ["日本語", "English"])
    include_citations = st.checkbox("論文引用を含める", value=True)
    show_charts = st.checkbox("データグラフを表示", value=True)

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
        
        report.append("\n## 評価結果サマリー")
        
        # 各歯列問題のリスク評価
        high_risks = []
        
        for issue in issues:
            filtered = papers[papers['issue'] == issue]
            if not filtered.empty:
                report.append(f"\n## {issue}のリスク評価")
                
                for _, row in filtered.iterrows():
                    # リスク値の抽出 (例: "42%上昇" から 42 を抽出)
                    risk_text = row['risk_description']
                    try:
                        risk_value = int(''.join(filter(str.isdigit, risk_text)))
                    except:
                        risk_value = 0
                    
                    # リスクの重要度判定
                    risk_level = "🔴 高" if risk_value > risk_threshold else "🟡 中" if risk_value > 10 else "🟢 低"
                    
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
        
        # グラフ表示
        if show_charts and issues:
            st.subheader("リスク比較グラフ")
            
            # 簡易的なグラフデータ作成
            chart_data = pd.DataFrame({
                '問題': papers[papers['issue'].isin(issues)]['issue'],
                'リスク値': papers[papers['issue'].isin(issues)]['risk_description'].str.extract('(\d+)').astype(float)
            })
            
            if not chart_data.empty:
                st.bar_chart(chart_data.set_index('問題'))
        
        # ダウンロードボタン
        st.download_button("レポートをダウンロード", "\n".join(report), f"歯科リスク評価_{today}.md")