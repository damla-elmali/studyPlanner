document.addEventListener('DOMContentLoaded', () => {
    const currentWeekDisplay = document.getElementById('current-week');
    const prevWeekButton = document.getElementById('prev-week');
    const nextWeekButton = document.getElementById('next-week');
    const weekDaysList = document.querySelector('.week-days');
    const addLessonForm = document.getElementById('add-lesson-form');
    const lessonDateInput = document.getElementById('lesson-date');
    const lessonNameInput = document.getElementById('lesson-name'); // Ders adı input'unu al
    const lessonTypeInput = document.getElementById('lesson-type');   // Ders türü input'unu al
    const studyDurationInput = document.getElementById('study-duration'); // Süre input'unu al
    const lessonTimeInput = document.getElementById('lesson-time');     // Ders saati input'unu al

    let currentDate = new Date();
    let currentWeekStart;
    let currentWeekEnd;

    function getStartOfWeek(date) {
        const day = date.getDay();
        const diff = date.getDate() - day + (day === 0 ? -6 : 1);
        const startOfWeek = new Date(date);
        startOfWeek.setDate(diff);
        startOfWeek.setHours(0, 0, 0, 0);
        return startOfWeek;
    }

    function getEndOfWeek(date) {
        const startOfWeek = getStartOfWeek(new Date(date));
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        endOfWeek.setHours(23, 59, 59, 999);
        return endOfWeek;
    }

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function displayCurrentWeek() {
        currentWeekStart = getStartOfWeek(new Date(currentDate));
        currentWeekEnd = getEndOfWeek(new Date(currentDate));
        const startDateFormatted = new Intl.DateTimeFormat('tr-TR', { month: 'long', day: 'numeric' }).format(currentWeekStart);
        const endDateFormatted = new Intl.DateTimeFormat('tr-TR', { month: 'long', day: 'numeric' }).format(currentWeekEnd);
        currentWeekDisplay.textContent = `${startDateFormatted} - ${endDateFormatted}`;
        renderWeekDays(currentWeekStart);

        lessonDateInput.min = formatDate(currentWeekStart);
        lessonDateInput.max = formatDate(currentWeekEnd);
    }

    function renderWeekDays(startOfWeek) {
        weekDaysList.innerHTML = '';
        const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
        const freeStudyDataJSON = localStorage.getItem('freeStudySession');

        let freeStudyData = null;
        if (freeStudyDataJSON) {
            freeStudyData = JSON.parse(freeStudyDataJSON);
            localStorage.removeItem('freeStudySession'); // Veriyi bir kere okuduktan sonra temizle
        }

        for (let i = 0; i < 7; i++) {
            const day = new Date(startOfWeek);
            day.setDate(startOfWeek.getDate() + i);
            const dayFormatted = formatDate(day);
            const dayName = new Intl.DateTimeFormat('tr-TR', { weekday: 'short' }).format(day);
            const dayNumber = day.getDate();

            const dayItem = document.createElement('li');
            dayItem.innerHTML = `<span class="day-number">${dayName} ${dayNumber}</span>`;

            // Serbest çalışma verisini takvime ekle
            if (freeStudyData) {
                const startTime = new Date(freeStudyData.startTime);
                const studyDayFormatted = formatDate(new Date(freeStudyData.date));

                if (studyDayFormatted === dayFormatted) {
                    const lessonDiv = document.createElement('div');
                    lessonDiv.classList.add('lesson');
                    lessonDiv.textContent = `Serbest (${Math.floor(freeStudyData.duration / 60)} dk) ${new Date(freeStudyData.startTime).toLocaleTimeString().slice(0, 5)}`;
                    lessonDiv.style.backgroundColor = 'cyan'; // Mor renk
                    dayItem.appendChild(lessonDiv);
                }
            }

            const lessonsOnDay = lessons.filter(lesson => lesson.time.startsWith(dayFormatted));


            lessonsOnDay.forEach(lesson => {
                const lessonDiv = document.createElement('div');
                lessonDiv.classList.add('lesson');
                const lessonStartTime = lesson.time.split('T')[1].slice(0, 5);
                lessonDiv.textContent = `${lesson.name} (${lesson.studyDuration} dk) ${lessonStartTime}`;
                lessonDiv.style.backgroundColor = lesson.color;
                if (lesson.completed) {
                    const tick = document.createElement('orange');
                    tick.classList.add('completed-tick');
                    tick.textContent = '✓';
                    lessonDiv.appendChild(tick);
                }
                dayItem.appendChild(lessonDiv);
            });
            weekDaysList.appendChild(dayItem);
        }
    }

    prevWeekButton.addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() - 7);
        displayCurrentWeek();
    });

    nextWeekButton.addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() + 7);
        displayCurrentWeek();
    });

    addLessonForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const lessonName = lessonNameInput.value;
        const lessonType = lessonTypeInput.value;
        const studyDuration = parseInt(studyDurationInput.value);
        const lessonDate = lessonDateInput.value;
        const lessonTime = lessonTimeInput.value;
        const combinedDateTime = `${lessonDate}T${lessonTime}:00`;

        const selectedDate = new Date(lessonDate);

        if (selectedDate >= currentWeekStart && selectedDate <= currentWeekEnd) {
            let lessonColor = '';
            switch (lessonType) {
                case 'matematik': lessonColor = '#add8e6'; // Mavi
                    break;
                case 'fen': lessonColor = '#90ee90'; // Yeşil
                    break;
                case 'turkce': lessonColor = '#ff0000'; // Kırmızı
                    break;
                case 'sosyal': lessonColor = '#ffff00'; // Sarı
                    break;
                default: lessonColor = '#e0e0e0';
            }

            const newLesson = {
                name: lessonName,
                type: lessonType,
                studyDuration: studyDuration,
                time: combinedDateTime,
                completed: false,
                color: lessonColor,
                day: new Intl.DateTimeFormat('tr-TR', { weekday: 'long' }).format(selectedDate).toLowerCase() // Hangi güne eklendiği bilgisi
            };

            const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
            lessons.push(newLesson);
            localStorage.setItem('lessons', JSON.stringify(lessons));
            addLessonForm.reset();
            displayCurrentWeek();
        } else {
            alert('Lütfen sadece mevcut haftaya ders ekleyebilirsiniz.');
        }
    });

    function checkCompletedLessons() {
        const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
        const updatedLessons = lessons.map(lesson => {
            const completedTimers = JSON.parse(localStorage.getItem('completedTimers')) || [];
            const isCompleted = completedTimers.some(timer =>
                timer.lessonName === lesson.name && timer.startTime.startsWith(lesson.time.split('T')[0]) && timer.startTime.endsWith(lesson.time.split('T')[1].slice(0, 8))
            );
            return isCompleted ? { ...lesson, completed: true } : lesson;
        });
        localStorage.setItem('lessons', JSON.stringify(updatedLessons));
        displayCurrentWeek();
    }

    displayCurrentWeek();
    checkCompletedLessons();
    
});