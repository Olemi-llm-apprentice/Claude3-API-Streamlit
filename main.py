import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

# GUIウィンドウを表示しないようにするコードはStreamlitでは不要なため削除

# Anthropicクライアントの初期化
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# Streamlitアプリのタイトル
st.title("日本の山についての質問")

# ユーザー入力を受け取る
user_input = st.text_input("質問を入力してください", "日本で２番目に高い山は？")

def generate_responses():
    # Claudeに質問を解析させるリクエストを作成
    with client.messages.stream(
        model="claude-3-opus-20240229",  # モデル指定
        max_tokens=1024,  # 最大トークン数
        messages=[{"role": "user", "content": user_input}],
    ) as stream:
        for text in stream.text_stream:
            yield text

if st.button("送信"):
    # 応答をストリームで表示
    st.write_stream(generate_responses())