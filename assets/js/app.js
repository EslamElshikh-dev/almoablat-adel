(() => {
  'use strict';

  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const themeButton = document.querySelector('[data-theme-toggle]');

  const promoText = 'عرض العودة إلى المدارس: خصم 25٪ على خدمات تأسيس وتشطيب وإصلاح بلاط وسيراميك الأرضيات والجدران';
  const promoWhatsapp = `https://wa.me/966567372527?text=${encodeURIComponent('مرحبًا المبلط عادل، أرغب في الاستفادة من عرض العودة إلى المدارس بخصم 25٪ على خدمات البلاط والسيراميك.')}`;
  if (header && !header.querySelector('[data-promo-bar]')) {
    const promoContent = `
      <svg class="promo-spark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/></svg>
      <span>عرض العودة إلى المدارس: <strong>خصم 25٪</strong> على خدمات تأسيس وتشطيب وإصلاح بلاط وسيراميك الأرضيات والجدران</span>
    `;
    header.insertAdjacentHTML('afterbegin', `
      <aside class="promo-bar" data-promo-bar aria-label="${promoText}">
        <div class="promo-viewport">
          <div class="promo-track">
            <a class="promo-item" href="${promoWhatsapp}" target="_blank" rel="noopener" aria-label="${promoText}. اضغط لطلب العرض عبر واتساب">${promoContent}</a>
            <a class="promo-item" href="${promoWhatsapp}" target="_blank" rel="noopener" aria-hidden="true" tabindex="-1">${promoContent}</a>
          </div>
        </div>
      </aside>
    `);
  }

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
    tileOverTile: {
      reply: 'يمكن تركيب بلاط فوق بلاط عندما يكون السطح القديم ثابتًا وخاليًا من التطبيل والرطوبة، وتسمح مناسيب الأبواب والمصارف بالارتفاع الجديد. المعاينة تحدد صلاحية الحل قبل التنفيذ.',
      message: 'مرحبًا المبلط عادل، أحتاج فحص إمكانية تركيب بلاط فوق البلاط الحالي في الرياض.',
    },
    duration: {
      reply: 'تتحدد المدة حسب المساحة ومقاس البلاط وحالة السطح وعدد القصّات وزمن جفاف المواد. بعد الصور أو المعاينة يمكن وضع مدة تقريبية وجدول تنفيذ أوضح.',
      message: 'مرحبًا المبلط عادل، أريد معرفة المدة المتوقعة لتنفيذ أعمال البلاط في موقعي بالرياض.',
    },
    areas: {
      reply: 'نخدم أحياء مدينة الرياض، ويُنسق موعد المعاينة حسب موقع المشروع وحجم العمل وتوفر الفريق. أرسل اسم الحي وموقعًا تقريبيًا لتأكيد الموعد المناسب.',
      message: 'مرحبًا المبلط عادل، أريد التأكد من توفر الخدمة في الحي الذي أسكن فيه بمدينة الرياض.',
    },
    materials: {
      reply: 'يمكن الاتفاق على توفير مواد التثبيت والترويب والعزل ضمن نطاق العمل، أو تنفيذ التركيب بمواد يوفّرها العميل بعد مراجعة المواصفات والكميات قبل البدء.',
      message: 'مرحبًا المبلط عادل، أحتاج توضيح خيارات توفير مواد تركيب وتشطيب البلاط لمشروعي في الرياض.',
    },
    bathroomSlope: {
      reply: 'تُراجع مناسيب العتبة والمصرف وحالة القاعدة أولًا، ثم تُنفذ الميول باتجاه الصرف وتُختبر بالماء بعد اكتمال زمن المواد. مقاس البلاط وموقع المصرف يؤثران في توزيع القصّات.',
      message: 'مرحبًا المبلط عادل، أحتاج فحص وتنفيذ ميول بلاط حمام أو منطقة رطبة في الرياض.',
    },
  };

  if (!document.querySelector('[data-assistant]')) {
    document.body.insertAdjacentHTML('beforeend', `
      <div class="smart-assistant" data-assistant>
        <section class="assistant-panel" id="adel-assistant-panel" role="dialog" aria-label="مساعد المبلط عادل" aria-hidden="true">
          <header class="assistant-header">
            <span class="assistant-avatar" aria-hidden="true">
              <img src="/assets/images/assistant-contractor-3d.webp" width="44" height="44" alt="">
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
            <div class="assistant-conversation" data-assistant-scroll>
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
              <button class="assistant-option" type="button" data-assistant-option="tileOverTile">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16M8 3v6m8 0v6m-8 0v6"/></svg>
                <span>هل يمكن تركيب بلاط فوق بلاط؟</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="duration">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
                <span>كم تستغرق أعمال التركيب؟</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="areas">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/></svg>
                <span>هل تخدمون جميع أحياء الرياض؟</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="materials">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 8 4-8 4-8-4zM4 12l8 4 8-4M4 17l8 4 8-4"/></svg>
                <span>هل توفرون مواد التركيب والتشطيب؟</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              <button class="assistant-option" type="button" data-assistant-option="bathroomSlope">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h14M6 13l4 2 4-5 4 2"/><path d="M18 6v6h-6"/></svg>
                <span>كيف تُضبط ميول بلاط الحمام؟</span>
                <svg class="assistant-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>
              </button>
              </div>
              <div class="assistant-response" data-assistant-response aria-live="polite" tabindex="-1" hidden>
                <p data-assistant-reply></p>
                <div class="assistant-response-actions">
                  <a class="assistant-whatsapp" data-assistant-whatsapp href="https://wa.me/966567372527" target="_blank" rel="noopener">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.5 9.5 0 0 1-4-1l-5 1 1.2-4.5A8.5 8.5 0 1 1 21 11.5z"/><path d="M9 8c.5 3 2 4.5 5 5"/></svg>
                    إكمال الطلب على واتساب
                  </a>
                  <a class="assistant-call" href="tel:0567372527">اتصال</a>
                </div>
              </div>
            </div>
            <small class="assistant-privacy">لا تُرسل أي بيانات حتى تضغط على واتساب.</small>
          </div>
        </section>
        <span class="assistant-label" aria-hidden="true">المساعد الذكي</span>
        <button class="assistant-toggle" type="button" aria-label="فتح مساعد المبلط عادل" aria-controls="adel-assistant-panel" aria-expanded="false" data-assistant-toggle>
          <span class="assistant-toggle-portrait" aria-hidden="true"><img src="/assets/images/assistant-contractor-3d.webp" width="58" height="58" alt=""></span>
          <span class="assistant-pulse" aria-hidden="true"></span>
        </button>
      </div>
    `);

    const assistant = document.querySelector('[data-assistant]');
    const assistantPanel = assistant?.querySelector('.assistant-panel');
    const assistantToggle = assistant?.querySelector('[data-assistant-toggle]');
    const assistantClose = assistant?.querySelector('[data-assistant-close]');
    const assistantOptions = assistant?.querySelectorAll('[data-assistant-option]') || [];
    const assistantConversation = assistant?.querySelector('[data-assistant-scroll]');
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
        assistantConversation?.scrollTo({ top: 0 });
        window.setTimeout(() => firstOption?.focus({ preventScroll: true }), 80);
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
        window.requestAnimationFrame(() => {
          assistantConversation?.scrollTo({
            top: assistantConversation.scrollHeight,
            behavior: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
          });
        });
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

  const featuredCarousel = document.querySelector('[data-featured-carousel]');
  if (featuredCarousel) {
    const track = featuredCarousel.querySelector('[data-featured-track]');
    const cards = Array.from(track?.querySelectorAll('.featured-article-card') || []);
    const previous = featuredCarousel.closest('.container')?.querySelector('[data-featured-prev]');
    const next = featuredCarousel.closest('.container')?.querySelector('[data-featured-next]');
    const dots = Array.from(featuredCarousel.querySelectorAll('[data-featured-dot]'));
    const status = featuredCarousel.querySelector('[data-featured-status]');
    const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    let currentIndex = 0;
    let autoplayTimer = 0;
    let scrollTimer = 0;
    let touchResumeTimer = 0;
    const pauses = new Set();

    const updateState = (index, announce = false) => {
      currentIndex = Math.max(0, Math.min(cards.length - 1, index));
      dots.forEach((dot, dotIndex) => {
        if (dotIndex === currentIndex) dot.setAttribute('aria-current', 'true');
        else dot.removeAttribute('aria-current');
      });
      if (status && announce) status.textContent = `المقال ${currentIndex + 1} من ${cards.length}`;
    };

    const scheduleAutoplay = () => {
      window.clearTimeout(autoplayTimer);
      if (reducedMotion || pauses.size || document.hidden || cards.length < 2) return;
      autoplayTimer = window.setTimeout(() => {
        goTo((currentIndex + 1) % cards.length);
      }, 5200);
    };

    const goTo = (index, announce = false) => {
      if (!track || !cards.length) return;
      const normalized = (index + cards.length) % cards.length;
      const target = cards[normalized];
      const trackRect = track.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();
      track.scrollBy({
        left: targetRect.right - trackRect.right,
        behavior: reducedMotion ? 'auto' : 'smooth',
      });
      updateState(normalized, announce);
      scheduleAutoplay();
    };

    const detectCurrentCard = () => {
      if (!track || !cards.length) return;
      const trackRect = track.getBoundingClientRect();
      const closest = cards.reduce((best, card, index) => {
        const distance = Math.abs(card.getBoundingClientRect().right - trackRect.right);
        return distance < best.distance ? { index, distance } : best;
      }, { index: 0, distance: Number.POSITIVE_INFINITY });
      updateState(closest.index);
      scheduleAutoplay();
    };

    previous?.addEventListener('click', () => goTo(currentIndex - 1, true));
    next?.addEventListener('click', () => goTo(currentIndex + 1, true));
    dots.forEach((dot, index) => dot.addEventListener('click', () => goTo(index, true)));

    track?.addEventListener('scroll', () => {
      window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(detectCurrentCard, 120);
    }, { passive: true });

    featuredCarousel.addEventListener('pointerenter', () => {
      pauses.add('pointer');
      window.clearTimeout(autoplayTimer);
    });
    featuredCarousel.addEventListener('pointerleave', () => {
      pauses.delete('pointer');
      scheduleAutoplay();
    });
    featuredCarousel.addEventListener('focusin', () => {
      pauses.add('focus');
      window.clearTimeout(autoplayTimer);
    });
    featuredCarousel.addEventListener('focusout', (event) => {
      if (!featuredCarousel.contains(event.relatedTarget)) {
        pauses.delete('focus');
        scheduleAutoplay();
      }
    });
    track?.addEventListener('touchstart', () => {
      pauses.add('touch');
      window.clearTimeout(autoplayTimer);
      window.clearTimeout(touchResumeTimer);
    }, { passive: true });
    track?.addEventListener('touchend', () => {
      touchResumeTimer = window.setTimeout(() => {
        pauses.delete('touch');
        scheduleAutoplay();
      }, 4500);
    }, { passive: true });
    document.addEventListener('visibilitychange', scheduleAutoplay);

    updateState(0);
    scheduleAutoplay();
  }
})();
// Keep the blog label consistent on legacy cached markup without rewriting
// verification metadata in the homepage document.
document.querySelectorAll('a[href$="blog/"]').forEach((link) => {
  const compactLabel = link.querySelector('span:last-child');
  if (compactLabel && compactLabel.textContent.trim() === 'الدليل') {
    compactLabel.textContent = 'المدونة';
    return;
  }
  if (!link.children.length && link.textContent.trim() === 'دليل البلاط') {
    link.textContent = 'المدونة';
  }
});
