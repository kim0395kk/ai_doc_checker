// netlify/functions/classify.js
export async function handler(event) {
  // 1) 허용 메서드 확인
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  // 2) 요청 본문 파싱
  let text = '';
  try {
    ({ text } = JSON.parse(event.body || '{}'));
  } catch (e) {
    return { statusCode: 400, body: 'Invalid JSON' };
  }

  // 3) Gemini 2.5 Pro 호출
  const apiKey = process.env.JN_API_KEY;
  if (!apiKey) {
    return { statusCode: 500, body: 'API key missing' };
  }

  const reqBody = {
    contents: [{ text }],
    system_instruction: '분야를 한 단어(교통/도로/환경/복지/상하수도/행정/기타)로만 답하세요.'
  };

  try {
    const apiRes = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      }
    );
    const data = await apiRes.json();
    const category = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || '기타';

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category })
    };
  } catch (err) {
    console.error(err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
}
