from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from openai import OpenAI

# .env 파일에서 OPENAI_API_KEY 불러오기
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "<h1>🎤 GPT 노래 추천기 서버<br>예시: /recommend?s=남자&y=1990&m=신남</h1>"

@app.route("/recommend")
def recommend():
    gender = request.args.get("s")
    birth_year = request.args.get("y")
    mood = request.args.get("m")

    if not all([gender, birth_year, mood]):
        return jsonify({"error": "필수 정보가 누락되었습니다."}), 400

    prompt = f"""
당신은 음악 전문가입니다.
출생년도: {birth_year}, 성별: {gender}, 기분: {mood}인 사람에게 어울리는 한국 노래를 1곡만 추천하세요.

아래 JSON 형식으로만 응답하세요. 설명은 절대 하지 마세요:

{{
  "노래": "곡 제목",
  "아티스트": "가수 이름"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()

        # JSON 파싱 시도
        parsed = json.loads(content)
        return jsonify(parsed)

    except json.JSONDecodeError:
        return jsonify({"error": "❌ GPT 응답이 JSON 형식이 아닙니다.", "raw_response": content}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002, debug=True)
