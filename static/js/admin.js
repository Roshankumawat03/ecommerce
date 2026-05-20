// ─── SIDEBAR TOGGLE ───
const sidebar = document.getElementById('adminSidebar');
document.addEventListener('click', (e) => {
  if (sidebar && sidebar.classList.contains('open')) {
    if (!sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
      sidebar.classList.remove('open');
    }
  }
});

// ─── AUTO DISMISS FLASH ───
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => {
    flash.style.opacity = '0';
    flash.style.transition = 'opacity 0.4s';
    setTimeout(() => flash.remove(), 400);
  }, 4000);
});

// ─── MODAL OVERLAY CLOSE ───
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.style.display = 'none';
  });
});

// ─── ESC KEY CLOSE MODAL ───
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
    if (sidebar) sidebar.classList.remove('open');
  }
});

// ─── TABLE SEARCH (CLIENT SIDE) ───
const tableSearchInput = document.getElementById('tableSearch');
if (tableSearchInput) {
  tableSearchInput.addEventListener('input', function() {
    const term = this.value.toLowerCase();
    document.querySelectorAll('.admin-table tbody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  });
}

// ─── STAT CARD COUNTER ANIMATION ───
document.querySelectorAll('.stat-num').forEach(el => {
  const text = el.textContent.trim();
  const isRupee = text.startsWith('₹');
  const raw = text.replace(/[₹,]/g, '');
  const num = parseFloat(raw);
  if (!isNaN(num) && num > 0) {
    let start = 0;
    const duration = 1200;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(eased * num);
      if (isRupee) {
        el.textContent = '₹' + current.toLocaleString('en-IN');
      } else {
        el.textContent = current.toLocaleString('en-IN');
      }
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = text;
    };
    requestAnimationFrame(step);
  }
});

// ─── ORDER STATUS QUICK CHANGE CONFIRM ───
document.querySelectorAll('.inline-form select').forEach(sel => {
  const original = sel.value;
  sel.addEventListener('change', function() {
    const newVal = this.value;
    if (newVal === 'Cancelled') {
      if (!confirm(`Order cancel karna chahte ho? Yeh undo nahi ho sakta.`)) {
        this.value = original;
      }
    }
  });
});

// ─── IMAGE URL PREVIEW ───
const imageInputs = document.querySelectorAll('input[name="image_url"]');
imageInputs.forEach(input => {
  input.addEventListener('blur', function() {
    const url = this.value.trim();
    if (url) {
      let preview = this.parentElement.querySelector('.img-preview');
      if (!preview) {
        preview = document.createElement('img');
        preview.className = 'img-preview';
        preview.style.cssText = 'width:80px;height:80px;object-fit:cover;border-radius:8px;margin-top:.5rem;border:1px solid #e2e8f0;';
        this.parentElement.appendChild(preview);
      }
      preview.src = url;
      preview.onerror = () => preview.remove();
    }
  });
});

// ─── RESPONSIVE TABLE WRAP ───
document.querySelectorAll('.admin-table').forEach(table => {
  if (window.innerWidth < 640) {
    table.style.fontSize = '.78rem';
  }
});

console.log('🛡️ ShopNest Admin Panel - Ready!');
