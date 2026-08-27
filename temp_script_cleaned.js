
  const canManageTasks = true;
  const statuses = { open: 'Offen', in_progress: 'In Bearbeitung', completed: 'Erledigt' };
  const today = new Date().toISOString().slice(0, 10);
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const taskModal = document.getElementById('task-modal');
  const taskMessage = document.getElementById('task-message');
  function showTaskMessage(message, target = taskMessage) { target.textContent = message || ''; target.classList.toggle('is-visible', Boolean(message)); }
  async function loadOptions() {
    const response = await fetch('/api/task-options'); const data = await response.json();
    if (!data.success) throw new Error(data.message);
    document.getElementById('task-employee').innerHTML = data.employees.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
    document.getElementById('task-template').innerHTML = data.templates.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
  }
  let taskPage = 1; let taskTotalPages = 1; let taskSort = 'due_date'; let taskDirection = 'asc';
  const taskFilters = { employee: '', template: '', due_date: '', created_at: '' };
  function renderTasks(taskRows, total) { document.getElementById('task-count').textContent = `${total} Aufgaben`; document.getElementById('tasks-tbody').innerHTML = taskRows.length ? taskRows.map(task => `<tr><td>${task.id}</td><td>${escapeHtml(task.employee_name)}</td><td>${escapeHtml(task.template_task_title)}</td><td>${escapeHtml(task.title)}</td><td>${escapeHtml(task.description)}</td><td>${escapeHtml(task.due_date || '')}</td><td>${escapeHtml(statuses[task.status] || task.status)}</td><td>${escapeHtml(task.created_at || '')}</td><td><button class="secondary-btn task-edit" data-id="${task.id}" type="button">Bearbeiten</button></td></tr>`).join('') : '<tr><td colspan="9" class="table-message">Keine Aufgaben vorhanden.</td></tr>'; document.querySelectorAll('.task-edit').forEach(button => button.addEventListener('click', () => openEditTask(taskRows.find(task => String(task.id) === button.dataset.id)))); }
  async function loadTasks() { const params = new URLSearchParams({ page: taskPage, sort: taskSort, direction: taskDirection }); Object.entries(taskFilters).forEach(([key, value]) => { if (value) params.set(key, value); }); const response = await fetch(`/api/tasks?${params}`); const data = await response.json(); if (!data.success) throw new Error(data.message); taskPage = data.page; taskTotalPages = data.total_pages; renderTasks(data.tasks, data.total); document.getElementById('task-pagination').classList.toggle('is-hidden', data.total <= 800); document.getElementById('task-page-info').textContent = `Seite ${data.page} von ${data.total_pages}`; document.getElementById('task-prev').disabled = data.page <= 1; document.getElementById('task-next').disabled = data.page >= data.total_pages; }
  function openEditTask(task) { if (!task) return; document.getElementById('edit-task-id').value = task.id; document.getElementById('edit-task-name').value = task.title || ''; document.getElementById('edit-task-description').value = task.description || ''; document.getElementById('edit-task-due-date').value = task.due_date || ''; document.getElementById('edit-task-status').innerHTML = Object.entries(statuses).map(([key, label]) => `<option value="${key}" ${task.status === key ? 'selected' : ''}>${label}</option>`).join(''); document.getElementById('edit-task-modal').classList.remove('is-hidden'); }
  async function saveTask(event) { event.preventDefault(); const id = document.getElementById('edit-task-id').value; const response = await fetch(`/api/tasks/${id}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title: document.getElementById('edit-task-name').value, description: document.getElementById('edit-task-description').value, due_date: document.getElementById('edit-task-due-date').value, status: document.getElementById('edit-task-status').value}) }); const data = await response.json(); document.getElementById('edit-task-message').textContent = data.success ? 'Aufgabe gespeichert.' : data.message; if (data.success) { document.getElementById('edit-task-modal').classList.add('is-hidden'); loadTasks(); } }
  async function loadSuggestions(input) { const value = input.value.trim(); const container = input.nextElementSibling; if (value.length < 3) { taskFilters[input.dataset.field] = ''; container.classList.add('is-hidden'); taskPage = 1; loadTasks(); return; } const response = await fetch(`/api/tasks/suggestions?field=${input.dataset.field}&q=${encodeURIComponent(value)}`); const data = await response.json(); container.innerHTML = (data.suggestions || []).map(item => `<button type="button" class="task-suggestion" data-value="${escapeHtml(item.value)}">${escapeHtml(item.label)}</button>`).join('') || '<span class="task-suggestion-empty">Keine Treffer</span>'; container.classList.remove('is-hidden'); container.querySelectorAll('[data-value]').forEach(button => button.addEventListener('click', () => { input.value = button.textContent; taskFilters[input.dataset.field] = button.dataset.value; container.classList.add('is-hidden'); taskPage = 1; loadTasks(); })); }
  document.getElementById('assign-task-btn').addEventListener('click', () => { taskModal.classList.remove('is-hidden'); });
  document.getElementById('task-modal-close').addEventListener('click', () => taskModal.classList.add('is-hidden'));
  document.getElementById('task-form-cancel').addEventListener('click', () => taskModal.classList.add('is-hidden'));
  document.getElementById('edit-task-close').addEventListener('click', () => document.getElementById('edit-task-modal').classList.add('is-hidden'));
  document.getElementById('edit-task-cancel').addEventListener('click', () => document.getElementById('edit-task-modal').classList.add('is-hidden'));
  document.getElementById('edit-task-form').addEventListener('submit', saveTask);
  document.querySelectorAll('[data-sort]').forEach(button => button.addEventListener('click', () => { taskSort = button.dataset.sort; taskDirection = button.dataset.direction; taskPage = 1; loadTasks(); }));
  document.querySelectorAll('.task-filter input').forEach(input => input.addEventListener('input', () => loadSuggestions(input)));
  document.getElementById('task-prev').addEventListener('click', () => { taskPage = Math.max(1, taskPage - 1); loadTasks(); });
  document.getElementById('task-next').addEventListener('click', () => { taskPage = Math.min(taskTotalPages, taskPage + 1); loadTasks(); });
  document.getElementById('task-form').addEventListener('submit', async event => {
    event.preventDefault(); const formMessage = document.getElementById('task-form-message');
    const response = await fetch('/api/tasks', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({employee_id: document.getElementById('task-employee').value, entry_date: document.getElementById('task-entry-date').value, template_id: document.getElementById('task-template').value}) });
    const data = await response.json(); showTaskMessage(data.success ? `${data.created} Aufgaben zugewiesen.` : data.message, formMessage); if (data.success) { taskModal.classList.add('is-hidden'); loadTasks(); }
  });
  document.getElementById('task-entry-date').value = today;
  Promise.all([loadOptions(), loadTasks()]).catch(error => showTaskMessage(error.message));
