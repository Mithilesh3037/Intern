/* CartSense – Main JavaScript */

// ── Sidebar toggle ────────────────────────────────────────────────
const sidebar  = document.getElementById('sidebar');
const overlay  = document.getElementById('sidebarOverlay');
const menuBtn  = document.getElementById('menuBtn');
const closeBtn = document.getElementById('sidebarClose');

function openSidebar()  { sidebar.classList.add('open');  overlay.classList.add('show'); }
function closeSidebar() { sidebar.classList.remove('open'); overlay.classList.remove('show'); }

if (menuBtn)  menuBtn.addEventListener('click', openSidebar);
if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
if (overlay)  overlay.addEventListener('click', closeSidebar);

// ── Toast notifications ────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i class="fas ${icons[type] || icons.info}"></i>
    <span>${message}</span>
    <span class="toast-close" onclick="this.parentElement.remove()">
      <i class="fas fa-xmark"></i>
    </span>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── Flash messages → toasts ────────────────────────────────────────
if (window.__flashMessages) {
  window.__flashMessages.forEach(([cat, msg]) => {
    const type = cat === 'error' ? 'error' : cat === 'success' ? 'success' : 'info';
    showToast(msg, type);
  });
}

// ── Global fetch wrapper with toast on error ───────────────────────
window.csAPI = async function(url, options = {}) {
  try {
    const res  = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Request failed', 'error'); return null; }
    return data;
  } catch (e) {
    showToast('Network error — is the server running?', 'error');
    return null;
  }
};

// ── Animate stat numbers on scroll ────────────────────────────────
function animateNumber(el, target, duration = 1000) {
  const start = performance.now();
  const from  = 0;
  function update(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(from + (target - from) * ease);
    if (t < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

document.querySelectorAll('.stat-value').forEach(el => {
  const num = parseFloat(el.textContent);
  if (!isNaN(num) && num > 0) {
    const orig = el.textContent;
    el.textContent = '0';
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        animateNumber(el, num);
        obs.disconnect();
      }
    }, { threshold: 0.5 });
    obs.observe(el);
  }
});

// ── Table row click → navigate ────────────────────────────────────
document.querySelectorAll('table tbody tr[data-href]').forEach(row => {
  row.style.cursor = 'pointer';
  row.addEventListener('click', e => {
    if (!e.target.closest('button, a')) window.location = row.dataset.href;
  });
});
