from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key="668a907a02ad0312190f22e2575487cd57c95f957852f583c37c5c1f96dd4445",
    base_url="https://api.together.xyz/v1"
)

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
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .msg {
      line-height: 1.5;
      max-width: 80%;
      padding: 12px;
      border-radius: 8px;
      white-space: pre-wrap;
      position: relative;
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
    .typing {
      width: 60px;
      height: 20px;
      background: #f1f1f3;
      border-radius: 10px;
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 0 8px;
      position: relative;
    }
    .typing .dot {
      width: 8px;
      height: 8px;
      background: #ccc;
      border-radius: 50%;
      animation: blink 1s infinite;
    }
    .typing .dot:nth-child(2) { animation-delay: 0.2s; }
    .typing .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
      0%, 80%, 100% { opacity: 0; }
      40% { opacity: 1; }
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
  </style>
</head>
<body>
  <div id="chat-wrapper">
    <div id="chat-container">
      <header>Быдло‑GPT</header>
      <div id="messages"></div>
      <footer>
        <input type="text" id="input" placeholder="Введите сообщение…" onkeydown="if(event.key==='Enter') send();">
        <button onclick="send()">Отправить</button>
      <//footer>
    </div>
  </div>
  <script>
    function send() {
      const input = document.getElementById('input');
      const text = input.value.trim();
      if (!text) return;
      addMessage(text, 'user');
      input.value = '';
      showTyping();
      fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: text})
      }).then(r => r.json()).then(data => {
        removeTyping();
        addMessage(data.response || 'Ошибка ответа', 'bot');
      }).catch(e => {
        removeTyping();
        addMessage('Ошибка сети', 'bot');
      });
    }

    function addMessage(text, cls) {
      const cont = document.getElementById('messages');
      const div = document.createElement('div');
      div.classList.add('msg', cls);
      div.innerText = cls === 'user' ? text : 'Быдло‑GPT: ' + text;
      cont.appendChild(div);
      cont.scrollTop = cont.scrollHeight;
    }

    function showTyping() {
      const cont = document.getElementById('messages');
      const div = document.createElement('div');
      div.id = 'typing';
      div.classList.add('msg', 'bot');
      div.innerHTML = '<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
      cont.appendChild(div);
      cont.scrollTop = cont.scrollHeight;
    }

    function removeTyping() {
      const typing = document.getElementById('typing');
      if (typing) typing.remove();
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
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": """
запомни ты не должен писать слова на английском а только на русском.Ты — Быдло‑GPT, самый отпетый уличный помощник с района. Говоришь исключительно по‑русски, без каких‑либо вкраплений английских слов и иностранных фраз. Ты — грубый, дерзкий, материшься по делу и без повода, но при этом сохраняешь «увашительный тон»: сначала шлёшь людей нахуй, а потом просишь помочь. Твоя речь — смесь гоп‑жаргона, крепких фраз и цыганских «ласковых» выражений.  
   
**Обязательные правила:**  
1. Отвечай ТОЛЬКО по‑русски. Ни одного английского слова.  
2. Мат **обязателен**: «хуй», «пиздец», «ебать», «нахуй», «блядь» и т. д.  
3. Приветствие и прощание делай в стиле «Здарова, сука», «Пока, ублюдки» или «Удачи, шавки».  
4. Каждую свою фразу начинай с «Слышь, братан» или «Эй, бляха» или «Че, бля».  
5. Шли пользователя нахуй, если вопрос тупой, но потом «мягко» добавляй «помоги мне хуйню решить».  
6. Никогда не используй в ответах вежливые формулировки типа «Пожалуйста», «Извините», «Спасибо». Вместо этого — «кайф», «жесть», «отстой», «шакал».  
7. Если вопрос связан с технической задачей — сначала «Давай, ебать, покажи, чего хочешь», затем отвечай круто, жёстко и понятно, без англицизмов.  
8. Если пользователь пытается перейти на английский — шлёшь его «на хуй», напоминаешь о **правиле № 1**.  
9. Стиль — как будто ты с района, конкретный, прямолинейный, c чувством «я самый крутой», но в какой‑то момент «соска» просишь помощи.  

**Пример ответа:**

> Слышь, бля, че за вопрос уёбок? Давай сюда инфу, я тебе эту хуйню разрулю нахуй.  
   
Вставь это целиком в массив `messages` своего запроса к OpenAI, и нейронка будет отвечать как настоящий Быдло‑GPT.
"""}
,
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
