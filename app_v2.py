<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>토론 메이트</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #e0e7ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .chat-wrapper {
            max-width: 700px;
            margin: 30px auto;
            background-color: white;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 90vh;
        }

        .chat-header {
            background-color: #1e3a8a;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 22px;
            margin-bottom: 5px;
        }

        .chat-header p {
            font-size: 14px;
            margin-top: 0;
            color: #cbd5e1;
        }

        .topic-box {
            background-color: #1e40af;
            color: white;
            padding: 12px;
            font-weight: bold;
            text-align: center;
        }

        .chat-box {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        .message {
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }

        .bot .bubble {
            background-color: #f3f4f6;
            color: #111827;
        }

        .user .bubble {
            background-color: #3b82f6;
            color: white;
            margin-left: auto;
        }

        .bubble {
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 80%;
            line-height: 1.4;
            position: relative;
        }

        .bot img {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            margin-right: 10px;
        }

        .loader {
            border: 4px solid #e0e7ff;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .input-box {
            display: flex;
            padding: 10px;
            border-top: 1px solid #e5e7eb;
            background-color: #f9fafb;
        }

        .input-box input {
            flex: 1;
            padding: 12px;
            border-radius: 30px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
        }

        .input-box button {
            margin-left: 10px;
            padding: 12px 18px;
            background-color: #1d4ed8;
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
        }

        .new-topic-btn {
            display: inline-block;
            margin-top: 8px;
            background-color: #1e3a8a;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="chat-wrapper">
        <div class="chat-header">
            <h1>토론 메이트 - 오늘의 주제 한마디</h1>
            <p>흥미로운 사회 주제에 대해 함께 생각해보고 이야기 나눠보아요. 🧠</p>
        </div>
        <div id="topic" class="topic-box">📌 오늘의 주제: </div>
        <div class="chat-box" id="chat-box"></div>
        <div class="input-box">
            <input type="text" id="user-input" placeholder="메시지를 입력해주세요">
            <button onclick="sendMessage()">보내기</button>
        </div>
    </div>

    <script>
        const topics = [
            "출산 장려 정책, 효과가 있을까요?",
            "기후 변화 대응, 개인의 책임도 클까요?",
            "학벌 중심 사회, 과연 공정한가요?",
            "AI 기술 발전, 인간의 일자리를 위협할까요?",
            "범죄자 신상 공개, 국민의 알 권리인가요?"
        ];

        function getRandomTopic() {
            return topics[Math.floor(Math.random() * topics.length)];
        }

        function setTopic() {
            const topic = getRandomTopic();
            document.getElementById('topic').textContent = `📌 오늘의 주제: ${topic}`;
        }

        function appendMessage(text, sender = 'bot', isLoading = false) {
            const chatBox = document.getElementById('chat-box');
            const message = document.createElement('div');
            message.className = `message ${sender}`;

            if (sender === 'bot') {
                const avatar = document.createElement('img');
                avatar.src = "/mnt/data/chatbot_avatar.png";
                message.appendChild(avatar);
            }

            const bubble = document.createElement('div');
            bubble.className = 'bubble';

            if (isLoading) {
                const loader = document.createElement('div');
                loader.className = 'loader';
                bubble.appendChild(loader);
            } else {
                bubble.innerHTML = text;
                // Add "다른 주제 주세요" only for bot messages
                if (sender === 'bot') {
                    const newBtn = document.createElement('button');
                    newBtn.className = 'new-topic-btn';
                    newBtn.textContent = '🔄 다른 주제 주세요';
                    newBtn.onclick = setTopic;
                    bubble.appendChild(document.createElement('br'));
                    bubble.appendChild(newBtn);
                }
            }

            message.appendChild(bubble);
            chatBox.appendChild(message);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            input.value = '';

            appendMessage('', 'bot', true); // show loading

            setTimeout(() => {
                const chatBox = document.getElementById('chat-box');
                chatBox.lastChild.remove(); // remove loading
                appendMessage("그렇죠, 반대 의견도 중요하죠. 예를 들어 전업주부 A씨는 “출산 장려 정책은 실효성이 없다”고 말했어요.", 'bot');
            }, 1200);
        }

        window.onload = () => {
            setTopic();
            appendMessage("안녕하세요, 저는 오늘의 주제를 함께 이야기 나누는 '토론 메이트'예요! 😊<br><strong>🗣️ 오늘의 주제:</strong> 출산 장려 정책, 효과가 있을까요?<br>이 주제에 대해 어떻게 생각하시나요? 찬성/반대 또는 다른 관점에서 자유롭게 이야기해 주세요.", 'bot');
        };
    </script>
</body>
</html>
