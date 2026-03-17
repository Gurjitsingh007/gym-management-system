// ═══════════════════════════════════════════
// FITCORE PRO — MAIN JS
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── Theme Toggle ──
  const html = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');
  const savedTheme = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (themeIcon) themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
  }

  // ── Sidebar Toggle ──
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
    // Close on outside click on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  // ── Auto-dismiss alerts ──
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-6px)';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // ── Set today's date in date inputs ──
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"]').forEach(input => {
    if (!input.value) input.value = today;
  });

  // ── Active nav highlight ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      item.classList.add('active');
    }
  });

  // ── Animate numbers ──
  function animateCounters() {
    document.querySelectorAll('.counter').forEach(el => {
      const target = parseInt(el.dataset.target) || 0;
      let count = 0;
      const step = Math.max(1, Math.ceil(target / 40));
      const timer = setInterval(() => {
        count = Math.min(count + step, target);
        el.textContent = count.toLocaleString();
        if (count >= target) clearInterval(timer);
      }, 30);
    });
  }
  animateCounters();

  // ── Ripple effect on buttons ──
  document.querySelectorAll('.btn, .btn-login').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.cssText = `
        position:absolute; width:${size}px; height:${size}px;
        background:rgba(255,255,255,0.2); border-radius:50%;
        top:${e.clientY-rect.top-size/2}px; left:${e.clientX-rect.left-size/2}px;
        animation:ripple 0.5s ease; pointer-events:none;
      `;
      if (!['absolute','relative','fixed'].includes(getComputedStyle(this).position)) {
        this.style.position = 'relative';
      }
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 500);
    });
  });

  // Ripple keyframe
  if (!document.getElementById('ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = '@keyframes ripple{from{transform:scale(0);opacity:1}to{transform:scale(2);opacity:0}}';
    document.head.appendChild(style);
  }

  // ── Table row click to highlight ──
  document.querySelectorAll('.data-table tbody tr').forEach(row => {
    row.style.cursor = 'default';
    row.addEventListener('mouseenter', () => row.style.transition = 'background 0.2s');
  });

  // ── Confirm delete dialogs ── (enhanced)
  document.querySelectorAll('[onsubmit]').forEach(form => {
    // Already handled inline
  });

  console.log('🏋️ FitCore Pro initialized');
});
