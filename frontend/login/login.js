document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginErrorDiv = document.getElementById('login-error');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Sayfanın yeniden yüklenmesini engelle

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch('/auth/token', { // FastAPI'deki giriş endpoint'i
                method: 'POST',
                body: formData, // application/x-www-form-urlencoded formatında gönderiyoruz
            });

            const data = await response.json();

            if (response.ok) {
                // Giriş başarılıysa, back-end'den dönen access token'ı alıyoruz
                console.log('Giriş Başarılı:', data);
                localStorage.setItem('accessToken', data.access_token);
                localStorage.setItem('tokenType', data.token_type);
                // Kullanıcıyı hub sayfasına yönlendir
                window.location.href = '../hub/hub.html';
            } else {
                // Giriş başarısızsa, hata mesajını göster
                loginErrorDiv.textContent = data.detail || 'Kullanıcı adı veya şifre hatalı.';
                loginErrorDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Giriş sırasında bir hata oluştu:', error);
            loginErrorDiv.textContent = 'Sunucuya bağlanılamadı.';
            loginErrorDiv.style.display = 'block';
        }
    });
});