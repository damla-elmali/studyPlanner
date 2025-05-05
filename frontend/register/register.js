document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const nameInput = document.getElementById('name');
    const surnameInput = document.getElementById('surname');
    const emailInput = document.getElementById('e-mail');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const passwordAgainInput = document.getElementById('password-again');
    const registerErrorDiv = document.getElementById('register-error');

    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Sayfanın yeniden yüklenmesini engelle

        const name = nameInput.value.trim();
        const surname = surnameInput.value.trim();
        const email = emailInput.value.trim();
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const passwordAgain = passwordAgainInput.value;

        if (password !== passwordAgain) {
            registerErrorDiv.textContent = 'Şifreler eşleşmiyor.';
            registerErrorDiv.style.display = 'block';
            return;
        }

        const userData = {
            create_user: username, // `create_user` alanı back-end'deki `username`'e karşılık geliyor
            email: email,
            first_name: name,
            last_name: surname,
            password: password,
            role: 'user', // Varsayılan olarak 'user' rolünü atayabilirsiniz
            phone_number: '', // İsteğe bağlı, kullanıcıdan alabilirsiniz
            grade: '',       // İsteğe bağlı, kullanıcıdan alabilirsiniz
        };

        try {
            const response = await fetch('/auth/get_user', { // FastAPI'deki kayıt endpoint'i
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (response.status === 201) {
                // Kayıt başarılıysa, kullanıcıya bir mesaj gösterin ve giriş sayfasına yönlendirin
                console.log('Kayıt Başarılı:', data);
                alert('Kayıt başarıyla tamamlandı! Giriş sayfasına yönlendiriliyorsunuz.');
                window.location.href = '../login/login.html';
            } else {
                // Kayıt başarısızsa, hata mesajını göster
                registerErrorDiv.textContent = data.detail || 'Kayıt başarısız.';
                registerErrorDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Kayıt sırasında bir hata oluştu:', error);
            registerErrorDiv.textContent = 'Sunucuya bağlanılamadı.';
            registerErrorDiv.style.display = 'block';
        }
    });
});