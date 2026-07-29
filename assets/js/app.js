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

  const assistantChoices = {
    installation: {
      reply: 'للتركيب الجديد جهّز نوع البلاط أو البورسلان، المقاس، المساحة التقريبية وصور السطح. هذه التفاصيل تساعد على تحديد التجهيز والمواد المطلوبة قبل المعاينة.',
      message: 'مرحبًا المبلط عادل، أحتاج تركيب بلاط أو سيراميك جديد في الرياض. أود ترتيب معاينة وتحديد التجهيز المطلوب.',
    },
    repair: {
      reply: 'في حالات التطبيل أو الكسر نحتاج صورة قريبة وصورة للمساحة كاملة، مع توضيح وجود رطوبة أو تسرب. بعدها يتحدد إن كان الإصلاح موضعيًا أو يحتاج نطاقًا أوسع.',
      message: 'مرحبًا المبلط عادل، لدي بلاط متطبل أو مكسور وأحتاج فحصه وإصلاحه في الرياض.',
    },
    waterproofing: {
      reply: 'للعزل نحتاج معرفة نوع المساحة وموقع المصرف وحالة الأرضية وهل يوجد تسرب حالي. يفضّل إرسال صور أو فيديو قصير قبل تحديد موعد المعاينة.',
      message: 'مرحبًا المبلط عادل، أحتاج عزل أرضية أو حمام ومعالجة قبل تركيب البلاط في الرياض.',
    },
    estimate: {
      reply: 'التقدير الأدق يعتمد على نوع الخدمة والمساحة وحالة السطح والقصّات والحي. أرسل هذه البيانات مع الصور، وسيتم توضيح نطاق العمل قبل الاتفاق.',
      message: 'مرحبًا المبلط عادل، أحتاج تقدير تكلفة لخدمة بلاط في الرياض وسأرسل المساحة والصور والحي.',
    },
  };

  if (!document.querySelector('[data-assistant]')) {
    document.body.insertAdjacentHTML('beforeend', `
      <div class="smart-assistant" data-assistant>
        <section class="assistant-panel" id="adel-assistant-panel" role="dialog" aria-label="مساعد المبلط عادل" aria-hidden="true">
          <header class="assistant-header">
            <span class="assistant-avatar" aria-hidden="true">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="7" width="14" height="12" rx="4"/><path d="M9 7V5a3 3 0 0 1 6 0v2M9 12h.01M15 12h.01M9 16h6"/></svg>
            </span>
            <span class="assistant-identity">
              <strong>مساعد المبلط عادل</strong>
              <span class="assistant-status">جاهز لمساعدتك</span>
            </span>
            <button class="assistant-close" type="button" data-assistant-close aria-label="إغلاق المساعد">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
            </button>
          </header>
          <div class="assistant-body">
            <p class="assistant-greeting">أهلًا بك. اختر احتياجك وسأوضح لك المعلومات المطلوبة قبل التواصل.</p>
            <div class="assistant-options" aria-label="اختر نوع المساعدة">
              <button class="assistant-option" type="button" data-assistant-option="installation">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>
                <span>أحتاج تركيب بلاط جديد</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="repair">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14.7 6.3 3-3a4 4 0 0 1-5 5l-7.4 7.4a2 2 0 1 1-2.8-2.8L9.9 5.5a4 4 0 0 1 4.8-5.2"/></svg>
                <span>عندي تطبيل أو كسر</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="waterproofing">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3s6 6.2 6 11a6 6 0 0 1-12 0c0-4.8 6-11 6-11z"/><path d="M9 15a3 3 0 0 0 3 3"/></svg>
                <span>أحتاج عزل حمام أو أرضية</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="estimate">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 3h10v18H7zM9.5 7h5M9.5 11h1M13.5 11h1M9.5 15h1M13.5 15h1"/></svg>
                <span>أريد تقدير التكلفة</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
            </div>
            <div class="assistant-response" data-assistant-response hidden>
              <p data-assistant-reply></p>
              <div class="assistant-response-actions">
                <a class="assistant-whatsapp" data-assistant-whatsapp href="https://wa.me/966567372527" target="_blank" rel="noopener">
                  <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.5 9.5 0 0 1-4-1l-5 1 1.2-4.5A8.5 8.5 0 1 1 21 11.5z"/><path d="M9 8c.5 3 2 4.5 5 5"/></svg>
                  إكمال الطلب على واتساب
                </a>
                <a class="assistant-call" href="tel:0567372527">اتصال</a>
              </div>
            </div>
            <small class="assistant-privacy">لا تُرسل أي بيانات حتى تضغط على واتساب.</small>
          </div>
        </section>
        <span class="assistant-label" aria-hidden="true">المساعد الذكي</span>
        <button class="assistant-toggle" type="button" aria-label="فتح مساعد المبلط عادل" aria-controls="adel-assistant-panel" aria-expanded="false" data-assistant-toggle>
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="7" width="14" height="12" rx="4"/><path d="M9 7V5a3 3 0 0 1 6 0v2M9 12h.01M15 12h.01M9 16h6"/></svg>
          <span class="assistant-pulse" aria-hidden="true"></span>
        </button>
      </div>
    `);

    const assistant = document.querySelector('[data-assistant]');
    const assistantPanel = assistant?.querySelector('.assistant-panel');
    const assistantToggle = assistant?.querySelector('[data-assistant-toggle]');
    const assistantClose = assistant?.querySelector('[data-assistant-close]');
    const assistantOptions = assistant?.querySelectorAll('[data-assistant-option]') || [];
    const assistantResponse = assistant?.querySelector('[data-assistant-response]');
    const assistantReply = assistant?.querySelector('[data-assistant-reply]');
    const assistantWhatsapp = assistant?.querySelector('[data-assistant-whatsapp]');

    const setAssistantState = (open, restoreFocus = false) => {
      if (!assistant || !assistantPanel || !assistantToggle) return;
      assistant.classList.toggle('is-open', open);
      assistantToggle.setAttribute('aria-expanded', String(open));
      assistantToggle.setAttribute('aria-label', open ? 'إغلاق مساعد المبلط عادل' : 'فتح مساعد المبلط عادل');
      assistantPanel.setAttribute('aria-hidden', String(!open));
      if (open) {
        const firstOption = assistant.querySelector('[data-assistant-option]');
        window.setTimeout(() => firstOption?.focus(), 80);
      } else if (restoreFocus) {
        assistantToggle.focus();
      }
    };

    assistantToggle?.addEventListener('click', () => {
      setAssistantState(!assistant.classList.contains('is-open'));
    });
    assistantClose?.addEventListener('click', () => setAssistantState(false, true));

    assistantOptions.forEach((option) => {
      option.addEventListener('click', () => {
        const choice = assistantChoices[option.dataset.assistantOption];
        if (!choice || !assistantResponse || !assistantReply || !assistantWhatsapp) return;
        assistantOptions.forEach((item) => item.classList.remove('is-selected'));
        option.classList.add('is-selected');
        assistantReply.textContent = choice.reply;
        const pageTitle = document.querySelector('h1')?.textContent?.trim() || document.title;
        const message = `${choice.message}\nالصفحة الحالية: ${pageTitle}\nالرابط: ${window.location.href}`;
        assistantWhatsapp.href = `https://wa.me/966567372527?text=${encodeURIComponent(message)}`;
        assistantResponse.hidden = false;
      });
    });

    document.addEventListener('click', (event) => {
      if (assistant?.classList.contains('is-open') && !assistant.contains(event.target)) {
        setAssistantState(false);
      }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && assistant?.classList.contains('is-open')) {
        setAssistantState(false, true);
      }
    });
  }
})();
