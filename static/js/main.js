// ══════════════════════════════════════════════
//   ShopX — Main JavaScript
// ══════════════════════════════════════════════

// ─── HAMBURGER MENU ───────────────────────────
const hamburger = document.getElementById('hamburger');
const mobileNav = document.getElementById('mobileNav');

if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
        mobileNav.classList.toggle('open');
        const spans = hamburger.querySelectorAll('span');
        spans.forEach(s => s.style.background = mobileNav.classList.contains('open') ? 'var(--gold)' : '');
    });
}

// ─── STICKY NAVBAR SHADOW ─────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (navbar) {
        if (window.scrollY > 20) {
            navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    }
});

// ─── AUTO-DISMISS FLASH MESSAGES ──────────────
document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
        flash.style.opacity = '0';
        flash.style.transform = 'translateX(100px)';
        flash.style.transition = '0.4s ease';
        setTimeout(() => flash.remove(), 400);
    }, 4000);
});

// ─── CARD ENTRANCE ANIMATIONS ─────────────────
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, idx) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, idx * 60);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .featured-card, .order-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(24px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
});

// ─── ADD TO CART ANIMATION ────────────────────
document.querySelectorAll('.btn-add-cart, .btn-detail-cart').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const originalHTML = this.innerHTML;
        this.innerHTML = '<i class="fas fa-check"></i> Added!';
        this.style.background = 'var(--green)';
        this.style.color = '#000';
        this.style.borderColor = 'var(--green)';
        setTimeout(() => {
            this.innerHTML = originalHTML;
            this.style.background = '';
            this.style.color = '';
            this.style.borderColor = '';
        }, 1500);
    });
});

// ─── SMOOTH SCROLL FOR ANCHOR LINKS ──────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            const offset = 80;
            const top = target.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    });
});

// ─── IMAGE LAZY LOADING FALLBACK ──────────────
document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    img.addEventListener('error', function() {
        this.src = 'https://via.placeholder.com/400x300/1a1a2e/d4af37?text=ShopX';
    });
});

// ─── CART QUANTITY INPUT ──────────────────────
document.querySelectorAll('.qty-input').forEach(input => {
    input.addEventListener('change', function() {
        const min = parseInt(this.min || 1);
        const max = parseInt(this.max || 999);
        let val = parseInt(this.value);
        if (isNaN(val) || val < min) this.value = min;
        else if (val > max) this.value = max;
    });
});

// ─── PRODUCT IMAGE HOVER ZOOM ─────────────────
document.querySelectorAll('.product-img-wrap').forEach(wrap => {
    wrap.addEventListener('mouseenter', function() {
        const img = this.querySelector('img');
        if (img) img.style.transform = 'scale(1.05)';
    });
    wrap.addEventListener('mouseleave', function() {
        const img = this.querySelector('img');
        if (img) img.style.transform = 'scale(1)';
    });
});

// ─── FORM VALIDATION FEEDBACK ─────────────────
document.querySelectorAll('input[required], select[required]').forEach(el => {
    el.addEventListener('invalid', function() {
        this.style.borderColor = 'var(--red)';
        this.style.boxShadow = '0 0 0 3px rgba(255,71,87,0.1)';
    });
    el.addEventListener('input', function() {
        if (this.validity.valid) {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        }
    });
});

// ─── RIPPLE EFFECT ON BUTTONS ─────────────────
document.querySelectorAll('.btn-checkout, .btn-place-order, .btn-auth, .btn-hero-primary').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.cssText = `
            position:absolute; width:${size}px; height:${size}px;
            border-radius:50%; background:rgba(255,255,255,0.3);
            transform:scale(0); animation:rippleAnim 0.5s linear;
            left:${e.clientX - rect.left - size/2}px;
            top:${e.clientY - rect.top - size/2}px;
            pointer-events:none;
        `;
        if (!this.style.position || this.style.position === 'static') {
            this.style.position = 'relative';
        }
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 500);
    });
});

// Ripple animation
const style = document.createElement('style');
style.textContent = `@keyframes rippleAnim { to { transform: scale(4); opacity: 0; } }`;
document.head.appendChild(style);

console.log('🛍️ ShopX loaded successfully!');
