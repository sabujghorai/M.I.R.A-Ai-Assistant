const API_BASE = "http://localhost:8000";

// ---- Navigation between views ----
const navButtons = document.querySelectorAll('.nav-btn');
const views = document.querySelectorAll('.view');

navButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    navButtons.forEach(b => b.classList.remove('active'));
    views.forEach(v => v.classList.remove('active'));

    btn.classList.add('active');
    const target = document.getElementById(btn.dataset.view);
    if (target) target.classList.add('active');

    if (btn.dataset.view === 'dashboard') loadDashboard();
    if (btn.dataset.view === 'schedule') loadSchedule();
  });
});

// ---- Dashboard ----
async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard`);
    if (!res.ok) throw new Error(`Dashboard request failed: ${res.status}`);
    const data = await res.json();

    const pendingEl = document.getElementById('pendingCount');
    const blocksEl = document.getElementById('blocksAvailable');
    if (pendingEl && data.pending_count !== undefined) pendingEl.textContent = data.pending_count;
    if (blocksEl && data.blocks_available !== undefined) blocksEl.textContent = data.blocks_available;

    const uptimeCard = document.querySelectorAll('.card p')[2];
    if (uptimeCard && data.asset_uptime !== undefined) uptimeCard.textContent = `${data.asset_uptime}%`;
  } catch (err) {
    console.warn('Could not reach the backend for dashboard data:', err.message);
  }
}

// ---- Schedule ----
const priorityClass = { Critical: 'critical', High: 'high', Medium: 'medium', Low: 'low' };

async function loadSchedule() {
  const scheduleBody = document.getElementById('scheduleBody');
  if (!scheduleBody) return;

  try {
    const res = await fetch(`${API_BASE}/api/schedule`);
    if (!res.ok) throw new Error(`Schedule request failed: ${res.status}`);
    const rows = await res.json();

    // The backend is the single source of truth here — including
    // submitted requests — so it's safe to fully replace the table.
    scheduleBody.innerHTML = '';
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.day}</td>
        <td>${r.department}</td>
        <td>${r.section}</td>
        <td>${r.block_time}</td>
        <td class="${priorityClass[r.priority] || ''}">${r.priority}</td>
      `;
      scheduleBody.appendChild(tr);
    });
  } catch (err) {
    // Backend unreachable — leave whatever static rows are already
    // in the HTML rather than guessing at data.
    console.warn('Could not reach the backend for schedule data:', err.message);
  }
}

// ---- Run optimizer ----
const optimizeBtn = document.getElementById('optimizeBtn');
const optimizeMsg = document.getElementById('optimizeMsg');

if (optimizeBtn) {
  optimizeBtn.addEventListener('click', async () => {
    optimizeBtn.disabled = true;
    optimizeBtn.textContent = 'Optimizing...';

    try {
      const res = await fetch(`${API_BASE}/api/optimize`, { method: 'POST' });
      const data = await res.json();

      if (!res.ok) throw new Error(data.message || 'Optimizer failed.');

      if (optimizeMsg) optimizeMsg.textContent = data.message;
      await loadSchedule();
      await loadDashboard();
    } catch (err) {
      if (optimizeMsg) optimizeMsg.textContent = err.message;
      console.error(err);
    } finally {
      optimizeBtn.disabled = false;
      optimizeBtn.textContent = 'Run AI Optimizer';
      if (optimizeMsg) setTimeout(() => { optimizeMsg.textContent = ''; }, 5000);
    }
  });
}

// ---- Request form ----
const requestForm = document.getElementById('requestForm');
const confirmMsg = document.getElementById('confirmMsg');

function showConfirmMsg(text, isError) {
  if (!confirmMsg) return;
  confirmMsg.textContent = text;
  confirmMsg.classList.toggle('error', !!isError);
  confirmMsg.style.display = 'block';

  clearTimeout(showConfirmMsg._timer);
  showConfirmMsg._timer = setTimeout(() => {
    confirmMsg.style.display = 'none';
  }, 5000);
}

if (requestForm) {
  requestForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const department = document.getElementById('department').value;
    const section = document.getElementById('section').value;
    const issue = document.getElementById('issue').value.trim();
    const priority = document.getElementById('priority').value;

    if (!department || !section || !issue || !priority) return;

    try {
      const res = await fetch(`${API_BASE}/api/requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ department, section, issue, priority }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Request failed.');

      showConfirmMsg(`Request for ${section} (${department}) submitted — check Block Schedule.`, false);
      requestForm.reset();

      await loadSchedule();
      await loadDashboard();
    } catch (err) {
      showConfirmMsg(`Could not submit — ${err.message} Make sure the backend is running on ${API_BASE}.`, true);
      console.error(err);
    }
  });
}

// ---- Initial load ----
loadDashboard();
loadSchedule();
