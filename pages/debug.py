import streamlit as st
import requests
import json
import os
import sys

# タイトル表示
st.title("PubMed API連携デバッグツール")
st.write("このツールでPubMed API連携が適切に機能しているか確認できます")

# 基本接続テスト
st.header("1. 基本接続テスト")

if st.button("基本接続テスト実行"):
    with st.spinner("PubMed APIに接続中..."):
        try:
            # 基本的なAPIエンドポイントへの接続テスト
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json"
            
            # APIキーの取得を試みる
            api_key = None
            try:
                api_key = st.secrets.get("NCBI_API_KEY")
                if api_key:
                    st.info("Streamlit CloudのシークレットからAPIキーを取得しました")
            except:
                pass
            
            if not api_key:
                api_key = os.environ.get("NCBI_API_KEY")
                if api_key:
                    st.info("環境変数からAPIキーを取得しました")
            
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
                st.json(result)
            else:
                st.warning("PubMed APIは応答していますが、予期しない形式です")
                st.code(response.text)
        
        except requests.exceptions.RequestException as e:
            st.error(f"PubMed APIへの接続に失敗しました: {str(e)}")
        
        except json.JSONDecodeError:
            st.error("APIレスポンスが有効なJSONではありません")
            st.code(response.text[:500])

# 環境情報表示
st.header("2. 環境情報")

col1, col2 = st.columns(2)
with col1:
    st.write("**Python情報**")
    import platform
    st.code(f"Python バージョン: {platform.python_version()}\nOS: {platform.platform()}")

with col2:
    st.write("**APIキー状態**")
    try:
        has_secret_key = "NCBI_API_KEY" in st.secrets
        st.write(f"Streamlitシークレット: {'✅ 設定済み' if has_secret_key else '❌ 未設定'}")
    except:
        st.write("Streamlitシークレット: ❌ 未設定")
    
    has_env_key = "NCBI_API_KEY" in os.environ
    st.write(f"環境変数: {'✅ 設定済み' if has_env_key else '❌ 未設定'}")

# トラブルシューティング情報
st.header("3. トラブルシューティング情報")

with st.expander("APIキー設定方法"):
    st.markdown("""
    ### Streamlit Cloudでのシークレット設定方法
    
    1. Streamlitダッシュボードで該当アプリの「⋮」メニューをクリック
    2. 「Settings」を選択
    3. 「Secrets」セクションに移動
    4. 以下の内容を追加：
       ```
       NCBI_API_KEY = "your_api_key_here"
       ```
    5. 「Save」をクリックして保存
    """)

with st.expander("接続エラーのトラブルシューティング"):
    st.markdown("""
    ### 接続エラーの一般的な原因
    
    1. **APIキーの問題**
       - APIキーが正しく入力されているか確認
       - APIキーが有効か確認（NCBIダッシュボードで確認）
    
    2. **ネットワークの問題**
       - インターネット接続が有効か確認
       - プロキシ設定が必要な環境の場合は設定を確認
    
    3. **PubMedサーバーの問題**
       - PubMedサーバーが一時的にダウンしている可能性
       - 時間をおいて再試行
    
    4. **レート制限**
       - APIリクエストの頻度が高すぎる場合、一時的に制限される
       - APIキーを設定することでレート制限が緩和される
    """)
