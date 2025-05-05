document.addEventListener('DOMContentLoaded', () => {
    const examTypeSelect = document.getElementById('exam-type');
    const tytForm = document.getElementById('tyt-form');
    const aytForm = document.getElementById('ayt-form');
    const aytAlanSelect = document.getElementById('ayt-alan');
    const aytDerslerDiv = document.getElementById('ayt-dersler');
    const saveResultsButton = document.getElementById('save-results');
    const notificationDiv = document.getElementById('notification');

    const tytSoruSayilari = {
        turkce: 40,
        sosyal: 20,
        matematik: 40,
        fen: 20
    };

    // Sınav türü değiştiğinde formları göster/gizle
    examTypeSelect.addEventListener('change', () => {
        if (examTypeSelect.value === 'tyt') {
            tytForm.style.display = 'block';
            aytForm.style.display = 'none';
        } else {
            tytForm.style.display = 'none';
            aytForm.style.display = 'block';
            // AYT seçildiğinde varsayılan olarak SAY alanını oluştur
            olusturAytDersAlanlari(aytAlanSelect.value);
        }
    });

    // TYT inputlarına sınırlandırma ekle
    const tytInputs = tytForm.querySelectorAll('input[type="number"]');
    tytInputs.forEach(input => {
        input.addEventListener('input', (event) => {
            const dersAdi = event.target.id.split('-')[1];
            sinirlaTytGiris(event.target, tytSoruSayilari[dersAdi.split('-')[0]]);
        });
    });

    function sinirlaTytGiris(inputElement, soruSayisi) {
        let value = parseInt(inputElement.value) || 0;
        if (value < 0) inputElement.value = 0;
        if (value > soruSayisi) inputElement.value = soruSayisi;

        const parentDersDiv = inputElement.closest('.ders');
        if (parentDersDiv) {
            const dogruInput = parentDersDiv.querySelector('input[id*="-dogru"]');
            const yanlisInput = parentDersDiv.querySelector('input[id*="-yanlis"]');
            if (dogruInput && yanlisInput) {
                let dogru = parseInt(dogruInput.value) || 0;
                let yanlis = parseInt(yanlisInput.value) || 0;
                if (dogru + yanlis > soruSayisi) {
                    if (inputElement === dogruInput) {
                        yanlisInput.value = soruSayisi - dogru;
                    } else {
                        dogruInput.value = soruSayisi - yanlis;
                    }
                }
            }
        }
    }

    // AYT alan seçimi değiştiğinde ders alanlarını oluştur
    aytAlanSelect.addEventListener('change', (event) => {
        olusturAytDersAlanlari(event.target.value);
    });

    function olusturAytDersAlanlari(alan) {
        aytDerslerDiv.innerHTML = '';
        const dersler = [];
        switch (alan) {
            case 'say':
                dersler.push({ ad: 'Matematik', soru: 40 });
                dersler.push({ ad: 'Fen Bilimleri', soru: 40 });
                break;
            case 'ea':
                dersler.push({ ad: 'Türkçe-Sosyal 1', soru: 40 });
                dersler.push({ ad: 'Matematik', soru: 40 });
                break;
            case 'söz':
                dersler.push({ ad: 'Türkçe-Sosyal 1', soru: 40 });
                dersler.push({ ad: 'Sosyal Bilgiler 2', soru: 40 });
                break;
        }

        dersler.forEach(ders => {
            const dersDiv = document.createElement('div');
            dersDiv.classList.add('ders');
            dersDiv.innerHTML = `
                <label for="ayt-${ders.ad.toLowerCase().replace(' ', '-')}-dogru">${ders.ad} Doğru (${ders.soru}):</label>
                <input type="number" id="ayt-${ders.ad.toLowerCase().replace(' ', '-')}-dogru" min="0" max="${ders.soru}">
                <label for="ayt-${ders.ad.toLowerCase().replace(' ', '-')}-yanlis">Yanlış:</label>
                <input type="number" id="ayt-${ders.ad.toLowerCase().replace(' ', '-')}-yanlis" min="0">
            `;
            aytDerslerDiv.appendChild(dersDiv);
        });
        aytDersAlanlarinaSinirEkle();
    }

    function sinirlaAytGiris(inputElement, soruSayisi) {
        let value = parseInt(inputElement.value) || 0;
        if (value < 0) inputElement.value = 0;
        if (value > soruSayisi) inputElement.value = soruSayisi;

        const parentDersDiv = inputElement.closest('.ders');
        if (parentDersDiv) {
            const dogruInput = parentDersDiv.querySelector('input[id*="-dogru"]');
            const yanlisInput = parentDersDiv.querySelector('input[id*="-yanlis"]');
            if (dogruInput && yanlisInput) {
                let dogru = parseInt(dogruInput.value) || 0;
                let yanlis = parseInt(yanlisInput.value) || 0;
                if (dogru + yanlis > soruSayisi) {
                    if (inputElement === dogruInput) {
                        yanlisInput.value = soruSayisi - dogru;
                    } else {
                        dogruInput.value = soruSayisi - yanlis;
                    }
                }
            }
        }
    }

    function aytDersAlanlarinaSinirEkle() {
        const aytInputs = aytDerslerDiv.querySelectorAll('input[type="number"]');
        aytInputs.forEach(input => {
            input.addEventListener('input', (event) => {
                sinirlaAytGiris(event.target, 40);
            });
        });
    }

    saveResultsButton.addEventListener('click', () => {
        const examType = examTypeSelect.value;
        const now = new Date();
        const date = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
        let results = JSON.parse(localStorage.getItem('examResults')) || [];
        let newResult = {
            examType: examType,
            date: date,
            net: {},
            totalNet: {}
        };

        if (examType === 'tyt') {
            newResult.net.tyt = {
                turkce: parseFloat((parseInt(document.getElementById('tyt-turkce-dogru').value) || 0) - ((parseInt(document.getElementById('tyt-turkce-yanlis').value) || 0) * 0.25)),
                sosyal: parseFloat((parseInt(document.getElementById('tyt-sosyal-dogru').value) || 0) - ((parseInt(document.getElementById('tyt-sosyal-yanlis').value) || 0) * 0.25)),
                matematik: parseFloat((parseInt(document.getElementById('tyt-matematik-dogru').value) || 0) - ((parseInt(document.getElementById('tyt-matematik-yanlis').value) || 0) * 0.25)),
                fen: parseFloat((parseInt(document.getElementById('tyt-fen-dogru').value) || 0) - ((parseInt(document.getElementById('tyt-fen-yanlis').value) || 0) * 0.25))
            };
            newResult.totalNet.tyt = Object.values(newResult.net.tyt).reduce((sum, net) => sum + net, 0);
        } else {
            const alan = aytAlanSelect.value;
            newResult.net.ayt = {};
            let aytToplamNet = 0;
            const dersler = [];
            switch (alan) {
                case 'say':
                    dersler.push('matematik', 'fen-bilimleri');
                    break;
                case 'ea':
                    dersler.push('türkçe-sosyal-1', 'matematik');
                    break;
                case 'söz':
                    dersler.push('türkçe-sosyal-1', 'sosyal-bilgiler-2');
                    break;
            }
            dersler.forEach(dersAdi => {
                const dogruId = `ayt-${dersAdi}-dogru`;
                const yanlisId = `ayt-${dersAdi}-yanlis`;
                const dogru = parseInt(document.getElementById(dogruId).value) || 0;
                const yanlis = parseInt(document.getElementById(yanlisId).value) || 0;
                const net = parseFloat(dogru - (yanlis * 0.25));
                newResult.net.ayt[dersAdi.replace('-', '_')] = net;
                aytToplamNet += net;
            });
            newResult.totalNet.ayt = aytToplamNet;
        }

        results.push(newResult);
        localStorage.setItem('examResults', JSON.stringify(results));
        notificationDiv.textContent = 'Netler Kaydedildi!';
        notificationDiv.style.display = 'block';
        setTimeout(() => {
            notificationDiv.style.display = 'none';
            window.location.href = 'result.html'; // Kaydetme işleminden sonra sonuç sayfasına geri dön
        }, 1500);
    });

    // Sayfa yüklendiğinde TYT formunu görünür, AYT formunu gizli yap
    if (examTypeSelect.value === 'tyt') {
        tytForm.style.display = 'block';
        aytForm.style.display = 'none';
    } else {
        tytForm.style.display = 'none';
        aytForm.style.display = 'block';
        olusturAytDersAlanlari(aytAlanSelect.value);
    }
});