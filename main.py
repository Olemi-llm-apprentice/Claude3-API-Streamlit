import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from anthropic.types.message_stream_event import MessageStartEvent, MessageDeltaEvent, ContentBlockDeltaEvent
import time
import pandas as pd
from forex_python.converter import CurrencyRates

# Anthropicクライアントの初期化
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# Streamlitアプリのタイトル
st.title("Claude3-Streamlit")

# ユーザー入力を受け取る
user_input = st.text_input("質問を入力してください", "日本で２番目に高い山は？名前だけ教えて")

# コスト計算結果を格納するDataFrameを初期化
cost_df = pd.DataFrame(columns=["Model", "Input Tokens", "Output Tokens", "Input Cost", "Output Cost", "Total Cost","総計_円換算","処理時間"])
# 為替レートを取得してUSDからJPYへ換算する関数
def convert_usd_to_jpy(usd_amount):
    c = CurrencyRates()
    try:
        rate = c.get_rate('USD', 'JPY')
    except Exception as e:
        print(f"為替レートの取得に失敗しました: {e}. フォールバック為替レートを使用します。")
        rate = 150  # フォールバックとして使用する為替レート
    return usd_amount * rate

def calculate_cost(model, input_tokens, output_tokens):
    # トークンごとのコストを定義
    token_costs = {
        "Claude 3 Opus": {"input": 0.000015, "output": 0.000075},
        "Claude 3 Sonnet": {"input": 0.000003, "output": 0.000015},
    }
    
    # 指定されたモデルのコストを取得
    model_costs = token_costs[model]
    
    # コストを計算
    input_cost = input_tokens * model_costs["input"]
    output_cost = output_tokens * model_costs["output"]
    total_cost = input_cost + output_cost
    
    return input_cost, output_cost, total_cost

# 第一のgenerate_responses関数
def generate_responses_sonnet():
    global cost_df  # これを追加
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
                # input_tokens_placeholder1.write(f"Input tokens: {input_tokens}")
            elif isinstance(event, MessageDeltaEvent):
                # MessageDeltaEventから直接usage情報を取得
                output_tokens = event.usage.output_tokens
                # プレースホルダーに output_tokens を表示
                # output_tokens_placeholder1.write(f"Output tokens: {output_tokens}")
            elif isinstance(event, ContentBlockDeltaEvent):
                return_text = event.delta.text
                yield return_text
                
    input_cost, output_cost, total_cost = calculate_cost("Claude 3 Sonnet", input_tokens, output_tokens)
    jpy_total_cost = convert_usd_to_jpy(total_cost) 
    end_time = time.time()
    response_time = end_time - start_time
    # DataFrameに結果を追加
    new_row = {
        "Model": "Claude 3 Sonnet",
        "Input Tokens": input_tokens,
        "Output Tokens": output_tokens,
        "Input Cost": f"${input_cost:.6f}",
        "Output Cost": f"${output_cost:.6f}",
        "Total Cost": f"${total_cost:.6f}",
        "総計_円換算": f"¥{jpy_total_cost:.3f}", 
        "処理時間": f"{response_time:.2f}秒"  # 応答テキストをDataFrameに追加
    }
    new_row_df = pd.DataFrame([new_row])
    cost_df = pd.concat([cost_df, new_row_df], ignore_index=True)

# 第二のgenerate_responses関数
def generate_responses_opus():
    global cost_df  # これを追加
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
                # input_tokens_placeholder2.write(f"入力tokens: {input_tokens}")
            elif isinstance(event, MessageDeltaEvent):
                # MessageDeltaEventから直接usage情報を取得
                output_tokens = event.usage.output_tokens
                # プレースホルダーに output_tokens を表示
                # output_tokens_placeholder2.write(f"出力tokens: {output_tokens}")
            elif isinstance(event, ContentBlockDeltaEvent):
                return_text = event.delta.text
                yield return_text
                
    input_cost, output_cost, total_cost = calculate_cost("Claude 3 Opus", input_tokens, output_tokens)
    jpy_total_cost = convert_usd_to_jpy(total_cost) 
    end_time = time.time()
    response_time = end_time - start_time
    # DataFrameに結果を追加
    new_row = {
        "Model": "Claude 3 opus",
        "Input Tokens": input_tokens,
        "Output Tokens": output_tokens,
        "Input Cost": f"${input_cost:.6f}",
        "Output Cost": f"${output_cost:.6f}",
        "Total Cost": f"${total_cost:.6f}",
        "総計_円換算": f"¥{jpy_total_cost:.3f}", 
        "処理時間": f"{response_time:.2f}秒" 
    }
    new_row_df = pd.DataFrame([new_row])
    cost_df = pd.concat([cost_df, new_row_df], ignore_index=True)

# DataFrameを表示


# 送信ボタンが押されたときの処理
if st.button("送信"):
    col1, col2 = st.columns(2)  # 画面を2つのカラムに分割
    with col1:
        st.write("Sonnet応答:")
        st.write_stream(generate_responses_sonnet())  
    with col2:
        st.write("Opus応答:")
        st.write_stream(generate_responses_opus())
    
    st.table(cost_df)

