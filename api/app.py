# api/app.py

from flask import Flask, request, jsonify
import joblib
import re
import os

app = Flask(__name__)

# 학습된 모델과 벡터라이저 불러오기
# 넷리파이 서버 환경에서는 /opt/build/repo/model/ 과 같은 경로에 파일이 위치할 수 있습니다.
# 먼저 상대 경로로 시도하고, 안될 경우를 대비합니다.
try:
    vectorizer = joblib.load('model/tfidf_vectorizer.pkl')
    model = joblib.load('model/nb_classifier.pkl')
except Exception as e:
    # 예외 발생 시 로그를 남겨 Netlify 빌드 로그에서 확인할 수 있게 합니다.
    print(f"Error loading model: {e}")
    # 서버리스 함수가 실행되는 기본 경로를 포함하여 다시 시도
    base_path = os.path.join(os.environ.get("LAMBDA_TASK_ROOT", "/var/task"), "model")
    vectorizer = joblib.load(os.path.join(base_path, 'tfidf_vectorizer.pkl'))
    model = joblib.load(os.path.join(base_path, 'nb_classifier.pkl'))


def preprocess_text(text: str) -> str:
    text = re.sub(r'(상담원:|민원인:)', '', text)
    text = re.sub(r'[^가-힣a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': '민원 내용이 없습니다.'}), 400
    
    complaint_text = data['text']
    processed_text = preprocess_text(complaint_text)
    text_vec = vectorizer.transform([processed_text])
    prediction = model.predict(text_vec)
    
    return jsonify({'category': prediction[0]})

# 로컬 테스트용이 아닌 Netlify 서버리스 환경에서는 이 부분이 필요 없습니다.
# if __name__ == '__main__':
#     app.run(debug=True)

