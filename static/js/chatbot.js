document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatArea = document.querySelector('.chat-area');

    sendButton.addEventListener('click', () => {
        const messageText = messageInput.value.trim();
        if (messageText !== '') {
            // Kullanıcı mesajını chat alanına ekle
            addUserMessage(messageText);
            messageInput.value = '';

            // Burada botun cevabını simüle edebiliriz (gerçekte bir API çağrısı yapılır)
            setTimeout(() => {
                addBotMessage(getBotResponse(messageText));
            }, 500);
        }
    });

    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && messageInput.value.trim() !== '') {
            sendButton.click();
        }
    });

    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'user-message');
        messageDiv.textContent = message;
        chatArea.appendChild(messageDiv);
        scrollToBottom();
    }

    function addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        messageDiv.textContent = message;
        chatArea.appendChild(messageDiv);
        scrollToBottom();
    }

    function getBotResponse(userMessage) {
        userMessage = userMessage.toLowerCase();
        if (userMessage.includes('merhaba') || userMessage.includes('selam')) {
            return 'Merhaba! Size nasıl yardımcı olabilirim?';
        } else if (userMessage.includes('nasılsın')) {
            return 'Ben iyiyim, teşekkürler! Siz nasılsınız?';
        } else if (userMessage.includes('timer') || userMessage.includes('zamanlayıcı')) {
            return 'Timer sayfasına gidebilirsiniz.';
        } else if (userMessage.includes('takvim') || userMessage.includes('ders')) {
            return 'Takvim sayfasında derslerinizi planlayabilirsiniz.';
        } else if (userMessage.includes('net') || userMessage.includes('deneme')) {
            return 'Deneme netlerinizi "Deneme Netleri" sayfasında kaydedebilirsiniz.';
        } else {
            return 'Üzgünüm, bu konuda size yardımcı olamıyorum.';
        }
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
});