import streamlit as st
import requests
import json
import pandas as pd
import sys
import os

# 親ディレクトリへのパスを追加して、メインのモジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pubmed_api.pyモジュールをインポート
try:
    from pubmed_api import fetch_pubmed_studies, get_pubmed_article_details, update_papers_csv
except ImportError:
    st.error("pubmed_api.pyモジュールをインポートできませんでした。ファイルが正しく配置されているか確認してください。")
    
    # 念のため関数のスタブを定義
    def fetch_pubmed_studies(*args, **kwargs):
        return {"error": "モジュールが見つかりません"}
    
    def get_pubmed_article_details(*args, **kwargs):
        return []
    
    def update_papers_csv(*args, **kwargs):
        return pd.DataFrame()

def test_pubmed_connection():
    """
    PubMed APIへの基本的な接続テストを実行します。
    """
    try:
        # 基本的なAPIエンドポイントへの接続テスト
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json"
        response = requests.get(url)
        response.raise_for_status()
        
        # レスポンスが有効なJSONかチェック
        result = response.json()
        
        if 'einforesult' in result:
            return {
                "status": "success",
                "message": "PubMed API基本接続テスト成功",
                "details": f"ステータスコード: {response.status_code}, API Version: {result.get('einforesult', {}).get('version', '不明')}"
            }
        else:
            return {
                "status": "warning",
                "message": "PubMed APIは応答していますが、予期しない形式です",
                "details": f"ステータスコード: {response.status_code}, レスポンス: {response.text[:200]}..."
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": "PubMed APIへの接続に失敗しました",
            "details": str(e)
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "APIレスポンスが有効なJSONではありません",
            "details": f"ステータスコード: {response.status_code}, レスポンス: {response.text[:200]}..."
        }

def perform_test_search(keyword="orthodontic AND malocclusion", max_results=2):
    """
    テスト検索を実行し、結果を返します。
    
    Parameters:
    -----------
    keyword : str
        検索キーワード
    max_results : int
        取得する最大結果数
        
    Returns:
    --------
    dict
        テスト結果を含む辞書
    """
    try:
        # 検索実行
        search_results = fetch_pubmed_studies(keyword, max_results, 30)
        
        if not search_results or 'esearchresult' not in search_results:
            return {
                "status": "error",
                "message": "検索結果が空または無効な形式です",
                "details": str(search_results)
            }
        
        pmid_list = search_results.get('esearchresult', {}).get('idlist', [])
        
        if not pmid_list:
            return {
                "status": "warning",
                "message": "検索結果が0件でした",
                "details": f"キーワード '{keyword}' での検索結果はありませんでした"
            }
        
        # 取得したPMIDの詳細情報を取得
        articles = get_pubmed_article_details(pmid_list)
        
        if not articles:
            return {
                "status": "warning",
                "message": "論文詳細の取得に失敗しました",
                "details": f"PMID: {', '.join(pmid_list)}"
            }
        
        # 成功
        return {
            "status": "success",
            "message": f"{len(articles)}件の論文を正常に取得しました",
            "details": articles,
            "pmid_list": pmid_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": "テスト検索実行中にエラーが発生しました",
            "details": str(e)
        }

# Streamlitアプリケーションのメイン部分
st.title("PubMed API連携デバッグツール")
st.write("このツールでPubMed API連携が適切に機能しているか確認できます")

with st.expander("1. 基本接続テスト", expanded=True):
    if st.button("基本接続テスト実行"):
        with st.spinner("PubMed APIに接続中..."):
            result = test_pubmed_connection()
            
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "warning":
                st.warning(result["message"])
            else:
                st.error(result["message"])
            
            st.code(result["details"])

with st.expander("2. テスト検索実行", expanded=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        test_keyword = st.text_input("テスト検索キーワード", "orthodontic AND malocclusion")
    with col2:
        test_max_results = st.number_input("最大結果数", min_value=1, max_value=10, value=2)
    
    if st.button("テスト検索実行"):
        with st.spinner("検索中..."):
            result = perform_test_search(test_keyword, test_max_results)
            
            if result["status"] == "success":
                st.success(result["message"])
                
                # 取得した論文情報を表示 (修正版: ネストしたexpanderを使わない)
                articles = result["details"]
                for i, article in enumerate(articles):
                    # 論文タイトルと基本情報
                    st.markdown(f"### 論文 {i+1}: {article.get('title', '不明')}")
                    st.markdown(f"**著者:** {article.get('authors', '不明')}")
                    st.markdown(f"**掲載誌:** {article.get('journal', '不明')} ({article.get('publication_year', '不明')})")
                    st.markdown(f"**DOI:** {article.get('doi', '不明')}")
                    st.markdown(f"**PMID:** {article.get('pmid', '不明')}")
                    st.markdown(f"**研究タイプ:** {article.get('study_type', '不明')}")
                    st.markdown(f"**URL:** [PubMed]({article.get('url', '#')})")
                    
                    # 抄録の表示（エクスパンダーではなくチェックボックスと条件付き表示を使用）
                    if 'abstract' in article and article['abstract']:
                        show_abstract = st.checkbox(f"抄録を表示 (論文 {i+1})", key=f"abstract_{i}")
                        if show_abstract:
                            st.markdown("**抄録:**")
                            st.markdown(f"```\n{article['abstract']}\n```")
                    
                    st.markdown("---")  # 論文間の区切り線
            elif result["status"] == "warning":
                st.warning(result["message"])
                st.code(result["details"])
            else:
                st.error(result["message"])
                st.code(result["details"])

with st.expander("3. 論文データベース確認", expanded=True):
    try:
        papers_df = pd.read_csv('papers.csv')
        st.write(f"**現在のデータベース統計**")
        st.write(f"- 総論文数: {len(papers_df)}")
        
        # 問題別の分布
        if 'issue' in papers_df.columns:
            issue_counts = papers_df['issue'].value_counts()
            st.write("**問題別の論文数:**")
            st.bar_chart(issue_counts)
        
        # エビデンスレベル分布
        if 'evidence_level' in papers_df.columns:
            evidence_counts = papers_df['evidence_level'].value_counts()
            st.write("**エビデンスレベル分布:**")
            st.bar_chart(evidence_counts)
        
        # データベースプレビュー (ネストなしで表示)
        st.markdown("### データベース内容プレビュー")
        show_preview = st.checkbox("データベース内容を表示", value=False)
        if show_preview:
            st.dataframe(papers_df)
    except Exception as e:
        st.error(f"論文データベース読み込みエラー: {str(e)}")

with st.expander("4. トラブルシューティング情報", expanded=False):
    st.markdown("""
    ## PubMed API連携のトラブルシューティング
    
    ### 基本接続エラーの場合
    - インターネット接続を確認してください
    - プロキシ設定が必要な環境では適切に設定してください
    - PubMedサーバーの状態を確認してください（一時的にダウンしている可能性）
    
    ### レート制限エラーの場合
    - APIリクエストの頻度を下げてください
    - NCBIアカウントを作成し、APIキーを取得・設定することで制限が緩和されます
    - APIキーは `pubmed_api.py` 内の関数に設定できます
    
    ### 検索結果がない場合
    - より一般的なキーワードで試してください
    - 検索条件が厳しすぎないか確認してください
    - PubMedの検索構文が正しいか確認してください
    
    ### 論文詳細取得エラーの場合
    - PMIDが有効かつ存在することを確認してください
    - XMLパース関連のエラーが発生した場合は、PubMedのレスポンス形式が変更された可能性があります
    """)

    st.markdown("---")
    
    st.markdown("""
    ### 環境情報
    
    以下の情報をデバッグ時に確認すると役立ちます：
    """)
    
    # 環境情報の表示
    import platform
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Python情報**")
        st.code(f"Python バージョン: {platform.python_version()}\nOS: {platform.system()} {platform.release()}")
    
    with col2:
        st.write("**ライブラリ情報**")
        import pandas as pd
        import streamlit as st
        import requests
        
        st.code(f"pandas: {pd.__version__}\nstreamlit: {st.__version__}\nrequests: {requests.__version__}")
