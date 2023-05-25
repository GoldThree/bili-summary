import openai
import os
import requests


def chat_with_sdk(prompt, text):
    openai.api_key = os.getenv("openai_key")
    print(os.getenv("openai_key"),os.getenv("http_proxy"),os.getenv("https_proxy"))
    # chat_completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}]
    # )
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    )
    ans = completions.choices[0].message.content
    return ans

def chat(prompt,text):
        # ChatGPT API的URL
        proxy = os.getenv("openai_proxy")
        url = f"{proxy}/v1/chat/completions"
        print(url)
        # ChatGPT API的访问密钥
        api_key = os.getenv("openai_key")
        # 请求参数
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ]
        parameters = {
                      "model": "gpt-3.5-turbo",
                      "messages":messages
                    }
        # 请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        # 发送请求
        response = requests.post(url, headers=headers, json=parameters)

        # 解析响应
        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            return text
        else:
            print(response)
            return "Sorry, something went wrong."


if __name__ == "__main__":
    ans = chat("hello", "介绍一下你自己")
    print(ans)
