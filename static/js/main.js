// ─── HAMBURGER MENU ───
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

// ─── CATEGORIES DROPDOWN ───
const catDropBtn = document.getElementById('catDropBtn');
const catDropdown = document.getElementById('catDropdown');
if (catDropBtn && catDropdown) {
  catDropBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    catDropdown.classList.toggle('open');
    catDropBtn.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!catDropBtn.contains(e.target) && !catDropdown.contains(e.target)) {
      catDropdown.classList.remove('open');
      catDropBtn.classList.remove('open');
    }
  });
}

// ─── AUTO DISMISS FLASH MESSAGES ───
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => {
    flash.style.opacity = '0';
    flash.style.transform = 'translateY(-10px)';
    flash.style.transition = 'all 0.4s ease';
    setTimeout(() => flash.remove(), 400);
  }, 4000);
});

// ─── SMOOTH SCROLL TO TOP ───
window.addEventListener('scroll', () => {
  const scrollTop = document.getElementById('scrollTop');
  if (scrollTop) {
    scrollTop.style.display = window.scrollY > 400 ? 'flex' : 'none';
  }
});

// ─── PRODUCT CARD HOVER ANIMATIONS ───
document.querySelectorAll('.product-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
  });
});

// ─── ADD TO CART ANIMATION ───
document.querySelectorAll('.add-cart-btn').forEach(btn => {
  btn.addEventListener('click', function(e) {
    if (this.disabled) return;
    const original = this.innerHTML;
    this.innerHTML = '<i class="fas fa-check"></i> Added!';
    this.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    setTimeout(() => {
      this.innerHTML = original;
      this.style.background = '';
    }, 1200);
  });
});

// ─── LAZY IMAGE LOADING ───
if ('IntersectionObserver' in window) {
  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        imgObserver.unobserve(img);
      }
    });
  }, { rootMargin: '100px' });
  document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
}

// ─── NAVBAR SCROLL EFFECT ───
let lastScroll = 0;
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
  const currentScroll = window.scrollY;
  if (navbar) {
    if (currentScroll > 100) {
      navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.12)';
    } else {
      navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.06)';
    }
  }
  lastScroll = currentScroll;
});

// ─── PRICE RANGE FILTER LIVE UPDATE ───
const minPriceInput = document.querySelector('input[name="min_price"]');
const maxPriceInput = document.querySelector('input[name="max_price"]');
if (minPriceInput && maxPriceInput) {
  [minPriceInput, maxPriceInput].forEach(input => {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        document.getElementById('priceForm')?.submit();
      }
    });
  });
}

// ─── MODAL CLOSE ON OVERLAY CLICK ───
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.style.display = 'none';
    }
  });
});

// ─── CART QTY FORM QUICK UPDATE ───
document.querySelectorAll('.qty-form').forEach(form => {
  form.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const val = parseInt(this.value);
      if (val <= 0) {
        if (!confirm('Item cart se remove karna chahte ho?')) {
          e.preventDefault();
        }
      }
    });
  });
});

// ─── KEYBOARD ESC CLOSE MOBILE MENU ───
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (mobileMenu) mobileMenu.classList.remove('open');
    document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
  }
});

// ─── STAGGERED PRODUCT CARD ANIMATION ───
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }, i * 60);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card').forEach((card, i) => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';
  card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
  observer.observe(card);
});

// ─── CATEGORY CARD ANIMATION ───
const catObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0) scale(1)';
      }, i * 80);
      catObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.category-card').forEach((card, i) => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(15px) scale(0.97)';
  card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
  catObserver.observe(card);
});

console.log('🛍️ ShopNest - Fully loaded!');
