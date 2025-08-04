import os
import openai

# OpenAI APIキーを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")

def analyze_content(text):
    try:
        if not text:
            return "内容が空のため解析できません。"

        # OpenAI GPT-4o で要約・分析を実行
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはスロットデータを専門に解析するAIです。データの特徴・傾向・注目すべき点を詳しく要約してください。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.5
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"GPT解析時にエラーが発生しました: {str(e)}"
