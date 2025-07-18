# api/app.py (최종 수정본)

from flask import Flask, request, jsonify
import joblib
import re
import os
import json
from datetime import datetime

# 구글 시트 연동을 위한 라이브러리 (지난번에 추가)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- 경로 설정 (더 간단하고 명확하게 수정) ---
# 현재 파일(app.py)이 위치한 디렉토리를 기준으로 model 폴더 경로를 지정합니다.
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

# --- 모델 로드 ---
try:
    vectorizer = joblib.load(os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl'))
    model = joblib.load(os.path.join(MODEL_DIR, 'nb_classifier.pkl'))
except FileNotFoundError:
    print(f"오류: {MODEL_DIR} 경로에 모델 파일이 없습니다. 깃허브에 model 폴더와 .pkl 파일이 잘 업로드되었는지 확인해주세요.")
    # 오류가 나도 서버가 죽지 않도록 임시 조치
    vectorizer, model = None, None

# --- 구글 시트 연동 설정 (변경 없음) ---
sheet = None
try:
    google_creds_json = os.environ.get('GOOGLE_CREDS_JSON')
    if google_creds_json:
        creds_dict = json.loads(google_creds_json)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("AI_Duty_Log").sheet1
except Exception as e:
    print(f"구글 시트 연동 실패: {e}")


# --- 텍스트 전처리 함수 (변경 없음) ---
def preprocess_text(text: str) -> str:
    # ... (이하 내용은 이전과 동일합니다)
    text = re.sub(r'(상담원:|민원인:)', '', text)
    text = re.sub(r'[^가-힣a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- API 엔드포인트 (변경 없음) ---
@app.route('/api/classify', methods=['POST'])
def classify():
    # ... (이하 내용은 이전과 동일합니다)
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': '민원 내용이 없습니다.'}), 400
    
    if not vectorizer or not model:
        return jsonify({'error': '모델이 로드되지 않았습니다. 서버 로그를 확인하세요.'}), 500

    complaint_text = data['text']
    
    processed_text = preprocess_text(complaint_text)
    text_vec = vectorizer.transform([processed_text])
    prediction = model.predict(text_vec)
    category = prediction[0]
    
    if sheet:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = [now, complaint_text, category]
            sheet.append_row(row)
        except Exception as e:
            print(f"구글 시트 기록 실패: {e}")

    return jsonify({'category': category})
