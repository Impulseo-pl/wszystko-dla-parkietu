(() => {
  const nav = document.querySelector('.nav');
  const burger = document.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }
  document.querySelectorAll('.dd > button').forEach(b => {
    b.addEventListener('click', () => {
      const dd = b.parentElement;
      const open = dd.classList.toggle('open');
      b.setAttribute('aria-expanded', open);
    });
  });
  document.addEventListener('click', e => {
    document.querySelectorAll('.dd.open').forEach(dd => {
      if (!dd.contains(e.target) && !nav.classList.contains('open')) {
        dd.classList.remove('open');
        dd.querySelector('button').setAttribute('aria-expanded', false);
      }
    });
  });
  const onScroll = () => nav.classList.toggle('scrolled', scrollY > 10);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* reveal */
  const els = document.querySelectorAll('.head, .card, .ba-fig, .split > *, .gal figure, .review, .tip, .steps li, .faq details, .stat, .factor, .always div, .form, .cta-box, .price');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -6% 0px' });
    els.forEach(el => { el.classList.add('rv'); io.observe(el); });
  }

  /* before / after */
  document.querySelectorAll('.ba').forEach(ba => {
    const r = ba.querySelector('input');
    const set = v => ba.style.setProperty('--pos', v + '%');
    r.addEventListener('input', () => set(r.value));
    set(r.value);
  });

  /* gallery filters */
  const filters = document.querySelector('.filters');
  if (filters) {
    const figs = [...document.querySelectorAll('.gal figure')];
    filters.addEventListener('click', e => {
      const b = e.target.closest('button');
      if (!b) return;
      filters.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
      const f = b.dataset.f;
      figs.forEach(fig => fig.classList.toggle('hide', f !== 'all' && fig.dataset.c !== f));
    });
  }

  /* lightbox */
  const gal = document.querySelectorAll('.gal');
  if (gal.length) {
    const lb = document.createElement('div');
    lb.className = 'lb';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Podgląd zdjęcia');
    const ico = d => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="${d}"/></svg>`;
    lb.innerHTML = `<img alt=""><button class="lb-x" aria-label="Zamknij">${ico('M6 6l12 12M18 6 6 18')}</button><button class="lb-p" aria-label="Poprzednie zdjęcie">${ico('M15 5l-7 7 7 7')}</button><button class="lb-n" aria-label="Następne zdjęcie">${ico('M9 5l7 7-7 7')}</button><div class="lb-count"></div>`;
    document.body.appendChild(lb);
    const img = lb.querySelector('img');
    const count = lb.querySelector('.lb-count');
    let list = [], i = 0, last = null;
    const show = () => {
      const fig = list[i];
      const src = fig.querySelector('img');
      img.src = src.dataset.full || src.src;
      img.alt = src.alt;
      count.textContent = (i + 1) + ' / ' + list.length;
    };
    const open = fig => {
      list = [...fig.parentElement.querySelectorAll('figure:not(.hide)')];
      i = list.indexOf(fig);
      last = document.activeElement;
      show();
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-x').focus();
    };
    const close = () => {
      lb.classList.remove('open');
      document.body.style.overflow = '';
      if (last) last.focus();
    };
    const step = d => { i = (i + d + list.length) % list.length; show(); };
    gal.forEach(g => g.querySelectorAll('figure').forEach(fig => {
      fig.tabIndex = 0;
      fig.setAttribute('role', 'button');
      fig.addEventListener('click', () => open(fig));
      fig.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(fig); } });
    }));
    lb.querySelector('.lb-x').addEventListener('click', close);
    lb.querySelector('.lb-p').addEventListener('click', () => step(-1));
    lb.querySelector('.lb-n').addEventListener('click', () => step(1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
    let x0 = null;
    lb.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
      x0 = null;
    });
  }

  /* form (demo) */
  const form = document.getElementById('form');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const msg = form.querySelector('.form-msg');
      if (!form.imie.value.trim() || !form.tel.value.trim()) {
        msg.textContent = 'Podaj imię i numer telefonu, żebyśmy mogli oddzwonić.';
        return;
      }
      msg.textContent = 'Wersja demo: na gotowej stronie zapytanie trafi prosto na skrzynkę firmy.';
      form.reset();
    });
  }
})();
