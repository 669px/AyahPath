;(function () {
    'use strict';

    const ICONS = {
        lying: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
        patience: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M12 6v6l4 2"/></svg>`,
        anger: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>`,
        charity: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>`,
        forgiveness: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>`,
        gratitude: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`,
        trust: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
        jealousy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
        stress: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M16 16s-1.5-2-4-2-4 2-4 2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>`,
        arrogance: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>`,
    };

    let currentScenarioData = null;
    let audioPlayer = null;
    let isPlaying = false;
    let dailyAudioUrl = null;
    let lastPrayerRenderToken = 0;
    const prayerPending = new Set();
    const THEMES = {
        dark: {
            label: 'Midnight',
            color: '#2CA4AB',
            description: 'A calm night palette with teal highlights and soft contrast.'
        },
        light: {
            label: 'Light',
            color: '#F7F8FA',
            description: 'A bright reading mode for longer study and reflection.'
        },
        arabic: {
            label: 'Arabic Majlis',
            color: '#8A623E',
            description: 'Warm parchment tones and classical Arabic-inspired typography.'
        },
        quranic: {
            label: 'Quranic Emerald',
            color: '#1F6F5F',
            description: 'Deep emerald, gold accents, and a manuscript-inspired atmosphere.'
        },
        ramadan: {
            label: 'Ramadan Lantern',
            color: '#43316B',
            description: 'A lantern-lit indigo palette with moonlit gold highlights.'
        }
    };

    const $ = (s) => document.querySelector(s);
    const $$ = (s) => document.querySelectorAll(s);

    document.addEventListener('DOMContentLoaded', () => {
        audioPlayer = $('#audio-player');
        initTheme();
        initAccessibilityAppearance();
        initLanguage();
        initTypography();
        initNav();
        initScroll();
        initAudio();
        initReflection();
        initGoals();
        initSettings();
        initNotifications();
        initPrayerTracker();
        loadScenarios();
        loadDailyAyah();
        loadStreak();
        loadHistory();
    });

    function initTheme() {
        const saved = localStorage.getItem('ayahpath-theme') || 'dark';
        const themeNames = Object.keys(THEMES);
        const toggle = $('#theme-toggle');
        const select = $('#settings-theme-select');

        const applyTheme = (themeName) => {
            const nextTheme = THEMES[themeName] ? themeName : 'dark';
            document.documentElement.setAttribute('data-theme', nextTheme);
            document.documentElement.style.colorScheme = nextTheme === 'light' ? 'light' : 'dark';
            localStorage.setItem('ayahpath-theme', nextTheme);
            if (select) {
                select.value = nextTheme;
            }
            const meta = document.querySelector('meta[name="theme-color"]');
            if (meta) {
                meta.setAttribute('content', THEMES[nextTheme].color);
            }
            const desc = $('#theme-description');
            if (desc) {
                desc.textContent = THEMES[nextTheme].description;
            }
            if (toggle) {
                toggle.setAttribute('aria-label', `Change theme from ${THEMES[nextTheme].label}`);
                toggle.title = THEMES[nextTheme].label;
            }
        };

        applyTheme(saved);

        if (toggle) {
            toggle.addEventListener('click', () => {
                const cur = document.documentElement.getAttribute('data-theme') || 'dark';
                const next = themeNames[(themeNames.indexOf(cur) + 1) % themeNames.length];
                applyTheme(next);
            });
        }

        if (select) {
            select.addEventListener('change', (e) => applyTheme(e.target.value));
        }
    }

    function initLanguage() {
        const toggle = $('#settings-lang-toggle');
        if (!toggle) return;
        const saved = localStorage.getItem('ayahpath-lang') || '131';
        toggle.value = saved;
        document.body.setAttribute('data-lang', saved);

        toggle.addEventListener('change', (e) => {
            const val = e.target.value;
            localStorage.setItem('ayahpath-lang', val);
            document.body.setAttribute('data-lang', val);
            loadDailyAyah();
            if ($('#page-simulation').classList.contains('active') && currentScenarioData) {
                openScenario(currentScenarioData);
            }
        });
    }

    function initAccessibilityAppearance() {
        const gradientToggle = $('#settings-disable-gradient');
        const cbSelect = $('#settings-colorblind-select');
        const root = document.documentElement;
        const gradSaved = localStorage.getItem('ayahpath-disable-gradient') === '1';
        const cbSaved = localStorage.getItem('ayahpath-colorblind') || 'none';

        const apply = () => {
            const disableGradient = gradientToggle ? gradientToggle.checked : gradSaved;
            const cbMode = cbSelect ? cbSelect.value : cbSaved;
            root.setAttribute('data-no-gradient', disableGradient ? 'true' : 'false');
            root.setAttribute('data-colorblind', cbMode);
            localStorage.setItem('ayahpath-disable-gradient', disableGradient ? '1' : '0');
            localStorage.setItem('ayahpath-colorblind', cbMode);
        };

        if (gradientToggle) gradientToggle.checked = gradSaved;
        if (cbSelect) cbSelect.value = cbSaved;
        apply();

        if (gradientToggle) gradientToggle.addEventListener('change', apply);
        if (cbSelect) cbSelect.addEventListener('change', apply);
    }

    function initSettings() {
        $('#clear-history-btn').addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all reflection history?')) return;
            try {
                await fetch('/api/history', {method: 'DELETE'});
                toast('History cleared');
                loadHistory();
            } catch (e) {
                toast('Clear failed');
            }
        });

        $('#clear-streak-btn').addEventListener('click', async () => {
            if (!confirm('Are you sure you want to wipe all streak and activity data?')) return;
            try {
                await fetch('/api/streak/anonymous_user', {method: 'DELETE'});
                await fetch('/api/goals', {method: 'DELETE'});
                localStorage.removeItem('ayahpath-streak');
                localStorage.removeItem('ayahpath-goals');
                localStorage.removeItem('ayahpath-activity');
                toast('Data cleared');
                loadStreak();
                loadGoals();
                loadActivity();
            } catch (e) {
                toast('Failed to clear some data');
            }
        });
    }

    function initTypography() {
        const MIN = -5;
        const MAX = 5;
        const STORAGE_KEY = 'ayahpath-font-size-level';
        const decBtn = $('#font-size-decrease');
        const incBtn = $('#font-size-increase');
        const valueEl = $('#settings-font-size-value');

        const normalize = (value) => {
            const parsed = Number.parseInt(value, 10);
            if (!Number.isFinite(parsed)) return 0;
            return Math.max(MIN, Math.min(MAX, parsed));
        };

        let level = normalize(localStorage.getItem(STORAGE_KEY) || '0');

        const apply = () => {
            document.documentElement.style.setProperty('--font-size-level', String(level));
            localStorage.setItem(STORAGE_KEY, String(level));
            if (valueEl) {
                valueEl.textContent = level > 0 ? `+${level}` : `${level}`;
            }
            if (decBtn) decBtn.disabled = level <= MIN;
            if (incBtn) incBtn.disabled = level >= MAX;
        };

        apply();

        if (decBtn) {
            decBtn.addEventListener('click', () => {
                if (level <= MIN) return;
                level -= 1;
                apply();
            });
        }

        if (incBtn) {
            incBtn.addEventListener('click', () => {
                if (level >= MAX) return;
                level += 1;
                apply();
            });
        }
    }

    function initNotifications() {
        const notifs = JSON.parse(localStorage.getItem('ayahpath-notifs') || '[]');
        if (notifs.length === 0) {
            notifs.push({
                id: Date.now().toString(),
                title: 'Welcome to AyahPath ✨',
                desc: "Your journey to Qur'anic wisdom begins here.",
                time: Date.now(),
                read: false
            });
            localStorage.setItem('ayahpath-notifs', JSON.stringify(notifs));
        }
        renderNotifications();
    }

    function renderNotifications() {
        const list = $('#notif-list');
        const empty = $('#notif-empty');
        const badge = $('#notif-badge');
        let notifs = JSON.parse(localStorage.getItem('ayahpath-notifs') || '[]');
        
        const unreadCount = notifs.filter(n => !n.read).length;
        if (unreadCount > 0) {
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }

        if (notifs.length === 0) {
            list.innerHTML = '';
            empty.style.display = 'block';
            return;
        }

        empty.style.display = 'none';
        list.innerHTML = '';
        notifs.sort((a,b) => b.time - a.time).forEach((n, i) => {
            const div = document.createElement('div');
            div.className = 'h-item';
            div.innerHTML = `
                <div class="h-item-body">
                    <span class="h-type ${n.read ? 'general' : 'scenario'}">${n.read ? 'Read' : 'New'}</span>
                    <h4>${esc(n.title)}</h4>
                    <p class="h-summary">${esc(n.desc)}</p>
                    <span class="h-time">${timeAgo(n.time)}</span>
                </div>
                <button class="h-del" data-id="${n.id}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M8 6V4h8v2"/></svg>
                </button>
            `;
            
            div.addEventListener('click', () => {
                if (!n.read) {
                    n.read = true;
                    localStorage.setItem('ayahpath-notifs', JSON.stringify(notifs));
                    renderNotifications();
                }
            });

            div.querySelector('.h-del').addEventListener('click', (e) => {
                e.stopPropagation();
                notifs = notifs.filter(x => x.id !== n.id);
                localStorage.setItem('ayahpath-notifs', JSON.stringify(notifs));
                renderNotifications();
            });
            list.appendChild(div);
        });
    }

    function initNav() {
        $$('.nav-item, .btm-item').forEach(btn => btn.addEventListener('click', () => go(btn.dataset.page)));
        $('#logo-home').addEventListener('click', (e) => { e.preventDefault(); go('home'); });
        $('#back-to-home').addEventListener('click', () => go('home'));

        const streakBtns = [$('#nav-streak-desktop'), $('#nav-streak')].filter(Boolean);
        streakBtns.forEach((btn) => {
            btn.addEventListener('click', (e) => streakClickFx(btn, e));
        });
    }

    function streakClickFx(btn, e) {
        try {
            const rect = btn.getBoundingClientRect();
            const cx = (e && typeof e.clientX === 'number') ? e.clientX : (rect.left + rect.width / 2);
            const cy = (e && typeof e.clientY === 'number') ? e.clientY : (rect.top + rect.height / 2);
            const x = cx - rect.left;
            const y = cy - rect.top;

            btn.classList.remove('streak-pop');
            void btn.offsetWidth;
            btn.classList.add('streak-pop');
            setTimeout(() => btn.classList.remove('streak-pop'), 260);

            const ripple = document.createElement('span');
            ripple.className = 'click-ripple';
            const size = Math.max(rect.width, rect.height) * 1.2;
            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 650);

            const count = 7;
            for (let i = 0; i < count; i++) {
                const dot = document.createElement('span');
                dot.className = 'streak-burst-dot';
                dot.style.left = `${x}px`;
                dot.style.top = `${y}px`;
                const ang = (Math.PI * 2 * i) / count;
                const r = 18 + Math.random() * 16;
                dot.style.setProperty('--dx', `${Math.cos(ang) * r}px`);
                dot.style.setProperty('--dy', `${Math.sin(ang) * r}px`);
                btn.appendChild(dot);
                setTimeout(() => dot.remove(), 750);
            }
        } catch (_) {
        }
    }

    function checkinBurstFx(btn) {
        try {
            const rect = btn.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;
            const styles = getComputedStyle(document.documentElement);
            const accent = styles.getPropertyValue('--emerald').trim() || '#2CA4AB';
            const colors = [
                accent,
                styles.getPropertyValue('--sky').trim() || '#38bdf8',
                styles.getPropertyValue('--amber').trim() || '#fbbf24',
                styles.getPropertyValue('--violet').trim() || '#a78bfa',
                styles.getPropertyValue('--rose').trim() || '#fb7185',
                '#4ade80'
            ];
            const container = document.createElement('div');
            container.style.cssText = 'position:fixed;inset:0;z-index:9999;pointer-events:none;overflow:hidden;';
            document.body.appendChild(container);

            const ring = document.createElement('div');
            ring.style.cssText = `
                position:absolute;left:${cx}px;top:${cy}px;
                width:0;height:0;border-radius:50%;
                border:2px solid ${accent};
                transform:translate(-50%,-50%);
                animation:checkinRing 0.7s ease-out forwards;
            `;
            container.appendChild(ring);

            const count = 18;
            for (let i = 0; i < count; i++) {
                const p = document.createElement('div');
                const angle = (Math.PI * 2 * i) / count;
                const dist = 60 + Math.random() * 80;
                const dx = Math.cos(angle) * dist;
                const dy = Math.sin(angle) * dist;
                const size = 4 + Math.random() * 5;
                const color = colors[Math.floor(Math.random() * colors.length)];
                const delay = Math.random() * 0.1;

                p.style.cssText = `
                    position:absolute;left:${cx}px;top:${cy}px;
                    width:${size}px;height:${size}px;
                    border-radius:50%;background:${color};
                    transform:translate(-50%,-50%) scale(1);
                    opacity:1;
                    animation:checkinParticle 0.7s ${delay}s ease-out forwards;
                    --dx:${dx}px;--dy:${dy}px;
                `;
                container.appendChild(p);
            }

            const check = document.createElement('div');
            check.style.cssText = `
                position:absolute;left:${cx}px;top:${cy}px;
                transform:translate(-50%,-50%) scale(0);
                font-size:2.5rem;opacity:0;
                animation:checkinCheck 0.8s 0.15s cubic-bezier(0.34,1.56,0.64,1) forwards;
            `;
            check.textContent = '✓';
            container.appendChild(check);

            setTimeout(() => container.remove(), 1200);
        } catch (_) {}
    }

    if (!document.getElementById('checkin-fx-styles')) {
        const style = document.createElement('style');
        style.id = 'checkin-fx-styles';
        style.textContent = `
            @keyframes checkinRing {
                0%   { width:0; height:0; opacity:1; }
                100% { width:200px; height:200px; opacity:0; border-width:1px; }
            }
            @keyframes checkinParticle {
                0%   { transform:translate(-50%,-50%) scale(1); opacity:1; }
                100% { transform:translate(calc(-50% + var(--dx)), calc(-50% + var(--dy))) scale(0.3); opacity:0; }
            }
            @keyframes checkinCheck {
                0%   { transform:translate(-50%,-50%) scale(0); opacity:0; }
                50%  { transform:translate(-50%,-50%) scale(1.3); opacity:1; }
                100% { transform:translate(-50%,-50%) scale(1); opacity:0; }
            }
        `;
        document.head.appendChild(style);
    }

    function go(page) {
        $$('.page').forEach(p => p.classList.remove('active'));
        $$('.nav-item, .btm-item').forEach(b => b.classList.remove('active'));

        if (page === 'simulation') {
            $('#page-simulation').classList.add('active');
        } else {
            const el = $(`#page-${page}`);
            if (el) el.classList.add('active');
            $$(`.nav-item[data-page="${page}"], .btm-item[data-page="${page}"]`).forEach(b => b.classList.add('active'));
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (page === 'history') loadHistory();
        if (page === 'streak') { loadStreak(); loadGoals(); loadActivity(); }
        if (page === 'prayer') { prayerViewDate = new Date(); renderPrayerPage(); }
        if (page === 'notifications') {
            const notifs = JSON.parse(localStorage.getItem('ayahpath-notifs') || '[]');
            let changed = false;
            notifs.forEach(n => { if (!n.read) { n.read = true; changed = true; } });
            if (changed) {
                localStorage.setItem('ayahpath-notifs', JSON.stringify(notifs));
                renderNotifications();
            }
        }
    }

    function initScroll() {
        const h = $('#header');
        let tick = false;
        window.addEventListener('scroll', () => {
            if (!tick) {
                requestAnimationFrame(() => { h.classList.toggle('scrolled', window.scrollY > 16); tick = false; });
                tick = true;
            }
        });
    }

    async function loadScenarios() {
        try {
            const r = await fetch('/api/scenarios');
            const d = await r.json();
            if (d.success) renderGrid(d.scenarios);
        } catch (e) {
            console.error('Failed to load scenarios:', e);
        }
    }

    function renderGrid(scenarios) {
        const g = $('#scenario-grid');
        g.innerHTML = '';
        scenarios.forEach((sc, i) => {
            const c = document.createElement('div');
            c.className = 'sc-card';
            c.dataset.cat = sc.category;
            c.style.animationDelay = `${i * 50}ms`;
            const icon = ICONS[sc.icon] || ICONS.patience;
            c.innerHTML = `
                <div class="sc-icon">${icon}</div>
                <h3>${esc(sc.title)}</h3>
                <p>${esc(sc.description)}</p>
                <div class="sc-arrow"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14"/><polyline points="12 5 19 12 12 19"/></svg></div>
            `;
            c.addEventListener('click', () => openScenario(sc));
            g.appendChild(c);
        });
    }

    async function openScenario(sc) {
        go('simulation');
        const icon = ICONS[sc.icon] || ICONS.patience;
        $('#sim-icon').innerHTML = icon;
        $('#sim-title').textContent = sc.title;
        $('#sim-desc').textContent = sc.description;

        show('#sim-loading');
        hide('#verse-card');
        hide('#extras-section');
        hide('#insight-section');
        hide('#action-row');

        try {
            const langId = localStorage.getItem('ayahpath-lang') || '131';
            const r = await fetch(`/api/scenarios/${sc.id}?trans=${langId}`);
            const d = await r.json();
            hide('#sim-loading');
            if (d.success) {
                currentScenarioData = d;
                renderSim(d);
            } else {
                toast('Failed to load guidance');
            }
        } catch (e) {
            hide('#sim-loading');
            toast('Connection error');
        }
    }

    function renderSim(d) {
        const a = d.primary_ayah;
        $('#verse-ref').textContent = `${a.surah_name} (${a.surah_name_ar}) — ${a.verse_key}`;
        $('#verse-ar').textContent = a.arabic;
        const targetUr = $('#verse-ur');
        if (targetUr) targetUr.textContent = a.secondary_translation || '';
        $('#verse-en').textContent = `"${a.translation}"`;
        show('#verse-card');

        if (a.audio_url) {
            audioPlayer.src = a.audio_url;
        }

        if (d.additional_ayahs && d.additional_ayahs.length) {
            const list = $('#extras-list');
            list.innerHTML = '';
            d.additional_ayahs.forEach(aa => {
                const div = document.createElement('div');
                div.className = 'mini-verse';
                div.innerHTML = `
                    <div class="mini-ctx">${esc(aa.context || '')}</div>
                    <p class="mini-ar">${aa.arabic}</p>
                    <p class="mini-trans" dir="auto">${esc(aa.secondary_translation || '')}</p>
                    <p class="mini-en">"${esc(aa.translation)}"</p>
                    <span class="mini-ref">${esc(aa.surah_name)} — ${aa.verse_key}</span>
                `;
                list.appendChild(div);
            });
            show('#extras-section');
        }

        if (d.insight && d.insight.success) {
            $('#txt-dunya').textContent = d.insight.dunya_impact;
            $('#txt-akhirah').textContent = d.insight.akhirah_impact;
            $('#txt-better').textContent = d.insight.better_choice;
            show('#insight-section');
        }

        renderVideoEmbeds(d.video_embeds, '#youtube-list', '#youtube-section');

        show('#action-row');
        resetSave($('#save-btn'));
        $('#save-btn').onclick = () => { saveReflection('scenario', d); markSaved($('#save-btn')); };
        $('#share-btn').onclick = () => shareResult(d);
    }

    function renderVideoEmbeds(videos, listId, sectionId) {
        if (videos && videos.length > 0) {
            const container = $(listId);
            container.innerHTML = '';
            videos.forEach(vid => {
                const wrapper = document.createElement('div');
                wrapper.className = 'video-card';
                const searchQuery = encodeURIComponent(vid.query || `${vid.channel || ''} ${vid.title || ''}`.trim());
                const searchUrl = vid.search_url || `https://www.youtube.com/results?search_query=${searchQuery}`;
                const targetUrl = vid.url || searchUrl;
                const thumbUrl = vid.thumbnail_url || '';
                const ctaLabel = vid.link_type === 'video' ? 'Watch on YouTube' : 'Open YouTube results';
                const thumbMarkup = thumbUrl
                    ? `<img class="video-thumb" src="${thumbUrl}" alt="${esc(vid.title)} thumbnail" loading="lazy" onerror="this.remove(); this.parentElement.classList.add('video-thumb-failed');" />`
                    : '';

                wrapper.innerHTML = `
                    <div class="video-responsive">
                        <a class="video-link" href="${targetUrl}" target="_blank" rel="noopener noreferrer" aria-label="${esc(vid.title)} (opens in YouTube)">
                            ${thumbMarkup}
                            <div class="video-thumb-fallback">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>
                                <span>${ctaLabel}</span>
                            </div>
                            <span class="video-play" aria-hidden="true">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><polygon points="9 7 19 12 9 17 9 7"/></svg>
                            </span>
                        </a>
                    </div>
                    <div class="video-info">
                        <h4 class="video-title">${esc(vid.title)}</h4>
                        <div class="video-meta">
                            <span class="video-channel">${esc(vid.channel)}</span>
                            <a href="${targetUrl}" target="_blank" rel="noopener noreferrer" class="video-search-link">${ctaLabel} &rarr;</a>
                        </div>
                    </div>
                `;
                container.appendChild(wrapper);
            });
            show(sectionId);
        } else {
            hide(sectionId);
        }
    }

    function initAudio() {
        const btn = $('#verse-audio-btn');
        const dailyAudioBtn = $('#daily-audio-btn');
        const dailyRefreshBtn = $('#daily-refresh-btn');
        const getReflectAudioBtn = () => $('#reflect-audio-btn');

        function resetAudioUI() {
            btn.classList.remove('playing');
            dailyAudioBtn.classList.remove('playing');
            const reflectAudioBtn = getReflectAudioBtn();
            if (reflectAudioBtn) reflectAudioBtn.classList.remove('playing');
            hide('#audio-track');
        }

        btn.addEventListener('click', () => {
            if (btn.classList.contains('playing')) {
                audioPlayer.pause();
                resetAudioUI();
                isPlaying = false;
            } else {
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
                resetAudioUI();
                
                audioPlayer.src = currentScenarioData?.primary_ayah?.audio_url || audioPlayer.src;
                
                audioPlayer.play().then(() => {
                    btn.classList.add('playing');
                    isPlaying = true;
                    show('#audio-track');
                    fetch('/api/activity', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({type: 'ayah_listened', details: 'Listened to recitation'}),
                    }).catch(() => {});
                }).catch(() => toast('Audio not available'));
            }
        });

        audioPlayer.addEventListener('timeupdate', () => {
            if (audioPlayer.duration) {
                const pct = (audioPlayer.currentTime / audioPlayer.duration) * 100;
                const fill = $('#track-fill');
                if (fill) fill.style.width = `${pct}%`;
            }
        });

        audioPlayer.addEventListener('ended', () => {
            btn.classList.remove('playing');
            dailyAudioBtn.classList.remove('playing');
            const reflectAudioBtn = getReflectAudioBtn();
            if (reflectAudioBtn) reflectAudioBtn.classList.remove('playing');
            isPlaying = false;
            const fill = $('#track-fill');
            if (fill) fill.style.width = '0%';
            setTimeout(() => hide('#audio-track'), 400);
        });

        dailyAudioBtn.addEventListener('click', () => {
            if (!dailyAudioUrl) return;
            if (dailyAudioBtn.classList.contains('playing')) {
                audioPlayer.pause();
                isPlaying = false;
                resetAudioUI();
            } else {
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
                resetAudioUI();

                audioPlayer.src = dailyAudioUrl;
                audioPlayer.play().then(() => {
                    isPlaying = true;
                    dailyAudioBtn.classList.add('playing');
                    show('#audio-track');
                }).catch(() => toast('Audio unavailable'));
            }
        });

        if (dailyRefreshBtn) {
            dailyRefreshBtn.addEventListener('click', async () => {
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
                resetAudioUI();
                await loadDailyAyah(true);
            });
        }
    }

    async function loadDailyAyah(forceRandom = false) {
        try {
            const langId = localStorage.getItem('ayahpath-lang') || '131';
            const lastVerseKey = localStorage.getItem('ayahpath-last-home-ayah') || '';
            const exclude = encodeURIComponent(lastVerseKey);
            let d = null;

            if (!forceRandom) {
                const personalized = await fetch(`/api/personalized-ayah?trans=${encodeURIComponent(langId)}&user_id=anonymous_user&exclude=${exclude}`, {
                    cache: 'no-store'
                });
                d = await personalized.json();
            }

            if (!d || !d.success) {
                const dailyResp = await fetch(`/api/daily-ayah?trans=${encodeURIComponent(langId)}&user_id=anonymous_user&random=1&exclude=${exclude}`, {
                    cache: 'no-store'
                });
                d = await dailyResp.json();
            }
            if (d.success && d.ayah && d.ayah.success) {
                if (d.ayah.verse_key) {
                    localStorage.setItem('ayahpath-last-home-ayah', d.ayah.verse_key);
                }
                const badgeLabel = $('#daily-badge-label');
                const reason = $('#daily-reason');
                if (badgeLabel) badgeLabel.textContent = d.source === 'personalized' ? 'Ayah for Today' : 'Ayah of the Day';
                if (reason) reason.textContent = d.reason || '';
                $('#daily-arabic').textContent = d.ayah.arabic;
                $('#daily-urdu').textContent = d.ayah.secondary_translation || '';
                $('#daily-translation').textContent = `"${d.ayah.translation}"`;
                $('#daily-ref').textContent = `${d.ayah.surah_name} — ${d.ayah.verse_key}`;
                dailyAudioUrl = d.ayah.audio_url;
            }
        } catch (e) {
            const banner = $('#daily-banner');
            if (banner) banner.style.display = 'none';
        }
    }

    function initReflection() {
        const input = $('#reflect-input');
        const ct = $('#char-count');

        input.addEventListener('input', () => {
            ct.textContent = `${input.value.length} / 500`;
        });

        $('#reflect-submit').addEventListener('click', submitReflection);

        input.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') submitReflection();
        });
    }

    async function submitReflection() {
        const input = $('#reflect-input');
        const sit = input.value.trim();
        if (sit.length < 10) {
            toast('Please describe your situation in more detail');
            return;
        }

        const btn = $('#reflect-submit');
        btn.disabled = true;
        show('#reflect-results');
        show('#reflect-loading');
        hide('#reflect-content');

        try {
            const langId = localStorage.getItem('ayahpath-lang') || '131';
            const r = await fetch('/api/reflections', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({situation: sit, trans: langId}),
            });
            const d = await r.json();
            if (d.success) {
                renderReflectionResults(d, sit);
            } else {
                toast(d.error || 'Failed to get guidance');
            }
        } catch (e) {
            toast('Service unavailable. Please check your connection or try again later.');
        } finally {
            btn.disabled = false;
            hide('#reflect-loading');
        }
    }

    function renderReflectionResults(d, situation) {
        const topic = $('#reflect-topic');
        topic.innerHTML = `<span class="topic-tag">${esc(d.matched_scenario)}</span>`;
        if (d.why_this_verse) {
            topic.innerHTML += `<p style="color:var(--tx-3);font-size:.82rem;margin-top:6px">${esc(d.why_this_verse)}</p>`;
        }

        const vc = $('#reflect-verse-card');
        if (d.ayah && d.ayah.success) {
            vc.innerHTML = `
                <div class="verse-top"><span class="verse-badge">Relevant Verse</span><span class="verse-ref">${esc(d.ayah.surah_name)} — ${d.ayah.verse_key}</span></div>
                <p class="verse-ar">${d.ayah.arabic}</p>
                <p class="verse-trans" dir="auto">${esc(d.ayah.secondary_translation || '')}</p>
                <blockquote class="verse-en">"${esc(d.ayah.translation)}"</blockquote>
                <div class="verse-controls">
                    <button class="btn-audio" id="reflect-audio-btn">
                        <svg class="ico-play" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                        <svg class="ico-pause" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="display:none"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>
                        <span>Recitation</span>
                    </button>
                </div>
            `;
            vc.style.display = 'block';

            const reflectAudioBtn = $('#reflect-audio-btn');
            if (reflectAudioBtn) {
                reflectAudioBtn.addEventListener('click', () => {
                    if (reflectAudioBtn.classList.contains('playing')) {
                        audioPlayer.pause();
                        reflectAudioBtn.classList.remove('playing');
                        isPlaying = false;
                        return;
                    }

                    audioPlayer.pause();
                    audioPlayer.currentTime = 0;
                    $('#verse-audio-btn').classList.remove('playing');
                    $('#daily-audio-btn').classList.remove('playing');
                    reflectAudioBtn.classList.remove('playing');

                    const audioUrl = (d.ayah && d.ayah.audio_url) || '';
                    if (!audioUrl) {
                        toast('Audio unavailable');
                        return;
                    }

                    audioPlayer.src = audioUrl;
                    audioPlayer.play().then(() => {
                        reflectAudioBtn.classList.add('playing');
                        isPlaying = true;
                    }).catch(() => toast('Audio unavailable'));
                });
            }
        } else {
            vc.style.display = 'none';
        }

        const ig = $('#reflect-insights');
        ig.innerHTML = '';
        if (d.insight && d.insight.success) {
            ig.innerHTML = `
                <div class="icard icard-dunya">
                    <div class="icard-head">
                        <span class="icon-3d icon-3d-sky" aria-hidden="true">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10A15.3 15.3 0 0112 2z"/></svg>
                        </span>
                        <h4>Dunya Impact</h4>
                    </div>
                    <p>${esc(d.insight.dunya_impact)}</p>
                </div>
                <div class="icard icard-akhirah">
                    <div class="icard-head">
                        <span class="icon-3d icon-3d-violet" aria-hidden="true">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                        </span>
                        <h4>Akhirah Impact</h4>
                    </div>
                    <p>${esc(d.insight.akhirah_impact)}</p>
                </div>
                <div class="icard icard-better">
                    <div class="icard-head">
                        <span class="icon-3d icon-3d-emerald" aria-hidden="true">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                        </span>
                        <h4>The Better Choice</h4>
                    </div>
                    <p>${esc(d.insight.better_choice)}</p>
                </div>
            `;
        }

        renderVideoEmbeds(d.video_embeds, '#reflect-youtube-list', '#reflect-youtube-section');

        const saveBtn = $('#reflect-save-btn');
        resetSave(saveBtn);
        saveBtn.onclick = () => {
            saveReflection('reflection', {
                scenario: {title: d.matched_scenario},
                primary_ayah: d.ayah,
                insight: d.insight,
                userSituation: situation
            });
            markSaved(saveBtn);
        };
        show('#reflect-content');
    }

    async function loadStreak() {
        try {
            const r = await fetch('/api/streak');
            const d = await r.json();
            if (!d.success) return;

            $('#mini-streak-count').textContent = d.current_streak;
            const dots = $('#streak-dots');
            dots.innerHTML = '';
            d.week_activity.forEach(day => {
                const dot = document.createElement('div');
                dot.className = `streak-dot ${day.active ? 'active' : ''}`;
                dots.appendChild(dot);
            });

            $('#streak-number').textContent = d.current_streak;
            $('#streak-sub').textContent = `Longest: ${d.longest_streak} days  •  Total active: ${d.total_days_active} days`;

            const wg = $('#week-grid');
            wg.innerHTML = '';
            d.week_activity.forEach(day => {
                const wd = document.createElement('div');
                wd.className = 'week-day';
                wd.innerHTML = `
                    <div class="week-day-label">${day.day}</div>
                    <div class="week-day-dot ${day.active ? 'active' : ''}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                `;
                wg.appendChild(wd);
            });
        } catch (e) {
            console.error('Failed to load streak:', e);
        }

        const cb = $('#checkin-btn');
        cb.onclick = async () => {
            try {
                cb.disabled = true;
                const r = await fetch('/api/streak/anonymous_user/checkin', {method: 'POST'});
                const d = await r.json();
                if (d.success) {
                    cb.classList.remove('success-pulse');
                    void cb.offsetWidth;
                    cb.classList.add('success-pulse');

                    checkinBurstFx(cb);

                    toast(`Checked in! Streak: ${d.current_streak} days 🔥`);
                    setTimeout(() => {
                        cb.classList.remove('success-pulse');
                        loadStreak();
                    }, 800);
                } else {
                    cb.disabled = false;
                }
            } catch (e) {
                toast('Check-in failed');
                cb.disabled = false;
            }
        };
    }

    function initGoals() {
        const modal = $('#goal-modal');
        const showModal = () => { modal.style.display = 'flex'; };
        const hideModal = () => { modal.style.display = 'none'; };
        $('#add-goal-btn').addEventListener('click', showModal);
        $('#goal-modal-close').addEventListener('click', hideModal);
        modal.addEventListener('click', (e) => { if (e.target === modal) hideModal(); });

        $('#goal-create-btn').addEventListener('click', async () => {
            const title = $('#goal-title-input').value.trim() || 'My Goal';
            const type = $('#goal-type-select').value;
            const target = parseInt($('#goal-target-input').value) || 5;

            try {
                const r = await fetch('/api/goals', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({title, type, target}),
                });
                const d = await r.json();
                if (d.success) {
                    toast('Goal created!');
                    modal.style.display = 'none';
                    $('#goal-title-input').value = '';
                    $('#goal-target-input').value = '5';
                    loadGoals();
                }
            } catch (e) {
                toast('Failed to create goal');
            }
        });
    }

    async function loadGoals() {
        try {
            const r = await fetch('/api/goals');
            const d = await r.json();
            if (!d.success) return;

            const list = $('#goals-list');
            const empty = $('#goals-empty');
            const all = [...d.active_goals, ...d.completed_goals];

            if (all.length === 0) {
                empty.hidden = false;
                list.innerHTML = '';
                return;
            }
            empty.hidden = true;
            list.innerHTML = '';

            all.forEach(g => {
                const pct = g.target > 0 ? Math.min((g.current / g.target) * 100, 100) : 0;
                const circumference = 2 * Math.PI * 16;
                const offset = circumference - (pct / 100) * circumference;
                const color = g.completed ? 'var(--emerald)' : 'var(--sky)';

                const item = document.createElement('div');
                item.className = 'goal-item';
                item.innerHTML = `
                    <svg class="goal-progress-ring" viewBox="0 0 40 40">
                        <circle cx="20" cy="20" r="16" fill="none" stroke="var(--bdr)" stroke-width="3"/>
                        <circle cx="20" cy="20" r="16" fill="none" stroke="${color}" stroke-width="3"
                            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                            transform="rotate(-90 20 20)" stroke-linecap="round"/>
                        <text x="20" y="22" text-anchor="middle" fill="var(--tx-2)" font-size="9" font-weight="600" font-family="var(--f-body)">${Math.round(pct)}%</text>
                    </svg>
                    <div class="goal-info">
                        <div class="goal-title">${esc(g.title)}</div>
                        <div class="goal-meta">${g.current} / ${g.target} • ${esc(g.type)}${g.completed ? ' ✓ Complete' : ''}</div>
                    </div>
                    <button class="goal-delete" data-id="${g.id}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                `;

                item.querySelector('.goal-delete').addEventListener('click', async () => {
                    await fetch(`/api/goals/${g.id}`, {method: 'DELETE'});
                    loadGoals();
                });

                list.appendChild(item);
            });
        } catch (e) {
            console.error('Failed to load goals:', e);
        }
    }

    async function loadActivity() {
        try {
            const r = await fetch('/api/activity');
            const d = await r.json();
            if (!d.success) return;

            const list = $('#activity-list');
            const empty = $('#activity-empty');

            if (d.activities.length === 0) {
                empty.hidden = false;
                list.innerHTML = '';
                return;
            }
            empty.hidden = true;
            list.innerHTML = '';

            const typeMap = {
                scenario_viewed: {cls: 'scenario', label: 'Explored'},
                reflection_submitted: {cls: 'reflection', label: 'Reflected'},
                daily_ayah_viewed: {cls: 'daily', label: 'Daily Ayah'},
                ayah_listened: {cls: 'general', label: 'Listened'},
                manual_checkin: {cls: 'general', label: 'Checked in'},
            };

            d.activities.slice().reverse().slice(0, 15).forEach(a => {
                const info = typeMap[a.type] || {cls: 'general', label: a.type};
                const item = document.createElement('div');
                item.className = 'act-item';
                item.innerHTML = `
                    <div class="act-dot ${info.cls}"></div>
                    <span class="act-text">${esc(info.label)}${a.details ? ': ' + esc(a.details) : ''}</span>
                    <span class="act-time">${timeAgo(a.timestamp)}</span>
                `;
                list.appendChild(item);
            });
        } catch (e) {
            console.error('Failed to load activity:', e);
        }
    }

    async function saveReflection(type, d) {
        try {
            const r = await fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type,
                    title: (d.scenario && d.scenario.title) || 'Reflection',
                    verse_key: (d.primary_ayah && d.primary_ayah.verse_key) || (d.ayah && d.ayah.verse_key) || '',
                    situation: d.userSituation || '',
                    insight_summary: (d.insight && d.insight.better_choice) || '',
                    dunya_impact: (d.insight && d.insight.dunya_impact) || '',
                    akhirah_impact: (d.insight && d.insight.akhirah_impact) || ''
                }),
            });
            const res = await r.json();
            if (res.success) toast('Reflection saved ✓');
        } catch (e) {
            toast('Save failed');
        }
    }

    function markSaved(btn) {
        btn.classList.add('saved');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg> Saved`;
        btn.disabled = true;
    }

    function resetSave(btn) {
        btn.classList.remove('saved');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg> Save`;
        btn.disabled = false;
    }

    async function loadHistory() {
        try {
            const r = await fetch('/api/history?user_id=anonymous_user');
            if (!r.ok) throw new Error('History unavailable');
            const d = await r.json();
            if (d.success) renderHistory(d.reflections);
        } catch (e) {
            console.error('Failed to load history:', e);
        }
    }

    function renderHistory(items) {
        const list = $('#history-list');
        const empty = $('#history-empty');
        if (!items || items.length === 0) {
            empty.style.display = 'block';
            list.innerHTML = '';
            return;
        }
        empty.style.display = 'none';
        list.innerHTML = '';

        items.forEach((item, i) => {
            const div = document.createElement('div');
            div.className = 'h-item';
            div.style.animationDelay = `${i * 40}ms`;
            const summary = (item.guidance && item.guidance.better_choice) || item.insight_summary || '';
            div.innerHTML = `
                <div class="h-item-body">
                    <span class="h-type ${item.assigned_category || 'general'}">${esc(item.assigned_category || 'Reflection')}</span>
                    <h4>${esc(item.scenario || item.title)}</h4>
                    ${(item.reference || item.verse_key) ? `<p class="h-verse">Verse: ${esc(item.reference || item.verse_key)}</p>` : ''}
                    ${summary ? `<p class="h-summary">${esc(truncate(summary, 110))}</p>` : ''}
                    <span class="h-time">${timeAgo(item.timestamp)}</span>
                </div>
                <button class="h-del" data-id="${item.id}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M8 6V4h8v2"/></svg>
                </button>
            `;
            div.querySelector('.h-del').addEventListener('click', async (e) => {
                e.stopPropagation();
                await fetch(`/api/reflections/${item.id}`, {method: 'DELETE'});
                div.style.opacity = '0';
                div.style.transform = 'translateX(16px)';
                div.style.transition = 'all .28s ease';
                setTimeout(() => {
                    div.remove();
                    if (!list.children.length) empty.style.display = 'block';
                }, 280);
            });
            list.appendChild(div);
        });
    }

    function shareResult(d) {
        const title = (d.scenario && d.scenario.title) || 'AyahPath';
        const verseKey = (d.primary_ayah && d.primary_ayah.verse_key) || '';
        const translation = (d.primary_ayah && d.primary_ayah.translation) || '';
        const betterChoice = (d.insight && d.insight.better_choice) || '';
        const text = `📖 AyahPath — ${title}\n\nVerse ${verseKey}:\n"${translation}"\n\n💡 ${betterChoice}\n\n— AyahPath`;

        if (navigator.share) {
            navigator.share({title: `AyahPath — ${title}`, text}).catch(() => {});
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard')).catch(() => {});
        }
    }

    function show(sel) {
        const el = $(sel);
        if (el) {
            el.hidden = false;
            el.style.display = '';
        }
    }

    function hide(sel) {
        const el = $(sel);
        if (el) {
            el.hidden = true;
            el.style.display = 'none';
        }
    }

    function toast(msg) {
        const t = $('#toast');
        const m = $('#toast-msg');
        if (t && m) {
            m.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2600);
        }
    }

    function truncate(s, n) {
        if (!s) return '';
        return s.length > n ? s.substring(0, n) + '…' : s;
    }

    function esc(str) {
        if (!str) return '';
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function timeAgo(ts) {
        if (!ts) return '';
        const s = Math.floor((Date.now() - new Date(ts)) / 1000);
        if (s < 0) return 'Just now';
        if (s < 60) return 'Just now';
        if (s < 3600) return `${Math.floor(s/60)}m ago`;
        if (s < 86400) return `${Math.floor(s/3600)}h ago`;
        if (s < 604800) return `${Math.floor(s/86400)}d ago`;
        return new Date(ts).toLocaleDateString();
    }

    const PRAYERS = [
        { id: 'fajr',    name: 'Fajr Prayer',    defaultTime: '05:30' },
        { id: 'dhuhr',   name: 'Dhuhr Prayer',   defaultTime: '12:30' },
        { id: 'asr',     name: 'Asr Prayer',     defaultTime: '15:45' },
        { id: 'maghrib', name: 'Maghrib Prayer',  defaultTime: '18:30' },
        { id: 'isha',    name: 'Isha Prayer',     defaultTime: '20:00' },
    ];

    let prayerViewDate = new Date();
    let prayerCache = {};
    
    function clonePrayerState(prayers) {
        const next = {};
        PRAYERS.forEach((p) => {
            next[p.id] = !!(prayers && prayers[p.id]);
        });
        return next;
    }

    function prayerDateStr(d) {
        const dt = d || prayerViewDate;
        return `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`;
    }

    function formatDateLabel(d) {
        const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
        const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        return `${days[d.getDay()]} ${d.getDate()} ${months[d.getMonth()]}`;
    }

    function getApproxHijriDate(d) {
        const jd = Math.floor(367 * d.getFullYear() - Math.floor(7 * (d.getFullYear() + Math.floor((d.getMonth() + 9) / 12)) / 4) + Math.floor(275 * (d.getMonth() + 1) / 9) + d.getDate() + 1721013.5);
        const l = jd - 1948440 + 10632;
        const n = Math.floor((l - 1) / 10631);
        const l2 = l - 10631 * n + 354;
        const j = Math.floor((10985 - l2) / 5316) * Math.floor((50 * l2) / 17719) + Math.floor(l2 / 5670) * Math.floor((43 * l2) / 15238);
        const l3 = l2 - Math.floor((30 - j) / 15) * Math.floor((17719 * j) / 50) - Math.floor(j / 16) * Math.floor((15238 * j) / 43) + 29;
        const hMonth = Math.floor((24 * l3) / 709);
        const hDay = l3 - Math.floor((709 * hMonth) / 24);
        const hYear = 30 * n + j - 30;
        const hijriMonths = ["Muharram","Safar","Rabi' al-Awwal","Rabi' al-Thani","Jumada al-Ula","Jumada al-Thani","Rajab","Sha'ban","Ramadan","Shawwal","Dhul Qi'dah","Dhul Hijjah"];
        return `${hDay} ${hijriMonths[(hMonth - 1) % 12] || ''} ${hYear} AH`;
    }

    function isSameDay(d1, d2) {
        return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
    }

    function initPrayerTracker() {
        prayerViewDate = new Date();
        renderPrayerPage();

        $('#prayer-prev-day').addEventListener('click', () => {
            prayerViewDate.setDate(prayerViewDate.getDate() - 1);
            renderPrayerPage();
        });

        $('#prayer-next-day').addEventListener('click', () => {
            prayerViewDate.setDate(prayerViewDate.getDate() + 1);
            renderPrayerPage();
        });
    }

    async function renderPrayerPage() {
        const dateStr = prayerDateStr();
        const renderToken = ++lastPrayerRenderToken;

        $('#prayer-date-label').textContent = formatDateLabel(prayerViewDate);
        $('#prayer-hijri-label').textContent = getApproxHijriDate(prayerViewDate);

        const todayBadge = document.querySelector('.prayer-today-badge');
        if (todayBadge) {
            todayBadge.style.display = isSameDay(prayerViewDate, new Date()) ? 'inline-block' : 'none';
        }

        let prayerData = clonePrayerState(prayerCache[dateStr]);
        try {
            const r = await fetch(`/api/prayers/${dateStr}`);
            const d = await r.json();
            if (d.success) {
                prayerData = clonePrayerState(d.prayers);
                prayerCache[dateStr] = prayerData;
            }
        } catch (e) {
            prayerData = clonePrayerState(prayerCache[dateStr]);
        }

        if (renderToken !== lastPrayerRenderToken) {
            return;
        }

        const list = $('#prayer-list');
        list.innerHTML = '';

        PRAYERS.forEach(p => {
            const checked = !!prayerData[p.id];
            const item = document.createElement('div');
            item.className = `prayer-item${checked ? ' prayer-completed' : ''}`;
            item.innerHTML = `
                <button class="prayer-check-btn${checked ? ' checked' : ''}" data-prayer="${p.id}" aria-label="Mark ${p.name}">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                </button>
                <div class="prayer-info">
                    <span class="prayer-name">${p.name}</span>
                    <span class="prayer-time">${p.defaultTime}</span>
                </div>
            `;

            const btn = item.querySelector('.prayer-check-btn');
            const pendingKey = `${dateStr}:${p.id}`;
            if (prayerPending.has(pendingKey)) {
                btn.disabled = true;
                item.classList.add('prayer-pending');
            }
            btn.addEventListener('click', async () => {
                if (prayerPending.has(pendingKey)) return;

                btn.classList.remove('prayer-pop');
                void btn.offsetWidth;
                btn.classList.add('prayer-pop');
                setTimeout(() => btn.classList.remove('prayer-pop'), 450);

                prayerPending.add(pendingKey);
                const nextState = !checked;
                prayerCache[dateStr] = {
                    ...clonePrayerState(prayerCache[dateStr]),
                    [p.id]: nextState
                };
                renderPrayerPage();

                try {
                    const r = await fetch(`/api/prayers/${dateStr}/${p.id}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({})
                    });
                    const d = await r.json();
                    if (d.success) {
                        prayerCache[dateStr] = clonePrayerState(d.prayers);
                        if (d.stats) {
                            updatePrayerStatsFromData(d.stats);
                        }
                    } else {
                        prayerCache[dateStr] = {
                            ...clonePrayerState(prayerCache[dateStr]),
                            [p.id]: checked
                        };
                        toast('Failed to update prayer');
                    }
                } catch (e) {
                    prayerCache[dateStr] = {
                        ...clonePrayerState(prayerCache[dateStr]),
                        [p.id]: checked
                    };
                    toast('Connection error');
                } finally {
                    prayerPending.delete(pendingKey);
                    renderPrayerPage();
                }
            });

            list.appendChild(item);
        });

        const completedCount = PRAYERS.filter(p => !!prayerData[p.id]).length;
        const pct = (completedCount / PRAYERS.length) * 100;
        const fill = $('#prayer-progress-fill');
        if (fill) fill.style.width = `${pct}%`;
        const label = $('#prayer-progress-label');
        if (label) label.textContent = `${completedCount} / ${PRAYERS.length} completed`;

        fetchPrayerWeekStrip();
        fetchPrayerStats();
    }

    async function fetchPrayerWeekStrip() {
        const strip = $('#prayer-week-strip');
        const dateStr = prayerDateStr();

        try {
            const r = await fetch(`/api/prayers/week?date=${dateStr}`);
            const d = await r.json();
            if (d.success && d.week) {
                renderWeekStripFromData(d.week);
                return;
            }
        } catch (e) {
        }
        strip.innerHTML = '';
        const dayLabels = ['M','T','W','T','F','S','S'];
        dayLabels.forEach(l => {
            const circle = document.createElement('div');
            circle.className = 'prayer-day-circle';
            circle.textContent = l;
            strip.appendChild(circle);
        });
    }

    function renderWeekStripFromData(weekData) {
        const strip = $('#prayer-week-strip');
        strip.innerHTML = '';

        weekData.forEach(day => {
            const circle = document.createElement('div');
            circle.className = 'prayer-day-circle';
            if (day.is_complete) circle.classList.add('completed');
            else if (day.completed_count > 0) circle.classList.add('partial');
            if (day.is_today) circle.classList.add('today');
            circle.textContent = day.day_label;
            circle.title = `${day.date} — ${day.completed_count}/5`;

            circle.style.cursor = 'pointer';
            circle.addEventListener('click', () => {
                prayerViewDate = new Date(day.date + 'T12:00:00');
                renderPrayerPage();
            });

            strip.appendChild(circle);
        });
    }

    async function fetchPrayerStats() {
        try {
            const r = await fetch('/api/prayers/stats');
            const d = await r.json();
            if (d.success) {
                updatePrayerStatsFromData(d);
            }
        } catch (e) {
        }
    }

    function updatePrayerStatsFromData(stats) {
        const streakEl = $('#prayer-streak-count');
        if (streakEl) streakEl.textContent = stats.current_streak || 0;

        const totalEl = $('#prayer-total-prayers');
        if (totalEl) totalEl.textContent = stats.total_prayers || 0;

        const rateEl = $('#prayer-completion-rate');
        if (rateEl) rateEl.textContent = `${stats.week_completion_pct || 0}%`;
    }

})();
