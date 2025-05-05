document.addEventListener('DOMContentLoaded', () => {
    const freeStudyBtn = document.getElementById('free-study-btn');
    const planStudyBtn = document.getElementById('plan-study-btn');
    const freeStudyModeDiv = document.getElementById('free-study-mode');
    const planStudyModeDiv = document.getElementById('plan-study-mode');
    const timerModeSelectionDiv = document.querySelector('.timer-mode-selection');

    // Serbest Çalışma Modu Elemanları
    const minutesFreeSpan = document.getElementById('free-minutes');
    const secondsFreeSpan = document.getElementById('free-seconds');
    const startStopFreeBtn = document.getElementById('startStopFree');
    const resetFreeBtn = document.getElementById('resetFree');
    const finishFreeBtn = document.getElementById('finishFree');
    const freeStudyLogDiv = document.getElementById('free-study-log');
    const loggedMinutesSpan = document.getElementById('logged-minutes');
    const loggedSecondsSpan = document.getElementById('logged-seconds');
    const freeStudyMessageP = document.getElementById('free-study-message');
    const freeStudyTopicInput = document.getElementById('free-study-topic');
    let freeInterval;
    let freeTotalSeconds = 0;
    let isFreeRunning = false;
    let freeStartTime; // Serbest çalışmanın başlangıç zamanını saklayacak değişken

    // Yeni Elemanlar
    const freeStudyDateInput = document.createElement('input');
    freeStudyDateInput.type = 'date';
    freeStudyDateInput.id = 'free-study-date';
    freeStudyDateInput.style.display = 'none'; // Başlangıçta gizli
    freeStudyLogDiv.insertBefore(freeStudyDateInput, freeStudyLogDiv.firstChild); // freeStudyLogDiv'in başına ekle
    let freeStudyDate; // Serbest çalışma tarihini saklayacak değişken

    // Plandan Çalışma Modu Elemanları
    const plannedLessonSelect = document.getElementById('planned-lesson-select');
    const minutesPlanSpan = document.getElementById('plan-minutes');
    const secondsPlanSpan = document.getElementById('plan-seconds');
    const startStopPlanBtn = document.getElementById('startStopPlan');
    const pauseResumePlanBtn = document.getElementById('pauseResumePlan');
    const finishPlanBtn = document.getElementById('finishPlan');
    const planStudyMessageP = document.getElementById('plan-study-message');
    let plannedLessons = [];
    let selectedLesson;
    let planInterval;
    let planRemainingSeconds = 0;
    let planIsRunning = false;
    let currentPlannedLesson; // Şu anda çalışılan planlı dersin bilgileri

    // Mod Seçimi Olayları
    freeStudyBtn.addEventListener('click', () => {
        timerModeSelectionDiv.classList.add('hidden');
        freeStudyModeDiv.classList.remove('hidden');
        planStudyModeDiv.classList.add('hidden');
        resetFreeTimer();
    });

    planStudyBtn.addEventListener('click', () => {
        timerModeSelectionDiv.classList.add('hidden');
        freeStudyModeDiv.classList.add('hidden');
        planStudyModeDiv.classList.remove('hidden');
        loadPlannedLessons(); // Tüm planlanmış dersleri yükle
        resetPlanTimer();
    });

    // --- Serbest Çalışma Modu ---
    startStopFreeBtn.addEventListener('click', () => {
        isFreeRunning = !isFreeRunning;
        if (isFreeRunning) {
            startFreeTimer();
            startStopFreeBtn.textContent = 'Durdur';
            freeStartTime = new Date().toISOString(); // Çalışma başladığında zamanı kaydet
        } else {
            stopFreeTimer();
            startStopFreeBtn.textContent = 'Başlat';
        }
    });

    resetFreeBtn.addEventListener('click', resetFreeTimer);

    finishFreeBtn.addEventListener('click', () => {
        stopFreeTimer();
        const minutes = Math.floor(freeTotalSeconds / 60);
        const seconds = freeTotalSeconds % 60;
        loggedMinutesSpan.textContent = String(minutes).padStart(2, '0');
        loggedSecondsSpan.textContent = String(seconds).padStart(2, '0');
        freeStudyLogDiv.classList.remove('hidden');

        // Tarih input'unu göster
        freeStudyDateInput.style.display = 'block';

        const topic = freeStudyTopicInput.value.trim();
        freeStudyDate = freeStudyDateInput.value; // Tarihi al

        if (freeStudyDate) {
            const freeStudyData = {
                startTime: freeStartTime,
                endTime: new Date().toISOString(),
                duration: freeTotalSeconds,
                topic: topic || 'Serbest Çalışma',
                date: freeStudyDate  // Tarihi kaydet
            };

            localStorage.setItem('freeStudySession', JSON.stringify(freeStudyData));
            window.location.href = '../planner/planner.html'; // Planner sayfasına yönlendir
        } else {
            freeStudyMessageP.textContent = 'Lütfen çalışma tarihini seçin.';
            setTimeout(() => freeStudyMessageP.textContent = '', 2000);
        }
    });

    function startFreeTimer() {
        freeInterval = setInterval(() => {
            freeTotalSeconds++;
            updateFreeTimerDisplay();
        }, 1000);
    }

    function stopFreeTimer() {
        clearInterval(freeInterval);
    }

    function resetFreeTimer() {
        stopFreeTimer();
        freeTotalSeconds = 0;
        updateFreeTimerDisplay();
        startStopFreeBtn.textContent = 'Başlat';
        isFreeRunning = false;
        freeStudyLogDiv.classList.add('hidden');
        freeStudyMessageP.textContent = '';
        freeStudyTopicInput.value = '';
        freeStudyDateInput.style.display = 'none'; // Tarih input'unu gizle
        freeStudyDateInput.value = ''; // Tarih input'unu temizle
    }

    function updateFreeTimerDisplay() {
        const minutes = Math.floor(freeTotalSeconds / 60);
        const seconds = freeTotalSeconds % 60;
        minutesFreeSpan.textContent = String(minutes).padStart(2, '0');
        secondsFreeSpan.textContent = String(seconds).padStart(2, '0');
    }

    // --- Plandan Çalışma Modu ---
    function loadPlannedLessons() {
        const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
        const completedTimers = JSON.parse(localStorage.getItem('completedTimers')) || [];
        plannedLessonSelect.innerHTML = '<option value="">Lütfen bir ders seçin</option>';
        lessons.forEach(lesson => {
            // Tamamlanmış dersleri filtrele
            const isCompleted = completedTimers.some(timer => timer.lessonName === lesson.name && timer.lessonTime === lesson.time);
            if (!isCompleted) {
                const option = document.createElement('option');
                option.value = lesson.name;
                option.textContent = `${lesson.name} (${lesson.time} - ${lesson.studyDuration} dk) - ${lesson.day}`;
                option.dataset.duration = lesson.studyDuration;
                option.dataset.startTime = lesson.time;
                option.dataset.lessonData = JSON.stringify(lesson);
                plannedLessonSelect.appendChild(option);
            }
        });
        resetPlanTimer();
    }

    plannedLessonSelect.addEventListener('change', () => {
        const selectedOption = plannedLessonSelect.options[plannedLessonSelect.selectedIndex];
        if (selectedOption && selectedOption.value !== "") {
            currentPlannedLesson = JSON.parse(selectedOption.dataset.lessonData);
            resetPlanTimer(currentPlannedLesson.studyDuration * 60);
            pauseResumePlanBtn.disabled = false;
        } else {
            currentPlannedLesson = null;
            resetPlanTimer(0);
            pauseResumePlanBtn.disabled = true;
        }
    });

    startStopPlanBtn.addEventListener('click', () => {
        if (currentPlannedLesson) {
            planIsRunning = !planIsRunning;
            if (planIsRunning) {
                startPlanTimer();
                startStopPlanBtn.textContent = 'Durdur';
                pauseResumePlanBtn.textContent = 'Durdur';
            } else {
                stopPlanTimer();
                startStopPlanBtn.textContent = 'Başlat';
                pauseResumePlanBtn.textContent = 'Devam Et';
            }
        } else {
            planStudyMessageP.textContent = 'Lütfen önce bir ders seçin.';
            setTimeout(() => planStudyMessageP.textContent = '', 2000);
        }
    });

    pauseResumePlanBtn.addEventListener('click', () => {
        if (currentPlannedLesson) {
            planIsRunning = !planIsRunning;
            if (planIsRunning) {
                startPlanTimer();
                startStopPlanBtn.textContent = 'Durdur';
                pauseResumePlanBtn.textContent = 'Durdur';
            } else {
                stopPlanTimer();
                startStopPlanBtn.textContent = 'Başlat';
                pauseResumePlanBtn.textContent = 'Devam Et';
            }
        } else {
            planStudyMessageP.textContent = 'Lütfen önce bir ders seçin.';
            setTimeout(() => planStudyMessageP.textContent = '', 2000);
        }
    });

    finishPlanBtn.addEventListener('click', () => {
        if (currentPlannedLesson) {
            stopPlanTimer();
            // Tamamlanan dersi local storage'a kaydet
            saveCompletedLesson(currentPlannedLesson.name, currentPlannedLesson.time);
            markLessonAsCompleted(currentPlannedLesson.name, currentPlannedLesson.time);
            planStudyMessageP.textContent = `${currentPlannedLesson.name} için çalışma tamamlandı!`;
            setTimeout(() => {
                planStudyMessageP.textContent = '';
                planStudyModeDiv.classList.add('hidden');
                timerModeSelectionDiv.classList.remove('hidden');
                loadPlannedLessons();
                resetPlanTimer();
            }, 3000);
        } else {
            planStudyMessageP.textContent = 'Lütfen önce bir ders seçin.';
            setTimeout(() => planStudyMessageP.textContent = '', 2000);
        }
    });

    function startPlanTimer() {
        planInterval = setInterval(() => {
            planRemainingSeconds--;
            updatePlanTimerDisplay();
            if (planRemainingSeconds <= 0 && planIsRunning && currentPlannedLesson) {
                stopPlanTimer();
                planIsRunning = false;
                // Süre bittiğinde dersi tamamlandı olarak işaretle ve kaydet
                saveCompletedLesson(currentPlannedLesson.name, currentPlannedLesson.time);
                markLessonAsCompleted(currentPlannedLesson.name, currentPlannedLesson.time);
                planStudyMessageP.textContent = `${currentPlannedLesson.name} için çalışma süresi doldu!`;
                setTimeout(() => {
                    planStudyMessageP.textContent = '';
                    planStudyModeDiv.classList.add('hidden');
                    timerModeSelectionDiv.classList.remove('hidden');
                    loadPlannedLessons();
                    resetPlanTimer();
                }, 3000);
            }
        }, 1000);
    }

    function stopPlanTimer() {
        clearInterval(planInterval);
    }

    function resetPlanTimer(durationInSeconds = 0) {
        stopPlanTimer();
        planRemainingSeconds = durationInSeconds;
        updatePlanTimerDisplay();
        planIsRunning = false;
        startStopPlanBtn.textContent = 'Başlat';
        pauseResumePlanBtn.textContent = 'Durdur';
        pauseResumePlanBtn.disabled = !currentPlannedLesson;
        planStudyMessageP.textContent = '';
    }

    function updatePlanTimerDisplay() {
        const minutes = Math.floor(planRemainingSeconds / 60);
        const seconds = planRemainingSeconds % 60;
        minutesPlanSpan.textContent = String(minutes).padStart(2, '0');
        secondsPlanSpan.textContent = String(seconds).padStart(2, '0');
    }

    function markLessonAsCompleted(lessonName, lessonTime) {
        const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
        const updatedLessons = lessons.map(lesson =>
            lesson.name === lessonName && lesson.time === lessonTime ? { ...lesson, completed: true } : lesson
        );
        localStorage.setItem('lessons', JSON.stringify(updatedLessons));
    }

    function saveCompletedLesson(lessonName, lessonTime) {
        const completedLessons = JSON.parse(localStorage.getItem('completedTimers')) || [];
        completedLessons.push({ lessonName: lessonName, lessonTime: lessonTime });
        localStorage.setItem('completedTimers', JSON.stringify(completedLessons));
    }

    loadPlannedLessons();
});