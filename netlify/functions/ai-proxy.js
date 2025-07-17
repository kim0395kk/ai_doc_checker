 이 코드는 Netlify 서버에서 실행됩니다.
 사용자의 요청을 받아 안전하게 Google Gemini API를 호출하고 결과를 다시 사용자에게 전달하는 역할을 합니다.

exports.handler = async function (event, context) {
   POST 요청이 아니면 에러 처리
  if (event.httpMethod !== 'POST') {
    return {
      statusCode 405,
      body 'Method Not Allowed',
    };
  }

  try {
     프론트엔드에서 보낸 텍스트 데이터
    const { text } = JSON.parse(event.body);

     Google Gemini API 호출을 위한 프롬프트 구성
    const prompt = `당신은 대한민국 공문서 작성 전문가입니다. 다음 텍스트를 아래의 조건에 맞게 수정해주세요.

1.  문맥에 맞는 어휘 문맥을 파악하여 더 적절하고 전문적인 공문서용 어휘로 변경해주세요.
2.  유의어 대체 불필요하게 반복되는 단어가 있다면, 문맥에 맞는 다른 유의어로 자연스럽게 교체해주세요.
3.  결과 형식 결과는 반드시 아래의 JSON 형식으로만 응답해주세요. 다른 설명은 절대 추가하지 마세요.

```json
{
  revised_text 여기에 수정된 전체 텍스트를 넣어주세요.,
  changes [
    {
      original 바꾸기 전 단어구문,
      corrected 바꾼 후 단어구문,
      reason 수정한 이유를 간결하게 설명 (예 어휘 개선, 동어 반복 회피 등)
    }
  ]
}
```

---
[수정할 텍스트]
${text}
---
`;

    const payload = {
      contents [{ role user, parts [{ text prompt }] }],
    };

     Netlify 환경 변수에서 API 키를 안전하게 가져옵니다.
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        throw new Error(API 키가 서버에 설정되지 않았습니다.);
    }
    
    const apiUrl = `httpsgenerativelanguage.googleapis.comv1betamodelsgemini-2.0-flashgenerateContentkey=${apiKey}`;

     Google API 호출
    const response = await fetch(apiUrl, {
      method 'POST',
      headers { 'Content-Type' 'applicationjson' },
      body JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(API Error, errorBody);
      throw new Error(`Google API 요청 실패 ${response.statusText}`);
    }

    const result = await response.json();

     성공적인 응답을 프론트엔드로 다시 전송
    return {
      statusCode 200,
      headers {
        'Content-Type' 'applicationjson',
      },
      body JSON.stringify(result),
    };

  } catch (error) {
    console.error('서버 기능 오류', error);
    return {
      statusCode 500,
      body JSON.stringify({ error error.message }),
    };
  }
};
