import openai
import os

os.environ["HTTP_PROXY"] = os.getenv("http_proxy")
os.environ["HTTPS_PROXY"] = os.getenv("https_proxy")


def chat(prompt, text):
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


if __name__ == "__main__":
    ans = chat("hello", "介绍一下你自己")
    print(ans)
