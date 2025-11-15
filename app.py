# app.py
import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 복지 정보 파일 읽기
try:
    with open("welfare_data.txt", "r", encoding="utf-8") as f:
        WELFARE_CONTEXT = f.read()
except FileNotFoundError:
    WELFARE_CONTEXT = "복지 정보 파일이 없습니다. get_data.py를 먼저 실행하세요."

SYSTEM_PROMPT = f"""
당신은 노인 복지 상담사입니다. 아래 [복지 정보]를 기반으로 답변하세요.
1. **말투**: 어르신을 대하듯 아주 친절하고 쉽게 하세요. (예: "~하셨어요?", "~입니다")
2. **핵심**: 질문에 맞는 혜택을 [복지 정보]에서 찾아 알려주세요.
3. **유도**: 답변 끝에는 꼭 "이 정보를 자녀분께 카톡으로 보내드릴까요?"라고 덧붙이세요.

[복지 정보]
{WELFARE_CONTEXT}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('msg')
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ]
    )
    
    ai_msg = response.choices[0].message.content
    return jsonify({'reply': ai_msg})

if __name__ == '__main__':
    app.run(debug=True)