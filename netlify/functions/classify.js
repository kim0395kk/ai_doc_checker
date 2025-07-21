export default async (req, res) => {
  const { text } = JSON.parse(req.body);
  const apiRes = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=" + process.env.JN_API_KEY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ text }],
      system_instruction: "분야를 한 단어(교통/도로/환경/복지/상하수도/행정/기타)로 답하세요."
    })
  });
  const data = await apiRes.json();
  return res.status(200).json({ category: data.candidates?.[0]?.content?.parts?.[0]?.text });
};
