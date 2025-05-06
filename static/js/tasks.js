// Genel veri (sadece örnek, backend yerine AJAX/FastAPI API'den alınmalı)
let tasks = [
    { id: 1, title: "Örnek görev", completed: false }
];

// ---------- Görev Listeleme (tasks.html) ----------
document.addEventListener('DOMContentLoaded', () => {
    const taskListEl = document.getElementById('taskList');
    if (taskListEl) renderTasks(); // Sadece tasks.html yüklendiyse çalışsın
});

function renderTasks() {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `
            <span class="${task.completed ? 'text-decoration-line-through' : ''}">
                ${task.title}
            </span>
            <div>
                <button class="btn btn-sm btn-success me-2" onclick="toggleComplete(${task.id})">
                    ${task.completed ? 'Geri Al' : 'Tamamla'}
                </button>
                <button class="btn btn-sm btn-warning me-2" onclick="editTask(${task.id})">
                    Düzenle
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">
                    Sil
                </button>
            </div>
        `;
        taskList.appendChild(li);
    });
}

function toggleComplete(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        renderTasks();
    }
}

function deleteTask(id) {
    tasks = tasks.filter(t => t.id !== id);
    renderTasks();
}

function editTask(id) {
    window.location.href = `/edit-task/${id}`;
}

// ---------- Yeni Görev Ekleme (add-task.html) ----------
document.addEventListener('DOMContentLoaded', () => {
    const addForm = document.getElementById('addTaskForm');
    if (addForm) {
        addForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const titleInput = document.getElementById('title');
            const title = titleInput.value.trim();

            if (title !== '') {
                fetch('/add-task', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ title })
                })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/tasks';
                    } else {
                        alert("Görev eklenemedi.");
                    }
                });
            }
        });
    }
});

// ---------- Görev Düzenleme (edit-task.html) ----------
document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('editTaskForm');
    if (editForm) {
        editForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const id = editForm.dataset.id; // form'da data-id="123" gibi
            const titleInput = document.getElementById('title');
            const title = titleInput.value.trim();

            if (title !== '') {
                fetch(`/edit-task/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ title })
                })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/tasks';
                    } else {
                        alert("Görev güncellenemedi.");
                    }
                });
            }
        });
    }
});
