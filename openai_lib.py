import openai


def chat(prompt, text):
    openai.api_key = "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"

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
