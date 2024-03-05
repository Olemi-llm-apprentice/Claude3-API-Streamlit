import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from anthropic.types.message_stream_event import MessageStartEvent, MessageDeltaEvent, ContentBlockDeltaEvent
import time


# Anthropicクライアントの初期化
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# Streamlitアプリのタイトル
st.title("Claude3-Streamlit")

# ユーザー入力を受け取る
user_input = st.text_input("質問を入力してください", "日本で２番目に高い山は？")

# 第一のgenerate_responses関数
def generate_responses_sonnet():
    start_time = time.time()
    # Claudeに質問を解析させるリクエストを作成
    with client.messages.stream(
        model="claude-3-sonnet-20240229",  # モデル指定
        max_tokens=1024,  # 最大トークン数
        messages=[{"role": "user", "content": user_input}],
    ) as stream:
        for event in stream:
            if isinstance(event, MessageStartEvent):
                # usage情報を取得
                usage_info = event.message.usage
                input_tokens = usage_info.input_tokens
                input_tokens_placeholder1.write(f"Input tokens: {input_tokens}")
            elif isinstance(event, MessageDeltaEvent):
                # MessageDeltaEventから直接usage情報を取得
                output_tokens = event.usage.output_tokens
                # プレースホルダーに output_tokens を表示
                output_tokens_placeholder1.write(f"Output tokens: {output_tokens}")
            elif isinstance(event, ContentBlockDeltaEvent):
                return_text = event.delta.text
                yield return_text
    end_time = time.time()
    response_time = end_time - start_time
    response_time_sonnet.write(f"処理時間: {response_time:.2f}秒")
    return
# 第二のgenerate_responses関数
def generate_responses_opus():
    start_time = time.time()
    # Claudeに質問を解析させるリクエストを作成
    with client.messages.stream(
        model="claude-3-opus-20240229",  # モデル指定
        max_tokens=1024,  # 最大トークン数
        messages=[{"role": "user", "content": user_input}],
    ) as stream:
        for event in stream:
            if isinstance(event, MessageStartEvent):
                # usage情報を取得
                usage_info = event.message.usage
                input_tokens = usage_info.input_tokens
                input_tokens_placeholder2.write(f"入力tokens: {input_tokens}")
            elif isinstance(event, MessageDeltaEvent):
                # MessageDeltaEventから直接usage情報を取得
                output_tokens = event.usage.output_tokens
                # プレースホルダーに output_tokens を表示
                output_tokens_placeholder2.write(f"出力tokens: {output_tokens}")
            elif isinstance(event, ContentBlockDeltaEvent):
                return_text = event.delta.text
                yield return_text
    end_time = time.time()
    response_time = end_time - start_time
    response_time_opus.write(f"処理時間: {response_time:.2f}秒")
    return

# 送信ボタンが押されたときの処理
if st.button("送信"):
    col1, col2 = st.columns(2)  # 画面を2つのカラムに分割
    with col1:
        # input_tokens と output_tokens を表示するためのプレースホルダーを作成
        input_tokens_placeholder1 = st.empty()
        output_tokens_placeholder1 = st.empty()
        response_time_sonnet = st.empty()
        st.write("Sonnetモデルの応答:")
        st.write_stream(generate_responses_sonnet())  
    with col2:
        input_tokens_placeholder2 = st.empty()
        output_tokens_placeholder2 = st.empty()
        response_time_opus = st.empty()
        st.write("Opusモデルの応答:")
        st.write_stream(generate_responses_opus()) 

