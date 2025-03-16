import streamlit as st
import requests
import json
import pandas as pd
import sys
import os
import time

# 親ディレクトリへのパスを追加して、メインのモジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# PubMed API関連のモジュールをインポート
try:
    from pubmed_api import fetch_pubmed_studies, get_pubmed_article_details, update_papers_csv
    api_modules_imported = True
except ImportError as e:
    st.error(f"pubmed_api.pyモジュールのインポートエラー: {str(e)}")
    api_modules_imported = False

# バッチ処理モジュールをインポート
try:
    from batch_pubmed_fetch import ORTHO_KEYWORDS
    batch_module_imported = True
except ImportError as e:
    st.warning(f"batch_pubmed_fetch.pyモジュールのインポートエラー: {str(e)}")
    batch_module_imported = False
    # デフォルトのキーワードリスト（バックアップ用）
    ORTHO_KEYWORDS = [
        "dental crowding evidence",
        "open bite treatment orthodontic",
        "deep bite treatment orthodontic", 
        "orthodontic treatment timing"
    ]

# APIキーを取得する関数
def get_api_key():
    """
    APIキーを環境変数またはStreamlitシークレットから取得します。
    """
    # 1. Streamlit Cloudsのシークレットから取得を試みる
    try:
        api_key = st.secrets.get("NCBI_API_KEY")
        if api_key:
            return api_key, "Streamlitシークレット"
    except:
        pass
    
    # 2. 環境変数から取得を試みる
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        return api_key, "環境変数"
    
    return None, "なし"

# タイトル表示
st.title("PubMed API連携デバッグツール")
st.write("このツールでPubMed API連携が適切に機能しているか確認できます")

# APIキー情報を取得
api_key, api_key_source = get_api_key()

# 1. 基本接続テスト
with st.expander("1. 基本接続テスト", expanded=True):
    st.write(f"**APIキー状態:** {'✅ 設定済み' if api_key else '❌ 未設定'} (ソース: {api_key_source})")
    
    if st.button("基本接続テスト実行"):
        with st.spinner("PubMed APIに接続中..."):
            try:
                # 基本的なAPIエンドポイントへの接続テスト
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json"
                
                # リクエストパラメータ
                params = {}
                if api_key:
                    params['api_key'] = api_key
                
                # リクエスト送信
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                # レスポンスが有効なJSONかチェック
                result = response.json()
                
                if 'einforesult' in result:
                    st.success("PubMed API基本接続テスト成功")
                    
                    with st.expander("API応答の詳細"):
                        st.json(result)
                else:
                    st.warning("PubMed APIは応答していますが、予期しない形式です")
                    st.code(response.text)
            
            except requests.exceptions.RequestException as e:
                st.error(f"PubMed APIへの接続に失敗しました: {str(e)}")
            
            except json.JSONDecodeError:
                st.error("APIレスポンスが有効なJSONではありません")
                st.code(response.text[:500])

# 2. テスト検索
with st.expander("2. テスト検索実行", expanded=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        test_keyword = st.text_input("テスト検索キーワード", "orthodontic AND malocclusion")
    with col2:
        test_max_results = st.number_input("最大結果数", min_value=1, max_value=10, value=2)
    
    if st.button("テスト検索実行"):
        if not api_modules_imported:
            st.error("pubmed_api.pyモジュールがインポートできないため、検索を実行できません")
        else:
            with st.spinner("検索中..."):
                try:
                    # 検索実行
                    search_results = fetch_pubmed_studies(test_keyword, test_max_results, 90)
                    
                    if 'esearchresult' in search_results and 'idlist' in search_results['esearchresult']:
                        pmid_list = search_results['esearchresult']['idlist']
                        
                        if pmid_list:
                            st.success(f"{len(pmid_list)}件の論文が見つかりました")
                            
                            # 論文詳細の取得
                            articles = get_pubmed_article_details(pmid_list)
                            
                            if articles:
                                # 取得した論文情報を表示
                                for i, article in enumerate(articles):
                                    st.markdown(f"### 論文 {i+1}: {article.get('title', '不明')}")
                                    st.markdown(f"**著者:** {article.get('authors', '不明')}")
                                    st.markdown(f"**掲載誌:** {article.get('journal', '不明')} ({article.get('publication_year', '不明')})")
                                    st.markdown(f"**DOI:** {article.get('doi', '不明')}")
                                    st.markdown(f"**PMID:** {article.get('pmid', '不明')}")
                                    st.markdown(f"**研究タイプ:** {article.get('study_type', '不明')}")
                                    st.markdown(f"**URL:** [PubMed]({article.get('url', '#')})")
                                    
                                    # 抄録の表示
                                    if 'abstract' in article and article['abstract']:
                                        show_abstract = st.checkbox(f"抄録を表示 (論文 {i+1})", key=f"abstract_{i}")
                                        if show_abstract:
                                            st.markdown("**抄録:**")
                                            st.text_area("", article['abstract'], height=150, key=f"abstract_text_{i}", disabled=True)
                                    
                                    st.markdown("---")  # 論文間の区切り線
                            else:
                                st.warning("論文詳細の取得に失敗しました")
                        else:
                            st.warning(f"キーワード '{test_keyword}' での検索結果はありませんでした")
                    else:
                        st.error("検索結果が無効な形式です")
                        st.json(search_results)
                
                except Exception as e:
                    st.error(f"テスト検索実行中にエラーが発生しました: {str(e)}")

# 3. 論文データベース確認
with st.expander("3. 論文データベース確認", expanded=True):
    try:
        if os.path.exists('papers.csv'):
            papers_df = pd.read_csv('papers.csv')
            st.write(f"**現在のデータベース統計**")
            st.write(f"- 総論文数: {len(papers_df)}件")
            
            # 問題別の分布
            if 'issue' in papers_df.columns:
                issue_counts = papers_df['issue'].value_counts()
                st.write("**問題別の論文数:**")
                st.bar_chart(issue_counts)
            
            # エビデンスレベル分布
            if 'evidence_level' in papers_df.columns:
                evidence_counts = papers_df['evidence_level'].value_counts()
                st.write("**エビデンスレベル別の論文数:**")
                st.bar_chart(evidence_counts)
            
            # データベースプレビュー
            st.markdown("### データベース内容プレビュー")
            show_preview = st.checkbox("データベース内容を表示", value=False)
            if show_preview:
                st.dataframe(papers_df)
        else:
            st.warning("papers.csvファイルが見つかりません。データベースは空です。")
    except Exception as e:
        st.error(f"論文データベース読み込みエラー: {str(e)}")

# 4. 論文データ一括取得
with st.expander("4. 論文データ一括取得", expanded=True):
    st.markdown("""
    ### PubMed APIから論文データを一括取得
    
    このツールを使用して、事前に複数の論文データを取得し、データベースを充実させることができます。
    """)
    
    # パラメータ設定
    col1, col2 = st.columns(2)
    with col1:
        max_results = st.slider("キーワードごとの最大取得数", 5, 50, 20)
        days_recent = st.slider("過去の日数", 30, 1095, 365, 
                               help="何日前までの論文を検索するか（1年=365日、3年=1095日）")
    with col2:
        pause_seconds = st.slider("リクエスト間隔（秒）", 1, 10, 3, 
                                help="APIレート制限を回避するための待機時間")
        keyword_option = st.radio("キーワード選択", ["デフォルト", "カスタム"])
    
    # カスタムキーワード入力欄
    if keyword_option == "カスタム":
        custom_keywords = st.text_area("カスタムキーワード（1行に1つ）", 
                                      height=150,
                                      placeholder="例:\northodontic treatment\ndental crowding")
    
    # 実行ボタン
    if st.button("論文データ取得開始", type="primary"):
        if not api_modules_imported:
            st.error("pubmed_api.pyモジュールがインポートできないため、一括取得を実行できません")
        else:
            # 実行確認
            keywords = ORTHO_KEYWORDS
            if keyword_option == "カスタム" and custom_keywords.strip():
                keywords = [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            
            st.write(f"**{len(keywords)}個**のキーワードを使用して、キーワードごとに最大**{max_results}件**の論文を取得します")
            
            # 進捗表示用のプレースホルダー
            progress_placeholder = st.empty()
            log_placeholder = st.empty()
            
            with st.spinner("論文データ取得中..."):
                # 進捗バーの初期化
                progress_bar = progress_placeholder.progress(0)
                
                # カウンター初期化
                total_articles = 0
                total_new_articles = 0
                
                # キーワードごとに処理
                for i, keyword in enumerate(keywords):
                    # 進捗更新
                    progress = (i / len(keywords))
                    progress_bar.progress(progress)
                    
                    # キーワード表示
                    log_placeholder.markdown(f"**処理中:** '{keyword}' ({i+1}/{len(keywords)})")
                    
                    try:
                        # 検索実行
                        search_results = fetch_pubmed_studies(keyword, max_results, days_recent)
                        
                        if 'esearchresult' in search_results and 'idlist' in search_results['esearchresult']:
                            pmid_list = search_results['esearchresult']['idlist']
                            
                            if pmid_list:
                                log_placeholder.markdown(f"  **{len(pmid_list)}件**の論文が見つかりました")
                                
                                # 論文詳細の取得
                                articles = get_pubmed_article_details(pmid_list)
                                
                                # CSVに追加
                                if articles:
                                    # CSVファイルの存在確認
                                    csv_exists = os.path.exists('papers.csv')
                                    
                                    # 更新前のサイズを記録
                                    if csv_exists:
                                        old_df = pd.read_csv('papers.csv')
                                        old_size = len(old_df)
                                    else:
                                        old_size = 0
                                    
                                    # CSVファイルを更新
                                    updated_df = update_papers_csv(articles)
                                    
                                    # 新規追加論文数
                                    if csv_exists and len(updated_df) > 0:
                                        new_articles = len(updated_df) - old_size
                                    else:
                                        new_articles = len(articles)
                                    
                                    total_articles += len(articles)
                                    total_new_articles += new_articles
                                    
                                    log_placeholder.markdown(f"  **{new_articles}件**の新規論文をデータベースに追加しました")
                                else:
                                    log_placeholder.warning("  論文詳細の取得に失敗しました")
                            else:
                                log_placeholder.info("  該当する論文が見つかりませんでした")
                        else:
                            log_placeholder.error(f"  検索結果が無効な形式です")
                    
                    except Exception as e:
                        log_placeholder.error(f"  エラーが発生しました: {str(e)}")
                    
                    # 次のリクエストまで待機（レート制限対策）
                    if i < len(keywords) - 1:
                        # APIキーがある場合は待機時間を短縮可能
                        actual_pause = max(1, pause_seconds // 3) if api_key else pause_seconds
                        
                        for remaining in range(actual_pause, 0, -1):
                            log_placeholder.markdown(f"  次のキーワードまで**{remaining}秒**待機中...")
                            time.sleep(1)
                
                # 完了
                progress_bar.progress(1.0)
                
                # 成功メッセージ
                st.success(f"データ取得が完了しました! {total_new_articles}件の新しい論文がデータベースに追加されました。")
                
                # データベースの最新状態を表示
                try:
                    if os.path.exists('papers.csv'):
                        updated_df = pd.read_csv('papers.csv')
                        st.write(f"現在のデータベース総論文数: {len(updated_df)}件")
                        
                        # 問題別の分布
                        if 'issue' in updated_df.columns:
                            issue_counts = updated_df['issue'].value_counts()
                            st.write("**問題別の論文数:**")
                            st.bar_chart(issue_counts)
                        
                        # エビデンスレベル分布
                        if 'evidence_level' in updated_df.columns:
                            evidence_counts = updated_df['evidence_level'].value_counts()
                            st.write("**エビデンスレベル別の論文数:**")
                            st.bar_chart(evidence_counts)
                except Exception as e:
                    st.error(f"データベース統計の取得中にエラーが発生しました: {str(e)}")

# 5. 環境情報
with st.expander("5. システム情報", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Python情報**")
        import platform
        st.code(f"Python バージョン: {platform.python_version()}\nOS: {platform.platform()}")
    
    with col2:
        st.write("**ライブラリ情報**")
        try:
            import pandas as pd
            import streamlit as st
            import requests
            
            st.code(f"pandas: {pd.__version__}\nstreamlit: {st.__version__}\nrequests: {requests.__version__}")
        except Exception as e:
            st.code(f"ライブラリ情報の取得エラー: {str(e)}")
    
    st.write("**モジュール読み込み状態**")
    st.write(f"- pubmed_api.py: {'✅ 正常' if api_modules_imported else '❌ エラー'}")
    st.write(f"- batch_pubmed_fetch.py: {'✅ 正常' if batch_module_imported else '❌ エラー'}")

# 6. トラブルシューティング情報
with st.expander("6. トラブルシューティング", expanded=False):
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
