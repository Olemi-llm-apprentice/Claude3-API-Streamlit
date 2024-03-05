import pandas as pd
from forex_python.converter import CurrencyRates
import time
import anthropic
from anthropic.types.message_stream_event import MessageStartEvent, MessageDeltaEvent, ContentBlockDeltaEvent


class ClaudeLlm:
    def __init__(self, client, user_input):
        self.client = client
        self.user_input = user_input
        self.cost_df = pd.DataFrame(columns=["Model", "Input Tokens", "Output Tokens", "Input Cost", "Output Cost", "Total Cost", "総計_円換算", "処理時間"])

    def convert_usd_to_jpy(self, usd_amount):
        c = CurrencyRates()
        try:
            rate = c.get_rate('USD', 'JPY')
            jpy_rate = (f"為替レート: {rate:.2f}円/ドル")
            return usd_amount * rate, jpy_rate
        except Exception as e:
            rate = 150  # フォールバックとして使用する為替レート
            jpy_rate = (f"為替レート: {rate:.2f}円/ドル想定")
            return usd_amount * rate, jpy_rate

    def calculate_cost(self, model, input_tokens, output_tokens):
        token_costs = {
            "claude-3-opus-20240229": {"input": 0.000015, "output": 0.000075},
            "claude-3-sonnet-20240229": {"input": 0.000003, "output": 0.000015},
        }
        model_costs = token_costs[model]
        input_cost = input_tokens * model_costs["input"]
        output_cost = output_tokens * model_costs["output"]
        total_cost = input_cost + output_cost
        return input_cost, output_cost, total_cost

    def generate_responses(self, model_name):
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0
        try:
            with self.client.messages.stream(
                model=model_name,
                max_tokens=1024,
                messages=[{"role": "user", "content": self.user_input}],
            ) as stream:
                for event in stream:
                    if isinstance(event, MessageStartEvent):
                        usage_info = event.message.usage
                        input_tokens = usage_info.input_tokens
                    elif isinstance(event, MessageDeltaEvent):
                        output_tokens = event.usage.output_tokens
                    elif isinstance(event, ContentBlockDeltaEvent):
                        return_text = event.delta.text
                        yield return_text
        except anthropic.APIStatusError as e:
            error_response = e.response.json()
            if 'error' in error_response and error_response['error'].get('type') == 'overloaded_error':
                return "APIが過負荷状態です。しばらくしてから再試行してください。"

        input_cost, output_cost, total_cost = self.calculate_cost(model_name, input_tokens, output_tokens)
        jpy_total_cost, _ = self.convert_usd_to_jpy(total_cost)
        end_time = time.time()
        response_time = end_time - start_time
        new_row = {
            "Model": model_name,
            "Input Tokens": input_tokens,
            "Output Tokens": output_tokens,
            "Input Cost": f"${input_cost:.6f}",
            "Output Cost": f"${output_cost:.6f}",
            "Total Cost": f"${total_cost:.6f}",
            "総計_円換算": f"¥{jpy_total_cost:.3f}",
            "処理時間": f"{response_time:.2f}秒"
        }
        new_row_df = pd.DataFrame([new_row])
        self.cost_df = pd.concat([self.cost_df, new_row_df], ignore_index=True)
        return self.cost_df