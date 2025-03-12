import streamlit as st
import pandas as pd

# 論文データ読み込み
papers = pd.read_csv('papers.csv')

# タイトル表示
st.title('🦷 歯科エビデンス生成システム')

# 入力フォーム
with st.form("input_form"):
    age = st.number_input('患者年齢', min_value=6, max_value=100)
    issues = st.multiselect('歯列問題', papers['issue'].unique())
    submitted = st.form_submit_button("レポート生成")

# レポート作成
if submitted:
    report = []
    for issue in issues:
        filtered = papers[papers['issue'] == issue]
        if not filtered.empty:
            report.append(f"## {issue}のリスク")
            for _, row in filtered.iterrows():
                report.append(f"- {row['risk_description']} (DOI: {row['doi']})")
    
    st.markdown("\n".join(report))
    st.download_button("レポート出力", "\n".join(report), "report.md")