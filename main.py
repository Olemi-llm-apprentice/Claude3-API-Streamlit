import streamlit as st
import anthropic
from claude import ClaudeLlm  # claude.py から ClaudeLlm クラスをインポート
import os
import base64

# 環境変数からAPIキーを取得する代わりに、サイドバーから入力を受け取る
api_key = st.sidebar.text_input("APIキーを入力してください", type="password", help="APIキーをここに入力してください。")

# APIキーが入力されていない場合は、警告を表示して処理を中断
if not api_key:
    st.error("APIキーが必要です。サイドバーから入力してください。")
else:
    client = anthropic.Anthropic(api_key=api_key)
    
# モード選択
mode = st.sidebar.radio("モードを選択してください", ('Text', 'Vision'))

if mode == 'Text':
    # Streamlitアプリのタイトル
    st.title("Claude3-Streamlit")
    # ユーザー入力を受け取る
    user_input = st.text_area("テキストを入力してください", placeholder="日本で２番目に高い山は？名前だけ教えて", height=200)
    # 送信ボタンが押されたときの処理
    if st.button("送信"):
        # ClaudeLlm クラスのインスタンスを作成
        claude = ClaudeLlm(client, user_input)
        
        col1, col2 = st.columns(2)  # 画面を2つのカラムに分割
        with col1:
            st.write("Opus応答:")
            st.write_stream(claude.generate_responses("claude-3-opus-20240229"))
        with col2:
            st.write("Sonnet応答:")
            st.write_stream(claude.generate_responses("claude-3-sonnet-20240229"))
        # コスト計算結果を表示
        st.table(claude.cost_df)
        _, jpy_rate = claude.convert_usd_to_jpy(1)  # 1USDの為替レートを取得するためのダミー呼び出し
        st.write(jpy_rate)

elif mode == 'Vision':
    st.title("Claude3-Streamlit-vision")
    uploaded_file = st.file_uploader("画像ファイルを選択してください", type=["jpg", "jpeg", "png", "gif"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)
        # ファイルの拡張子を取得
        prompt = st.text_area("テキストを入力してください", placeholder="画像について説明してください。", height=200)
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        # 拡張子に基づいてメディアタイプを設定
        if file_extension in [".jpg", ".jpeg"]:
            image_media_type = "image/jpeg"
        elif file_extension == ".png":
            image_media_type = "image/png"
        elif file_extension == ".gif":
            image_media_type = "image/gif"
        else:
            st.error("サポートされていないファイル形式です。")
            st.stop()

        image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")

        # prompt の設定

        user_input = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_media_type,
                    "data": image_data,
                },
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
        if st.button("送信"):
            # ClaudeLlm クラスのインスタンスを作成
            claude = ClaudeLlm(client, user_input)
            col1, col2 = st.columns(2)  # 画面を2つのカラムに分割
            with col1:
                st.write("Opus応答:")
                st.write_stream(claude.generate_responses("claude-3-opus-20240229"))
            with col2:
                st.write("Sonnet応答:")
                st.write_stream(claude.generate_responses("claude-3-sonnet-20240229"))
            # コスト計算結果を表示
            st.table(claude.cost_df)
            _, jpy_rate = claude.convert_usd_to_jpy(1)  # 1USDの為替レートを取得するためのダミー呼び出し
            st.write(jpy_rate)

