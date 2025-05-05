document.addEventListener('DOMContentLoaded', () => {
    const last5TytList = document.getElementById('last-5-tyt');
    const last5AytList = document.getElementById('last-5-ayt');
    const tytChartCanvas = document.getElementById('tytChart');
    const aytChartCanvas = document.getElementById('aytChart');
    const goToAddNewNetButton = document.getElementById('go-to-add-net');

    goToAddNewNetButton.addEventListener('click', () => {
        window.location.href = 'result_add.html'; // Yeni net ekleme sayfasına yönlendir
    });

    function loadLastResults() {
        const allResults = JSON.parse(localStorage.getItem('examResults')) || [];
        const tytResults = allResults.filter(result => result.examType === 'tyt').slice(-5);
        const aytResults = allResults.filter(result => result.examType === 'ayt').slice(-5);

        displayLastResults('tyt', tytResults);
        displayLastResults('ayt', aytResults);
        drawCharts(tytResults, aytResults);
    }

    function displayLastResults(examType, results) {
        const listElement = examType === 'tyt' ? last5TytList : last5AytList;
        listElement.innerHTML = '';
        if (results.length === 0) {
            const listItem = document.createElement('li');
            listItem.textContent = `Henüz ${examType.toUpperCase()} sonucu girilmemiş.`;
            listElement.appendChild(listItem);
            return;
        }
        results.forEach(result => {
            const listItem = document.createElement('li');
            let netInfo = '';
            if (examType === 'tyt') {
                netInfo = `Türkçe: ${result.net.tyt.turkce.toFixed(2)}, Sosyal: ${result.net.tyt.sosyal.toFixed(2)}, Mat: ${result.net.tyt.matematik.toFixed(2)}, Fen: ${result.net.tyt.fen.toFixed(2)} (Toplam: ${result.totalNet.tyt.toFixed(2)})`;
            } else {
                let aytNetDetails = '';
                for (const ders in result.net.ayt) {
                    aytNetDetails += `${ders}: ${result.net.ayt[ders].toFixed(2)}, `;
                }
                netInfo = `${aytNetDetails} (Toplam: ${result.totalNet.ayt.toFixed(2)})`;
            }
            listItem.textContent = `${result.date}: ${netInfo}`;
            listElement.appendChild(listItem);
        });
    }

    function drawCharts(tytResults, aytResults) {
        drawTytChart(tytResults);
        drawAytChart(aytResults);
    }

    function drawTytChart(results) {
        const dates = results.map(r => r.date);
        const totalNets = results.map(r => r.totalNet.tyt);

        new Chart(tytChartCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Toplam TYT Neti',
                    data: totalNets,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 2,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function drawAytChart(results) {
        const dates = results.map(r => r.date);
        const totalNets = results.map(r => r.totalNet.ayt);

        new Chart(aytChartCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Toplam AYT Neti',
                    data: totalNets,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 2,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    loadLastResults();
});