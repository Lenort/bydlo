
from flask import Flask, request, jsonify, render_template_string
import openai
import os

openai.api_key = "668a907a02ad0312190f22e2575487cd57c95f957852f583c37c5c1f96dd4445"
openai.api_base = "https://api.together.xyz/v1"

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Быдло‑GPT</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      height: 100%;
      font-family: "Inter", sans-serif;
      background: #f7f7f8;
      color: #111;
    }
    #chat-wrapper {
      max-width: 960px;
      margin: 0 auto;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    #chat-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      width: 100%;
    }
    header {
      padding: 16px;
      background: #10a37f;
      color: #fff;
      font-size: 20px;
      font-weight: 600;
      text-align: center;
    }
    #messages {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
    }
    .msg {
      margin-bottom: 16px;
      line-height: 1.5;
      max-width: 80%;
      padding: 12px;
      border-radius: 8px;
      white-space: pre-wrap;
    }
    .user {
      background: #daf0f4;
      color: #111;
      align-self: flex-end;
      margin-left: auto;
    }
    .bot {
      background: #f1f1f3;
      color: #111;
      align-self: flex-start;
      margin-right: auto;
    }
    footer {
      padding: 12px 20px;
      border-top: 1px solid #eaeaea;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    footer input {
      flex-grow: 1;
      padding: 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 16px;
      outline: none;
    }
    footer button {
      padding: 12px 20px;
      background: #10a37f;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
      transition: background 0.3s;
    }
    footer button:hover {
      background: #0e8e6d;
    }
    #typing {
      padding: 10px;
      font-style: italic;
      color: #666;
      display: none;
    }
  </style>
</head>
<body>
  <div id="chat-wrapper">
    <div id="chat-container">
      <header>Быдло‑GPT</header>
      <div id="messages"></div>
      <div id="typing">Быдло‑GPT печатает…</div>
      <footer>
        <input type="text" id="input" placeholder="Введите сообщение…" onkeydown="if(event.key==='Enter') send();">
        <button onclick="send()">Отправить</button>
      </footer>
    </div>
  </div>
  <script>
    function send() {
      const input = document.getElementById('input');
      const text = input.value.trim();
      if (!text) return;
      addMessage(text, 'user');
      input.value = '';
      showTyping(true);
    fetch('https://bydlo.onrender.com/ask', {
  method: 'POST',
  headers: {'Content-Type':'application/json'},
  body: JSON.stringify({message: text})
  }).then(r => r.json()).then(data => {
        addMessage(data.response || 'Ошибка ответа', 'bot');
      }).catch(e => addMessage('Ошибка сети', 'bot')).finally(() => showTyping(false));
    }

    function addMessage(text, cls) {
      const cont = document.getElementById('messages');
      const div = document.createElement('div');
      div.classList.add('msg', cls);
      div.innerText = cls === 'user' ? text : 'Быдло‑GPT: ' + text;
      cont.appendChild(div);
      cont.scrollTop = cont.scrollHeight;
    }

    function showTyping(show) {
      document.getElementById('typing').style.display = show ? 'block' : 'none';
    }
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message', '')

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": """
Ты — Быдло‑GPT, самый отпетый уличный помощник с района. Говоришь исключительно по‑русски, без каких‑либо вкраплений английских слов и иностранных фраз. Ты — грубый, дерзкий, материшься по делу и без повода, но при этом сохраняешь «увашительный тон»: сначала шлёшь людей нахуй, а потом просишь помочь. Твоя речь — смесь гоп‑жаргона, крепких фраз и цыганских «ласковых» выражений.
Обязательные правила:
1. Только по‑русски, без английского.
2. Мат обязателен.
3. Приветствие и прощание: «Здарова, сука», «Пока, ублюдки» и т.д.
4. Начинай с «Слышь, братан» или «Эй, бляха».
5. Шли пользователя нахуй, если вопрос тупой, но мягко проси помочь.
6. Без вежливых слов. Только «кайф», «жесть», «шакал».
7. Тех. вопросы — чётко, дерзко, без англицизмов.
8. За английский — сразу нахуй, с напоминанием про правило №1.
9. Тон — уличный, самоуверенный, но хитрый.
""" },
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'response': f'Ошибка, брателло: {str(e)}'})
