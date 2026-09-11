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

    // Refresh data whenever a view is opened
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

    // Third stat card (Asset Uptime) has no id in the markup, so it's
    // targeted by position. Left untouched if the backend omits it.
    const uptimeCard = document.querySelectorAll('.card p')[2];
    if (uptimeCard && data.asset_uptime !== undefined) uptimeCard.textContent = `${data.asset_uptime}%`;
  } catch (err) {
    // No backend yet, or it's unreachable — leave the placeholder
    // values in the HTML alone instead of clearing them.
    console.warn('Dashboard not loaded from API (using placeholder values):', err.message);
  }
}

// ---- Schedule ----
const priorityClass = { High: 'high', Medium: 'medium', Low: 'low' };

async function loadSchedule() {
  const scheduleBody = document.getElementById('scheduleBody');
  if (!scheduleBody) return;

  try {
    const res = await fetch(`${API_BASE}/api/schedule`);
    if (!res.ok) throw new Error(`Schedule request failed: ${res.status}`);
    const rows = await res.json();

    // Only replace the static demo rows once we actually have data.
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
    // No backend yet — keep the static rows already in the HTML.
    console.warn('Schedule not loaded from API (showing static rows):', err.message);
  }
}

// ---- Run optimizer (only wired up if these elements exist) ----
const optimizeBtn = document.getElementById('optimizeBtn');
const optimizeMsg = document.getElementById('optimizeMsg');

if (optimizeBtn) {
  optimizeBtn.addEventListener('click', async () => {
    optimizeBtn.disabled = true;
    optimizeBtn.textContent = 'Optimizing...';

    try {
      const res = await fetch(`${API_BASE}/api/optimize`, { method: 'POST' });
      if (!res.ok) throw new Error(`Optimize request failed: ${res.status}`);
      const data = await res.json();

      if (optimizeMsg) optimizeMsg.textContent = data.message || 'Optimization complete.';
      await loadSchedule();
      await loadDashboard();
    } catch (err) {
      if (optimizeMsg) optimizeMsg.textContent = 'Optimizer failed — check backend is running.';
      console.error(err);
    } finally {
      optimizeBtn.disabled = false;
      optimizeBtn.textContent = '⚙️ Run AI Optimizer';
      if (optimizeMsg) setTimeout(() => { optimizeMsg.textContent = ''; }, 5000);
    }
  });
}

// ---- Local fallback helpers (used when the backend isn't reachable) ----
function addLocalScheduleRow({ department, section, priority }) {
  const scheduleBody = document.getElementById('scheduleBody');
  if (!scheduleBody) return;

  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>Unscheduled</td>
    <td>${department}</td>
    <td>${section}</td>
    <td>TBD</td>
    <td class="${priorityClass[priority] || ''}">${priority}</td>
  `;
  scheduleBody.appendChild(tr);

  // Brief highlight so it's obvious which row was just added.
  tr.style.transition = 'background-color 1.2s ease';
  tr.style.backgroundColor = '#e4efec';
  setTimeout(() => { tr.style.backgroundColor = ''; }, 1200);
}

function bumpPendingCount(delta) {
  const pendingEl = document.getElementById('pendingCount');
  if (!pendingEl) return;
  const current = parseInt(pendingEl.textContent, 10);
  if (!isNaN(current)) pendingEl.textContent = current + delta;
}

// ---- Request form ----
const requestForm = document.getElementById('requestForm');
const confirmMsg = document.getElementById('confirmMsg');

if (requestForm) {
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

      if (confirmMsg) {
        confirmMsg.style.color = '';
        confirmMsg.textContent = `Request for ${section} (${department}) submitted successfully.`;
      }
      requestForm.reset();

      // The backend now has the new record — re-fetch both views so
      // the schedule table and dashboard counts reflect it.
      await loadSchedule();
      await loadDashboard();

      if (confirmMsg) setTimeout(() => { confirmMsg.textContent = ''; }, 4000);
    } catch (err) {
      console.error(err);

      // No backend reachable — don't just show an error and drop the
      // request. Add it to the schedule table directly so what the
      // user just submitted is visibly reflected, marked as unscheduled
      // until a real backend or the optimizer assigns it a slot.
      addLocalScheduleRow({ department, section, priority });
      bumpPendingCount(1);

      if (confirmMsg) {
        confirmMsg.style.color = '#b3852c';
        confirmMsg.textContent = `Request for ${section} (${department}) saved locally — backend unreachable, so it hasn't synced to the server yet.`;
      }
      requestForm.reset();

      if (confirmMsg) setTimeout(() => { confirmMsg.textContent = ''; }, 6000);
    }
  });
}

// ---- Initial load ----
loadDashboard();
loadSchedule();