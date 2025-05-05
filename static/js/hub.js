document.addEventListener('DOMContentLoaded', () => {
    const upcomingLessonsList = document.getElementById('upcoming-lessons-list');

    function loadUpcomingLessons() {
        upcomingLessonsList.innerHTML = '';
        const lessons = JSON.parse(localStorage.getItem('lessons')) || [];
        const completedTimers = JSON.parse(localStorage.getItem('completedTimers')) || [];  // Tamamlanan dersleri al

        const now = new Date();
        const upcoming = lessons.filter(lesson => {
            const lessonTime = new Date(lesson.time);
            const isCompleted = completedTimers.some(timer => {
                // Aynı ders adı ve zamanına sahip bir tamamlanmış kayıt var mı kontrol et
                return timer.lessonName === lesson.name && timer.startTime === lesson.time;
            });
            return lessonTime > now && !isCompleted; // Gelecekteki ve tamamlanmamış dersler
        })
            .sort((a, b) => new Date(a.time) - new Date(b.time))
            .slice(0, 5); // En Yakın 5 Ders

        if (upcoming.length > 0) {
            upcoming.forEach(lesson => {
                const listItem = document.createElement('li');
                listItem.textContent = `${lesson.name} (${lesson.type}) - ${new Intl.DateTimeFormat('tr-TR', {
                    weekday: 'short',
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit'
                }).format(new Date(lesson.time))}`;
                listItem.style.backgroundColor = lesson.color;
                upcomingLessonsList.appendChild(listItem);
            });
        } else {
            const emptyMessage = document.createElement('li');
            emptyMessage.classList.add('empty-message');
            emptyMessage.textContent = 'Yaklaşan ders bulunmuyor.';
            upcomingLessonsList.appendChild(emptyMessage);
        }
    }

    loadUpcomingLessons();
    window.addEventListener('focus', loadUpcomingLessons); // Sayfa odaklandığında güncelle
});
