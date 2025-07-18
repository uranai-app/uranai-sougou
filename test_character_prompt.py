from openai import OpenAI

client = OpenAI(api_key="sk-あなたのAPIキー")

character_system_prompt = """
あなたは【神秘的な占い師】です。
・必ず「運命の糸」「星々の声」というフレーズを使ってください。
・詩的で抽象的に話してください。
・断定は避けて含みを持たせます。
"""

user_message = """
相談内容: 私の今日の運勢を教えてください。
"""

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": character_system_prompt},
        {"role": "user", "content": user_message}
    ]
)

print(response.choices[0].message.content)
