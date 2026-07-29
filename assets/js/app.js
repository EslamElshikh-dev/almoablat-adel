(() => {
  'use strict';

  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const themeButton = document.querySelector('[data-theme-toggle]');

  const getPreferredTheme = () => {
    try {
      const saved = localStorage.getItem('adel-theme');
      if (saved === 'dark' || saved === 'light') return saved;
    } catch (_) {}
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const applyTheme = (theme) => {
    root.dataset.theme = theme;
    if (themeButton) {
      themeButton.setAttribute('aria-label', theme === 'dark' ? 'تفعيل المظهر الفاتح' : 'تفعيل المظهر الداكن');
      themeButton.setAttribute('title', theme === 'dark' ? 'المظهر الفاتح' : 'المظهر الداكن');
    }
    const color = theme === 'dark' ? '#181816' : '#9a6a1f';
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', color);
  };

  applyTheme(getPreferredTheme());

  if (themeButton) {
    themeButton.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      try { localStorage.setItem('adel-theme', next); } catch (_) {}
    });
  }

  const closeMenu = () => {
    if (!menu || !menuButton) return;
    menu.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'فتح القائمة');
  };

  if (menu && menuButton) {
    menuButton.addEventListener('click', () => {
      const open = menu.classList.toggle('is-open');
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'إغلاق القائمة' : 'فتح القائمة');
    });
    menu.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('click', (event) => {
      if (!menu.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMenu();
        menuButton.focus();
      }
    });
  }

  const updateHeader = () => {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  document.querySelectorAll('img').forEach((image) => {
    const markFallback = () => {
      const target = image.closest('.card-media, .hero-visual');
      if (target) target.classList.add('is-fallback');
    };
    if (image.complete && image.naturalWidth === 0) markFallback();
    image.addEventListener('error', markFallback, { once: true });
  });

  document.querySelectorAll('[data-year], [data-current-year]').forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });

  document.querySelectorAll('[data-share]').forEach((button) => {
    button.addEventListener('click', async () => {
      const data = {
        title: button.dataset.shareTitle || document.title,
        text: document.querySelector('meta[name="description"]')?.content || '',
        url: window.location.href,
      };
      try {
        if (navigator.share) {
          await navigator.share(data);
        } else if (navigator.clipboard) {
          await navigator.clipboard.writeText(data.url);
          const original = button.textContent;
          button.textContent = 'تم نسخ الرابط';
          window.setTimeout(() => { button.textContent = original; }, 1800);
        }
      } catch (error) {
        if (error && error.name !== 'AbortError') console.warn('تعذر مشاركة الرابط', error);
      }
    });
  });

  const normalizePhone = (value) => String(value || '').replace(/[^0-9+]/g, '');
  document.querySelectorAll('[data-whatsapp-form]').forEach((form) => {
    const status = form.querySelector('[data-form-status]');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const fields = new FormData(form);
      const name = String(fields.get('name') || '').trim();
      const phone = normalizePhone(fields.get('phone'));
      const service = String(fields.get('service') || '').trim();
      const location = String(fields.get('area') || fields.get('location') || '').trim();
      const details = String(fields.get('details') || '').trim();

      if (name.length < 2 || phone.length < 8 || !service) {
        if (status) {
          status.textContent = 'يرجى إدخال الاسم ورقم جوال صحيح واختيار الخدمة.';
          status.setAttribute('role', 'alert');
        }
        return;
      }

      const message = [
        'مرحبًا المبلط عادل، أحتاج طلب خدمة:',
        `الاسم: ${name}`,
        `رقم التواصل: ${phone}`,
        `الخدمة: ${service}`,
        location ? `الحي أو الموقع: ${location}` : '',
        details ? `التفاصيل: ${details}` : '',
        `الصفحة: ${window.location.href}`,
      ].filter(Boolean).join('\n');

      if (status) {
        status.textContent = 'سيتم فتح واتساب لإرسال الطلب.';
        status.setAttribute('role', 'status');
      }
      window.open(`https://wa.me/966567372527?text=${encodeURIComponent(message)}`, '_blank', 'noopener,noreferrer');
    });
  });
})();
