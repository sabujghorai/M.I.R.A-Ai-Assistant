const API_BASE = "http://localhost:8000";

const navButtons = document.querySelectorAll('.nav-btn');
const views = document.querySelectorAll('.view');

navButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    navButtons.forEach(b => b.classList.remove('active'));
    views.forEach(v => v.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(btn.dataset.view).classList.add('active');

    if (btn.dataset.view === 'dashboard') loadDashboard();
    if (btn.dataset.view === 'schedule') loadSchedule();
  });
});

async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard`);
    const data = await res.json();

    document.getElementById('pendingCount').textContent = data.pending_count;
    document.getElementById('blocksAvailable').textContent = data.blocks_available;
    document.getElementById('assetUptime').textContent = `${data.asset_uptime}%`;
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

const priorityClass = { High: 'high', Medium: 'medium', Low: 'low' };

async function loadSchedule() {
  const scheduleBody = document.getElementById('scheduleBody');
  try {
    const res = await fetch(`${API_BASE}/api/schedule`);
    const rows = await res.json();

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
    console.error('Failed to load schedule:', err);
  }
}

const optimizeBtn = document.getElementById('optimizeBtn');
const optimizeMsg = document.getElementById('optimizeMsg');

if (optimizeBtn) {
  optimizeBtn.addEventListener('click', async () => {
    optimizeBtn.disabled = true;
    optimizeBtn.textContent = 'Optimizing...';

    try {
      const res = await fetch(`${API_BASE}/api/optimize`, { method: 'POST' });
      const data = await res.json();

      optimizeMsg.textContent = data.message;
      await loadSchedule();
      await loadDashboard();
    } catch (err) {
      optimizeMsg.textContent = 'Optimizer failed — check backend is running.';
      console.error(err);
    } finally {
      optimizeBtn.disabled = false;
      optimizeBtn.textContent = '⚙️ Run AI Optimizer';
      setTimeout(() => { optimizeMsg.textContent = ''; }, 5000);
    }
  });
}

const requestForm = document.getElementById('requestForm');
const confirmMsg = document.getElementById('confirmMsg');

requestForm.addEventListener('submit', async function (e) {
  e.preventDefault();

  const department = document.getElementById('department').value;
  const section = document.getElementById('section').value.trim();
  const issue = document.getElementById('issue').value.trim();
  const priority = document.getElementById('priority').value;

  if (!department || !section || !issue || !priority) return;

  try {
    const res = await fetch(`${API_BASE}/api/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ department, section, issue, priority }),
    });

    if (!res.ok) throw new Error('Request failed');

    confirmMsg.style.color = '#4ade80';
    confirmMsg.textContent = `Request for ${section} (${department}) submitted successfully.`;
    requestForm.reset();
    await loadDashboard();

    setTimeout(() => { confirmMsg.textContent = ''; }, 4000);
  } catch (err) {
    confirmMsg.style.color = '#ff6b6b';
    confirmMsg.textContent = 'Failed to submit — check backend is running.';
    console.error(err);
  }
});

loadDashboard();
loadSchedule();
