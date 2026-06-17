/**
 * API wrapper with auth header, error handling, toast notifications.
 */

// ── Toast System ─────────────────────────────────────────────
function initToasts() {
  if (!document.getElementById('toast-container')) {
    const tc = document.createElement('div');
    tc.id = 'toast-container';
    document.body.appendChild(tc);
  }
}

function showToast(message, type = 'info', duration = 3500) {
  initToasts();
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  document.getElementById('toast-container').appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

window.showToast = showToast;

// ── Auth Token ───────────────────────────────────────────────
function getToken() {
  return localStorage.getItem('qlkns_token');
}

function setToken(token) {
  localStorage.setItem('qlkns_token', token);
}

function clearToken() {
  localStorage.removeItem('qlkns_token');
  localStorage.removeItem('qlkns_user');
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('qlkns_user') || 'null');
  } catch { return null; }
}

function setUser(user) {
  localStorage.setItem('qlkns_user', JSON.stringify(user));
}

window.getToken = getToken;
window.setToken = setToken;
window.clearToken = clearToken;
window.getUser = getUser;
window.setUser = setUser;

// ── API Fetch Wrapper ────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const url = window.API_BASE + path;

  try {
    const resp = await fetch(url, {
      ...options,
      headers,
      body: options.body ? (typeof options.body === 'string' ? options.body : JSON.stringify(options.body)) : undefined
    });

    // Handle 401 - redirect to login
    if (resp.status === 401) {
      clearToken();
      window.location.href = '/index.html';
      return null;
    }

    const data = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      throw new Error(data.error || `Lỗi ${resp.status}`);
    }

    return data;
  } catch (err) {
    if (err.message !== 'Failed to fetch') {
      throw err;
    }
    throw new Error('Không thể kết nối đến server. Hãy kiểm tra server đang chạy.');
  }
}

async function apiGet(path)          { return apiFetch(path); }
async function apiPost(path, body)   { return apiFetch(path, { method: 'POST', body }); }
async function apiPut(path, body)    { return apiFetch(path, { method: 'PUT', body }); }
async function apiDelete(path)       { return apiFetch(path, { method: 'DELETE' }); }

window.apiGet    = apiGet;
window.apiPost   = apiPost;
window.apiPut    = apiPut;
window.apiDelete = apiDelete;
window.apiFetch  = apiFetch;

// ── Utility helpers ──────────────────────────────────────────
function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function truncate(str, n = 40) {
  if (!str) return '—';
  return str.length > n ? str.slice(0, n) + '…' : str;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

window.formatDate  = formatDate;
window.truncate    = truncate;
window.escapeHtml  = escapeHtml;

// ── Modal helpers ────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
}

window.openModal = openModal;
window.closeModal = closeModal;
window.closeAllModals = closeAllModals;

// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ── Auth Guard ───────────────────────────────────────────────
function requireLogin(role = null) {
  const token = getToken();
  const user = getUser();
  if (!token || !user) {
    window.location.href = '/index.html';
    return false;
  }
  if (role && user.role !== role) {
    showToast('Không có quyền truy cập trang này', 'error');
    setTimeout(() => { window.location.href = '/index.html'; }, 1500);
    return false;
  }
  return true;
}

window.requireLogin = requireLogin;

// ── Render sidebar user info ──────────────────────────────────
function renderUserInfo() {
  const user = getUser();
  if (!user) return;
  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (nameEl) nameEl.textContent = user.full_name || user.username;
  if (roleEl) roleEl.textContent = user.role === 'manager' ? '👔 Quản Lý' : '👷 Nhân Viên';
  if (avatarEl) avatarEl.textContent = (user.full_name || user.username || 'U')[0].toUpperCase();
}

window.renderUserInfo = renderUserInfo;

function logout() {
  clearToken();
  window.location.href = '/index.html';
}
window.logout = logout;
