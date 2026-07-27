        function escapeHtml(str) {
            if (str == null) return '';
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        }

        function escapeJsString(str) {
            if (str == null) return '';
            // Every call site embeds the result inside a single-quoted JS
            // string literal within a double-quoted HTML onclick="..."
            // attribute. Escaping only backslash/quote protects the JS
            // string boundary but leaves the attribute boundary open (a
            // raw '"' or '<'/'>' would still break out of the attribute),
            // so also HTML-escape after JS-escaping.
            const jsEscaped = String(str)
                .replace(/\\/g, '\\\\')
                .replace(/'/g, "\\'")
                .replace(/\n/g, '\\n')
                .replace(/\r/g, '\\r');
            return escapeHtml(jsEscaped);
        }

        function safeStorageGet(storage, key) {
            try { return storage.getItem(key); } catch (e) { return null; }
        }
        function safeStorageSet(storage, key, value) {
            try { storage.setItem(key, value); } catch (e) { /* ignore */ }
        }
        function safeStorageRemove(storage, key) {
            try { storage.removeItem(key); } catch (e) { /* ignore */ }
        }

        // Reads and validates the user's persisted max-query-limit preference.
        // Re-validates on every call (not just at write time) since a
        // devtools-edited localStorage value bypasses saveSettings() entirely;
        // the server independently clamps this again regardless (defense in depth).
        function getUserQueryLimit() {
            const raw = safeStorageGet(localStorage, 'socrates_maxQueryLimit');
            const n = parseInt(raw, 10);
            if (isNaN(n) || n < 1000 || n > 500000) return CONFIG.DEFAULT_QUERY_LIMIT;
            return n;
        }

        function getUserMaxUploadSizeMB() {
            const raw = safeStorageGet(localStorage, 'socrates_maxUploadSizeMB');
            const n = parseInt(raw, 10);
            if (isNaN(n) || n < 100 || n > 20000) return CONFIG.DEFAULT_UPLOAD_SIZE_MB;
            return n;
        }

        function sortEventTypes(types) {
            const order = { alert: 0, sigmaalert: 1, filealerts: 2, log: 3 };
            return [...types].sort((a, b) => {
                const ai = order[a] ?? 99;
                const bi = order[b] ?? 99;
                if (ai !== bi) return ai - bi;
                return a.localeCompare(b);
            });
        }

        const THEMES = {
            dark: { label: 'Midnight', group: 'dark' },
            light: { label: 'Daylight', group: 'light' },
            sguil: { label: 'Sguil', group: 'fun' },
            hacker: { label: 'Hacker', group: 'fun' },
            cga: { label: 'CGA', group: 'fun' },
            c64: { label: 'C64', group: 'fun' },
            'matte-black': { label: 'Matte Black', group: 'dark' },
            'tokyo-night': { label: 'Tokyo Night', group: 'dark' },
            'retro-82': { label: 'Retro 82', group: 'dark' },
            'ethereal': { label: 'Ethereal', group: 'dark' },
            'lumon': { label: 'Lumon', group: 'dark' },
            'catppuccin': { label: 'Catppuccin', group: 'dark' },
            'catppuccin-latte': { label: 'Catppuccin Latte', group: 'light' },
            'everforest': { label: 'Everforest', group: 'dark' },
            'gruvbox': { label: 'Gruvbox', group: 'dark' },
            'hackerman': { label: 'Hackerman', group: 'dark' },
            'kanagawa': { label: 'Kanagawa', group: 'dark' },
            'miasma': { label: 'Miasma', group: 'dark' },
            'nord': { label: 'Nord', group: 'dark' },
            'osaka-jade': { label: 'Osaka Jade', group: 'dark' },
            'ristretto': { label: 'Ristretto', group: 'dark' },
            'rose-pine': { label: 'Rose Pine', group: 'light' },
            'vantablack': { label: 'Vantablack', group: 'dark' },
            'white': { label: 'White', group: 'light' },
        };

        const THEME_GROUP_LABELS = { dark: 'Dark Themes', fun: 'Fun Themes', light: 'Light Themes' };
        const THEME_GROUP_ORDER = ['dark', 'fun', 'light'];

        // Menu/hotkey cycle order: group by section (Dark, Fun, Light),
        // alphabetical by label within each section.
        const THEME_MENU_ORDER = THEME_GROUP_ORDER.flatMap(group =>
            Object.keys(THEMES)
                .filter(k => THEMES[k].group === group)
                .sort((a, b) => THEMES[a].label.localeCompare(THEMES[b].label))
        );

        function getCurrentTheme() {
            return document.documentElement.getAttribute('data-theme') || 'dark';
        }

        let menuBaseTheme = null;

        function setTheme(themeName) {
            const valid = Object.prototype.hasOwnProperty.call(THEMES, themeName);
            if (!valid) return;
            const html = document.documentElement;
            if (themeName === 'dark') {
                html.removeAttribute('data-theme');
            } else {
                html.setAttribute('data-theme', themeName);
            }
            safeStorageSet(localStorage, 'socrates-theme', themeName);
            updateThemeMenu();
            updateCodeRain();
            updateFavicon();
            // If the menu is open, treat this as the new baseline so a later
            // close/revert does not undo the change.
            const dropdown = document.getElementById('appHeaderMenuDropdown');
            if (dropdown && dropdown.classList.contains('active')) {
                menuBaseTheme = themeName;
            }
        }

        function previewTheme(themeName) {
            const valid = Object.prototype.hasOwnProperty.call(THEMES, themeName);
            if (!valid) return;
            const html = document.documentElement;
            if (themeName === 'dark') {
                html.removeAttribute('data-theme');
            } else {
                html.setAttribute('data-theme', themeName);
            }
            updateCodeRain();
            updateFavicon();
            updateThemeMenu();
        }

        function revertTheme() {
            if (menuBaseTheme !== null) {
                previewTheme(menuBaseTheme);
            }
        }

        function commitTheme(themeName) {
            setTheme(themeName);
            closeMenu();
        }

        function toggleTheme() {
            const order = THEME_MENU_ORDER;
            const current = getCurrentTheme();
            const nextIndex = (order.indexOf(current) + 1) % order.length;
            const nextTheme = order[nextIndex];
            setTheme(nextTheme);
            showToast('Switched to ' + THEMES[nextTheme].label + ' theme');
        }

        function updateThemeMenu() {
            // Mark the menu item for the currently applied theme. Tracks
            // hover previews too (setTheme/previewTheme both call this), so
            // the checkmark always matches what is on screen.
            const current = getCurrentTheme();
            const items = document.querySelectorAll('.app-header-menu-item[data-theme-option]');
            items.forEach(function(item) {
                const isActive = item.getAttribute('data-theme-option') === current;
                item.classList.toggle('theme-active', isActive);
                if (isActive) {
                    item.setAttribute('aria-current', 'true');
                } else {
                    item.removeAttribute('aria-current');
                }
            });
        }

        const GEAR_ICON_SVG = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.17 15a1.65 1.65 0 0 0-1.51-1H2a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.17 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.17a1.65 1.65 0 0 0 1-1.51V2a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;

        function renderGearMenu() {
            let themeSections = '';
            for (const group of THEME_GROUP_ORDER) {
                themeSections += `<div class="app-header-menu-header">${THEME_GROUP_LABELS[group]}</div>`;
                for (const key of THEME_MENU_ORDER.filter(k => THEMES[k].group === group)) {
                    themeSections += `
                        <button class="app-header-menu-item" data-theme-option="${key}"
                                onmouseenter="previewTheme('${key}')"
                                onmouseleave="revertTheme()"
                                onclick="commitTheme('${key}')">
                            <span>${THEMES[key].label}</span>
                        </button>`;
                }
            }
            return `
                <div class="app-header-menu">
                    <button class="app-header-menu-btn" onclick="toggleMenu()" title="Menu" id="appHeaderMenuBtn">
                        ${GEAR_ICON_SVG}
                    </button>
                    <div class="app-header-menu-dropdown" id="appHeaderMenuDropdown">
                        <button class="app-header-menu-item" onclick="showHelpModal(); closeMenu();">
                            <span><svg class="theme-icon-help" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span>
                            <span>Help</span>
                        </button>
                        <button class="app-header-menu-item" onclick="showSettingsModal(); closeMenu();">
                            <span><svg class="theme-icon-help" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.17 15a1.65 1.65 0 0 0-1.51-1H2a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.17 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.17a1.65 1.65 0 0 0 1-1.51V2a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg></span>
                            <span>Settings</span>
                        </button>
                        <div class="app-header-menu-sep"></div>
                        ${themeSections}
                    </div>
                </div>`;
        }

        // Subtle code-rain background for Hacker theme.
        let codeRainCtx = null;
        let codeRainCols = [];
        let codeRainFontSize = 14;
        let codeRainAnimationId = null;
        let codeRainLastDraw = 0;
        const codeRainChars = '0123456789ABCDEFｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ';

        function resizeCodeRain() {
            const canvas = document.getElementById('codeRain');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            if (!ctx) return;
            codeRainCtx = ctx;
            const dpr = window.devicePixelRatio || 1;
            canvas.width = window.innerWidth * dpr;
            canvas.height = window.innerHeight * dpr;
            codeRainCtx.scale(dpr, dpr);
            codeRainFontSize = Math.max(12, Math.min(16, Math.floor(window.innerWidth / 120)));
            codeRainCtx.font = codeRainFontSize + 'px monospace';
            const colCount = Math.ceil(window.innerWidth / (codeRainFontSize * 1.6));
            codeRainCols = [];
            for (let i = 0; i < colCount; i++) {
                codeRainCols.push(Math.random() * -window.innerHeight);
            }
        }

        function drawCodeRain(timestamp) {
            const canvas = document.getElementById('codeRain');
            if (!canvas || getCurrentTheme() !== 'hacker') return;
            if (!codeRainCtx) resizeCodeRain();
            if (!codeRainCtx) return;

            const dt = timestamp - codeRainLastDraw;
            if (dt < 50) {
                codeRainAnimationId = requestAnimationFrame(drawCodeRain);
                return;
            }
            codeRainLastDraw = timestamp;

            const width = window.innerWidth;
            const height = window.innerHeight;
            codeRainCtx.fillStyle = 'rgba(0, 0, 0, 0.08)';
            codeRainCtx.fillRect(0, 0, width, height);

            for (let i = 0; i < codeRainCols.length; i++) {
                const char = codeRainChars[Math.floor(Math.random() * codeRainChars.length)];
                const x = i * codeRainFontSize * 1.6;
                const y = codeRainCols[i];
                if (y > 0 && y < height + codeRainFontSize) {
                    const fade = Math.min(1, y / height + 0.3);
                    codeRainCtx.fillStyle = 'rgba(0, 255, 65, ' + (0.35 + fade * 0.65) + ')';
                    codeRainCtx.fillText(char, x, y);
                }
                codeRainCols[i] += codeRainFontSize * 0.6;
                if (y > height && Math.random() > 0.975) {
                    codeRainCols[i] = Math.random() * -codeRainFontSize * 10;
                }
            }

            codeRainAnimationId = requestAnimationFrame(drawCodeRain);
        }

        function startCodeRain() {
            if (codeRainAnimationId) return;
            resizeCodeRain();
            if (!codeRainCtx) return;
            codeRainLastDraw = performance.now();
            codeRainAnimationId = requestAnimationFrame(drawCodeRain);
        }

        function stopCodeRain() {
            if (codeRainAnimationId) {
                cancelAnimationFrame(codeRainAnimationId);
                codeRainAnimationId = null;
            }
            const canvas = document.getElementById('codeRain');
            if (canvas && codeRainCtx) {
                codeRainCtx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        function updateCodeRain() {
            if (getCurrentTheme() === 'hacker') {
                startCodeRain();
            } else {
                stopCodeRain();
            }
        }

        function updateFavicon() {
            const link = document.getElementById('faviconLink');
            if (!link) return;
            const theme = getCurrentTheme();
            // Every theme except dark/light has a matching
            // static/favicon-<theme>.svg; dark and light use the plain one.
            link.href = (theme === 'dark' || theme === 'light')
                ? 'static/favicon.svg'
                : `static/favicon-${theme}.svg`;
        }

        window.addEventListener('resize', resizeCodeRain);
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopCodeRain();
            } else {
                updateCodeRain();
            }
        });

        function toggleMenu() {
            const dropdown = document.getElementById('appHeaderMenuDropdown');
            if (!dropdown) return;
            const willOpen = !dropdown.classList.contains('active');
            dropdown.classList.toggle('active');
            if (willOpen) {
                menuBaseTheme = getCurrentTheme();
            } else {
                // Closing without a commit reverts any preview.
                revertTheme();
                menuBaseTheme = null;
            }
        }

        function closeMenu() {
            const dropdown = document.getElementById('appHeaderMenuDropdown');
            if (dropdown) dropdown.classList.remove('active');
            revertTheme();
            menuBaseTheme = null;
        }

        document.addEventListener('click', function(e) {
            const menu = document.querySelector('.app-header-menu');
            if (menu && !menu.contains(e.target)) {
                closeMenu();
            }
        });

        const COLORS = {
            EVENT: {
                alert: '#ff6b6b',
                anomaly: '#ff9800',
                dns: '#66bb6a',
                dnp3: '#26c6da',
                filealerts: '#e91e63',
                fileinfo: '#9c27b0',
                flow: '#bc8cff',
                ftp: '#00bcd4',
                http: '#ffa726',
                log: '#b0b0b0',
                modbus: '#ab47bc',
                pgsql: '#ff7043',
                sigmaalert: '#ff6b6b',
                stats: '#9e9e9e',
                tls: '#58a6ff',
                connection: '#8b949e',
            },
            SEVERITY: {
                1: '#ff6b6b',
                2: '#ffa726',
                3: '#ffca28',
                4: '#66bb6a',
                default: '#8b949e',
            },
        };

        // Value->color maps for the dot indicator used on categorical table columns
        // (Protocol, HTTP Method, DNS Type, TLS Version). Falls back to --text-muted
        // for values not explicitly mapped, so new/unusual values still render sanely.
        const DOT_COLORS = {
            // Chosen to avoid the Type column's colors (TLS/Flow/HTTP already
            // use blue/purple/orange) so the two columns never show identical
            // dots in the same row - see the widest gaps in Type's hue wheel.
            PROTO: { TCP: '#a8d94f', UDP: '#4fd9a0', ICMP: '#4f52d9' },
            HTTP_METHOD: {
                GET: '#58a6ff', POST: '#66bb6a', PUT: '#ffa726', DELETE: '#ff6b6b',
                PATCH: '#bc8cff', HEAD: '#8b949e', OPTIONS: '#8b949e', CONNECT: '#8b949e',
            },
            DNS_TYPE: {
                A: '#58a6ff', AAAA: '#58a6ff', CNAME: '#26c6da', MX: '#ffa726',
                NS: '#bc8cff', TXT: '#66bb6a', PTR: '#ff79c6', SOA: '#ab47bc', SRV: '#00bcd4',
            },
            SIGMA_SEVERITY: {
                critical: 'var(--badge-danger-text)',
                high: '#ff7043',
                medium: 'var(--badge-warning-text)',
                low: '#ffca28',
                informational: 'var(--accent)',
            },
        };

        function valueDotSpan(color) {
            return `<span class="value-dot" style="background:${color || 'var(--text-muted)'}"></span>`;
        }

        function tlsVersionColor(version) {
            if (!version) return null;
            if (version.includes('1.3')) return '#66bb6a';
            if (version.includes('1.2')) return '#58a6ff';
            if (version.includes('1.1')) return '#ffa726';
            if (version.includes('1.0')) return '#ff6b6b';
            if (version.toUpperCase().includes('SSL')) return '#ff6b6b';
            return null;
        }
        const CONFIG = {
            DEFAULT_QUERY_LIMIT: 75000,
            DEFAULT_UPLOAD_SIZE_MB: 1000,
            MAX_POLLING_ATTEMPTS: 120,
            POLLING_INTERVAL_MS: 1000,
            TLS_ISSUER_MAX_LENGTH: 30,
            TLS_SUBJECT_MAX_LENGTH: 40,
            USER_AGENT_MAX_LENGTH: 50,
            AGGREGATION_TOP_N: 10,
            SEARCH_DEBOUNCE_MS: 300,
            SANKEY_BOTTOM_MARGIN: 60,
            SANKEY_MAX_NODES_PER_COLUMN: 50,
            TABLE_PAGE_SIZE: 100,
        };
        const DEFAULT_SAMPLE_URL = 'https://www.malware-traffic-analysis.net/2026/02/03/2026-02-03-GuLoader-for-AgentTesla-style-infection-with-FTP-data-exfil.pcap.zip';
        const FILE_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>';
        const REFRESH_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>';
        const DELETE_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>';
        const FOLDER_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>';
        const FOLDER_OPEN_ICON_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><polyline points="2 13 6 9 10 13"></polyline></svg>';
        const DOWN_ARROW_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>';
        const CHECKMARK_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        const LIGHTBULB_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-7 7c0 2.5 1.5 4.5 3 6h8c1.5-1.5 3-3.5 3-6a7 7 0 0 0-7-7z"/></svg>';
        const SEARCH_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
        const CALENDAR_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>';
        function getWelcomeHelpContent() { return `
            <p style="color: var(--text-muted); font-size: 0.95rem;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Maximum file size is ${getUserMaxUploadSizeMB().toLocaleString()}MB (adjustable in Settings).
            </p>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 15px;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Processing may take a minute or two depending on the size of the file.
            </p>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 15px;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> File types supported:
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.9rem; color: var(--text-primary);">
                <thead>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 18%;">File Type</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 40%;">File Extensions</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 18%;">Engine</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 24%;">Ruleset</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid var(--bg-tertiary);">
                        <td style="padding: 8px 12px;"><strong style="color: var(--accent);">Packet Capture</strong></td>
                        <td style="padding: 8px 12px;">.pcap, .pcapng, .cap, .trace</td>
                        <td style="padding: 8px 12px;">Suricata</td>
                        <td style="padding: 8px 12px;">Emerging Threats Open</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--bg-tertiary);">
                        <td style="padding: 8px 12px;"><strong style="color: var(--accent);">Logs</strong></td>
                        <td style="padding: 8px 12px;">.evtx, .json, .jsonl, .csv, .xml, .log</td>
                        <td style="padding: 8px 12px;">Zircolite</td>
                        <td style="padding: 8px 12px;">SigmaHQ</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px;"><strong style="color: var(--accent);">Binary / Other</strong></td>
                        <td style="padding: 8px 12px;">.exe, .dll, .elf, .pdf, etc.</td>
                        <td style="padding: 8px 12px;">YARA</td>
                        <td style="padding: 8px 12px;">YARA Forge</td>
                    </tr>
                </tbody>
            </table>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 8px; margin-bottom: 0;">
                Any of the above file types can be uploaded inside a .zip archive to automatically extract and analyze the first supported file found.
            </p>
        `; }
        const WELCOME_FEATURES_HTML = `
            <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color); margin-top: 20px;">
                <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 10px; text-align: center;">SO-CRATES provides basic analysis. Need more advanced functionality?<br>Take a look at the full <a href="https://securityonion.net" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-weight: 600;">Security Onion</a> platform available in a free Community Edition!<br>If you need enterprise features, consider upgrading to <a href="https://securityonion.com/pro" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-weight: 600;">Security Onion Pro</a>!</div>
                <table class="feature-table" style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <th style="text-align: left; padding: 10px; color: var(--text-muted); font-size: 0.8rem; text-transform: none; cursor: default;">Feature</th>
                            <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">SO-CRATES</th>
                            <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">Security Onion</th>
                            <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">Security Onion Pro</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Import Files</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Investigate Alerts</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Slice and Dice Metadata</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Pivot to ASCII Transcript</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Download Carved PCAP</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Airgap / Offline Deployment</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Analyze Live Traffic</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Production Deployments</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Distributed Deployments</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Endpoint Visibility</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Log Management</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Case Management</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Guided Analysis</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Onion AI Assistant</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Open ID Connect (OIDC)</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">FIPS</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">STIG Compliance for the OS</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Connect API</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">External Notifications</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Manager of Managers (MoM)</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">MCP Server</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                            <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                        </tr>
                    </tbody>
                </table>
                <div style="margin-top: 15px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; font-size: 0.85rem;">
                    <a href="https://securityonion.net" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none;">Security Onion</a>
                    <span style="color: var(--bg-hover);">|</span>
                    <a href="http://securityonion.net/docs/about" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none;">Security Onion Documentation</a>
                    <span style="color: var(--bg-hover);">|</span>
                    <a href="https://securityonion.com/pro" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none;">Security Onion Pro</a>
                    <span style="color: var(--bg-hover);">|</span>
                    <a href="http://securityonion.net/docs/security-onion-pro" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none;">Security Onion Pro Documentation</a>
                </div>
            </div>
        `;
        let lastSampleUrl = DEFAULT_SAMPLE_URL;
        function yaraTagBadgeHtml(tag) {
            const t = (tag || '').toUpperCase();
            let color;
            if (['RANSOMWARE','TROJAN','BACKDOOR','MALWARE','BOTNET'].includes(t)) {
                color = 'var(--tag-red-text)';
            } else if (['STORMBAMBOO','CHARMINGKITTEN','TURLA','LAZARUS','PLATINUM','HATMAN','CHARMINGCYPRESS','INKYPINE','INKYSQUID','EVILBAMBOO','TRANSPARENTJASMINE','UTA0040','WHEELEDASH'].includes(t)) {
                color = 'var(--tag-purple-text)';
            } else if (t.startsWith('CVE_')) {
                color = 'var(--tag-orange-text)';
            } else if (['FILE','MEMORY','SCRIPT','LOG'].includes(t)) {
                color = 'var(--tag-blue-text)';
            } else if (['INFO','UTILITY','HIGHVOL'].includes(t)) {
                color = 'var(--tag-gray-text)';
            } else {
                color = 'var(--tag-green-text)';
            }
            return `<span style="margin-right:12px;white-space:nowrap;display:inline-block;">${valueDotSpan(color)}${escapeHtml(tag)}</span>`;
        }

        function buildStreamUrl(endpoint, src, sport, dst, dport) {
            const md5Param = currentMd5 ? `&md5=${encodeURIComponent(currentMd5)}` : '';
            return `/api/${endpoint}?src=${encodeURIComponent(src)}&sport=${encodeURIComponent(sport)}&dst=${encodeURIComponent(dst)}&dport=${encodeURIComponent(dport)}${md5Param}`;
        }

        // Serialized currentSearch terms for API query strings ('&q=a&q=b'), or ''.
        function buildSearchQuery() {
            return currentSearch.length > 0 ? currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('') : '';
        }

        // Classify a filename as 'pcap', 'log', or 'binary' by extension.
        function detectFileType(name) {
            if (name && /\.(pcap|pcapng|cap|trace)$/i.test(name)) return 'pcap';
            if (name && /\.(evtx|json|jsonl|csv|xml|log)$/i.test(name)) return 'log';
            return 'binary';
        }

        function showTab(sectionId, el) {
            document.querySelectorAll('.section').forEach(s => s.classList.add('section-hidden'));
            document.getElementById(sectionId).classList.remove('section-hidden');
            document.querySelectorAll('.stat-card').forEach(c => c.classList.remove('tab-active'));
            if (el) el.classList.add('tab-active');
            
            const eventType = sectionId.replace('section-', '');
            loadTabData(eventType, el);
        }
        
        let tabDataCache = {};
        
        async function loadTabData(eventType, activeCard) {
            resetPagination();
            const sectionId = `section-${eventType}`;
            const sectionEl = document.getElementById(sectionId);

            if (activeCard) {
                activeCard.classList.add('tab-active');
            } else {
                document.querySelectorAll('.stat-card').forEach(card => {
                    const onclick = card.getAttribute('onclick');
                    if (onclick && onclick.includes(eventType)) {
                        const match = onclick.match(/showTab\('section-([^']+)'\)/);
                        if (match && match[1] === eventType) {
                            card.classList.add('tab-active');
                        }
                    }
                });
            }
            
            if (eventType === 'all') {
                if (canUseScalableFetch()) {
                    if (needsFullBatch('all')) await ensureCappedBatch('all');
                    if (sectionEl) await buildAllEvents();
                    if (sectionEl && advancedMode) await buildAggregationsSectionAll();
                    updateFilterBarVisibility();
                    await updateSankeyDiagram();
                    return;
                }
                try {
                    await ensureCappedBatch('all');
                } catch(e) {
                    console.error('Failed to load all events:', e);
                }
                if (sectionEl) buildAllEvents();
                if (sectionEl && advancedMode) await buildAggregationsSectionAll();
                updateFilterBarVisibility();
                await updateSankeyDiagram();
                return;
            }

            if (isLogAnalysisMode && eventType === 'log') {
                // Lazily hydrate tabDataCache['log'] on first visit to this
                // tab - no-op if already cached (same helper every other
                // eventType uses).
                await ensureCappedBatch('log');
                const events = tabDataCache['log'] || [];
                const filtered = getFilteredLogEvents(events);
                if (sectionEl) buildLogSectionContent(sectionId, filtered);
                if (advancedMode) buildLogAggregations(filtered, sectionId);
                updateFilterBarVisibility();
                return;
            }

            if (isLogAnalysisMode && eventType === 'sigmaalert') {
                if (canUseScalableFetch()) {
                    if (advancedMode) await ensureCappedBatch('sigmaalert');
                    if (sectionEl) await buildSigmaAlertSectionContent(sectionId, null);
                    if (advancedMode) buildSigmaAlertAggregations(getFilteredSigmaAlerts(tabDataCache['sigmaalert'] || []), sectionId);
                    updateFilterBarVisibility();
                    return;
                }
                try {
                    await ensureCappedBatch('sigmaalert');
                } catch(e) {
                    console.error('Failed to load sigma alerts:', e);
                }
                const alerts = tabDataCache['sigmaalert'] || [];
                const filtered = getFilteredSigmaAlerts(alerts);
                if (sectionEl) buildSigmaAlertSectionContent(sectionId, filtered);
                if (advancedMode) buildSigmaAlertAggregations(filtered, sectionId);
                updateFilterBarVisibility();
                return;
            }

            if (canUseScalableFetch()) {
                if (needsFullBatch(eventType)) await ensureCappedBatch(eventType);
                if (sectionEl) await buildSection(eventType, tabDataCache[eventType] || []);
                if (advancedMode) await buildAggregationsSection(eventType, getFilteredEvents(sectionId, tabDataCache[eventType] || [], eventType));
                updateFilterBarVisibility();
                await updateSankeyDiagram();
                return;
            }

            if (tabDataCache[eventType]) {
                const filtered = getFilteredEvents(sectionId, tabDataCache[eventType], eventType);
                if (advancedMode && sectionEl) {
                    await buildAggregationsSection(eventType, filtered);
                    buildSection(eventType, tabDataCache[eventType]);
                } else if (sectionEl) {
                    buildSection(eventType, tabDataCache[eventType]);
                }
                updateFilterBarVisibility();
                await updateSankeyDiagram();
                return;
            }
            
            try {
                await ensureCappedBatch(eventType);
                const events = tabDataCache[eventType] || [];

                const filtered = getFilteredEvents(sectionId, events, eventType);
                if (advancedMode) {
                    if (sectionEl) {
                        await buildAggregationsSection(eventType, filtered);
                    }
                }
                if (sectionEl) buildSection(eventType, events);
                updateFilterBarVisibility();
                await updateSankeyDiagram();
            } catch(e) {
                console.error('Failed to load tab data:', e);
                if (sectionEl) {
                    sectionEl.innerHTML = `<div class="section-header">${escapeHtml(typeLabels[eventType] || eventType.toUpperCase())}</div><div class="loading">Error loading data</div>`;
                }
            }
        }
        
        function toggleRow(tr) {
            const detailRow = tr.nextElementSibling;
            if (detailRow && detailRow.classList.contains('detail-row')) {
                const wasHidden = !detailRow.classList.contains('visible');
                tr.classList.toggle('expanded-row');
                detailRow.classList.toggle('visible');
                
                if (wasHidden) {
                    const asciiDiv = detailRow.querySelector('.stream-payload');
                    if (asciiDiv) {
                        const srcIp = asciiDiv.dataset.srcIp;
                        const srcPort = asciiDiv.dataset.srcPort;
                        const dstIp = asciiDiv.dataset.dstIp;
                        const dstPort = asciiDiv.dataset.dstPort;
                        const pre = asciiDiv.querySelector('.ascii-transcript');
                        if (pre && !pre.innerHTML) {
                            pre.innerHTML = '<div style="color:var(--text-muted);padding:10px 0;display:flex;align-items:center;gap:8px;"><span class="ascii-loading"></span>Loading ASCII transcript...</div>';
                            loadAsciiTranscript(srcIp, srcPort, dstIp, dstPort, pre);
                        }
                    }
                }
            }
        }
        
        async function loadAsciiTranscript(src, sport, dst, dport, pre) {
            const url = buildStreamUrl('ascii-stream', src, sport, dst, dport);
            try {
                const resp = await fetch(url);
                const text = await resp.text();
                
                // Try to parse as JSON (new format with direction)
                try {
                    const data = JSON.parse(text);
                    if (data.lines && data.lines.length > 0) {
                        let html = '';
                        let groupHtml = '';
                        let lastDirection = '';
                        for (const line of data.lines) {
                            const direction = line.direction;
                            const color = direction === 'src' ? '#ff6b6b' : '#58a6ff';
                            if (direction !== lastDirection && groupHtml) {
                                const bar = `<span style="display:inline-block;width:3px;background:${lastDirection === 'src' ? '#ff6b6b' : '#58a6ff'};margin-right:8px;flex-shrink:0;"></span>`;
                                html += `<div style="display:flex;align-items:stretch;">${bar}<div style="flex:1;">${groupHtml}</div></div>`;
                                groupHtml = '';
                            }
                            groupHtml += line.text.split('\n').map(t => `<div>${escapeHtml(t)}</div>`).join('');
                            lastDirection = direction;
                        }
                        if (groupHtml) {
                            const bar = `<span style="display:inline-block;width:3px;background:${lastDirection === 'src' ? '#ff6b6b' : '#58a6ff'};margin-right:8px;flex-shrink:0;"></span>`;
                            html += `<div style="display:flex;align-items:stretch;">${bar}<div style="flex:1;">${groupHtml}</div></div>`;
                        }
                        pre.innerHTML = html;
                        if (data.truncated) {
                            pre.innerHTML += '<div style="margin-top:10px;color:var(--text-muted);font-style:italic;">[Truncated - stream too large. Use Download PCAP to view full capture.]</div>';
                        }
                        return;
                    }
                } catch (jsonErr) {
                    // Not JSON or parse failed, continue to plain text
                }
                
                // Legacy plain text format (backward compatibility)
                pre.textContent = text || 'No payload data';
            } catch(err) {
                pre.textContent = 'Error loading transcript: ' + err.message;
            }
        }
        
        async function switchStreamView(view, src, sport, dst, dport, btn) {
            const wrapper = btn.closest('.stream-payload');
            const asciiEl = wrapper.querySelector('.ascii-transcript');
            const hexdumpEl = wrapper.querySelector('.hexdump-content');
            const tabs = wrapper.querySelectorAll('.view-tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            
            if (view === 'hexdump') {
                asciiEl.style.display = 'none';
                hexdumpEl.style.display = '';
                if (hexdumpEl.dataset.loaded !== 'true') {
                    hexdumpEl.innerHTML = '<div style="color:var(--text-muted);padding:10px 0;"><span class="ascii-loading"></span>Loading hexdump...</div>';
                    await loadHexdumpData(src, sport, dst, dport, hexdumpEl);
                }
            } else {
                hexdumpEl.style.display = 'none';
                asciiEl.style.display = '';
            }
        }
        
        async function loadHexdumpData(src, sport, dst, dport, container) {
            const url = buildStreamUrl('hexdump-stream', src, sport, dst, dport);
            
            try {
                const resp = await fetch(url);
                const data = await resp.json();
                
                if (data.packets && data.packets.length > 0) {
                    let html = '<div class="packet-controls"><button class="packet-control-btn" onclick="expandAllPackets(this.parentNode.parentNode)">Expand All</button><button class="packet-control-btn" onclick="collapseAllPackets(this.parentNode.parentNode)">Collapse All</button></div>';
                    
                    data.packets.forEach((pkt) => {
                        const isExpanded = false;
                        const arrow = isExpanded ? '▾' : '▸';
                        const dirParts = pkt.header.split(' > ');
                        const isSrc = dirParts.length >= 2 ? dirParts[0].includes(src) : pkt.header.indexOf(src) < pkt.header.indexOf(dst);
                        const dirClass = isSrc ? 'src-dir' : 'dst-dir';
                        html += `
                            <div class="packet-block ${dirClass}">
                                <div class="packet-header" onclick="togglePacket(this)">
                                    <span>${arrow}</span><span>${escapeHtml(pkt.header)}</span>
                                </div>
                                <div class="packet-content${isExpanded ? '' : ' hidden'}">
                                    <pre>${escapeHtml(pkt.lines.join('\n'))}</pre>
                                </div>
                            </div>
                        `;
                    });
                    
                    if (data.truncated) {
                        html += '<div style="margin-top:10px;color:var(--text-muted);font-style:italic;">[Truncated - stream too large. Use Download PCAP to view full capture.]</div>';
                    }
                    
                    container.innerHTML = html;
                    container.dataset.loaded = 'true';
                } else {
                    container.innerHTML = '<div style="color:var(--text-muted);">No packets found</div>';
                    container.dataset.loaded = 'true';
                }
            } catch(err) {
                container.innerHTML = 'Error loading hexdump: ' + escapeHtml(err.message);
            }
        }
        
        function togglePacket(headerEl) {
            const contentEl = headerEl.nextElementSibling;
            const arrowEl = headerEl.querySelector('span:first-child');
            const isHidden = contentEl.classList.contains('hidden');
            arrowEl.textContent = isHidden ? '▾' : '▸';
            contentEl.classList.toggle('hidden');
        }
        
        function expandAllPackets(container) {
            container.querySelectorAll('.packet-content').forEach(el => el.classList.remove('hidden'));
            container.querySelectorAll('.packet-header > span:first-child').forEach(el => el.textContent = '▾');
        }
        
        function collapseAllPackets(container) {
            container.querySelectorAll('.packet-content').forEach(el => el.classList.add('hidden'));
            container.querySelectorAll('.packet-header > span:first-child').forEach(el => el.textContent = '▸');
        }
        
        function htmlRow(label, innerHtml, className, style) {
            const valueCls = className ? `detail-value ${className}` : 'detail-value';
            const sty = style ? ` style="${style}"` : '';
            return `<span class="detail-label">${escapeHtml(label)}</span><span class="${valueCls}"${sty}>${innerHtml}</span>`;
        }
        
        function htmlRowText(label, text, className, style) {
            return htmlRow(label, escapeHtml(String(text || '')), className, style);
        }

        function maybeLinkifyValue(value) {
            const s = String(value || '').trim();
            const lower = s.toLowerCase();
            if (lower.startsWith('http://') || lower.startsWith('https://')) {
                return `${escapeHtml(s)} <a href="${escapeHtml(s)}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; margin-left: 4px; font-size: 0.8em;">↗</a>`;
            }
            return escapeHtml(s);
        }

        function htmlSection(title, color) {
            return `<span style="color: var(--text-muted); margin-top: 10px; grid-column: 1 / -1; border-bottom: 1px solid var(--border-color); padding-bottom: 5px; color: ${color};">${escapeHtml(title)}</span>`;
        }

        function renderMetadataRows(meta) {
            if (!meta || Object.keys(meta).length === 0) return '';
            let html = '';
            Object.entries(meta).forEach(([k, v]) => {
                html += htmlRow(k.charAt(0).toUpperCase() + k.slice(1), maybeLinkifyValue(v));
            });
            return html;
        }
        
        function _formatEventCommon(e) {
            const ts = (e.timestamp || '').slice(0, 19);
            let html = `<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 8px; font-size: 0.85rem; min-width: 0;">`;
            html += htmlRowText('Timestamp', ts);
            html += htmlRow('Event Type', `${valueDotSpan(COLORS.EVENT[e.event_type])}${escapeHtml(e.event_type || '')}`);
            if (e.proto) html += htmlRowText('Protocol', e.proto);
            if (e.flow_id) html += htmlRowText('Flow ID', e.flow_id);
            if (e.pcap_cnt) html += htmlRowText('PCAP Count', e.pcap_cnt);
            if (e.src_ip || e.src_port || e.dest_ip || e.dest_port) {
                html += htmlSection('Connection', COLORS.EVENT.connection);
                if (e.src_ip) html += htmlRowText('Source IP', e.src_ip, 'mono');
                if (e.src_port) html += htmlRowText('Source Port', e.src_port, 'mono');
                if (e.dest_ip) html += htmlRowText('Dest IP', e.dest_ip, 'mono');
                if (e.dest_port) html += htmlRowText('Dest Port', e.dest_port, 'mono');
            }
            return html;
        }

        function _formatEventPayload(e) {
            if (!e.src_ip || !e.src_port || !e.dest_ip || !e.dest_port) return '';
            const srcIpJs = escapeJsString(e.src_ip);
            const dstIpJs = escapeJsString(e.dest_ip);
            const srcIpHtml = escapeHtml(e.src_ip);
            const dstIpHtml = escapeHtml(e.dest_ip);
            // Ports are embedded unquoted in onclick handlers and raw in data
            // attributes, so coerce to integers to guarantee they are numeric.
            const srcPort = parseInt(e.src_port, 10) || 0;
            const dstPort = parseInt(e.dest_port, 10) || 0;
            return `<div class="stream-payload" data-src-ip="${srcIpHtml}" data-src-port="${srcPort}" data-dst-ip="${dstIpHtml}" data-dst-port="${dstPort}" style="margin-top: 15px;"><div style="color: var(--text-muted); font-size: 0.85rem; border-bottom: 1px solid var(--border-color); padding-bottom: 5px; margin-bottom: 5px;">Payload</div><div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 10px;"><div class="view-tabs"><button class="view-tab active" onclick="switchStreamView('ascii','${srcIpJs}',${srcPort},'${dstIpJs}',${dstPort},this)">ASCII Transcript</button><button class="view-tab" onclick="switchStreamView('hexdump','${srcIpJs}',${srcPort},'${dstIpJs}',${dstPort},this)">Hexdump</button></div><button class="stream-btn" onclick="downloadPcap('${srcIpJs}','${srcPort}','${dstIpJs}','${dstPort}')" style="margin-left: 12px;">Download PCAP</button></div><div class="stream-view-container" style="background: var(--bg-primary); padding: 15px; border-radius: 8px; font-size: 0.8rem; margin: 0;"><div class="ascii-transcript" style="white-space: pre-wrap; overflow-wrap: break-word;"></div><div class="hexdump-content" style="display: none;"></div></div></div>`;
        }

        function renderAlertDetails(e) {
            let html = htmlSection('Alert Details', COLORS.EVENT.alert);
            html += htmlRowText('Signature', e.alert?.signature);
            html += htmlRowText('Category', e.alert?.category);
            html += htmlRowText('Severity', e.alert?.severity);
            html += htmlRowText('Action', e.alert?.action);
            html += htmlRowText('GID', e.alert?.gid);
            html += htmlRowText('SID', e.alert?.signature_id);
            html += htmlRow('Rule', escapeHtml(e.alert?.rule || ''), 'mono', 'white-space: pre-wrap; overflow-wrap: break-word; min-width: 0;');
            return html;
        }

        function renderDnsDetails(e) {
            let html = htmlSection('DNS Details', COLORS.EVENT.dns);
            html += htmlRowText('Type', e.dns?.type);
            // Suricata 8's new V3 DNS logging format moved rrname/rrtype off
            // the top level into queries[0] - see the 'Query'/'Type' cases
            // in extractValue for details. e.dns.answers[].rdata already
            // worked under both formats, unaffected.
            html += htmlRowText('Query Name', e.dns?.rrname || e.dns?.queries?.[0]?.rrname, 'mono');
            html += htmlRowText('Query Type', e.dns?.rrtype || e.dns?.queries?.[0]?.rrtype);
            if (e.dns?.answers) {
                html += htmlRowText('Answers', e.dns.answers.map(a => a.rdata).join(', '), 'mono');
            }
            return html;
        }

        function renderHttpDetails(e) {
            let html = htmlSection('HTTP Details', COLORS.EVENT.http);
            html += htmlRow('Method', `${valueDotSpan(DOT_COLORS.HTTP_METHOD[(e.http?.http_method || '').toUpperCase()])}${escapeHtml(e.http?.http_method || '')}`);
            html += htmlRowText('Host', e.http?.hostname, 'mono');
            html += htmlRowText('URL', e.http?.url, 'mono');
            html += htmlRowText('User Agent', e.http?.http_user_agent, '', 'word-break: break-all;');
            html += htmlRowText('Status', e.http?.status);
            html += htmlRowText('Content Type', e.http?.http_content_type);
            return html;
        }

        function renderTlsDetails(e) {
            let html = htmlSection('TLS Details', COLORS.EVENT.tls);
            html += htmlRowText('SNI', e.tls?.sni, 'mono');
            html += htmlRow('Version', `${valueDotSpan(tlsVersionColor(e.tls?.version))}${escapeHtml(e.tls?.version || '')}`);
            html += htmlRowText('Subject', e.tls?.subject, 'mono');
            html += htmlRowText('Issuer', e.tls?.issuerdn, 'mono');
            html += htmlRowText('Not Before', e.tls?.notbefore);
            html += htmlRowText('Not After', e.tls?.notafter);
            html += htmlRowText('Fingerprint', e.tls?.fingerprint, 'mono');
            return html;
        }

        function renderFlowDetails(e) {
            let html = htmlSection('Flow Details', COLORS.EVENT.flow);
            html += htmlRowText('State', e.flow?.state);
            html += htmlRowText('Age', `${e.flow?.age || ''} seconds`);
            html += htmlRowText('Pkts to Server', (e.flow?.pkts_toserver || 0).toLocaleString());
            html += htmlRowText('Pkts to Client', (e.flow?.pkts_toclient || 0).toLocaleString());
            html += htmlRowText('Bytes to Server', (e.flow?.bytes_toserver || 0).toLocaleString());
            html += htmlRowText('Bytes to Client', (e.flow?.bytes_toclient || 0).toLocaleString());
            html += htmlRowText('Alerted', e.flow?.alerted ? 'Yes' : 'No');
            return html;
        }

        function renderFtpDetails(e) {
            let html = htmlSection('FTP Details', COLORS.EVENT.ftp);
            html += htmlRowText('Command', e.ftp?.command);
            html += htmlRowText('Reply', e.ftp?.reply);
            html += htmlRowText('Data Channel', e.ftp?.data_channel?.active ? 'Active' : 'Passive');
            return html;
        }

        function renderAnomalyDetails(e) {
            let html = htmlSection('Anomaly Details', COLORS.EVENT.anomaly);
            // BUGFIX: was e.anomaly?.message, a field that has never existed
            // in Suricata's eve.json anomaly schema (real field is 'event',
            // e.g. "APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION") - same
            // root cause as the Detail-column fix elsewhere, missed here.
            html += htmlRowText('Event', e.anomaly?.event);
            html += htmlRowText('Type', e.anomaly?.type);
            html += htmlRowText('Layer', e.anomaly?.layer);
            html += htmlRowText('App Proto', e.anomaly?.app_proto);
            return html;
        }

        function renderModbusDetails(e) {
            const m = e.modbus || {};
            const req = m.request || {};
            const resp = m.response || {};
            let html = htmlSection('Modbus Details', COLORS.EVENT.modbus);
            html += htmlRowText('Transaction ID', m.id);

            html += htmlSection('Request', COLORS.EVENT.modbus);
            html += htmlRowText('Function', req.function_code);
            html += htmlRowText('Unit ID', req.unit_id);
            html += htmlRowText('Access Type', req.access_type);
            html += htmlRowText('Category', req.category);
            html += htmlRowText('Error Flags', req.error_flags);
            if (req.read) {
                html += htmlRowText('Read Address', req.read.address);
                html += htmlRowText('Read Quantity', req.read.quantity);
            }
            if (req.write) {
                html += htmlRowText('Write Address', req.write.address);
                html += htmlRowText('Write Data', req.write.data);
            }
            if (req.diagnostic) {
                html += htmlRowText('Diagnostic Code', req.diagnostic.code);
                html += htmlRowText('Diagnostic Data', req.diagnostic.data);
            }

            html += htmlSection('Response', COLORS.EVENT.modbus);
            html += htmlRowText('Function', resp.function_code);
            html += htmlRowText('Unit ID', resp.unit_id);
            html += htmlRowText('Access Type', resp.access_type);
            html += htmlRowText('Category', resp.category);
            html += htmlRowText('Error Flags', resp.error_flags);
            if (resp.read) {
                html += htmlRowText('Read Data', resp.read.data);
            }
            if (resp.diagnostic) {
                html += htmlRowText('Diagnostic Code', resp.diagnostic.code);
                html += htmlRowText('Diagnostic Data', resp.diagnostic.data);
            }
            if (resp.exception) {
                html += htmlRowText('Exception Code', resp.exception.code);
            }
            return html;
        }

        function renderDnp3Details(e) {
            const d = e.dnp3 || {};
            let html = htmlSection('DNP3 Details', COLORS.EVENT.dnp3);
            html += htmlRowText('Type', d.type);
            html += htmlRowText('Source Address', d.src);
            html += htmlRowText('Destination Address', d.dst);
            if (d.application) {
                html += htmlRowText('Application Function', d.application.function_code);
                html += htmlRowText('Complete', d.application.complete ? 'Yes' : 'No');
            }
            if (d.control) {
                html += htmlRowText('Control Function', d.control.function_code);
            }
            if (d.iin && d.iin.indicators && d.iin.indicators.length) {
                html += htmlRowText('IIN Indicators', d.iin.indicators.join(', '));
            }
            ['request', 'response'].forEach(dir => {
                const obj = d[dir];
                if (!obj) return;
                html += htmlSection(dir.charAt(0).toUpperCase() + dir.slice(1), COLORS.EVENT.dnp3);
                html += htmlRowText('Type', obj.type);
                html += htmlRowText('Source', obj.src);
                html += htmlRowText('Destination', obj.dst);
                if (obj.application) {
                    html += htmlRowText('Function', obj.application.function_code);
                    html += htmlRowText('Complete', obj.application.complete ? 'Yes' : 'No');
                }
            });
            return html;
        }

        function renderPgsqlDetails(e) {
            const p = e.pgsql || {};
            const req = p.request || {};
            const resp = p.response || {};
            let html = htmlSection('PostgreSQL Details', COLORS.EVENT.pgsql);
            html += htmlRowText('TX ID', p.tx_id);

            if (req.simple_query || req.message || req.protocol_version || req.startup_parameters || req.process_id !== undefined || req.sasl_authentication_mechanism) {
                html += htmlSection('Request', COLORS.EVENT.pgsql);
                html += htmlRowText('Query', req.simple_query);
                html += htmlRowText('Message', req.message);
                html += htmlRowText('Protocol Version', req.protocol_version);
                if (req.startup_parameters && req.startup_parameters.user) {
                    html += htmlRowText('User', req.startup_parameters.user);
                }
                html += htmlRowText('Process ID', req.process_id);
                html += htmlRowText('SASL Mechanism', req.sasl_authentication_mechanism);
            }

            if (resp.command_completed || resp.code || resp.message || resp.data_rows !== undefined || resp.ssl_accepted !== undefined) {
                html += htmlSection('Response', COLORS.EVENT.pgsql);
                html += htmlRowText('Command Completed', resp.command_completed);
                html += htmlRowText('Response Code', resp.code);
                html += htmlRowText('Response Message', resp.message);
                html += htmlRowText('Severity', resp.severity_non_localizable);
                html += htmlRowText('Data Rows', resp.data_rows);
                html += htmlRowText('Data Size', resp.data_size);
                if (resp.ssl_accepted !== undefined) {
                    html += htmlRowText('SSL Accepted', resp.ssl_accepted ? 'Yes' : 'No');
                }
                if (resp.file) {
                    html += htmlRowText('Error File', resp.file);
                    html += htmlRowText('Error Line', resp.line);
                    html += htmlRowText('Routine', resp.routine);
                }
            }
            return html;
        }

        function renderFileAlertDetails(e) {
            const fa = e.filealerts || {};
            let html = htmlRowText('Rule', fa.rule_name);
            html += htmlRowText('SHA256', fa.sha256, 'mono');
            if (fa.author) {
                html += htmlRowText('Author', fa.author);
            }
            if (fa.tags && fa.tags.length > 0) {
                html += htmlRow('Tags', fa.tags.map(t => yaraTagBadgeHtml(t)).join(''));
            }
            html += renderMetadataRows(fa.meta);
            return html;
        }

        function renderFileInfoDetails(e) {
            let html = htmlSection('File Info', COLORS.EVENT.fileinfo);
            html += htmlRowText('Filename', e.fileinfo?.filename, 'mono');
            html += htmlRowText('Magic', e.fileinfo?.magic);
            html += htmlRowText('MD5', e.fileinfo?.md5, 'mono');
            html += htmlRowText('SHA1', e.fileinfo?.sha1, 'mono');
            html += htmlRowText('SHA256', e.fileinfo?.sha256, 'mono');
            html += htmlRowText('Size', `${(e.fileinfo?.size || 0).toLocaleString()} bytes`);

            const meta = e.fileinfo?.metadata || {};
            if (meta.file_type || meta.mime_type || meta.entropy !== undefined || (meta.strings && meta.strings.length)) {
                html += htmlSection('File Metadata', COLORS.EVENT.fileinfo);
                if (meta.file_type) html += htmlRowText('File Type', meta.file_type);
                if (meta.mime_type) html += htmlRowText('MIME Type', meta.mime_type);
                if (meta.entropy !== undefined) html += htmlRowText('Entropy', String(meta.entropy));
                if (meta.strings && meta.strings.length) {
                    html += htmlRowText('Top Strings', meta.strings.slice(0, 20).join(', '), '', 'word-break: break-all;');
                }
            }

            if (meta.exif && Object.keys(meta.exif).length) {
                html += htmlSection('Exif Metadata', COLORS.EVENT.fileinfo);
                Object.entries(meta.exif).forEach(([k, v]) => {
                    html += htmlRowText(escapeHtml(k), escapeHtml(v), '', 'word-break: break-all;');
                });
            }

            const fileSha = e.fileinfo?.sha256 || '';
            const matches = allEvents.filter(ev => ev.event_type === 'filealerts' && ev.filealerts?.sha256 === fileSha);
            html += htmlSection('File Alerts', COLORS.EVENT.filealerts);
            if (matches.length > 0) {
                matches.forEach(m => {
                    html += htmlRowText('Rule', m.filealerts?.rule_name);
                    if (m.filealerts?.tags && m.filealerts.tags.length) {
                        html += htmlRowText('Tags', m.filealerts.tags.join(', '));
                    }
                });
            } else {
                html += `<span style="color: var(--bg-hover-light); grid-column: 1 / -1;">No YARA matches</span>`;
            }
            return html;
        }

        const EVENT_RENDERERS = {
            alert: renderAlertDetails,
            dns: renderDnsDetails,
            dnp3: renderDnp3Details,
            http: renderHttpDetails,
            modbus: renderModbusDetails,
            pgsql: renderPgsqlDetails,
            tls: renderTlsDetails,
            flow: renderFlowDetails,
            ftp: renderFtpDetails,
            anomaly: renderAnomalyDetails,
            filealerts: renderFileAlertDetails,
            fileinfo: renderFileInfoDetails,
        };

        function formatEvent(e) {
            let html = _formatEventCommon(e);
            const renderer = EVENT_RENDERERS[e.event_type];
            if (renderer) {
                html += renderer(e);
            }
            html += `</div>`;
            html += _formatEventPayload(e);
            return html;
        }
        
        function downloadPcap(src, sport, dst, dport) {
            const url = buildStreamUrl('download-stream', src, sport, dst, dport);
            const a = document.createElement('a');
            a.href = url;
            a.download = `stream_${src}_${sport}_to_${dst}_${dport}.pcap`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
        
        
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'TH') {
                const th = e.target;
                // Skip if cursor is default (non-sortable table)
                if (window.getComputedStyle(th).cursor === 'default') return;
                const thead = th.closest('thead');
                if (!thead) return;
                const index = Array.from(thead.querySelectorAll('th')).indexOf(th);
                sortCurrentTable(index);
            }

            // Delegated handler for previous analyses buttons
            const btn = e.target.closest('#previousAnalysesList button[data-action]');
            if (btn) {
                const md5 = btn.dataset.md5;
                const name = btn.dataset.name;
                const action = btn.dataset.action;
                if (action === 'reanalyze') {
                    openReanalyzeModal(md5, name);
                } else if (action === 'delete') {
                    openDeleteAnalysis(md5, name);
                }
            }
        });
        
        function showLoading(message) {
            document.getElementById('loadingText').textContent = message || 'Loading...';
            document.getElementById('loadingModal').classList.add('active');
        }
        
        function hideLoading() {
            document.getElementById('loadingModal').classList.remove('active');
        }

        function clearAnalysisContainers() {
            isLogAnalysisMode = false;
            document.body.classList.remove('file-analysis');
            const statsGrid = document.getElementById('statsGrid');
            if (statsGrid) {
                statsGrid.innerHTML = '';
                statsGrid.style.display = '';
            }
            document.getElementById('sankeyPanel').style.display = 'none';
            document.getElementById('sankeyPanel').innerHTML = '';
            document.getElementById('aggregations').innerHTML = '';
            document.getElementById('sections').innerHTML = '';
            document.getElementById('filterBarContainer').innerHTML = '';
            document.getElementById('filterBarContainer').style.display = 'none';
            document.querySelectorAll('.file-info-card').forEach(c => c.remove());
            const fileInfoContainer = document.getElementById('fileInfoContainer');
            if (fileInfoContainer) {
                fileInfoContainer.innerHTML = '';
                fileInfoContainer.style.display = 'none';
            }
        }

        function showWelcomeUI() {
            document.getElementById('mainHeader').style.display = 'none';
            document.getElementById('dataPanel').style.display = 'none';
            document.getElementById('searchBarContainer').style.display = 'none';
            document.getElementById('inputBoxes').style.display = 'block';
            document.getElementById('appHeaderFilename').innerHTML = '';
            document.getElementById('appHeaderMeta').innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">Security Onion Containerized Rapid Analysis of Threats, Evil, and Sus</span>';
            document.getElementById('appHeaderRight').innerHTML = renderGearMenu();
            updateThemeMenu();
        }

        function shouldShowHelpModal() {
            if (safeStorageGet(localStorage, 'socrates_hideHelp') === 'true') return false;
            if (safeStorageGet(sessionStorage, 'socrates_helpShown') === 'true') return false;
            return true;
        }

        function showHelpModal() {
            const isWelcome = document.getElementById('inputBoxes').style.display !== 'none';
            const modalTitle = document.getElementById('helpModalTitle');
            const modalBody = document.getElementById('helpModalBody');
            const checkboxContainer = document.getElementById('helpShowAgainContainer');
            const checkbox = document.getElementById('helpShowAgain');

            const helpModal = document.getElementById('helpModal');
            if (isWelcome) {
                modalTitle.textContent = 'Welcome to SO-CRATES!';
                modalBody.innerHTML = getWelcomeHelpContent();
                checkboxContainer.style.display = 'flex';
                checkbox.checked = safeStorageGet(localStorage, 'socrates_hideHelp') !== 'true';
                helpModal.classList.add('wide');
            } else {
                modalTitle.textContent = 'Analysis Help';
                const isLogFile = detectFileType(currentFileName) === 'log';
                const isFileOnly = document.body.classList.contains('file-analysis');
                let helpText;
                if (isLogFile) {
                    helpText = `<span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Investigate Sigma Alerts and then review Log Events. Filter using the search bar or aggregation tables.`;
                } else if (isFileOnly) {
                    helpText = `<span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Review the FILE INFO section for metadata and then the data table at the bottom for any matches found by the YARA rules.`;
                } else {
                    helpText = `<span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Start by reviewing all alerts and then you can change to one of the other data types like DNS, HTTP, or TLS. Filter using the search bar, sankey diagram, or aggregation tables. When you find something interesting, you can drill into the row in the data table at the bottom. This will allow you to see the ASCII transcript and hexdump and optionally download the PCAP file for that stream.`;
                }
                modalBody.innerHTML = '<div style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.6;">' + helpText + '</div>';
                checkboxContainer.style.display = 'none';
                helpModal.classList.remove('wide');
            }

            helpModal.classList.add('active');
        }

        function closeHelpModal() {
            document.getElementById('helpModal').classList.remove('active');
            const isWelcome = document.getElementById('inputBoxes').style.display !== 'none';
            if (isWelcome) {
                safeStorageSet(sessionStorage, 'socrates_helpShown', 'true');
                if (!document.getElementById('helpShowAgain').checked) {
                    safeStorageSet(localStorage, 'socrates_hideHelp', 'true');
                } else {
                    safeStorageRemove(localStorage, 'socrates_hideHelp');
                }
            }
        }

        function handleHelpBackdropClick(event) {
            if (event.target === document.getElementById('helpModal')) {
                closeHelpModal();
            }
        }

        function showSettingsModal() {
            const input = document.getElementById('maxQueryLimitInput');
            const hint = document.getElementById('settingsHint');
            const errorEl = document.getElementById('settingsError');
            input.value = getUserQueryLimit();
            errorEl.style.display = 'none';
            hint.textContent = `Default: ${CONFIG.DEFAULT_QUERY_LIMIT.toLocaleString()}.`;

            const uploadInput = document.getElementById('maxUploadSizeInput');
            const uploadHint = document.getElementById('uploadSizeHint');
            const uploadErrorEl = document.getElementById('uploadSizeError');
            uploadInput.value = getUserMaxUploadSizeMB();
            uploadErrorEl.style.display = 'none';
            uploadHint.textContent = `Default: ${CONFIG.DEFAULT_UPLOAD_SIZE_MB.toLocaleString()} MB.`;

            // Never block the modal on this - fall back to showing just the
            // defaults if the server can't be reached (mirrors safeStorageGet's
            // "never throw, always degrade" approach).
            fetch('/api/limits').then(r => r.json()).then(data => {
                input.max = data.maxQueryLimit;
                hint.textContent = `Default: ${CONFIG.DEFAULT_QUERY_LIMIT.toLocaleString()}. Server maximum: ${data.maxQueryLimit.toLocaleString()}.`;
                const maxUploadMB = Math.round(data.maxUploadSize / (1024 * 1024));
                uploadInput.max = maxUploadMB;
                uploadHint.textContent = `Default: ${CONFIG.DEFAULT_UPLOAD_SIZE_MB.toLocaleString()} MB. Server maximum: ${maxUploadMB.toLocaleString()} MB.`;
            }).catch(() => {});
            document.getElementById('settingsModal').classList.add('active');
        }

        function closeSettingsModal() {
            document.getElementById('settingsModal').classList.remove('active');
        }

        function handleSettingsBackdropClick(event) {
            if (event.target === document.getElementById('settingsModal')) {
                closeSettingsModal();
            }
        }

        // Validates and (if valid) persists a single numeric Settings field.
        // Returns 'saved' (persisted, nothing more to do), 'pending' (value
        // was above the server ceiling -- auto-corrected in the input and
        // needs a second Save click to confirm, nothing persisted yet), or
        // 'invalid' (below floor, nothing persisted, error shown).
        function _validateAndMaybeSaveNumberSetting(inputId, errorId, storageKey, floor, floorMessage, fallbackCeiling) {
            const input = document.getElementById(inputId);
            const errorEl = document.getElementById(errorId);
            const value = parseInt(input.value, 10);
            const serverMax = input.max ? parseInt(input.max, 10) : fallbackCeiling;

            if (isNaN(value) || value < floor) {
                errorEl.textContent = floorMessage;
                errorEl.style.display = 'block';
                return 'invalid';
            }
            if (value > serverMax) {
                input.value = serverMax;
                errorEl.textContent = `Clamped to the server maximum of ${serverMax.toLocaleString()}. Click Save again to confirm.`;
                errorEl.style.display = 'block';
                return 'pending';
            }
            errorEl.style.display = 'none';
            safeStorageSet(localStorage, storageKey, String(value));
            return 'saved';
        }

        async function saveSettings() {
            const queryLimitResult = _validateAndMaybeSaveNumberSetting(
                'maxQueryLimitInput', 'settingsError', 'socrates_maxQueryLimit',
                1000, 'Please enter a number of at least 1,000.', 500000
            );
            const uploadSizeResult = _validateAndMaybeSaveNumberSetting(
                'maxUploadSizeInput', 'uploadSizeError', 'socrates_maxUploadSizeMB',
                100, 'Please enter a number of at least 100.', 20000
            );

            // refreshAnalysisData() only matters for the query-limit field --
            // upload size has no bearing on already-loaded analysis data.
            if (queryLimitResult === 'saved') {
                if (currentMd5) {
                    const saveBtn = document.getElementById('settingsSaveBtn');
                    saveBtn.disabled = true;
                    try {
                        await refreshAnalysisData();
                    } finally {
                        saveBtn.disabled = false;
                    }
                }
            }

            if (queryLimitResult === 'saved' && uploadSizeResult === 'saved') {
                closeSettingsModal();
            }
        }

        function showAnalysisUI() {
            document.getElementById('inputBoxes').style.display = 'none';
            document.getElementById('mainHeader').style.display = 'block';
            document.getElementById('dataPanel').style.display = '';
            document.getElementById('searchBarContainer').style.display = 'block';
        }
        
        async function showWelcome() {
            document.title = 'SO-CRATES - Welcome';
            if (window.location.search.includes('file=') || window.location.search.includes('pcap=')) {
                history.replaceState({}, '', window.location.pathname);
            }
            clearAnalysisContainers();
            showWelcomeUI();
            if (shouldShowHelpModal()) {
                showHelpModal();
            }
            
            // Load previous analyses
            let previousHtml = '';
            let previousAnalysisCount = 0;
            try {
                const resp = await fetch('/api/analyses');
                const analyses = await resp.json();
                previousAnalysisCount = analyses.length;
                if (analyses.length > 0) {
                    previousHtml = analyses.map(a => 
                        `<div class="previous-analysis-row" style="display: flex; align-items: center; padding: 8px 10px; border-bottom: 1px solid var(--border-color);">
                            <a href="?file=${escapeHtml(a.md5)}" onclick="event.preventDefault(); loadAnalysis('${escapeJsString(a.md5)}');" style="color: var(--accent); text-decoration: none; flex: 1;">${FOLDER_ICON_SVG}${escapeHtml(a.name)}</a>
                            <button data-md5="${escapeHtml(a.md5)}" data-name="${escapeHtml(a.name)}" data-action="reanalyze" class="previous-analysis-reanalyze" style="border: none; cursor: pointer; font-size: 1rem; padding: 4px 10px; border-radius: 6px; margin-right: 4px;" title="Re-analyze">${REFRESH_ICON_SVG}</button>
                            <button class="previous-analysis-delete" data-md5="${escapeHtml(a.md5)}" data-name="${escapeHtml(a.name)}" data-action="delete" style="border: none; cursor: pointer; font-size: 1rem; padding: 4px 10px; border-radius: 6px;" title="Delete">${DELETE_ICON_SVG}</button>
                        </div>`
                    ).join('');
                } else {
                    previousHtml = '<span style="color: var(--bg-hover-light);">No previous analyses available</span>';
                }
            } catch(err) {
                console.error('Failed to load analyses:', err);
                previousHtml = '<span style="color: var(--bg-hover-light);">Error loading analyses</span>';
            }
            const deleteAllButtonHtml = previousAnalysisCount > 0
                ? `<button class="previous-analysis-delete-all" onclick="openDeleteAllAnalyses(${previousAnalysisCount})" style="border: none; cursor: pointer; font-size: 0.8rem; padding: 4px 10px; border-radius: 6px;" title="Delete all previous analyses">Delete All</button>`
                : '';
            
            document.getElementById('inputBoxes').innerHTML = `
                <div style="max-width: 900px; margin: 0 auto;">
                    <div style="display: flex; flex-direction: column; gap: 20px; margin-bottom: 20px;">
                        <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color); width: 100%; box-sizing: border-box;">
                            <div style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; margin-bottom: 15px; font-weight: 600;">${DOWN_ARROW_ICON_SVG} Select a sample file, import a file from URL, or import a file from your local system</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 15px;">
                                <div class="sample-card" onclick="loadSampleUrl('${DEFAULT_SAMPLE_URL}')">
                                     <span class="sample-label">Sample pcap file</span>
                                 </div>
                                <div class="sample-card" onclick="loadSampleUrl('https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES/raw/refs/heads/master/Defense%20Evasion/apt10_jjs_sideloading_prochollowing_persist_as_service_sysmon_1_7_8_13.evtx')">
                                    <span class="sample-label">Sample log file</span>
                                </div>
                                <div class="sample-card" onclick="loadSampleUrl('https://secure.eicar.org/eicar.com')">
                                    <span class="sample-label">Sample binary file</span>
                                </div>
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 15px;">
                                <div style="flex: 1; text-align: center;">
                                    <a href="https://www.malware-traffic-analysis.net/" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-size: 0.85rem;">More pcap samples ↗</a>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <a href="https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-size: 0.85rem;">More log samples ↗</a>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <a href="https://www.eicar.org/" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-size: 0.85rem;">More binary samples ↗</a>
                                </div>
                            </div>
                            <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 15px;">— OR —</div>
                            <div style="display: flex; gap: 8px; margin-bottom: 15px;">
                                <input type="text" id="pcapUrl" value="${DEFAULT_SAMPLE_URL}" onfocus="this.value=''" onkeydown="if(event.key==='Enter')loadFromUrl()" style="background: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 4px; font-size: 0.95rem; flex: 1;">
                                <button onclick="loadFromUrl()" style="background: var(--accent); color: var(--bg-primary); padding: 8px 20px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 0.95rem; border: none;">Go</button>
                            </div>
                            <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 15px;">— OR —</div>
                            <input type="file" id="pcapUpload" onchange="uploadPcap()" style="display: none;">
                            <div id="dropZone" style="background: var(--bg-primary); color: var(--accent); padding: 20px; border-radius: 4px; cursor: pointer; font-size: 0.95rem; border: 2px dashed var(--border-color); text-align: center; transition: border-color 0.2s, background 0.2s;"
                                 ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)"
                                 onclick="document.getElementById('pcapUpload').click()">
                                 <div style="font-size: 1.5rem; margin-bottom: 8px;"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><polyline points="2 13 6 9 10 13"></polyline></svg></div>
                                 <div>Choose file or drag and drop here</div>
                             </div>
                         </div>
                     </div>
                       <div class="previous-analyses-section" style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color);">
                           <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                               <div style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; font-weight: 600;">${FOLDER_OPEN_ICON_SVG} Previous Analyses</div>
                               ${deleteAllButtonHtml}
                           </div>
                          <div id="previousAnalysesList">${previousHtml}</div>
                      </div>
                     ${WELCOME_FEATURES_HTML}
                 </div>
             `;
            
            document.getElementById('pcapUrl').value = lastSampleUrl;
        }
        
        let keyBuffer = '';
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeMenu();
                closeHelpModal();
            }
            if (e.key === '?' && !e.ctrlKey && !e.altKey && !e.metaKey && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                showHelpModal();
            }
            if (e.key === 't' && !e.ctrlKey && !e.altKey && !e.metaKey && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && !e.target.isContentEditable) {
                e.preventDefault();
                toggleTheme();
            }
            // Easter eggs: type "31337" for Hacker theme, "sguil" for Sguil
            // theme, "cga" for CGA theme, or "c64" for C64 theme. Checked with endsWith() rather
            // than === since the buffer holds the last 5 keys typed
            // session-wide - a code shorter than 5 characters (like "cga")
            // would otherwise only ever match in the first few keystrokes
            // after page load, when the buffer hasn't filled up yet.
            const tag = e.target.tagName;
            const isTyping = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.target.isContentEditable;
            if (!isTyping && e.key.length === 1) {
                keyBuffer += e.key.toLowerCase();
                if (keyBuffer.length > 5) {
                    keyBuffer = keyBuffer.slice(-5);
                }
                if (keyBuffer.endsWith('31337')) {
                    e.preventDefault();
                    setTheme('hacker');
                    showToast('Switched to Hacker theme. You are truly 31337!');
                    keyBuffer = '';
                }
                if (keyBuffer.endsWith('sguil')) {
                    e.preventDefault();
                    setTheme('sguil');
                    showToast('Switched to Sguil theme.');
                    keyBuffer = '';
                }
                if (keyBuffer.endsWith('cga')) {
                    e.preventDefault();
                    setTheme('cga');
                    showToast('Switched to CGA theme.');
                    keyBuffer = '';
                }
                if (keyBuffer.endsWith('c64')) {
                    e.preventDefault();
                    setTheme('c64');
                    showToast('Switched to C64 theme.');
                    keyBuffer = '';
                }
            }
        });

        function showToast(message) {
            document.querySelectorAll('.socrates-toast').forEach(t => t.remove());
            const toast = document.createElement('div');
            toast.className = 'socrates-toast';
            toast.textContent = message;
            toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: var(--bg-secondary); color: var(--accent); border: 1px solid var(--accent); padding: 12px 20px; border-radius: 6px; font-family: inherit; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: opacity 0.5s;';
            document.body.appendChild(toast);
            setTimeout(function() {
                toast.style.opacity = '0';
                setTimeout(function() { toast.remove(); }, 500);
            }, 2000);
        }
        
        // Single delegated listener for advanced toggle (prevents memory leak from repeated loadAnalysis calls)
        async function toggleDiagram() {
            diagramMode = !diagramMode;
            if (diagramMode) {
                const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
                const eventType = visibleSection ? visibleSection.id.replace('section-', '') : null;
                if (eventType && eventType !== 'sigmaalert' && eventType !== 'log'
                    && Object.keys(currentFilters).length > 0) {
                    await ensureCappedBatch(eventType);
                }
            }
            updateFilterBarVisibility();
            await updateSankeyDiagram();
        }

        async function toggleAggregations() {
            advancedMode = !advancedMode;
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            if (!visibleSection) {
                // Binary analysis mode: no tab sections, rebuild aggregations directly
                const fileAlerts = allEvents.filter(e => e.event_type === 'filealerts');
                const filtered = fileAlerts.filter(e => matchesCurrentFilters(e, (ev, col) => extractValue(ev, col, -1)));
                if (advancedMode) {
                    hiddenAggregations = new Set();
                    buildBinaryAggregations(filtered);
                } else {
                    const aggContainer = document.getElementById('aggregations');
                    if (aggContainer) aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                }
                updateFilterBarVisibility();
                return;
            }
            const eventType = visibleSection.id.replace('section-', '');
            if (advancedMode) {
                // needsFullBatch (not an unconditional ensureCappedBatch) so
                // opening the aggregation view for an eligible pcap per-type
                // tab with no active filter goes straight through
                // buildAggregationsSection's own server-aggregation branch
                // instead of always eagerly fetching the full capped batch.
                if (needsFullBatch(eventType)) await ensureCappedBatch(eventType);
                hiddenAggregations = new Set();
                if (eventType === 'all') {
                    await buildAggregationsSectionAll();
                } else if (isLogAnalysisMode && eventType === 'log') {
                    const events = tabDataCache['log'] || [];
                    const filtered = getFilteredLogEvents(events);
                    buildLogAggregations(filtered, visibleSection.id);
                } else if (isLogAnalysisMode && eventType === 'sigmaalert') {
                    const alerts = tabDataCache['sigmaalert'] || [];
                    const filtered = getFilteredSigmaAlerts(alerts);
                    buildSigmaAlertAggregations(filtered, visibleSection.id);
                } else {
                    const events = tabDataCache[eventType] || [];
                    const filtered = getFilteredEvents(visibleSection.id, events, eventType);
                    await buildAggregationsSection(eventType, filtered);
                }
            } else {
                const aggContainer = document.getElementById('aggregations');
                if (aggContainer) {
                    aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                }
            }
            updateFilterBarVisibility();
        }
        
        const typeLabels = {
            alert: 'Network Alerts',
            anomaly: 'Anomalies',
            dns: 'DNS Queries',
            filealerts: 'File Alerts',
            fileinfo: 'File Info',
            flow: 'Flows',
            ftp: 'FTP',
            http: 'HTTP',
            log: 'Log Events',
            sigmaalert: 'Sigma Alerts',
            stats: 'Stats',
            tls: 'TLS'
        };
        
        function buildSankeyData(events) {
            const nodeMap = new Map();
            const linkMap = new Map();

            function getNodeId(name, column) {
                return column + ':' + name;
            }

            function addNode(name, column) {
                const id = getNodeId(name, column);
                if (!nodeMap.has(id)) {
                    nodeMap.set(id, { id: id, name: name, column: column });
                }
                return id;
            }

            function addLink(sourceId, targetId) {
                const key = sourceId + '->' + targetId;
                if (!linkMap.has(key)) {
                    linkMap.set(key, { source: sourceId, target: targetId, value: 0 });
                }
                linkMap.get(key).value += 1;
            }

            for (const e of events) {
                if (!e || e.event_type === 'stats') continue;
                const src = e.src_ip || '?';
                const dst = e.dest_ip || '?';
                const port = String(e.dest_port || '?');
                const srcId = addNode(src, 0);
                const dstId = addNode(dst, 1);
                const portId = addNode(port, 2);
                addLink(srcId, dstId);
                addLink(dstId, portId);
            }

            function capColumn(columnIndex, limit) {
                const columnNodes = Array.from(nodeMap.values()).filter(n => n.column === columnIndex);
                if (columnNodes.length <= limit) return;
                columnNodes.sort((a, b) => {
                    const av = Array.from(linkMap.values()).filter(l => l.source === a.id || l.target === a.id).reduce((s, l) => s + l.value, 0);
                    const bv = Array.from(linkMap.values()).filter(l => l.source === b.id || l.target === b.id).reduce((s, l) => s + l.value, 0);
                    return bv - av;
                });
                const otherId = addNode('Other', columnIndex);

                for (const node of columnNodes.slice(limit)) {
                    nodeMap.delete(node.id);
                }

                const newLinks = new Map();
                for (const [key, link] of linkMap) {
                    const s = link.source;
                    const t = link.target;
                    const sExists = nodeMap.has(s);
                    const tExists = nodeMap.has(t);
                    if (sExists && tExists) {
                        newLinks.set(key, link);
                    } else if (!sExists && tExists) {
                        const newKey = otherId + '->' + t;
                        const existing = newLinks.get(newKey);
                        if (existing) { existing.value += link.value; }
                        else { newLinks.set(newKey, { source: otherId, target: t, value: link.value }); }
                    } else if (sExists && !tExists) {
                        const newKey = s + '->' + otherId;
                        const existing = newLinks.get(newKey);
                        if (existing) { existing.value += link.value; }
                        else { newLinks.set(newKey, { source: s, target: otherId, value: link.value }); }
                    }
                }
                linkMap.clear();
                for (const [k, v] of newLinks) { linkMap.set(k, v); }
            }

            for (let i = 0; i < 3; i++) {
                capColumn(i, CONFIG.SANKEY_MAX_NODES_PER_COLUMN);
            }

            return { nodes: Array.from(nodeMap.values()), links: Array.from(linkMap.values()) };
        }

        function renderSankeySVG(data, container) {
            const width = container.clientWidth || 900;
            const nodesByCol = [[], [], []];
            for (const n of data.nodes) { nodesByCol[n.column].push(n); }
            const maxColNodes = Math.max(nodesByCol[0].length, nodesByCol[1].length, nodesByCol[2].length);
            const minNodeH = 8;
            const nodeGap = 4;
                    const height = Math.max(400, maxColNodes * (minNodeH + nodeGap) + CONFIG.SANKEY_BOTTOM_MARGIN);
            container.innerHTML = '';

            if (!data.nodes.length) return;

            const svg = d3.select(container).append('svg')
                .attr('class', 'sankey-svg')
                .attr('width', width)
                .attr('height', height)
                .attr('viewBox', [0, 0, width, height]);

            const nodeIndex = new Map();
            data.nodes.forEach((n, i) => nodeIndex.set(n.id, i));

            const graph = {
                nodes: data.nodes.map(n => ({ name: n.name, column: n.column })),
                links: data.links.map(l => ({
                    source: nodeIndex.get(l.source),
                    target: nodeIndex.get(l.target),
                    value: l.value
                }))
            };

            const sankey = d3.sankey()
                .nodeWidth(18)
                .nodePadding(nodeGap)
                .extent([[30, 35], [width - 30, height - 10]]);

            let { nodes, links } = sankey(graph);

            function ipToColor(ip) {
                let hash = 0;
                for (let i = 0; i < ip.length; i++) { hash = ((hash << 5) - hash) + ip.charCodeAt(i); }
                return 'hsl(' + (Math.abs(hash) % 360) + ', 70%, 60%)';
            }

            const linkGroup = svg.append('g');
            linkGroup.selectAll('path')
                .data(links)
                .join('path')
                .attr('class', 'sankey-link')
                .attr('d', d3.sankeyLinkHorizontal())
                .attr('stroke', d => ipToColor(d.source.name))
                .attr('stroke-width', d => Math.max(d.width, 1))
                .on('click', function(event, d) {
                    const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
                    if (!visibleSection) return;
                    applyFilters(visibleSection.id, [
                        {column: getColumnNameFromSankeyColumn(d.source.column), value: d.source.name},
                        {column: getColumnNameFromSankeyColumn(d.target.column), value: d.target.name}
                    ]);
                })
                .append('title')
                .text(d => d.source.name + ' \u2192 ' + d.target.name + ' (' + d.value + ')');

            const nodeGroup = svg.append('g')
                .selectAll('g')
                .data(nodes)
                .join('g')
                .attr('class', 'sankey-node')
                .attr('transform', d => 'translate(' + d.x0 + ',' + d.y0 + ')');

            nodeGroup.append('rect')
                .attr('height', d => d.y1 - d.y0)
                .attr('width', d => d.x1 - d.x0)
                .on('click', function(event, d) {
                    const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
                    if (!visibleSection) return;
                    applyFilters(visibleSection.id, [
                        {column: getColumnNameFromSankeyColumn(d.column), value: d.name}
                    ]);
                })
                .append('title')
                .text(d => d.name + ' (' + d.value + ')');

            nodeGroup.append('text')
                .attr('x', d => d.x0 < width / 2 ? (d.x1 - d.x0) + 5 : -5)
                .attr('y', d => (d.y1 - d.y0) / 2)
                .attr('dy', '0.35em')
                .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
                .style('opacity', d => (d.y1 - d.y0) >= minNodeH ? 1 : 0)
                .text(d => {
                    const label = d.name + ' (' + d.value + ')';
                    return label.length > 24 ? d.name.slice(0, 21) + '\u2026 (' + d.value + ')' : label;
                });

            const colLabels = ['Source IP', 'Dest IP', 'Dest Port'];
            const colCenters = [0, 1, 2].map(i => {
                const colNodes = nodes.filter(n => n.column === i);
                if (!colNodes.length) return width * (i + 0.5) / 3;
                return d3.mean(colNodes, n => (n.x0 + n.x1) / 2);
            });

            svg.append('g')
                .selectAll('text')
                .data(colLabels)
                .join('text')
                .attr('class', 'sankey-title')
                .attr('x', (d, i) => colCenters[i])
                .attr('y', 20)
                .attr('text-anchor', 'middle')
                .text(d => d);
        }

        function getSankeyEvents() {
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            if (!visibleSection) return [];
            const eventType = visibleSection.id.replace('section-', '');
            if (eventType === 'all') {
                return getFilteredEvents(visibleSection.id, allEvents, 'all');
            }
            const events = tabDataCache[eventType] || [];
            return getFilteredEvents(visibleSection.id, events, eventType);
        }

        async function updateSankeyDiagram() {
            const sankeyPanel = document.getElementById('sankeyPanel');
            if (!sankeyPanel) return;
            sankeyPanel.innerHTML = '';

            if (!diagramMode) {
                sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▸ Sankey Diagram</div>';
                return;
            }

            sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▾ Sankey Diagram</div><div style="padding:20px;color:var(--text-muted);display:flex;align-items:center;gap:8px;"><span class="ascii-loading"></span>Loading Sankey diagram...</div>';

            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            const eventType = visibleSection ? visibleSection.id.replace('section-', '') : null;

            const gen = bumpFetchGeneration();
            let data;
            if (canUseServerSankey(eventType)) {
                data = await fetchSankeyData(eventType);
            } else {
                data = buildSankeyData(getSankeyEvents());
            }
            if (isStaleFetch(gen)) return;

            if (!data || !data.nodes || data.nodes.length === 0) {
                sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▾ Sankey Diagram</div>';
                return;
            }
            sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▾ Sankey Diagram</div><div class="sankey-content"></div>';
            const svgContainer = sankeyPanel.querySelector('.sankey-content');
            renderSankeySVG(data, svgContainer);
        }

        function getColumnsForType(eventType) {
            switch(eventType) {
                case 'alert':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Alert', 'Category', 'Severity'];
                case 'dns':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Query', 'Type'];
                case 'http':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Method', 'Host', 'URL', 'User-Agent', 'Status'];
                case 'tls':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'SNI / Host', 'Version', 'Subject', 'Issuer'];
                case 'flow':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Pkts →', 'Pkts ←', 'Bytes →', 'Bytes ←', 'State', 'Alerted'];
                case 'fileinfo':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Filename'];
                case 'filealerts':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Rule Name', 'Tags'];
                case 'modbus':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Function', 'Unit ID', 'Access Type', 'Category', 'Error Flags'];
                case 'dnp3':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Type', 'Source Addr', 'Dest Addr', 'Function'];
                case 'pgsql':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Query', 'Command', 'Rows', 'SSL'];
                case 'enip':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Command', 'Status'];
                case 'log': {
                    const logEvents = tabDataCache['log'] || [];
                    const cols = discoverLogColumns(logEvents);
                    const labels = ['Time'];
                    cols.forEach(c => labels.push(c.label));
                    labels.push('Detail');
                    return labels;
                }
                case 'sigmaalert':
                    return ['Time', 'Severity', 'Rule', 'MITRE Technique', 'Log Source'];
                case 'quic':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'SNI', 'QUIC Version', 'JA3', 'JA3S'];
                case 'dhcp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'DHCP Type', 'Client MAC', 'Assigned IP', 'Hostname'];
                case 'ftp_data':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'FTP Command', 'Filename'];
                case 'smb':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'SMB Command', 'Filename', 'Share', 'SMB User'];
                case 'ssh':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Client Version', 'Server Version'];
                case 'krb5':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Client', 'Service', 'Realm', 'Error Code'];
                case 'sip':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'SIP Method', 'URI', 'SIP Code', 'Reason'];
                case 'snmp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'SNMP Version', 'PDU Type', 'Community'];
                case 'mqtt':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'MQTT Type', 'Topic', 'Client ID'];
                case 'dcerpc':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Interface UUID', 'Opnum', 'Call ID'];
                case 'rdp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'RDP Event', 'Cookie', 'Client Name'];
                case 'tftp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Packet', 'File', 'Mode'];
                case 'ike':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Exchange Type', 'IKE Version', 'Init SPI'];
                case 'nfs':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Procedure', 'Filename'];
                case 'rfb':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Client Version', 'Server Version', 'Security Type'];
                case 'bittorrent_dht':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Request Type', 'Info Hash'];
                case 'smtp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Helo', 'Mail From', 'Rcpt To'];
                case 'ftp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Command', 'Command Data', 'Completion Code', 'Reply'];
                case 'anomaly':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Event', 'Type', 'Layer', 'App Proto'];
                case 'ntp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Version', 'Mode', 'Stratum', 'Reference ID'];
                case 'websocket':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Opcode', 'Fin', 'Payload'];
                case 'pop3':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Command', 'Args', 'Status'];
                case 'mdns':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Query', 'Type'];
                case 'ldap':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Operation', 'Message ID', 'Result Code'];
                case 'arp':
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Opcode', 'Src MAC', 'Dest MAC'];
                case 'all':
                    return ALL_EVENTS_COLUMNS;
                default:
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port'];
            }
        }
        
        // Shared leading cells for every per-type event row: timestamp, proto
        // badge, and the source/dest IP:PORT columns.
        function rowPrefixCells(e) {
            const ts = (e.timestamp || '').slice(0, 19);
            const proto = e.proto || '';
            const srcIp = e.src_ip || '';
            const srcPort = e.src_port || '';
            const dstIp = e.dest_ip || '';
            const dstPort = e.dest_port || '';
            return `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td>${valueDotSpan(DOT_COLORS.PROTO[proto.toUpperCase()])}${escapeHtml(proto)}</td><td class="mono-fixed" title="${escapeHtml(srcIp)}">${escapeHtml(srcIp)}</td><td class="mono-fixed">${escapeHtml(String(srcPort))}</td><td class="mono-fixed" title="${escapeHtml(dstIp)}">${escapeHtml(dstIp)}</td><td class="mono-fixed">${escapeHtml(String(dstPort))}</td>`;
        }

        function buildRowForEvent(e) {
            const etype = e.event_type || '';
            const formatted = formatEvent(e);

            let row = '';
            let colSpan = 6;

            switch(etype) {
                case 'alert':
                    const sig = e.alert?.signature || 'N/A';
                    const cat = e.alert?.category || '';
                    const sev = e.alert?.severity || 0;
                    const sevColor = COLORS.SEVERITY[sev] || COLORS.SEVERITY.default;
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(sig)}</td><td>${escapeHtml(cat)}</td><td>${valueDotSpan(sevColor)}Sev ${sev}</td></tr>`;
                    break;
                case 'dns':
                    // Suricata 8's new V3 DNS logging format moved rrname/
                    // rrtype off the top level into queries[0] - see the
                    // 'Query'/'Type' cases in extractValue for details.
                    const rrname = e.dns?.rrname || e.dns?.queries?.[0]?.rrname || '';
                    const rrtype = e.dns?.rrtype || e.dns?.queries?.[0]?.rrtype || '';
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(rrname)}</td><td>${valueDotSpan(DOT_COLORS.DNS_TYPE[rrtype.toUpperCase()])}${escapeHtml(rrtype)}</td></tr>`;
                    break;
                case 'http':
                    const method = e.http?.http_method || '';
                    const host = e.http?.hostname || '';
                    const url = e.http?.url || '';
                    const status = e.http?.status || '';
                    const ua = (e.http?.http_user_agent || '').slice(0, CONFIG.TLS_ISSUER_MAX_LENGTH);
                    const statusColor = status && parseInt(status) < 400 ? 'var(--badge-success-text)' : status && parseInt(status) < 500 ? 'var(--badge-warning-text)' : 'var(--badge-danger-text)';
                    colSpan = 11;
                    row = rowPrefixCells(e) + `<td>${valueDotSpan(DOT_COLORS.HTTP_METHOD[method.toUpperCase()])}${escapeHtml(method)}</td><td class="mono">${escapeHtml(host)}</td><td class="mono">${escapeHtml(url)}</td><td>${escapeHtml(ua)}</td><td>${valueDotSpan(statusColor)}${escapeHtml(String(status))}</td></tr>`;
                    break;
                case 'tls':
                    const sni = e.tls?.sni || '-';
                    const version = e.tls?.version || '-';
                    const subject = (e.tls?.subject || '-').slice(0, CONFIG.TLS_SUBJECT_MAX_LENGTH);
                    let issuer = e.tls?.issuerdn || '-';
                    if (issuer && issuer.includes('CN=')) issuer = issuer.split('CN=')[1].split(',')[0];
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(sni)}</td><td>${valueDotSpan(tlsVersionColor(version))}${escapeHtml(version)}</td><td class="mono">${escapeHtml(subject)}</td><td class="mono">${escapeHtml(issuer.slice(0, CONFIG.TLS_ISSUER_MAX_LENGTH))}</td></tr>`;
                    break;
                case 'flow':
                    const pktsTs = e.flow?.pkts_toserver || 0;
                    const pktsTc = e.flow?.pkts_toclient || 0;
                    const bytesTs = e.flow?.bytes_toserver || 0;
                    const bytesTc = e.flow?.bytes_toclient || 0;
                    const state = e.flow?.state || '';
                    const alerted = e.flow?.alerted || false;
                    const alertedColor = alerted ? 'var(--badge-danger-text)' : 'var(--badge-success-text)';
                    const alertedText = alerted ? 'Yes' : 'No';
                    colSpan = 12;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(String(pktsTs.toLocaleString()))}</td><td>${escapeHtml(String(pktsTc.toLocaleString()))}</td><td>${escapeHtml(String(bytesTs.toLocaleString()))}</td><td>${escapeHtml(String(bytesTc.toLocaleString()))}</td><td>${escapeHtml(state)}</td><td>${valueDotSpan(alertedColor)}${escapeHtml(alertedText)}</td></tr>`;
                    break;
                case 'fileinfo':
                    const filename = e.fileinfo?.filename || '';
                    colSpan = 7;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(filename)}</td></tr>`;
                    break;
                case 'filealerts':
                    const fa = e.filealerts || {};
                    const ruleName = fa.rule_name || 'N/A';
                    const tagsHtml = (fa.tags || []).map(t => yaraTagBadgeHtml(t)).join('');
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(ruleName)}</td><td>${tagsHtml}</td></tr>`;
                    break;
                case 'modbus': {
                    const mr = e.modbus?.request || {};
                    colSpan = 11;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(mr.function_code || '')}</td><td>${escapeHtml(String(mr.unit_id || ''))}</td><td>${escapeHtml(mr.access_type || '')}</td><td>${escapeHtml(mr.category || '')}</td><td>${escapeHtml(mr.error_flags || '')}</td></tr>`;
                    break;
                }
                case 'dnp3': {
                    const dnp = e.dnp3 || {};
                    const dnpType = dnp.type || dnp.request?.type || dnp.response?.type || '';
                    const dnpSrc = dnp.src !== undefined ? dnp.src : (dnp.request?.src !== undefined ? dnp.request.src : '');
                    const dnpDst = dnp.dst !== undefined ? dnp.dst : (dnp.request?.dst !== undefined ? dnp.request.dst : '');
                    const dnpFunc = dnp.application?.function_code !== undefined ? dnp.application.function_code : (dnp.request?.application?.function_code !== undefined ? dnp.request.application.function_code : (dnp.response?.application?.function_code !== undefined ? dnp.response.application.function_code : ''));
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(dnpType)}</td><td>${escapeHtml(String(dnpSrc))}</td><td>${escapeHtml(String(dnpDst))}</td><td>${escapeHtml(String(dnpFunc))}</td></tr>`;
                    break;
                }
                case 'pgsql': {
                    const pq = e.pgsql || {};
                    const pqQuery = (pq.request?.simple_query || '').slice(0, 60);
                    const pqCmd = pq.response?.command_completed || '';
                    const pqRows = pq.response?.data_rows !== undefined ? pq.response.data_rows : '';
                    const pqSsl = pq.response?.ssl_accepted !== undefined ? (pq.response.ssl_accepted ? 'Yes' : 'No') : '';
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td class="mono" style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(pq.request?.simple_query || '')}">${escapeHtml(pqQuery)}</td><td>${escapeHtml(pqCmd)}</td><td>${escapeHtml(String(pqRows))}</td><td>${escapeHtml(pqSsl)}</td></tr>`;
                    break;
                }
                case 'enip': {
                    const en = e.enip || {};
                    const enCommand = en.request?.command || en.response?.command || '';
                    const enStatus = en.response?.status || en.request?.status || '';
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(enCommand)}</td><td>${escapeHtml(enStatus)}</td></tr>`;
                    break;
                }
                case 'quic': {
                    const q = e.quic || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(q.sni || '')}</td><td>${escapeHtml(q.version || '')}</td><td class="mono" title="${escapeHtml(q.ja3?.string || '')}">${escapeHtml(q.ja3?.hash || '')}</td><td class="mono" title="${escapeHtml(q.ja3s?.string || '')}">${escapeHtml(q.ja3s?.hash || '')}</td></tr>`;
                    break;
                }
                case 'dhcp': {
                    const dh = e.dhcp || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(dh.dhcp_type || dh.type || '')}</td><td class="mono">${escapeHtml(dh.client_mac || '')}</td><td class="mono">${escapeHtml(dh.assigned_ip || '')}</td><td>${escapeHtml(dh.hostname || '')}</td></tr>`;
                    break;
                }
                case 'ftp_data': {
                    const fd = e.ftp_data || {};
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(fd.command || '')}</td><td class="mono">${escapeHtml(fd.filename || '')}</td></tr>`;
                    break;
                }
                case 'smb': {
                    const sm = e.smb || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(sm.command || '')}</td><td class="mono">${escapeHtml(sm.filename || '')}</td><td>${escapeHtml(sm.share || '')}</td><td>${escapeHtml(sm.ntlmssp?.user || sm.kerberos?.cname || '')}</td></tr>`;
                    break;
                }
                case 'ssh': {
                    const sh = e.ssh || {};
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(sh.client?.software_version || '')}</td><td class="mono">${escapeHtml(sh.server?.software_version || '')}</td></tr>`;
                    break;
                }
                case 'krb5': {
                    const kb = e.krb5 || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(kb.cname || '')}</td><td>${escapeHtml(kb.sname || '')}</td><td>${escapeHtml(kb.realm || '')}</td><td>${escapeHtml(kb.error_code || '')}</td></tr>`;
                    break;
                }
                case 'sip': {
                    const sp = e.sip || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(sp.method || '')}</td><td class="mono">${escapeHtml(sp.uri || '')}</td><td>${escapeHtml(String(sp.code || ''))}</td><td>${escapeHtml(sp.reason || '')}</td></tr>`;
                    break;
                }
                case 'snmp': {
                    const sn = e.snmp || {};
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(String(sn.version || ''))}</td><td>${escapeHtml(sn.pdu_type || '')}</td><td>${escapeHtml(sn.community || '')}</td></tr>`;
                    break;
                }
                case 'mqtt': {
                    const mq = e.mqtt || {};
                    const mqttType = Object.keys(mq)[0] || '';
                    const mqttSub = mq[mqttType] || {};
                    const topic = mqttSub.topic || (mqttSub.topics || []).map(t => t.topic || t).join(', ') || '';
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(mqttType)}</td><td class="mono">${escapeHtml(topic)}</td><td>${escapeHtml(mqttSub.client_id || '')}</td></tr>`;
                    break;
                }
                case 'dcerpc': {
                    const dc = e.dcerpc || {};
                    const dcUuid = (dc.interfaces || [])[0]?.uuid || '';
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(dcUuid)}</td><td>${escapeHtml(String(dc.req?.opnum ?? dc.request?.opnum ?? ''))}</td><td>${escapeHtml(String(dc.call_id ?? ''))}</td></tr>`;
                    break;
                }
                case 'rdp': {
                    const rd = e.rdp || {};
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(rd.event_type || '')}</td><td class="mono">${escapeHtml(rd.cookie || '')}</td><td>${escapeHtml(rd.client_name || '')}</td></tr>`;
                    break;
                }
                case 'tftp': {
                    const tf = e.tftp || {};
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(tf.packet || '')}</td><td class="mono">${escapeHtml(tf.file || '')}</td><td>${escapeHtml(tf.mode || '')}</td></tr>`;
                    break;
                }
                case 'ike': {
                    const ik = e.ike || {};
                    const ikeVersion = (ik.version_major !== undefined) ? `${ik.version_major}.${ik.version_minor || 0}` : '';
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(ik.exchange_type || '')}</td><td>${escapeHtml(ikeVersion)}</td><td class="mono">${escapeHtml(ik.init_spi || '')}</td></tr>`;
                    break;
                }
                case 'nfs': {
                    const nf = e.nfs || {};
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(nf.procedure || '')}</td><td class="mono">${escapeHtml(nf.filename || '')}</td></tr>`;
                    break;
                }
                case 'rfb': {
                    const rf = e.rfb || {};
                    const cpv = rf.client_protocol_version;
                    const spv = rf.server_protocol_version;
                    const clientVer = cpv ? `${cpv.major}.${cpv.minor}` : '';
                    const serverVer = spv ? `${spv.major}.${spv.minor}` : '';
                    const securityType = rf.authentication?.security_type;
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(clientVer)}</td><td class="mono">${escapeHtml(serverVer)}</td><td>${escapeHtml(securityType != null ? String(securityType) : '')}</td></tr>`;
                    break;
                }
                case 'bittorrent_dht': {
                    const bt = e.bittorrent_dht || {};
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(bt.request_type || bt.request?.request_type || '')}</td><td class="mono">${escapeHtml(bt.info_hash || bt.request?.info_hash || '')}</td></tr>`;
                    break;
                }
                case 'smtp': {
                    const sm2 = e.smtp || {};
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(sm2.helo || '')}</td><td class="mono">${escapeHtml(sm2.mail_from || '')}</td><td class="mono">${escapeHtml((sm2.rcpt_to || []).join(', '))}</td></tr>`;
                    break;
                }
                case 'ftp': {
                    const ft = e.ftp || {};
                    const ftReply = (ft.reply || []).join(' | ').slice(0, 100);
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(ft.command || '')}</td><td class="mono">${escapeHtml(ft.command_data || '')}</td><td>${escapeHtml((ft.completion_code || []).join(', '))}</td><td class="mono">${escapeHtml(ftReply)}</td></tr>`;
                    break;
                }
                case 'anomaly': {
                    const an = e.anomaly || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(an.event || '')}</td><td>${escapeHtml(an.type || '')}</td><td>${escapeHtml(an.layer || '')}</td><td>${escapeHtml(an.app_proto || '')}</td></tr>`;
                    break;
                }
                case 'ntp': {
                    const nt = e.ntp || {};
                    colSpan = 10;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(nt.version !== undefined ? String(nt.version) : '')}</td><td>${escapeHtml(nt.mode !== undefined ? String(nt.mode) : '')}</td><td>${escapeHtml(nt.stratum !== undefined ? String(nt.stratum) : '')}</td><td class="mono">${escapeHtml(nt.reference_id || '')}</td></tr>`;
                    break;
                }
                case 'websocket': {
                    const ws = e.websocket || {};
                    const payload = ws.payload_printable || ws.payload_base64 || '';
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(ws.opcode || '')}</td><td>${escapeHtml(ws.fin !== undefined ? String(ws.fin) : '')}</td><td class="mono">${escapeHtml(payload.slice(0, 100))}</td></tr>`;
                    break;
                }
                case 'pop3': {
                    const p3 = e.pop3 || {};
                    const p3args = (p3.request?.args || []).join(' ');
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(p3.request?.command || '')}</td><td class="mono">${escapeHtml(p3args)}</td><td>${escapeHtml(p3.response?.status || '')}</td></tr>`;
                    break;
                }
                case 'mdns': {
                    const md = e.mdns || {};
                    const mdQuery = md.queries?.[0] || {};
                    colSpan = 8;
                    row = rowPrefixCells(e) + `<td class="mono">${escapeHtml(mdQuery.rrname || '')}</td><td>${valueDotSpan(DOT_COLORS.DNS_TYPE[(mdQuery.rrtype || '').toUpperCase()])}${escapeHtml(mdQuery.rrtype || '')}</td></tr>`;
                    break;
                }
                case 'ldap': {
                    const ld = e.ldap || {};
                    const ldOp = ld.request?.operation || ld.responses?.[0]?.operation || '';
                    const ldMsgId = ld.request?.message_id !== undefined ? ld.request.message_id : (ld.responses?.[0]?.message_id !== undefined ? ld.responses[0].message_id : '');
                    // result_code lives inside a differently-named
                    // sub-object per operation (bind_response, search_
                    // result_done, ...) - look for the first response with one.
                    const ldResult = (ld.responses || []).map(r => {
                        for (const key in r) {
                            if (r[key] && typeof r[key] === 'object' && 'result_code' in r[key]) return r[key].result_code;
                        }
                        return undefined;
                    }).find(v => v !== undefined) || '';
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(ldOp)}</td><td>${escapeHtml(String(ldMsgId))}</td><td>${escapeHtml(ldResult)}</td></tr>`;
                    break;
                }
                case 'arp': {
                    const ap = e.arp || {};
                    colSpan = 9;
                    row = rowPrefixCells(e) + `<td>${escapeHtml(ap.opcode || '')}</td><td class="mono">${escapeHtml(ap.src_mac || '')}</td><td class="mono">${escapeHtml(ap.dest_mac || '')}</td></tr>`;
                    break;
                }
                default:
                    colSpan = 6;
                    row = rowPrefixCells(e) + `</tr>`;
            }

            return row + `<tr class="detail-row"><td colspan="${colSpan}"><div class="detail-content">${formatted}</div></td></tr>`;
        }
        
        function buildFileInfoHtml(events) {
            const fileinfoEvent = events.find(e => e.event_type === 'fileinfo');
            if (!fileinfoEvent || !fileinfoEvent.fileinfo) return '';

            const fi = fileinfoEvent.fileinfo;
            const meta = fi.metadata || {};
            const strings = (meta.strings || []).slice(0, 10);
            const stringsHtml = strings.length
                ? `<span class="value" style="word-break: break-all;">${escapeHtml(strings.join(', '))}</span>`
                : '<span class="value" style="color: var(--bg-hover-light);">—</span>';

            const exif = meta.exif || {};
            const exifEntries = Object.entries(exif).slice(0, 12);
            const exifHtml = exifEntries.length
                ? exifEntries.map(([k, v]) => `<span class="label">${escapeHtml(k)}</span><span class="value" style="word-break: break-all;">${escapeHtml(v)}</span>`).join('')
                : '';

            return `
                <div class="file-info-card">
                    <h3>${FILE_ICON_SVG} File Info</h3>
                    <div class="file-info-grid">
                        <span class="label">Filename</span><span class="value">${escapeHtml(fi.filename || '')}</span>
                        <span class="label">Size</span><span class="value">${escapeHtml(String((fi.size || 0).toLocaleString()))} bytes</span>
                        <span class="label">MD5</span><span class="value">${escapeHtml(fi.md5 || '')}</span>
                        <span class="label">SHA1</span><span class="value">${escapeHtml(fi.sha1 || '')}</span>
                        <span class="label">SHA256</span><span class="value">${escapeHtml(fi.sha256 || '')}</span>
                        <span class="label">Magic</span><span class="value">${escapeHtml(fi.magic || '')}</span>
                        ${meta.mime_type ? `<span class="label">MIME Type</span><span class="value">${escapeHtml(meta.mime_type)}</span>` : ''}
                        ${meta.entropy !== undefined ? `<span class="label">Entropy</span><span class="value">${escapeHtml(String(meta.entropy))}</span>` : ''}
                        ${exifHtml}
                        ${strings.length ? `<span class="label">Top Strings</span>${stringsHtml}` : ''}
                    </div>
                </div>
            `;
        }

        function buildBinaryYaraRow(e) {
            const fa = e.filealerts || {};
            const ruleName = fa.rule_name || 'N/A';
            const tagsHtml = (fa.tags || []).map(t => yaraTagBadgeHtml(t)).join('');
            const author = fa.author || '';
            const formatted = formatEvent(e);
            return `<tr onclick="toggleRow(this)"><td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(ruleName)}</td><td>${tagsHtml}</td><td>${escapeHtml(author)}</td></tr><tr class="detail-row"><td colspan="3"><div class="detail-content">${formatted}</div></td></tr>`;
        }

        function buildBinaryYaraTable(events) {
            const columns = ['Rule Name', 'Tags', 'Author'];
            const sorted = [...events].sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

            let filteredEvents = sorted;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sorted.filter(e => matchesCurrentFilters(e, (ev, col) => extractValue(ev, col, -1)));
            }

            let html = '<div class="section-content">';
            if (filteredEvents.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else if (filteredEvents.length === 0) {
                html += '<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;">No YARA matches found</div>';
            } else {
                html += renderPaginatedTable({
                    sectionKey: 'section-binary',
                    columns,
                    items: filteredEvents,
                    extractFn: extractValue,
                    rowRenderer: buildBinaryYaraRow,
                    rerender: () => buildBinaryAnalysisView(allEvents)
                });
            }
            html += '</div>';
            return html;
        }

        function buildBinaryAggregations(events) {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;
            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }
            const columns = ['Rule Name', 'Tags', 'Author'];
            const html = buildAggregationTablesCore(events, columns, 'section-binary', extractValue);
            aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + html + '</div></div>';
        }

        function buildBinaryAnalysisView(events, baseEvents) {
            const fileAlerts = events.filter(e => e.event_type === 'filealerts');
            const filteredAlerts = fileAlerts.filter(e => matchesCurrentFilters(e, (ev, col) => extractValue(ev, col, -1)));
            const fileInfoSource = baseEvents || baseAllEvents || events;
            const fileInfoHtml = buildFileInfoHtml(fileInfoSource);
            const fileInfoContainer = document.getElementById('fileInfoContainer');
            if (fileInfoContainer) {
                fileInfoContainer.innerHTML = fileInfoHtml;
                fileInfoContainer.style.display = 'block';
            }
            const yaraTableHtml = buildBinaryYaraTable(filteredAlerts);
            const sectionsEl = document.getElementById('sections');
            if (sectionsEl) {
                sectionsEl.innerHTML = yaraTableHtml;
            }
            buildBinaryAggregations(filteredAlerts);
        }
        
        function buildLogEventRow(evt, columns) {
            let jsonData = _parseLogEventJson(evt);
            const timestamp = escapeHtml((evt.timestamp || '').slice(0, 19));
            const detail = getLogEventSmartDetail(jsonData);
            const detailTruncated = detail.length > 120 ? detail.slice(0, 117) + '...' : detail;
            const detailId = 'log-detail-' + (evt.row_id || ++_detailIdCounter);
            // id attribute needs HTML escaping; the onclick argument also
            // needs JS-string escaping (escapeHtml alone would let a quote
            // break out of the JS string after attribute decoding).
            const detailIdAttr = escapeHtml(String(detailId));
            const detailIdJs = escapeJsString(String(detailId));
            const totalCols = 2 + (columns ? columns.length : 0); // Time + [cols] + Detail

            let row = `<tr onclick="toggleLogRow(this, '${detailIdJs}')">`;
            row += `<td class="timestamp">${timestamp}</td>`;
            if (columns) {
                columns.forEach(c => {
                    let val = '';
                    if (c.type === 'base') {
                        if (c.field === 'Channel') val = jsonData.Channel || jsonData.Provider_Name || evt.app_proto || '';
                        else if (c.field === 'EventID') val = String(jsonData.EventID || '');
                        else if (c.field === 'Computer') val = jsonData.Computer || '';
                    } else {
                        val = getLogColumnValue(evt, c.field);
                    }
                    row += `<td>${val ? escapeHtml(val) : '<span style="color:var(--text-muted);">—</span>'}</td>`;
                });
            }
            row += `<td>${detailTruncated ? escapeHtml(detailTruncated) : '<span style="color:var(--text-muted);">—</span>'}</td>`;
            row += '</tr>';

            const detailHtml = formatLogEventDetail(jsonData);
            row += `<tr class="detail-row" id="${detailIdAttr}"><td colspan="${totalCols}"><div class="log-detail-panel">${detailHtml}</div></td></tr>`;
            return row;
        }

        function toggleLogRow(tr, detailId) {
            const detailRow = document.getElementById(detailId);
            if (detailRow) {
                tr.classList.toggle('expanded-row');
                detailRow.classList.toggle('visible');
            }
        }

        function buildSigmaAlertRow(alert) {
            const sev = (alert.severity || 'low').toLowerCase();
            const sevColor = DOT_COLORS.SIGMA_SEVERITY[sev] || DOT_COLORS.SIGMA_SEVERITY.informational;
            const ruleTitle = escapeHtml(alert.rule_title || 'Unknown');
            const ruleId = escapeHtml(alert.rule_id || '');
            const timestamp = escapeHtml(alert.timestamp || '');
            const logsource = escapeHtml(alert.logsource || '');

            const mitreHtml = mitreTechniquesHtml(alert.mitre_techniques);

            const detailId = 'sigma-detail-' + (alert.id || Math.random().toString(36).substr(2, 9));
            // See buildLogEventRow: attribute escaping vs JS-string escaping.
            const detailIdAttr = escapeHtml(String(detailId));
            const detailIdJs = escapeJsString(String(detailId));

            let row = `<tr onclick="toggleSigmaRow(this, '${detailIdJs}')">`;
            row += `<td class="timestamp">${timestamp}</td>`;
            row += `<td>${valueDotSpan(sevColor)}${escapeHtml(sev.toUpperCase())}</td>`;
            row += `<td><strong>${ruleTitle}</strong>${ruleId ? '<br><span style="color:var(--text-muted);font-size:0.8rem;">' + ruleId + '</span>' : ''}</td>`;
            row += `<td>${mitreHtml}</td>`;
            row += `<td>${logsource}</td>`;
            row += '</tr>';

            const detailHtml = formatSigmaAlertDetail(alert);
            row += `<tr class="detail-row" id="${detailIdAttr}"><td colspan="5"><div class="log-detail-panel">${detailHtml}</div></td></tr>`;
            return row;
        }

        function toggleSigmaRow(tr, detailId) {
            const detailRow = document.getElementById(detailId);
            if (detailRow) {
                tr.classList.toggle('expanded-row');
                detailRow.classList.toggle('visible');
            }
        }

        // Log Analysis UI helpers
        let _detailIdCounter = 0;
        const LOG_FIELD_LABELS = {
            'Image': 'Image', 'CommandLine': 'Command Line', 'Commandline': 'Command Line',
            'User': 'User', 'TargetUserName': 'Target User',
            'SourceIp': 'Source IP', 'SourceIP': 'Source IP',
            'DestinationIp': 'Dest IP', 'DestIP': 'Dest IP',
            'TargetFilename': 'Target File', 'TargetObject': 'Target Object',
            'ParentImage': 'Parent Image', 'IpAddress': 'IP Address',
            'LogonType': 'Logon Type', 'ServiceName': 'Service',
            'SourcePort': 'Src Port', 'DestinationPort': 'Dst Port',
            'ProcessId': 'PID', 'ParentProcessId': 'Parent PID',
            'exe': 'Executable', 'comm': 'Command', 'auid': 'Audit UID', 'uid': 'UID',
            'pid': 'PID', 'ppid': 'Parent PID', 'message': 'Message', 'msg': 'Message',
            'Message': 'Message', 'query': 'Query', 'hostname': 'Hostname', 'host': 'Host',
            'program': 'Program', 'facility': 'Facility', 'priority': 'Priority', 'level': 'Level',
            'type': 'Type', 'syscall': 'Syscall', 'terminal': 'Terminal',
            'status': 'Status', 'method': 'Method', 'url': 'URL', 'port': 'Port',
            'ip': 'IP', 'service': 'Service', 'action': 'Action', 'result': 'Result',
            'cmd': 'Command', 'command': 'Command', 'path': 'Path', 'file': 'File',
            'src_ip': 'Source IP', 'src_port': 'Source Port', 'dest_ip': 'Dest IP', 'dest_port': 'Dest Port',
            'dst_ip': 'Dest IP', 'dst_port': 'Dest Port',
        };

        const LOG_FIELD_PRIORITY = {
            'Image': 100, 'CommandLine': 100, 'Commandline': 100, 'cmd': 100, 'command': 100, 'comm': 100, 'exe': 100,
            'User': 95, 'TargetUserName': 95, 'uid': 93, 'auid': 93,
            'SourceIp': 90, 'DestinationIp': 90, 'SourceIP': 90, 'DestIP': 90, 'src_ip': 90, 'dst_ip': 90, 'ip': 90,
            'TargetFilename': 85, 'TargetObject': 80, 'path': 83, 'file': 83,
            'ParentImage': 78, 'IpAddress': 78,
            'LogonType': 75, 'ServiceName': 75, 'service': 75,
            'SourcePort': 72, 'DestinationPort': 72, 'port': 72, 'src_port': 72, 'dest_port': 72, 'dst_port': 72,
            'ProcessId': 70, 'ParentProcessId': 70, 'pid': 70, 'ppid': 70,
            'message': 65, 'msg': 65, 'Message': 65, 'query': 65,
            'hostname': 65, 'host': 65, 'program': 63, 'facility': 62, 'priority': 62, 'level': 62,
            'type': 60, 'syscall': 60, 'terminal': 60, 'action': 60, 'result': 60,
            'status': 58, 'method': 58, 'url': 58,
            'Channel': 50, 'EventID': 50, 'Computer': 50,
        };

        const LOG_NOISE_FIELDS = new Set([
            'timestamp', 'event_type', 'id', 'json_data', 'row_id',
            'proto', 'flow_id', 'tx_id', 'pcap_cnt', 'event_id',
            'TimeCreated', 'SystemTime', 'UtcTime', 'TimeCreated_systemTime',
            'Provider_Name', 'ProviderName', 'ProviderGuid',
            'RecordNumber', 'EventRecordID', 'EventRecordId',
            'ProcessGuid', 'LogonGuid', 'ParentProcessGuid',
            'Version', 'Description', 'Company', 'Product', 'FileVersion',
            'Task', 'Opcode', 'Keywords', 'Level',
        ]);

        function _getLabelForField(field) {
            return LOG_FIELD_LABELS[field] || field;
        }

        function _getFieldForLabel(label) {
            for (const [field, lbl] of Object.entries(LOG_FIELD_LABELS)) {
                if (lbl === label) return field;
            }
            return label;
        }

        function _parseLogEventJson(event) {
            let jd = event.json_data;
            if (typeof jd === 'string') {
                try { jd = JSON.parse(jd || '{}'); } catch(e) { jd = {}; }
            }
            if (!jd || typeof jd !== 'object') return {};
            // Unwrap nested json_data (outer dict has event_type, timestamp, etc.)
            if (jd.json_data) {
                if (typeof jd.json_data === 'string') {
                    try { jd = JSON.parse(jd.json_data); } catch(e) {}
                } else if (typeof jd.json_data === 'object') {
                    jd = jd.json_data;
                }
            }
            return jd;
        }

        function discoverLogColumns(events) {
            if (!events || events.length === 0) return [];
            const total = events.length;
            const threshold = Math.max(2, total * 0.1);
            const counts = {};
            const allFields = new Set();

            events.forEach(e => {
                const jd = _parseLogEventJson(e);
                if (!jd || typeof jd !== 'object') return;
                Object.keys(jd).forEach(k => {
                    if (LOG_NOISE_FIELDS.has(k)) return;
                    allFields.add(k);
                    const val = jd[k];
                    if (val !== undefined && val !== null && val !== '') {
                        counts[k] = (counts[k] || 0) + 1;
                    }
                });
            });

            const baseFields = ['Channel', 'EventID', 'Computer'];
            const baseCols = [];
            baseFields.forEach(f => {
                if ((counts[f] || 0) > 0) {
                    baseCols.push({ field: f, label: _getLabelForField(f), type: 'base' });
                }
            });

            const discovered = Array.from(allFields)
                .filter(f => !baseFields.includes(f))
                .filter(f => (counts[f] || 0) >= threshold)
                .sort((a, b) => {
                    const pa = LOG_FIELD_PRIORITY[a] || 0;
                    const pb = LOG_FIELD_PRIORITY[b] || 0;
                    if (pb !== pa) return pb - pa;
                    return (counts[b] || 0) - (counts[a] || 0);
                })
                .slice(0, 6 - baseCols.length)
                .map(f => ({ field: f, label: _getLabelForField(f), type: 'dynamic' }));

            return [...baseCols, ...discovered];
        }

        function getLogColumnValue(event, field) {
            const jd = _parseLogEventJson(event);
            const val = jd[field];
            if (val === undefined || val === null || val === '') return '';
            return String(val);
        }

        function getLogEventSmartDetail(jsonData) {
            const jd = jsonData;
            if (!jd || typeof jd !== 'object') return '';
            // Network events
            if (jd.SourceIp || jd.DestinationIp || jd.src_ip || jd.dst_ip) {
                const src = jd.SourceIp || jd.src_ip || '';
                const sport = jd.SourcePort || jd.src_port || '';
                const dst = jd.DestinationIp || jd.dst_ip || '';
                const dport = jd.DestinationPort || jd.dest_port || jd.dst_port || '';
                let detail = '';
                if (src && sport) detail += `${src}:${sport}`;
                else if (src) detail += src;
                if (detail && (dst || dport)) detail += ' → ';
                if (dst && dport) detail += `${dst}:${dport}`;
                else if (dst) detail += dst;
                return detail;
            }
            // Process events
            if (jd.CommandLine || jd.cmd || jd.command || jd.comm) return String(jd.CommandLine || jd.cmd || jd.command || jd.comm);
            if (jd.Image || jd.exe) return String(jd.Image || jd.exe);
            // File events
            if (jd.TargetFilename || jd.path || jd.file) return String(jd.TargetFilename || jd.path || jd.file);
            // Registry events
            if (jd.TargetObject) return String(jd.TargetObject);
            // Auth events
            if (jd.TargetUserName || jd.uid || jd.auid) return String(jd.TargetUserName || jd.uid || jd.auid);
            if (jd.User) return String(jd.User);
            // Service events
            if (jd.ServiceName || jd.service) return String(jd.ServiceName || jd.service);
            // Query / URL
            if (jd.query || jd.hostname || jd.host) return String(jd.query || jd.hostname || jd.host);
            if (jd.url || jd.method || jd.status) {
                return [jd.method, jd.url, jd.status].filter(Boolean).join(' ');
            }
            // Fallback
            if (jd.message || jd.msg || jd.Message) return String(jd.message || jd.msg || jd.Message);
            return '';
        }

        function matchesCurrentFilters(e, extractFn) {
            for (const [col, val] of Object.entries(currentFilters)) {
                if (extractFn(e, col) !== val) return false;
            }
            return true;
        }

        function parseMitreTechniques(mitreJson) {
            try {
                return JSON.parse(mitreJson || '[]').map(t => t.replace(/^attack\./i, '').toUpperCase());
            } catch(e) {
                return [];
            }
        }

        function mitreTechniquesHtml(mitreJson) {
            return parseMitreTechniques(mitreJson).map(tid => {
                // Sub-techniques (e.g. T1055.012) live at a nested MITRE URL
                // (/techniques/T1055/012/), not a dotted slug.
                const urlPath = tid.split('.').map(encodeURIComponent).join('/');
                return `<a href="https://attack.mitre.org/techniques/${urlPath}/" target="_blank" rel="noopener noreferrer" class="mitre-tag" onclick="event.stopPropagation()">${escapeHtml(tid)}</a>`;
            }).join('');
        }

        function extractSigmaValue(alert, col) {
            switch(col) {
                case 'Severity': return alert.severity || '';
                case 'Rule': return alert.rule_title || '';
                case 'MITRE Technique': return parseMitreTechniques(alert.mitre_techniques).join(', ');
                case 'Log Source': return alert.logsource || '';
                case 'Time': return alert.timestamp || '';
                default: {
                    // Dynamic column from original_log
                    try {
                        const logObj = JSON.parse(alert.original_log || '{}');
                        if (logObj && typeof logObj === 'object') {
                            const field = _getFieldForLabel(col);
                            return String(logObj[field] || '');
                        }
                    } catch(e) { return ''; }
                    return '';
                }
            }
        }

        function extractLogValue(ev, col) {
            if (col === 'Time') return (ev.timestamp || '').slice(0, 19);
            if (col === 'Detail') return getLogEventSmartDetail(_parseLogEventJson(ev));
            return getLogColumnValue(ev, _getFieldForLabel(col));
        }

        function getFilteredLogEvents(events) {
            if (Object.keys(currentFilters).length === 0) return events;
            return events.filter(e => matchesCurrentFilters(e, extractLogValue));
        }

        function getFilteredSigmaAlerts(alerts) {
            if (Object.keys(currentFilters).length === 0) return alerts;
            return alerts.filter(a => matchesCurrentFilters(a, extractSigmaValue));
        }

        function buildLogSectionContent(sectionId, events) {
            const container = document.getElementById(sectionId);
            if (!container) return;
            let html = '<div class="section-content">';
            if (events.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else if (events.length === 0) {
                html += '<div class="no-matches">No log events found</div>';
            } else {
                const discoveredCols = discoverLogColumns(events);
                const columns = ['Time', ...discoveredCols.map(c => c.label), 'Detail'];
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns,
                    items: events,
                    extractFn: extractLogValue,
                    rowRenderer: (evt) => buildLogEventRow(evt, discoveredCols),
                    rerender: () => buildLogSectionContent(sectionId, events)
                });
            }
            html += '</div>';
            container.innerHTML = html;
        }

        // `alerts` is ignored in scalable mode (no active filter/sort) - the
        // function fetches its own current page directly from the server, so
        // callers may pass null there (e.g. loadTabData's scalable branch).
        async function buildSigmaAlertSectionContent(sectionId, alerts) {
            const container = document.getElementById(sectionId);
            if (!container) return;

            if (canUseScalableFetch()) {
                const { items, serverTotal, gen } = await fetchSigmaAlertsPage();
                if (isStaleFetch(gen)) return;
                let html = '<div class="section-content">';
                if (serverTotal === 0) {
                    html += '<div class="no-matches">No Sigma alerts detected</div>';
                } else {
                    html += renderPaginatedTable({
                        sectionKey: sectionId,
                        columns: getColumnsForType('sigmaalert'),
                        items,
                        serverTotal,
                        extractFn: extractSigmaValue,
                        rowRenderer: buildSigmaAlertRow,
                        // Recomputes a real, filtered list rather than hardcoding
                        // null - a sort click (sigmaalert isn't server-sortable)
                        // flips canUseScalableFetch() false before invoking this
                        // same closure, so it must not assume scalable mode still
                        // applies. tabDataCache['sigmaalert'] is guaranteed
                        // populated by then since sortCurrentTable always awaits
                        // ensureCappedBatch() first for non-server-sortable types.
                        rerender: () => buildSigmaAlertSectionContent(sectionId, getFilteredSigmaAlerts(tabDataCache['sigmaalert'] || []))
                    });
                }
                html += '</div>';
                container.innerHTML = html;
                return;
            }

            // Defensive fallback matching buildBinaryAnalysisView's `||` style -
            // guards against any caller (present or future) passing a falsy
            // alerts value into this branch, which reads alerts.length below.
            if (!alerts) {
                alerts = getFilteredSigmaAlerts(tabDataCache['sigmaalert'] || []);
            }

            let html = '<div class="section-content">';
            if (alerts.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else if (alerts.length === 0) {
                html += '<div class="no-matches">No Sigma alerts detected</div>';
            } else {
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns: getColumnsForType('sigmaalert'),
                    items: alerts,
                    extractFn: extractSigmaValue,
                    rowRenderer: buildSigmaAlertRow,
                    rerender: () => buildSigmaAlertSectionContent(sectionId, alerts)
                });
            }
            html += '</div>';
            container.innerHTML = html;
        }

        // Shared aggregation-table renderer: countsByColumn maps column label ->
        // {value: count}; columns control display order. Hidden columns and
        // empty columns are skipped.
        function _renderAggTablesHtml(countsByColumn, columns, sectionId) {
            let html = '';
            for (const col of columns) {
                if (hiddenAggregations.has(sectionId + ':' + col)) continue;
                const colCounts = countsByColumn[col] || {};
                const entries = Object.entries(colCounts).sort((a, b) => b[1] - a[1]).slice(0, CONFIG.AGGREGATION_TOP_N);
                if (entries.length === 0) continue;
                html += `<div class="section agg-section" data-col="${escapeHtml(col)}"><div class="section-content"><div class="agg-table">
                    <div class="agg-header"><span>${escapeHtml(col)}</span><button class="agg-close" onclick="hideAggregationTable('${sectionId}', '${escapeJsString(col)}')" title="Hide">&times;</button></div>
                    <table><thead><tr><th style="width:60px;text-align:right;">Count</th><th>Value</th></tr></thead><tbody>`;
                for (const [val, count] of entries) {
                    const escapedVal = escapeHtml(val);
                    const filterVal = val === '(empty)' ? '' : val;
                    html += `<tr class="agg-row" onclick="applyFilter('${sectionId}', '${escapeJsString(col)}', '${escapeJsString(filterVal)}')">
                        <td style="text-align:right;color:var(--text-muted);">${count}</td><td class="agg-cell" title="${escapedVal}">${escapedVal}</td>
                    </tr>`;
                }
                html += '</tbody></table></div></div></div>';
            }
            return html;
        }

        function _wrapAggPanel(innerHtml) {
            return '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + innerHtml + '</div></div>';
        }

        function buildLogAggregations(events, sectionId) {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;
            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }
            const counts = {};
            const columns = discoverLogColumns(events);
            const aggCols = columns.map(c => c.label);
            aggCols.forEach(col => { counts[col] = {}; });
            events.forEach(e => {
                const jd = _parseLogEventJson(e);
                columns.forEach(c => {
                    let val = '';
                    if (c.type === 'base') {
                        if (c.field === 'Channel') val = jd.Channel || jd.Provider_Name || e.app_proto || '';
                        else if (c.field === 'EventID') val = String(jd.EventID || '');
                        else if (c.field === 'Computer') val = jd.Computer || '';
                    } else {
                        val = String(jd[c.field] || '');
                    }
                    if (val) counts[c.label][val] = (counts[c.label][val] || 0) + 1;
                });
            });
            aggContainer.innerHTML = _wrapAggPanel('<div class="agg-grid">' + _renderAggTablesHtml(counts, aggCols, sectionId) + '</div>');
        }

        function discoverSigmaAlertColumns(alerts) {
            if (!alerts || alerts.length === 0) return [];
            const total = alerts.length;
            const threshold = Math.max(2, total * 0.1);
            const counts = {};
            const allFields = new Set();

            alerts.forEach(a => {
                try {
                    const logObj = JSON.parse(a.original_log || '{}');
                    if (!logObj || typeof logObj !== 'object') return;
                    Object.keys(logObj).forEach(k => {
                        if (LOG_NOISE_FIELDS.has(k)) return;
                        allFields.add(k);
                        const val = logObj[k];
                        if (val !== undefined && val !== null && val !== '') {
                            counts[k] = (counts[k] || 0) + 1;
                        }
                    });
                } catch(e) {}
            });

            return Array.from(allFields)
                .filter(f => (counts[f] || 0) >= threshold)
                .sort((a, b) => (counts[b] || 0) - (counts[a] || 0))
                .slice(0, 3)
                .map(f => ({ field: f, label: _getLabelForField(f) }));
        }

        function buildSigmaAlertAggregations(alerts, sectionId) {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;
            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }
            const counts = {};
            const baseCols = ['Severity', 'Rule', 'MITRE Technique', 'Log Source'];
            const dynamicCols = discoverSigmaAlertColumns(alerts);
            const aggCols = [...baseCols, ...dynamicCols.map(c => c.label)];
            aggCols.forEach(col => { counts[col] = {}; });
            alerts.forEach(a => {
                const sev = a.severity || '';
                if (sev) counts['Severity'][sev] = (counts['Severity'][sev] || 0) + 1;
                const rule = a.rule_title || '';
                if (rule) counts['Rule'][rule] = (counts['Rule'][rule] || 0) + 1;
                parseMitreTechniques(a.mitre_techniques).forEach(tid => {
                    if (tid) counts['MITRE Technique'][tid] = (counts['MITRE Technique'][tid] || 0) + 1;
                });
                const logsource = a.logsource || '';
                if (logsource) counts['Log Source'][logsource] = (counts['Log Source'][logsource] || 0) + 1;
                dynamicCols.forEach(c => {
                    let val = '';
                    try {
                        const logObj = JSON.parse(a.original_log || '{}');
                        if (logObj && typeof logObj === 'object') {
                            val = String(logObj[c.field] || '');
                        }
                    } catch(e) {}
                    if (val) counts[c.label][val] = (counts[c.label][val] || 0) + 1;
                });
            });
            aggContainer.innerHTML = _wrapAggPanel('<div class="agg-grid">' + _renderAggTablesHtml(counts, aggCols, sectionId) + '</div>');
        }

        function formatLogEventDetail(jsonData) {
            if (!jsonData || Object.keys(jsonData).length === 0) return '<div style="color:var(--text-muted);padding:10px;">No event data available</div>';

            const sections = [
                {
                    title: 'Event Info',
                    color: '#b0b0b0',
                    fields: ['Channel', 'EventID', 'EventRecordID', 'Computer', 'SystemTime', 'UtcTime', 'Level', 'Task', 'Opcode', 'Keywords']
                },
                {
                    title: 'Process',
                    color: '#58a6ff',
                    fields: ['Image', 'CommandLine', 'CurrentDirectory', 'ParentImage', 'ParentCommandLine', 'ParentProcessId', 'ProcessId', 'ProcessGuid', 'IntegrityLevel', 'OriginalFileName']
                },
                {
                    title: 'Network',
                    color: '#66bb6a',
                    fields: ['SourceIp', 'SourcePort', 'SourceHostname', 'DestinationIp', 'DestinationPort', 'DestinationHostname', 'DestinationPortName', 'Protocol', 'Initiated']
                },
                {
                    title: 'User',
                    color: '#ffa726',
                    fields: ['User', 'UserID', 'LogonId', 'LogonGuid', 'TerminalSessionId']
                },
                {
                    title: 'File / Hashes',
                    color: '#9c27b0',
                    fields: ['Hashes', 'MD5', 'SHA1', 'SHA256', 'IMPHASH', 'Signed', 'Signature', 'SignatureStatus']
                },
                {
                    title: 'Other',
                    color: '#8b949e',
                    fields: ['Provider_Name', 'RuleName', 'Guid', 'Version', 'Description', 'Company', 'Product', 'FileVersion', 'ImageLoaded', 'PipeName']
                },
                {
                    title: 'Source',
                    color: '#8b949e',
                    fields: ['OriginalLogfile']
                }
            ];

            let html = `<div style="display: grid; grid-template-columns: 140px minmax(0, 1fr); gap: 8px 12px; font-size: 0.9rem; overflow-wrap: break-word;">`;
            let hasAny = false;

            for (const section of sections) {
                let sectionHtml = '';
                for (const field of section.fields) {
                    const val = jsonData[field];
                    if (val !== undefined && val !== null && val !== '') {
                        sectionHtml += htmlRowText(field, String(val), 'mono');
                    }
                }
                if (sectionHtml) {
                    html += htmlSection(section.title, section.color);
                    html += sectionHtml;
                    hasAny = true;
                }
            }

            // Raw JSON fallback for any fields not in known sections
            const knownFields = new Set(sections.flatMap(s => s.fields));
            const remaining = Object.entries(jsonData).filter(([k, v]) => {
                return !knownFields.has(k) && v !== undefined && v !== null && v !== '';
            });
            if (remaining.length > 0) {
                html += htmlSection('Raw Data', '#8b949e');
                for (const [k, v] of remaining) {
                    html += htmlRowText(k, String(v), 'mono');
                }
                hasAny = true;
            }

            html += '</div>';
            return hasAny ? html : '<div style="color:var(--text-muted);padding:10px;">No event data available</div>';
        }

                function formatSigmaAlertDetail(alert) {
            let html = `<div style="display: grid; grid-template-columns: 140px minmax(0, 1fr); gap: 8px 12px; font-size: 0.9rem; overflow-wrap: break-word;">`;

            // Matched Event
            let eventHtml = '';
            try {
                const logObj = JSON.parse(alert.original_log || '{}');
                if (logObj && Object.keys(logObj).length > 0) {
                    eventHtml = formatLogEventDetail(logObj);
                }
            } catch(e) {}
            if (eventHtml) {
                html += htmlSection('Matched Event', COLORS.EVENT.log);
                html += `<div style="grid-column: 1 / -1;">${eventHtml}</div>`;
            }

            // Sigma Rule
            html += htmlSection('Sigma Rule', COLORS.EVENT.sigmaalert);
            html += htmlRowText('Rule Title', alert.rule_title);
            html += htmlRowText('Rule ID', alert.rule_id);
            html += htmlRowText('Severity', alert.severity);
            html += htmlRowText('Level', alert.level);
            html += htmlRowText('Log Source', alert.logsource);

            const mitreHtml = mitreTechniquesHtml(alert.mitre_techniques);
            if (mitreHtml) {
                html += htmlRow('MITRE Techniques', mitreHtml);
            }

            let tagsText = '';
            try {
                const tags = JSON.parse(alert.tags || '[]');
                if (tags.length > 0) {
                    tagsText = tags.join(', ');
                }
            } catch(e) {}
            if (tagsText) {
                html += htmlRowText('Tags', tagsText);
            }

            html += '</div>';
            return html;
        }

        async function buildSection(eventType, events) {
            const columns = getColumnsForType(eventType);
            const sectionId = `section-${eventType}`;
            const container = document.getElementById(sectionId);
            if (!container) return;

            if (canUseScalableFetchForSort(eventType)) {
                const { items, serverTotal, gen } = await fetchEventsPage(eventType);
                if (isStaleFetch(gen)) return;
                let html = '<div class="section-content">';
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns,
                    items,
                    serverTotal,
                    extractFn: extractValue,
                    rowRenderer: buildRowForEvent,
                    rerender: () => buildSection(eventType, tabDataCache[eventType] || [])
                });
                html += '</div>';
                try {
                    container.innerHTML = html;
                } catch(e) {
                    console.error('Failed to render section:', e);
                    container.innerHTML = '<div class="loading">Error rendering table</div>';
                }
                return;
            }

            const sorted = [...events].sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

            let filteredEvents = sorted;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sorted.filter(e => matchesCurrentFilters(e, (ev, col) => extractValue(ev, col, columns.indexOf(col))));
            }

            let html = '<div class="section-content">';
            if (filteredEvents.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else {
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns,
                    items: filteredEvents,
                    extractFn: extractValue,
                    rowRenderer: buildRowForEvent,
                    rerender: () => buildSection(eventType, events)
                });
            }
            html += '</div>';

            try {
                container.innerHTML = html;
            } catch(e) {
                console.error('Failed to render section:', e);
                container.innerHTML = '<div class="loading">Error rendering table</div>';
            }
        }

        async function buildAggregationsSection(eventType, events) {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;

            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }

            const sectionId = `section-${eventType}`;

            if (canUseServerAggregation(eventType)) {
                const data = await fetchAggregationData(eventType);
                const countsByColumn = {};
                for (const [col, entries] of Object.entries(data)) {
                    countsByColumn[col] = {};
                    for (const { value, count } of entries) countsByColumn[col][value] = count;
                }
                const html = '<div class="agg-grid">' + _renderAggTablesHtml(countsByColumn, getColumnsForType(eventType), sectionId) + '</div>';
                aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + html + '</div></div>';
                return;
            }

            aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + buildAggregationTables(events, eventType) + '</div></div>';
        }
        
        // Whether the row table/aggregations/diagram for the currently-visible
        // tab are known to be operating on a capped (partial) dataset - see
        // truncatedTypes, maintained by ensureCappedBatch.
        function isCurrentTabTruncated() {
            const eventType = getVisibleEventType();
            return !!eventType && truncatedTypes.has(eventType);
        }

        function getVisibleEventType() {
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            return visibleSection ? visibleSection.id.replace('section-', '') : null;
        }

        // Actual number of rows currently cached for eventType - used in the
        // truncation-warning message since the effective limit is user-configurable
        // (getUserQueryLimit()) and may itself still be clamped lower server-side.
        function getFetchedLengthForType(eventType) {
            return (eventType === 'all' ? allEvents : (tabDataCache[eventType] || [])).length;
        }

        function buildFilterBarHtml() {
            const hasFilters = Object.keys(currentFilters).length > 0;
            let html = '';
            if (currentSearch.length > 0 || hasFilters) {
                html += `<div class="filter-bar"><span class="filter-label">${SEARCH_ICON_SVG} Active:</span>`;
                for (let i = 0; i < currentSearch.length; i++) {
                    const term = currentSearch[i];
                    html += `<span class="filter-chip">${SEARCH_ICON_SVG} "${escapeHtml(term)}" <span class="filter-chip-remove" onclick="clearSearchTerm(${i})">&times;</span></span>`;
                }
                for (const [col, val] of Object.entries(currentFilters)) {
                    html += `<span class="filter-chip">${escapeHtml(col)}: ${escapeHtml(val)} <span class="filter-chip-remove" onclick="clearFilter('${escapeJsString(col)}')">&times;</span></span>`;
                }
                html += '<button class="filter-clear-all" onclick="clearAllFilters()">Clear All</button></div>';
            }
            if (isCurrentTabTruncated()) {
                const fetchedCount = getFetchedLengthForType(getVisibleEventType()).toLocaleString();
                html += `<div class="filter-bar"><span style="color: var(--badge-warning-text);">⚠ Showing the first ${fetchedCount} matching events for this view — results may be incomplete.</span></div>`;
            }
            return html;
        }

        function updateFilterBarVisibility() {
            const filterBarContainer = document.getElementById('filterBarContainer');
            if (!filterBarContainer) return;

            const hasFilters = Object.keys(currentFilters).length > 0;
            if (currentSearch.length > 0 || hasFilters || isCurrentTabTruncated()) {
                filterBarContainer.innerHTML = buildFilterBarHtml();
                filterBarContainer.style.display = 'block';
            } else {
                filterBarContainer.innerHTML = '';
                filterBarContainer.style.display = 'none';
            }
        }
        
        let eventStats = {};
        
        function eventMatchesFilters(event) {
            if (Object.keys(currentFilters).length === 0) return true;
            return matchesCurrentFilters(event, (ev, col) => {
                if (col === 'Type' || col === 'Detail') {
                    const allColIndex = ALL_EVENTS_COLUMNS.indexOf(col);
                    return extractAllValue(ev, col, allColIndex);
                }
                return extractValue(event, col, -1);
            });
        }

        async function computeFilteredStats() {
            if (isLogAnalysisMode) {
                // eventMatchesFilters/sigmaAlertMatchesFilters only check
                // currentFilters (search is already reflected server-side in
                // eventStats via /api/count?q=/api/sigma-count?q=), so with no
                // active column filter eventStats already holds the exact
                // same counts - no need to touch the full arrays at all.
                if (Object.keys(currentFilters).length === 0) {
                    return eventStats;
                }
                await ensureCappedBatch('log');
                await ensureCappedBatch('sigmaalert');
                const stats = {};
                const logEvents = tabDataCache['log'] || [];
                const sigmaAlerts = tabDataCache['sigmaalert'] || [];
                let logCount = 0;
                for (const e of logEvents) {
                    if (eventMatchesFilters(e)) logCount++;
                }
                if (logCount > 0) stats['log'] = logCount;
                let sigmaCount = 0;
                for (const a of sigmaAlerts) {
                    if (sigmaAlertMatchesFilters(a)) sigmaCount++;
                }
                if (sigmaCount > 0) stats['sigmaalert'] = sigmaCount;
                return stats;
            }
            // eventMatchesFilters only ever checks currentFilters (search is
            // already reflected server-side in eventStats via /api/stats?q=),
            // so with no active column filter every event trivially matches -
            // eventStats already holds the exact same per-type counts, no need
            // to touch allEvents at all.
            if (Object.keys(currentFilters).length === 0) {
                return eventStats;
            }
            await ensureCappedBatch('all');
            const stats = {};
            const events = allEvents.filter(e => e.event_type !== 'stats');
            for (const e of events) {
                if (eventMatchesFilters(e)) {
                    const type = e.event_type || 'unknown';
                    stats[type] = (stats[type] || 0) + 1;
                }
            }
            return stats;
        }

        function sigmaAlertMatchesFilters(alert) {
            if (Object.keys(currentFilters).length === 0) return true;
            return matchesCurrentFilters(alert, extractSigmaValue);
        }

        function buildStats(filteredStats) {
            const grid = document.getElementById('statsGrid');
            const stats = [];
            const hasFilters = Object.keys(currentFilters).length > 0 || currentSearch.length > 0;
            
            eventTypes.forEach(type => {
                const total = baseEventStats[type] || 0;
                const filtered = filteredStats ? (filteredStats[type] || 0) : (eventStats[type] || 0);
                stats.push({
                    id: type,
                    label: typeLabels[type] || type.toUpperCase(),
                    count: filtered,
                    total: total,
                    color: COLORS.EVENT[type] || COLORS.EVENT.tls
                });
            });
            
            if (!isLogAnalysisMode) {
                const allFiltered = stats.reduce((a, s) => a + s.count, 0);
                const allTotal = Object.values(baseEventStats).reduce((a, b) => a + b, 0) - (baseEventStats['stats'] || 0);
                stats.push({
                    id: 'all',
                    label: 'All Events',
                    count: allFiltered,
                    total: allTotal,
                    color: 'var(--text-bright)'
                });
            }
            
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            const activeType = visibleSection ? visibleSection.id.replace('section-', '') : (stats[0] && stats[0].id);
            grid.innerHTML = stats.map(s => {
                const countDisplay = hasFilters ? `${s.count.toLocaleString()} / ${s.total.toLocaleString()}` : s.count.toLocaleString();
                const isClickable = s.count > 0;
                const activeClass = s.id === activeType ? ' tab-active' : '';
                const disabledClass = isClickable ? '' : ' stat-disabled';
                const onclickAttr = isClickable ? `onclick="showTab('section-${s.id}', this)"` : '';
                return `
                    <div class="stat-card${activeClass}${disabledClass}" ${onclickAttr}>
                        <div class="stat-number" style="color: ${s.color}">${countDisplay}</div>
                        <div class="stat-label">${s.label}</div>
                    </div>
                `;
            }).join('');
        }
        
        function buildSections() {
            const sectionsEl = document.getElementById('sections');
            let html = '';
            
            eventTypes.forEach((type, i) => {
                const label = typeLabels[type] || type.toUpperCase();
                html += `<div class="section${i > 0 ? ' section-hidden' : ''}" id="section-${type}"><div class="section-header">${label}</div><div class="loading">Loading...</div></div>`;
            });
            
            html += '<div class="section section-hidden" id="section-all"><div class="section-header">All Events</div><div class="loading">Loading...</div></div>';
            sectionsEl.innerHTML = html;
            
        }
        
        function buildAllEventRow(e) {
            const ts = (e.timestamp || '').slice(0, 19);
            const etype = e.event_type || '';
            const proto = e.proto || '';
            const srcIp = e.src_ip || '';
            const srcPort = e.src_port || '';
            const dstIp = e.dest_ip || '';
            const dstPort = e.dest_port || '';
            // Uses the canonical Detail logic (extractValue's 'Detail' case)
            // instead of maintaining a separate, independently-drifted copy -
            // the old inline copy here was missing modbus/dnp3/pgsql/filealerts
            // (always blank), even though those were already correctly
            // sortable/filterable via extractValue elsewhere.
            const detail = extractValue(e, 'Detail', -1);
            const formatted = formatEvent(e);
            return `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td>${valueDotSpan(COLORS.EVENT[etype])}${escapeHtml(etype.toUpperCase())}</td><td>${valueDotSpan(DOT_COLORS.PROTO[proto.toUpperCase()])}${escapeHtml(proto)}</td><td class="mono-fixed" title="${escapeHtml(srcIp)}">${escapeHtml(srcIp)}</td><td class="mono-fixed">${escapeHtml(String(srcPort))}</td><td class="mono-fixed" title="${escapeHtml(dstIp)}">${escapeHtml(dstIp)}</td><td class="mono-fixed">${escapeHtml(String(dstPort))}</td><td class="mono">${escapeHtml(detail)}</td></tr><tr class="detail-row"><td colspan="8"><div class="detail-content">${formatted}</div></td></tr>`;
        }

        async function buildAllEvents() {
            const allColumns = ALL_EVENTS_COLUMNS;
            const sectionId = 'section-all';
            const container = document.getElementById(sectionId);
            if (!container) return;

            if (canUseScalableFetchForSort('all')) {
                const { items, serverTotal, gen } = await fetchEventsPage('all');
                if (isStaleFetch(gen)) return;
                let html = '<div class="section-content">';
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns: allColumns,
                    items,
                    serverTotal,
                    extractFn: extractAllValue,
                    rowRenderer: buildAllEventRow,
                    rerender: buildAllEvents
                });
                html += '</div>';
                container.innerHTML = html;
                return;
            }

            const sortedAll = [...allEvents].filter(e => e.event_type !== 'stats').sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

            if (sortedAll.length === 0) return;

            let filteredEvents = sortedAll;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sortedAll.filter(e => matchesCurrentFilters(e, (ev, col) => extractAllValue(ev, col, allColumns.indexOf(col))));
            }

            let html = '<div class="section-content">';
            if (filteredEvents.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else {
                html += renderPaginatedTable({
                    sectionKey: sectionId,
                    columns: allColumns,
                    items: filteredEvents,
                    extractFn: extractAllValue,
                    rowRenderer: buildAllEventRow,
                    rerender: buildAllEvents
                });
            }
            html += '</div>';

            container.innerHTML = html;
        }
        
        async function buildAggregationsSectionAll() {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;

            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }

            const allColumns = ALL_EVENTS_COLUMNS;
            const sectionId = 'section-all';

            if (canUseServerAggregation('all')) {
                const data = await fetchAggregationData('all');
                const countsByColumn = {};
                for (const [col, entries] of Object.entries(data)) {
                    countsByColumn[col] = {};
                    for (const { value, count } of entries) countsByColumn[col][value] = count;
                }
                const html = '<div class="agg-grid">' + _renderAggTablesHtml(countsByColumn, allColumns, sectionId) + '</div>';
                aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + html + '</div></div>';
                return;
            }

            const sortedAll = [...allEvents].filter(e => e.event_type !== 'stats').sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));
            let filteredEvents = sortedAll;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sortedAll.filter(e => matchesCurrentFilters(e, (ev, col) => extractAllValue(ev, col, allColumns.indexOf(col))));
            }

            aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + buildAggregationTablesAll(filteredEvents, allColumns) + '</div></div>';
        }
        
        function extractAllValue(e, col, colIndex) {
            // 'Type' means something different here (the event_type itself,
            // e.g. "DNS"/"ANOMALY") than it does on a per-type tab (a DNS
            // record type, dnp3's type field, etc.) - this override is
            // real and must stay. 'Command' and 'Message' used to be
            // overridden here too, but both were stale: 'Command' predates
            // pgsql/enip/pop3 gaining their own real command fields (this
            // always returned '' for them, ignoring extractValue's own
            // already-correct per-protocol handling), and 'Message' read
            // e.anomaly?.message, a field that has never existed in
            // Suricata's eve.json anomaly schema (real field is 'event') -
            // also, no column has been labeled 'Message' since anomaly
            // gained real columns (Event/Type/Layer/App Proto). Both are
            // removed; extractValue's own switch already handles every
            // real per-type column correctly.
            if (col === 'Type') return (e.event_type || '').toUpperCase();
            return extractValue(e, col, colIndex);
        }
        
        function buildAggregationTablesCore(events, columns, sectionId, extractFn) {
            if (!events || events.length === 0) return '';

            const excludeCols = ['Time'];
            const aggCols = columns.filter(c => !excludeCols.includes(c) && !hiddenAggregations.has(sectionId + ':' + c));

            const counts = {};
            aggCols.forEach(col => { counts[col] = {}; });
            for (const col of aggCols) {
                const colIndex = columns.indexOf(col);
                for (const e of events) {
                    const val = extractFn(e, col, colIndex);
                    const key = val || '(empty)';
                    counts[col][key] = (counts[col][key] || 0) + 1;
                }
            }

            return '<div class="agg-grid">' + _renderAggTablesHtml(counts, aggCols, sectionId) + '</div>';
        }
        
        function buildAggregationTablesAll(events, columns) {
            return buildAggregationTablesCore(events, columns, 'section-all', extractAllValue);
        }
        
        function extractValue(e, col, colIndex) {
            switch(col) {
                case 'Protocol': return e.proto || '';
                case 'Source IP': return e.src_ip || '';
                case 'Source Port': return String(e.src_port || '');
                case 'Dest IP': return e.dest_ip || '';
                case 'Dest Port': return String(e.dest_port || '');
                case 'Alert': return e.alert?.signature || '';
                case 'Category': {
                    if (e.event_type === 'modbus') return e.modbus?.request?.category || '';
                    return e.alert?.category || '';
                }
                case 'Severity': return 'Sev ' + (e.alert?.severity || 0);
                case 'Type': {
                    if (e.event_type === 'dnp3') return e.dnp3?.type || '';
                    if (e.event_type === 'anomaly') return e.anomaly?.type || '';
                    if (e.event_type === 'mdns') return e.mdns?.queries?.[0]?.rrtype || '';
                    // See the 'Query' case above for why both the old flat
                    // field and the new Suricata 8 V3 queries[0] path are
                    // read here.
                    return e.dns?.rrtype || e.dns?.queries?.[0]?.rrtype || '';
                }
                case 'Method': return e.http?.http_method || '';
                case 'Host': return e.http?.hostname || '';
                case 'URL': return e.http?.url || '';
                case 'Status': {
                    if (e.event_type === 'enip') return e.enip?.response?.status || e.enip?.request?.status || '';
                    if (e.event_type === 'pop3') return e.pop3?.response?.status || '';
                    return String(e.http?.status || '');
                }
                case 'User-Agent': return (e.http?.http_user_agent || '').slice(0, CONFIG.USER_AGENT_MAX_LENGTH);
                case 'SNI / Host': return e.tls?.sni || '-';
                case 'Version': {
                    if (e.event_type === 'ntp') return e.ntp?.version !== undefined ? String(e.ntp.version) : '';
                    return e.tls?.version || '-';
                }
                case 'Subject': return (e.tls?.subject || '-').slice(0, CONFIG.TLS_SUBJECT_MAX_LENGTH);
                case 'Issuer': return (e.tls?.issuerdn || '-').slice(0, CONFIG.TLS_SUBJECT_MAX_LENGTH);
                case 'Pkts →': return String(e.flow?.pkts_toserver || 0);
                case 'Pkts ←': return String(e.flow?.pkts_toclient || 0);
                case 'Bytes →': return String(e.flow?.bytes_toserver || 0);
                case 'Bytes ←': return String(e.flow?.bytes_toclient || 0);
                case 'State': return e.flow?.state || '';
                case 'Alerted': return e.flow?.alerted ? 'Yes' : 'No';
                case 'Filename': {
                    if (e.event_type === 'smb') return e.smb?.filename || '';
                    if (e.event_type === 'ftp_data') return e.ftp_data?.filename || '';
                    if (e.event_type === 'nfs') return e.nfs?.filename || '';
                    return e.fileinfo?.filename || '';
                }
                case 'Rule Name': return e.filealerts?.rule_name || '';
                case 'Tags': return (e.filealerts?.tags || []).join(', ');
                case 'Author': return e.filealerts?.author || '';
                case 'Function': {
                    if (e.event_type === 'modbus') return e.modbus?.request?.function_code || '';
                    if (e.event_type === 'dnp3') {
                        return e.dnp3?.application?.function_code !== undefined ? String(e.dnp3.application.function_code) :
                               (e.dnp3?.request?.application?.function_code !== undefined ? String(e.dnp3.request.application.function_code) :
                               (e.dnp3?.response?.application?.function_code !== undefined ? String(e.dnp3.response.application.function_code) : ''));
                    }
                    return '';
                }
                case 'Unit ID': return e.modbus?.request?.unit_id !== undefined ? String(e.modbus.request.unit_id) : '';
                case 'Access Type': return e.modbus?.request?.access_type || '';
                case 'Error Flags': return e.modbus?.request?.error_flags || '';
                case 'Source Addr': return e.dnp3?.src !== undefined ? String(e.dnp3.src) : (e.dnp3?.request?.src !== undefined ? String(e.dnp3.request.src) : '');
                case 'Dest Addr': return e.dnp3?.dst !== undefined ? String(e.dnp3.dst) : (e.dnp3?.request?.dst !== undefined ? String(e.dnp3.request.dst) : '');
                case 'Query': {
                    if (e.event_type === 'pgsql') return e.pgsql?.request?.simple_query || '';
                    if (e.event_type === 'mdns') return e.mdns?.queries?.[0]?.rrname || '';
                    // dns.rrname/rrtype are the pre-Suricata-8 flat shortcut
                    // fields for "the query this transaction is about". As
                    // of Suricata 8's V3 DNS logging format (the new
                    // default - see rust/src/dns/log.rs), those flat fields
                    // are gone entirely and the same info lives at
                    // dns.queries[0].rrname/rrtype instead - confirmed
                    // against real Suricata 8.0.6 output, which silently
                    // rendered every DNS row's Query/Type as empty before
                    // this fix. Falling back to the old flat fields too
                    // keeps any previously-stored Suricata 7 analyses
                    // working.
                    return e.dns?.rrname || e.dns?.queries?.[0]?.rrname || '';
                }
                case 'Command': {
                    if (e.event_type === 'pgsql') return e.pgsql?.response?.command_completed || '';
                    if (e.event_type === 'enip') return e.enip?.request?.command || e.enip?.response?.command || '';
                    if (e.event_type === 'pop3') return e.pop3?.request?.command || '';
                    return e.ftp?.command || '';
                }
                case 'Rows': return e.pgsql?.response?.data_rows !== undefined ? String(e.pgsql.response.data_rows) : '';
                case 'SSL': return e.pgsql?.response?.ssl_accepted !== undefined ? (e.pgsql.response.ssl_accepted ? 'Yes' : 'No') : '';
                case 'SNI': return e.quic?.sni || '';
                case 'QUIC Version': return e.quic?.version || '';
                case 'JA3': return e.quic?.ja3?.hash || '';
                case 'JA3S': return e.quic?.ja3s?.hash || '';
                case 'DHCP Type': return e.dhcp?.dhcp_type || e.dhcp?.type || '';
                case 'Client MAC': return e.dhcp?.client_mac || '';
                case 'Assigned IP': return e.dhcp?.assigned_ip || '';
                case 'Hostname': return e.dhcp?.hostname || '';
                case 'FTP Command': return e.ftp_data?.command || '';
                case 'SMB Command': return e.smb?.command || '';
                case 'Share': return e.smb?.share || '';
                case 'SMB User': return e.smb?.ntlmssp?.user || e.smb?.kerberos?.cname || '';
                case 'Client Version': {
                    if (e.event_type === 'rfb') {
                        const cpv = e.rfb?.client_protocol_version;
                        return cpv ? `${cpv.major}.${cpv.minor}` : '';
                    }
                    return e.ssh?.client?.software_version || '';
                }
                case 'Server Version': {
                    if (e.event_type === 'rfb') {
                        const spv = e.rfb?.server_protocol_version;
                        return spv ? `${spv.major}.${spv.minor}` : '';
                    }
                    return e.ssh?.server?.software_version || '';
                }
                case 'Client': return e.krb5?.cname || '';
                case 'Service': return e.krb5?.sname || '';
                case 'Realm': return e.krb5?.realm || '';
                case 'Error Code': return e.krb5?.error_code || '';
                case 'SIP Method': return e.sip?.method || '';
                case 'URI': return e.sip?.uri || '';
                case 'SIP Code': return String(e.sip?.code || '');
                case 'Reason': return e.sip?.reason || '';
                case 'SNMP Version': return String(e.snmp?.version || '');
                case 'PDU Type': return e.snmp?.pdu_type || '';
                case 'Community': return e.snmp?.community || '';
                case 'MQTT Type': return e.mqtt ? (Object.keys(e.mqtt)[0] || '') : '';
                case 'Topic': {
                    const mqttType = e.mqtt ? Object.keys(e.mqtt)[0] : '';
                    const mqttSub = (mqttType && e.mqtt[mqttType]) || {};
                    return mqttSub.topic || (mqttSub.topics || []).map(t => t.topic || t).join(', ') || '';
                }
                case 'Client ID': {
                    const mqttType = e.mqtt ? Object.keys(e.mqtt)[0] : '';
                    return ((mqttType && e.mqtt[mqttType]) || {}).client_id || '';
                }
                case 'Interface UUID': return (e.dcerpc?.interfaces || [])[0]?.uuid || '';
                case 'Opnum': return String(e.dcerpc?.req?.opnum ?? e.dcerpc?.request?.opnum ?? '');
                case 'Call ID': return String(e.dcerpc?.call_id ?? '');
                case 'RDP Event': return e.rdp?.event_type || '';
                case 'Cookie': return e.rdp?.cookie || '';
                case 'Client Name': return e.rdp?.client_name || '';
                case 'Packet': return e.tftp?.packet || '';
                case 'File': return e.tftp?.file || '';
                case 'Mode': {
                    if (e.event_type === 'ntp') return e.ntp?.mode !== undefined ? String(e.ntp.mode) : '';
                    return e.tftp?.mode || '';
                }
                case 'Exchange Type': return e.ike?.exchange_type || '';
                case 'IKE Version': return e.ike?.version_major !== undefined ? `${e.ike.version_major}.${e.ike.version_minor || 0}` : '';
                case 'Init SPI': return e.ike?.init_spi || '';
                case 'Procedure': return e.nfs?.procedure || '';
                case 'Security Type': return String(e.rfb?.authentication?.security_type ?? '');
                case 'Request Type': return e.bittorrent_dht?.request_type || e.bittorrent_dht?.request?.request_type || '';
                case 'Info Hash': return e.bittorrent_dht?.info_hash || e.bittorrent_dht?.request?.info_hash || '';
                case 'Helo': return e.smtp?.helo || '';
                case 'Mail From': return e.smtp?.mail_from || '';
                case 'Rcpt To': return (e.smtp?.rcpt_to || []).join(', ');
                case 'Command Data': return e.ftp?.command_data || '';
                case 'Completion Code': return (e.ftp?.completion_code || []).join(', ');
                case 'Reply': return (e.ftp?.reply || []).join(' | ');
                case 'Event': return e.anomaly?.event || '';
                case 'Layer': return e.anomaly?.layer || '';
                case 'App Proto': return e.anomaly?.app_proto || '';
                case 'Stratum': return e.ntp?.stratum !== undefined ? String(e.ntp.stratum) : '';
                case 'Reference ID': return e.ntp?.reference_id || '';
                case 'Opcode': {
                    if (e.event_type === 'arp') return e.arp?.opcode || '';
                    return e.websocket?.opcode || '';
                }
                case 'Src MAC': return e.arp?.src_mac || '';
                case 'Dest MAC': return e.arp?.dest_mac || '';
                case 'Fin': return e.websocket?.fin !== undefined ? String(e.websocket.fin) : '';
                case 'Payload': return (e.websocket?.payload_printable || e.websocket?.payload_base64 || '').slice(0, 100);
                case 'Args': return (e.pop3?.request?.args || []).join(' ');
                case 'Operation': return e.ldap?.request?.operation || e.ldap?.responses?.[0]?.operation || '';
                case 'Message ID': {
                    const req = e.ldap?.request;
                    if (req?.message_id !== undefined) return String(req.message_id);
                    const resp = e.ldap?.responses?.[0];
                    return resp?.message_id !== undefined ? String(resp.message_id) : '';
                }
                case 'Result Code': {
                    for (const r of (e.ldap?.responses || [])) {
                        for (const key in r) {
                            if (r[key] && typeof r[key] === 'object' && 'result_code' in r[key]) return r[key].result_code;
                        }
                    }
                    return '';
                }
                case 'Channel': {
                    try { const jd = _parseLogEventJson(e); return jd.Channel || jd.Provider_Name || e.app_proto || ''; } catch(e2) { return e.app_proto || ''; }
                }
                case 'EventID': {
                    try { const jd = _parseLogEventJson(e); return String(jd.EventID || ''); } catch(e2) { return ''; }
                }
                case 'Computer': {
                    try { const jd = _parseLogEventJson(e); return jd.Computer || ''; } catch(e2) { return ''; }
                }
                case 'Detail': {
                    const etype = e.event_type || '';
                    if (etype === 'alert') return e.alert?.signature || '';
                    if (etype === 'dns') return e.dns?.rrname || e.dns?.queries?.[0]?.rrname || '';
                    if (etype === 'mdns') return e.mdns?.queries?.[0]?.rrname || '';
                    if (etype === 'http') return (e.http?.http_method || '') + ' ' + (e.http?.url || '');
                    if (etype === 'tls') return e.tls?.sni || '';
                    if (etype === 'flow') return `${e.src_ip || ''}:${e.src_port || ''} → ${e.dest_ip || ''}:${e.dest_port || ''}`;
                    if (etype === 'ftp') return e.ftp?.command || (e.ftp?.reply || [])[0] || '';
                    // BUGFIX: was e.anomaly?.message, a field that has never
                    // existed in Suricata's eve.json anomaly schema (real
                    // field is 'event', e.g. "APPLAYER_DETECT_PROTOCOL_ONLY_
                    // ONE_DIRECTION") - always silently returned '' before.
                    if (etype === 'anomaly') return e.anomaly?.event || '';
                    if (etype === 'fileinfo') return e.fileinfo?.filename || '';
                    if (etype === 'modbus') return e.modbus?.request?.function_code || '';
                    if (etype === 'dnp3') return e.dnp3?.type || e.dnp3?.request?.type || e.dnp3?.response?.type || '';
                    if (etype === 'pgsql') return e.pgsql?.request?.simple_query || e.pgsql?.response?.command_completed || '';
                    if (etype === 'enip') return e.enip?.request?.command || e.enip?.response?.command || '';
                    if (etype === 'ntp') return e.ntp?.version !== undefined ? `v${e.ntp.version} mode ${e.ntp?.mode ?? ''}` : '';
                    if (etype === 'websocket') return e.websocket?.opcode || '';
                    if (etype === 'pop3') return e.pop3?.request?.command || e.pop3?.response?.status || '';
                    if (etype === 'ldap') return e.ldap?.request?.operation || e.ldap?.responses?.[0]?.operation || '';
                    if (etype === 'arp') return `${e.arp?.opcode || ''} ${e.arp?.src_mac || ''} → ${e.arp?.dest_mac || ''}`.trim();
                    if (etype === 'quic') return e.quic?.sni || '';
                    if (etype === 'dhcp') return `${e.dhcp?.dhcp_type || e.dhcp?.type || ''} ${e.dhcp?.assigned_ip || ''}`.trim();
                    if (etype === 'ftp_data') return `${e.ftp_data?.command || ''} ${e.ftp_data?.filename || ''}`.trim();
                    if (etype === 'smb') return `${e.smb?.command || ''} ${e.smb?.filename || ''}`.trim();
                    if (etype === 'ssh') return e.ssh?.client?.software_version || e.ssh?.server?.software_version || '';
                    if (etype === 'krb5') return `${e.krb5?.cname || ''} → ${e.krb5?.sname || ''}`;
                    if (etype === 'sip') return e.sip?.method ? `${e.sip.method} ${e.sip?.uri || ''}` : `${e.sip?.code || ''} ${e.sip?.reason || ''}`;
                    if (etype === 'snmp') return e.snmp?.pdu_type || '';
                    if (etype === 'mqtt') return e.mqtt ? (Object.keys(e.mqtt)[0] || '') : '';
                    if (etype === 'dcerpc') return (e.dcerpc?.interfaces || [])[0]?.uuid || '';
                    if (etype === 'rdp') return e.rdp?.event_type || '';
                    if (etype === 'tftp') return `${e.tftp?.packet || ''} ${e.tftp?.file || ''}`.trim();
                    if (etype === 'ike') return e.ike?.exchange_type || '';
                    if (etype === 'nfs') return `${e.nfs?.procedure || ''} ${e.nfs?.filename || ''}`.trim();
                    if (etype === 'rfb') return e.rfb?.authentication?.security_type ?? '';
                    if (etype === 'bittorrent_dht') return e.bittorrent_dht?.request_type || e.bittorrent_dht?.request?.request_type || '';
                    if (etype === 'smtp') return e.smtp?.mail_from || '';
                    if (etype === 'log') {
                        try {
                            const jd = _parseLogEventJson(e);
                            return getLogEventSmartDetail(jd);
                        } catch(e2) { return ''; }
                    }
                    return '';
                }
                default: {
                    // Generic fallback for log analysis dynamic columns
                    const field = _getFieldForLabel(col);
                    if (field) {
                        const v = getLogColumnValue(e, field);
                        if (v !== '') return v;
                    }
                    return '';
                }
            }
        }
        
        function buildAggregationTables(events, eventType) {
            return buildAggregationTablesCore(events, getColumnsForType(eventType), 'section-' + eventType, extractValue);
        }
        
        let allEvents = [];
        let baseAllEvents = [];
        // Tracks which eventTypes' currently-cached tabDataCache/allEvents data is
        // known to be a partial (capped) result - i.e. the real total exceeds
        // getUserQueryLimit()'s current value. Cleared whenever those caches
        // themselves are reset (new file load, search change).
        // NOTE: must stay `var` (not let/const) so it attaches to the global
        // object - the JSDOM test harness assigns/reads it via separate
        // script evaluations, same reason as currentFilters/advancedMode below.
        var truncatedTypes = new Set();
        let eventTypes = [];
        let currentMd5 = '';
        let currentFileName = '';
        // NOTE: these must stay `var` (not let/const) so they attach to the
        // global object — the JSDOM test harness and inline handlers assign
        // them via separate script evaluations.
        var currentFilters = {};
        let currentSearch = [];
        var advancedMode = false;
        let diagramMode = true;

        // Pagination/sort state for the currently-visible data table. A single
        // set (not per-tab) is sufficient because loadTabData always fully
        // rebuilds whichever one section is visible at a time.
        let currentPage = 1;
        let currentSort = null;       // { sectionKey, colIndex, asc } | null
        let activeTableRender = null; // { sectionKey, rerender } - set each render

        function resetPagination() {
            currentPage = 1;
            currentSort = null;
        }

        // Whether the row table for the current view can be fetched a page at
        // a time directly from the server (arbitrarily large datasets), rather
        // than needing the whole filtered/sorted array in memory. Only true
        // when there's no active column filter and no active client-side sort
        // - both require the full array to be correct, since neither is
        // supported server-side yet.
        function canUseScalableFetch() {
            return Object.keys(currentFilters).length === 0 && currentSort === null;
        }

        // Guards against out-of-order async renders (tab switched, or
        // Prev/Next/sort clicked again, while a previous fetch is in flight).
        // Every scalable-mode fetch captures the generation at call time and
        // checks it's still current immediately before touching the DOM.
        let fetchGeneration = 0;
        function bumpFetchGeneration() { return ++fetchGeneration; }
        function isStaleFetch(gen) { return gen !== fetchGeneration; }

        // Fetches exactly one page (CONFIG.TABLE_PAGE_SIZE rows) of a per-type
        // or merged "all events" table directly from the server, plus the true
        // total via /api/count - both already support offset/limit and q.
        // eventType null/'all' -> merged multi-type query (no &type= param).
        async function fetchEventsPage(eventType) {
            const gen = bumpFetchGeneration();
            const qParam = buildSearchQuery();
            const typeParam = (eventType && eventType !== 'all') ? `&type=${eventType}` : '';
            const offset = (currentPage - 1) * CONFIG.TABLE_PAGE_SIZE;
            const sortParam = (currentSort && currentSort.sectionKey === `section-${eventType}` && canServerSortEventType(eventType))
                ? `&order_by=${encodeURIComponent(getColumnsForType(eventType)[currentSort.colIndex])}&sort_dir=${currentSort.asc ? 'asc' : 'desc'}`
                : '';
            const [rowsResp, countResp] = await Promise.all([
                fetch(`/api/events?md5=${currentMd5}${typeParam}&offset=${offset}&limit=${CONFIG.TABLE_PAGE_SIZE}${qParam}${sortParam}&t=${Date.now()}`),
                fetch(`/api/count?md5=${currentMd5}${typeParam}${qParam}&t=${Date.now()}`)
            ]);
            const items = await rowsResp.json();
            const { count } = await countResp.json();
            return { items, serverTotal: count, gen };
        }

        async function fetchSigmaAlertsPage() {
            const gen = bumpFetchGeneration();
            const qParam = buildSearchQuery();
            const offset = (currentPage - 1) * CONFIG.TABLE_PAGE_SIZE;
            const [rowsResp, countResp] = await Promise.all([
                fetch(`/api/sigma-alerts?md5=${currentMd5}&offset=${offset}&limit=${CONFIG.TABLE_PAGE_SIZE}${qParam}&t=${Date.now()}`),
                fetch(`/api/sigma-count?md5=${currentMd5}${qParam}&t=${Date.now()}`)
            ]);
            const items = await rowsResp.json();
            const { count } = await countResp.json();
            return { items, serverTotal: count, gen };
        }

        // Fetches an already-aggregated {nodes, links} Sankey payload (top-N
        // per column + Other bucketing computed server-side), so the diagram
        // can stay visible by default without needing the full capped batch.
        async function fetchSankeyData(eventType) {
            const qParam = buildSearchQuery();
            const typeParam = (eventType && eventType !== 'all') ? `&type=${eventType}` : '';
            const resp = await fetch(`/api/sankey-data?md5=${currentMd5}${typeParam}${qParam}&t=${Date.now()}`);
            return await resp.json();
        }

        // Whether the Sankey diagram can use the lightweight server-aggregated
        // fetch above instead of needing the full capped batch - only true
        // when there's no active column filter (search is already reflected
        // server-side). Deliberately not canUseScalableFetch(), which also
        // checks currentSort - sort has no bearing on the diagram.
        function canUseServerSankey(eventType) {
            return !!eventType && eventType !== 'sigmaalert' && eventType !== 'log'
                && Object.keys(currentFilters).length === 0;
        }

        // Whether the aggregation tables (the "advanced" per-column top-10
        // view) can be computed server-side via /api/aggregation-data
        // instead of needing the full capped batch. True for the 10 pcap
        // per-type tabs (sharing the generic buildAggregationTablesCore
        // /extractValue code path) plus the merged 'all' view (its 'Type'/
        // 'Detail' columns now have SQL equivalents too - db.py's
        // _all_events_detail_expr/UPPER(event_type)). sigmaalert/log stay
        // excluded (MITRE-Technique array-parse / entire column set being
        // data-dependent/untrusted, respectively) - and only when there's no
        // active column filter (the server endpoint is read-only/unfiltered).
        function canUseServerAggregation(eventType) {
            // 'mqtt'/'ldap' are excluded alongside sigmaalert/log/binary:
            // their fields are dynamically keyed by message/operation
            // subtype (connect/publish/subscribe/... for mqtt;
            // bind_request/search_request/modify_request/... for ldap),
            // which has no static JSON path representation server-side
            // (see db.py's AGGREGATION_JSON_PATHS) - falling back to
            // client-side computation here, like log/sigmaalert already do,
            // instead of hitting an always-empty server result.
            return !!eventType && eventType !== 'sigmaalert'
                && eventType !== 'log' && eventType !== 'binary'
                && eventType !== 'mqtt' && eventType !== 'ldap'
                && Object.keys(currentFilters).length === 0;
        }

        // Whether column-header sort can be performed server-side (via
        // /api/events' order_by/sort_dir params) for eventType. Same scope
        // as canUseServerAggregation - every column of the 10 pcap per-type
        // tabs plus the merged 'all' view now has a safe SQL expression via
        // db.py's _sort_expr (reusing the exact same mapping
        // /api/aggregation-data uses). sigmaalert/log/binary each have at
        // least one column with no server-side equivalent (sigmaalert's
        // MITRE-Technique array-parse, log's entire column set being
        // data-dependent/untrusted, binary having no scalable path at all),
        // so they keep the existing full-batch-then-client-sort fallback.
        function canServerSortEventType(eventType) {
            // 'mqtt'/'ldap' excluded for the same reason as
            // canUseServerAggregation: their column-specific fields have no
            // static JSON path server-side, so _sort_expr() returns None for
            // anything but 'Time' - fall back to full client-side sort,
            // which handles every column correctly.
            return !!eventType && eventType !== 'sigmaalert'
                && eventType !== 'log' && eventType !== 'binary'
                && eventType !== 'mqtt' && eventType !== 'ldap';
        }

        // Whether buildSection's scalable (per-page) fetch remains valid
        // given the CURRENT currentFilters/currentSort state - true when
        // unfiltered and either no sort is active, or the active sort is one
        // the server can perform for this eventType.
        function canUseScalableFetchForSort(eventType) {
            return Object.keys(currentFilters).length === 0
                && (currentSort === null || canServerSortEventType(eventType));
        }

        async function fetchAggregationData(eventType) {
            const qParam = buildSearchQuery();
            const typeParam = (eventType && eventType !== 'all') ? `&type=${eventType}` : '';
            const resp = await fetch(`/api/aggregation-data?md5=${currentMd5}${typeParam}${qParam}&t=${Date.now()}`);
            return await resp.json();
        }

        // Whether the (still fully client-side, for log/sigmaalert/binary/'all')
        // aggregation tables and/or the Sankey diagram need the full capped
        // batch loaded, independent of whatever mode the row table itself is
        // using.
        function needsFullBatch(eventType) {
            // The aggregation view only needs the full batch when it can't use
            // the lightweight server-aggregated fetch - i.e. for log/sigmaalert
            // (bespoke dynamic columns) or when a column filter is active
            // (canUseServerAggregation mirrors this same condition).
            if (advancedMode && (eventType === 'sigmaalert' || eventType === 'log'
                || !canUseServerAggregation(eventType))) return true;
            // The diagram only needs the full batch when it can't use the
            // lightweight server-aggregated fetch - i.e. when a column filter
            // is active (canUseServerSankey mirrors this same condition).
            if (eventType !== 'sigmaalert' && eventType !== 'log' && diagramMode
                && Object.keys(currentFilters).length > 0) return true;
            return false;
        }

        // Ensures tabDataCache[eventType] (or allEvents for 'all') is
        // populated, fetching at today's existing capped limit if not already
        // cached. No-op if already cached - safe to call redundantly. This is
        // the one fetch that feeds aggregation tables/Sankey (unchanged from
        // today) and is also what a mode transition into filtered/sorted
        // fallback rendering needs before it can render correctly.
        async function ensureCappedBatch(eventType) {
            const qParam = buildSearchQuery();
            if (eventType === 'all') {
                if (allEvents.length > 0) return;
                const [resp, countResp] = await Promise.all([
                    fetch(`/api/events?md5=${currentMd5}&limit=${getUserQueryLimit()}${qParam}&t=${Date.now()}`),
                    fetch(`/api/count?md5=${currentMd5}${qParam}&t=${Date.now()}`)
                ]);
                allEvents = await resp.json();
                const { count } = await countResp.json();
                if (allEvents.length < count) truncatedTypes.add('all'); else truncatedTypes.delete('all');
                return;
            }
            if (tabDataCache[eventType]) return;
            const limit = getUserQueryLimit();
            const endpoint = eventType === 'sigmaalert' ? '/api/sigma-alerts' : '/api/events';
            const countEndpoint = eventType === 'sigmaalert' ? '/api/sigma-count' : '/api/count';
            const typeParam = eventType === 'sigmaalert' ? '' : `&type=${eventType}`;
            const [resp, countResp] = await Promise.all([
                fetch(`${endpoint}?md5=${currentMd5}${typeParam}&limit=${limit}${qParam}&t=${Date.now()}`),
                fetch(`${countEndpoint}?md5=${currentMd5}${typeParam}${qParam}&t=${Date.now()}`)
            ]);
            tabDataCache[eventType] = await resp.json();
            const { count } = await countResp.json();
            if (tabDataCache[eventType].length < count) truncatedTypes.add(eventType); else truncatedTypes.delete(eventType);
        }

        // Fetches only the two event types binary-file analysis ever produces
        // (fileinfo: exactly one row, guaranteed by create_file_analysis_db's
        // insert-once call in db.py; filealerts: one row per YARA match) in
        // parallel, instead of every event type via ensureCappedBatch('all').
        // Binary-mode databases (routed here only when detectedType ===
        // 'binary') never contain any other event type, so this is a strict
        // narrowing with no fallback-loss risk.
        async function fetchBinaryEvents(qParam) {
            const q = qParam || '';
            const [fileAlertsResp, fileInfoResp] = await Promise.all([
                fetch(`/api/events?md5=${currentMd5}&type=filealerts&limit=${getUserQueryLimit()}${q}&t=${Date.now()}`),
                fetch(`/api/events?md5=${currentMd5}&type=fileinfo&limit=1${q}&t=${Date.now()}`)
            ]);
            const [fileAlerts, fileInfo] = await Promise.all([fileAlertsResp.json(), fileInfoResp.json()]);
            return [...fileInfo, ...fileAlerts];
        }

        // Cache-aware wrapper mirroring ensureCappedBatch('all')'s "no-op if
        // already populated" contract, for call sites (initial load,
        // applyFilters, clearFilter) that want to reuse an already-fetched
        // allEvents instead of forcing a fresh fetch on every column-filter
        // change.
        async function ensureBinaryEventsBatch() {
            if (allEvents.length > 0) return;
            allEvents = await fetchBinaryEvents(buildSearchQuery());
        }

        var hiddenAggregations = new Set();
        let baseEventStats = {};
        var isLogAnalysisMode = false;
        const ALL_EVENTS_COLUMNS = ['Time', 'Type', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Detail'];

        // Columns whose content is short and structurally identical across every
        // table (pcap per-type, All Events, Sigma Alerts). Fixed widths keep them
        // the same size everywhere, regardless of how many other columns a given
        // table has - table-layout:fixed otherwise splits width evenly by column
        // count alone, so the same field ends up a different width per tab.
        const FIXED_COLUMN_WIDTHS = {
            'Time': '170px',
            'Type': '130px',
            'Protocol': '110px',
            'Source IP': '150px',
            'Dest IP': '150px',
            'Source Port': '120px',
            'Dest Port': '120px',
            'Severity': '150px',
        };

        function tableHeaderCellsHtml(columns, sectionKey) {
            return columns.map((h, i) => {
                const w = FIXED_COLUMN_WIDTHS[h];
                const styleAttr = w ? ` style="width:${w}"` : '';
                let cls = '', arrow = '';
                if (sectionKey && currentSort && currentSort.sectionKey === sectionKey && currentSort.colIndex === i) {
                    cls = ` class="${currentSort.asc ? 'sort-asc' : 'sort-desc'}"`;
                    arrow = `<span class="sort-arrow">${currentSort.asc ? '▲' : '▼'}</span>`;
                }
                return `<th${styleAttr}${cls}>${escapeHtml(h)}${arrow}</th>`;
            }).join('');
        }

        // Sorts a copy of `items` by columns[colIndex], reusing the caller's
        // existing (label, colIndex) => value extractor. Numeric-aware, same
        // rule the old DOM-based sortTable used.
        function sortItemsByColumn(items, columns, extractFn, colIndex, asc) {
            const col = columns[colIndex];
            return [...items].sort((a, b) => {
                const aStr = String(extractFn(a, col, colIndex) ?? '').trim();
                const bStr = String(extractFn(b, col, colIndex) ?? '').trim();
                if (aStr !== '' && bStr !== '' && !isNaN(aStr) && !isNaN(bStr)) {
                    return asc ? parseFloat(aStr) - parseFloat(bStr) : parseFloat(bStr) - parseFloat(aStr);
                }
                return asc ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
            });
        }

        // Shared paginated-table renderer used by every data table (per-type
        // pcap tables, All Events, Sigma Alerts, Binary/YARA, Log Events).
        // `items` is the full already-filtered array for the current tab (not
        // yet sliced to a page). `rowRenderer` maps one item to its row HTML.
        // `rerender` re-invokes the exact call that produced `items`, so
        // Prev/Next and column-sort clicks know how to redraw.
        function renderPaginatedTable({ sectionKey, columns, items, extractFn, rowRenderer, rerender, serverTotal }) {
            activeTableRender = { sectionKey, rerender };

            let sortedItems = null, totalItems;
            if (serverTotal !== undefined) {
                // Scalable mode: `items` is already exactly one page, fetched
                // and ordered by the server - no local sort/slice needed.
                totalItems = serverTotal;
            } else {
                sortedItems = items;
                if (currentSort && currentSort.sectionKey === sectionKey) {
                    sortedItems = sortItemsByColumn(items, columns, extractFn, currentSort.colIndex, currentSort.asc);
                }
                totalItems = sortedItems.length;
            }

            const totalPages = Math.max(1, Math.ceil(totalItems / CONFIG.TABLE_PAGE_SIZE));
            currentPage = Math.min(Math.max(currentPage, 1), totalPages);
            const start = (currentPage - 1) * CONFIG.TABLE_PAGE_SIZE;
            const pageItems = sortedItems === null ? items : sortedItems.slice(start, start + CONFIG.TABLE_PAGE_SIZE);

            let html = '<div class="table-scroll-wrapper"><table><thead><tr>';
            html += tableHeaderCellsHtml(columns, sectionKey);
            html += '</tr></thead><tbody>';
            pageItems.forEach(item => { html += rowRenderer(item); });
            html += '</tbody></table></div>';
            html += buildPaginationControlsHtml(totalItems, start, pageItems.length, totalPages);

            return html;
        }

        function buildPaginationControlsHtml(totalItems, start, pageCount, totalPages) {
            if (totalItems <= CONFIG.TABLE_PAGE_SIZE) return '';
            const end = start + pageCount;
            return `<div class="pagination-bar">
                <span class="pagination-info">Showing ${start + 1}-${end} of ${totalItems}</span>
                <div class="pagination-controls">
                    <button class="pagination-btn" onclick="changeTablePage(-1)" ${currentPage <= 1 ? 'disabled' : ''}>&larr; Prev</button>
                    <span class="pagination-page">Page
                        <input type="number" id="paginationPageInput" class="pagination-page-input" min="1" max="${totalPages}" value="${currentPage}" onkeydown="if(event.key==='Enter'){jumpToPage()}">
                        of ${totalPages}
                    </span>
                    <button class="pagination-btn" onclick="jumpToPage()">Go</button>
                    <button class="pagination-btn" onclick="changeTablePage(1)" ${currentPage >= totalPages ? 'disabled' : ''}>Next &rarr;</button>
                </div>
            </div>`;
        }

        async function jumpToPage() {
            if (!activeTableRender) return;
            const input = document.getElementById('paginationPageInput');
            if (!input) return;
            const page = parseInt(input.value, 10);
            if (!isNaN(page)) {
                currentPage = page; // renderPaginatedTable clamps to the valid [1, totalPages] range
                await activeTableRender.rerender();
            } else {
                input.value = currentPage;
            }
        }

        async function changeTablePage(delta) {
            if (!activeTableRender) return;
            currentPage += delta;
            await activeTableRender.rerender();
        }

        // For the 10 pcap per-type tabs (canServerSortEventType), sort is
        // performed server-side - fetchEventsPage picks up the new
        // currentSort and re-fetches just one page in the new order, so no
        // full-batch fetch is needed here. For everything else ('all',
        // sigmaalert, log, binary), clicking a column header while in
        // scalable mode must first fetch the full capped batch (a no-op if
        // already cached for aggregations/Sankey) before currentSort takes
        // effect - canUseScalableFetch() becomes false the moment it's set,
        // so the next rerender() naturally takes the fallback (full-batch,
        // client-side sort) path through the same top-level build function.
        async function sortCurrentTable(colIndex) {
            if (!activeTableRender) return;
            const { sectionKey } = activeTableRender;
            const eventType = sectionKey.replace('section-', '');
            bumpFetchGeneration();
            if (!(Object.keys(currentFilters).length === 0 && canServerSortEventType(eventType))) {
                await ensureCappedBatch(eventType);
            }
            const sameCol = currentSort && currentSort.sectionKey === sectionKey && currentSort.colIndex === colIndex;
            currentSort = { sectionKey, colIndex, asc: sameCol ? !currentSort.asc : true };
            currentPage = 1;
            await activeTableRender.rerender();
            updateFilterBarVisibility();
        }

        const EMPTY_FILTER_STATE_HTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;">${SEARCH_ICON_SVG} No events match the current filters</div>`;
        const AGG_COLLAPSED_HTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▸ Aggregation Tables</div></div>';

        function hideAggregationTable(sectionId, col) {
            hiddenAggregations.add(sectionId + ':' + col);
            // col can contain quotes (attacker-controlled log field names), so
            // compare attributes directly instead of building a CSS selector.
            document.querySelectorAll('.agg-section').forEach(el => {
                if (el.getAttribute('data-col') === col) {
                    el.style.display = 'none';
                }
            });
            const anyVisible = document.querySelectorAll('.agg-section:not([style*="display: none"])').length > 0;
            if (!anyVisible) {
                advancedMode = false;
                const aggContainer = document.getElementById('aggregations');
                if (aggContainer) {
                    aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                }
            }
        }

        function getColumnNameFromSankeyColumn(col) {
            return ['Source IP', 'Dest IP', 'Dest Port'][col] || '';
        }

        async function refreshCurrentView(sectionId, eventType) {
            if (isLogAnalysisMode && eventType === 'log') {
                const events = tabDataCache['log'] || [];
                const filtered = getFilteredLogEvents(events);
                if (advancedMode) buildLogAggregations(filtered, sectionId);
                buildLogSectionContent(sectionId, filtered);
                return;
            }
            if (isLogAnalysisMode && eventType === 'sigmaalert') {
                const alerts = tabDataCache['sigmaalert'] || [];
                const filtered = getFilteredSigmaAlerts(alerts);
                if (advancedMode) buildSigmaAlertAggregations(filtered, sectionId);
                buildSigmaAlertSectionContent(sectionId, filtered);
                return;
            }
            if (eventType === 'all') {
                if (advancedMode) await buildAggregationsSectionAll();
                buildAllEvents();
                return;
            }
            const events = tabDataCache[eventType] || [];
            const filtered = getFilteredEvents(sectionId, events, eventType);
            if (advancedMode) {
                await buildAggregationsSection(eventType, filtered);
            }
            buildSection(eventType, events);
        }

        async function applyFilters(sectionId, filters) {
            resetPagination();
            for (const f of filters) {
                currentFilters[f.column] = f.value;
            }
            if (sectionId === 'section-binary') {
                await ensureBinaryEventsBatch();
                buildBinaryAnalysisView(allEvents);
                updateFilterBarVisibility();
                return;
            }
            const eventType = sectionId.replace('section-', '');
            bumpFetchGeneration();
            await ensureCappedBatch(eventType);
            await refreshCurrentView(sectionId, eventType);
            updateFilterBarVisibility();
            buildStats(await computeFilteredStats());
            await updateSankeyDiagram();
        }

        async function clearFilter(columnName) {
            resetPagination();
            delete currentFilters[columnName];
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            if (!visibleSection) {
                // Binary analysis mode
                await ensureBinaryEventsBatch();
                buildBinaryAnalysisView(allEvents);
                updateFilterBarVisibility();
                return;
            }
            const eventType = visibleSection.id.replace('section-', '');
            await refreshCurrentView(visibleSection.id, eventType);
            updateFilterBarVisibility();
            buildStats(await computeFilteredStats());
            await updateSankeyDiagram();
        }

        function applyFilter(sectionId, columnName, value) {
            applyFilters(sectionId, [{column: columnName, value: value}]);
        }

        async function clearAllFilters() {
            resetPagination();
            currentFilters = {};
            currentSearch = [];
            const input = document.getElementById('searchInput');
            if (input) input.value = '';
            updateFilterBarVisibility();
            await refreshAnalysisData();
        }
        
        function getFilteredEvents(sectionId, events, eventType) {
            if (Object.keys(currentFilters).length === 0) return events;

            if (eventType === 'all') {
                const allColumns = ALL_EVENTS_COLUMNS;
                return events.filter(e => matchesCurrentFilters(e, (ev, col) => extractAllValue(ev, col, allColumns.indexOf(col))));
            }

            const columns = getColumnsForType(eventType);
            return events.filter(e => matchesCurrentFilters(e, (ev, col) => extractValue(ev, col, columns.indexOf(col))));
        }
        
        async function performSearch() {
            const input = document.getElementById('searchInput');
            const text = input ? input.value.trim() : '';
            if (!text) return;

            resetPagination();
            const terms = text.match(/"[^"]+"|\S+/g) || [];
            for (const t of terms) {
                const term = t.replace(/^"|"$/g, '').trim();
                if (term && !currentSearch.includes(term)) {
                    currentSearch.push(term);
                }
            }

            if (input) input.value = '';
            updateFilterBarVisibility();
            await refreshAnalysisData();
        }

        async function clearSearchTerm(index) {
            resetPagination();
            currentSearch.splice(index, 1);
            updateFilterBarVisibility();
            await refreshAnalysisData();
        }

        // Fetch cheap log-event + sigma-alert *counts* in parallel, optionally
        // filtered by the current search terms. Deliberately does NOT fetch the
        // full arrays - _renderLogAnalysisView only needs counts to build the
        // stat cards and pick the default tab; the actual per-tab data is
        // fetched lazily, on-demand, by loadTabData when a tab is visited
        // (ensureCappedBatch('log') / buildSigmaAlertSectionContent's own
        // scalable fetch).
        async function _fetchLogAnalysisCounts(qParam) {
            const [logResp, sigmaResp] = await Promise.all([
                fetch(`/api/count?md5=${currentMd5}&type=log${qParam || ''}&t=${Date.now()}`),
                fetch(`/api/sigma-count?md5=${currentMd5}${qParam || ''}&t=${Date.now()}`)
            ]);
            const { count: logCount } = await logResp.json();
            const { count: sigmaCount } = await sigmaResp.json();
            return { log: logCount, sigmaalert: sigmaCount };
        }

        // Shared log-analysis view setup: records the (cheap) counts, builds
        // stat cards + sections, then loads the default tab. Deliberately does
        // NOT populate tabDataCache['log']/['sigmaalert'] - loadTabData
        // (defaultType) below does that lazily itself, and the non-default
        // tab's data is left uncached until (if ever) the user switches to it
        // via showTab().
        // Callers must set baseEventStats first (baseline or same-as-filtered).
        async function _renderLogAnalysisView(counts) {
            eventStats = counts;

            eventTypes = sortEventTypes(Object.keys(baseEventStats));
            buildStats(await computeFilteredStats());
            buildSections();

            const defaultType = counts.sigmaalert > 0 ? 'sigmaalert' : 'log';
            document.querySelectorAll('.section').forEach(s => s.classList.add('section-hidden'));
            const defaultSection = document.getElementById('section-' + defaultType);
            if (defaultSection) defaultSection.classList.remove('section-hidden');
            await loadTabData(defaultType, null);

            // loadTabData already builds the aggregation table itself when
            // advancedMode is true (for whichever type is defaultType) - the
            // only case it doesn't handle is collapsing the panel when
            // advancedMode is false.
            const aggContainer = document.getElementById('aggregations');
            if (aggContainer && !advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
            }
        }

        async function refreshAnalysisData() {
            if (!currentMd5) return;
            const gen = bumpFetchGeneration();
            showLoading(currentSearch.length > 0 ? 'Searching...' : 'Loading events...');

            try {
                const qParam = buildSearchQuery();

                const [statsResp, baseStatsResp] = await Promise.all([
                    fetch('/api/stats?md5=' + currentMd5 + qParam + '&t=' + Date.now()),
                    fetch('/api/stats?md5=' + currentMd5 + '&t=' + Date.now())
                ]);
                const statsCounts = (await statsResp.json()).counts;
                const baseStatsCounts = (await baseStatsResp.json()).counts;
                if (isStaleFetch(gen)) return;
                eventStats = statsCounts;
                baseEventStats = baseStatsCounts;

                const types = sortEventTypes(Object.keys(baseEventStats).filter(t => t !== 'stats' && t !== 'all'));
                eventTypes = types;

                // Invalidate any previously-cached full batch - the search
                // state just changed, so a stale array must not satisfy
                // ensureCappedBatch's cache guard. Whichever branch below
                // actually needs allEvents (binary mode, or stats when a
                // column filter is active) fetches it lazily on demand.
                allEvents = [];
                baseAllEvents = [];
                truncatedTypes.clear();

                // Use existing file-analysis class set during initial load
                const isFileOnly = document.body.classList.contains('file-analysis');
                const isLogFile = isLogAnalysisMode;

                if (isFileOnly) {
                document.querySelectorAll('.file-info-card').forEach(c => c.remove());
                document.getElementById('sections').innerHTML = '';
                tabDataCache = {};

                if (isLogFile) {
                    isLogAnalysisMode = true;

                    try {
                        // Fetch unfiltered baseline counts for totals
                        const baseCounts = await _fetchLogAnalysisCounts('');
                        baseEventStats = baseCounts;

                        // Fetch filtered counts if search is active
                        let counts = baseCounts;
                        if (qParam) {
                            counts = await _fetchLogAnalysisCounts(qParam);
                        }
                        await _renderLogAnalysisView(counts);
                    } catch(e) {
                        console.error('Failed to load log analysis:', e);
                        document.getElementById('sections').innerHTML = '<div class="log-events-section"><h3>📋 Log Events</h3><div class="no-matches">Error loading log events</div></div>';
                    }
                } else {
                    // Binary file analysis: unified view with search + aggregations + file info + YARA table
                    const statsGrid = document.getElementById('statsGrid');
                    if (statsGrid) {
                        statsGrid.innerHTML = '';
                        statsGrid.style.display = 'none';
                    }
                    // Keep file info visible even when the current search filter
                    // excludes the fileinfo event by using unfiltered events.
                    allEvents = await fetchBinaryEvents(qParam);
                    let baseEvents = allEvents;
                    if (qParam) {
                        baseEvents = await fetchBinaryEvents('');
                    }
                    baseAllEvents = baseEvents;
                    buildBinaryAnalysisView(allEvents, baseEvents);
                }
            } else {
                document.body.classList.remove('file-analysis');
                isLogAnalysisMode = false;
                const statsGrid = document.getElementById('statsGrid');
                if (statsGrid) statsGrid.style.display = '';
                buildStats(await computeFilteredStats());
                
                // Remember active section before rebuild
                const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
                const activeType = visibleSection ? visibleSection.id.replace('section-', '') : '';

                document.getElementById('sections').innerHTML = '';
                tabDataCache = {};
                buildSections();

                // Restore active section after rebuild
                if (activeType && activeType !== eventTypes[0]) {
                    document.querySelectorAll('.section').forEach(s => s.classList.add('section-hidden'));
                    const sectionEl = document.getElementById('section-' + activeType);
                    if (sectionEl) {
                        sectionEl.classList.remove('section-hidden');
                        await loadTabData(activeType, null);
                    }
                } else if (eventTypes[0]) {
                    await loadTabData(eventTypes[0], null);
                }
            }

            updateFilterBarVisibility();
            hideLoading();
            } catch(err) {
                console.error('refreshAnalysisData error:', err);
                hideLoading();
                showError('Failed to load data: ' + (err.message || 'Unknown error'));
            }
        }

        async function loadAnalysis(md5) {
            const gen = bumpFetchGeneration();
            try {
                const resp = await fetch('/api/load-analysis?md5=' + md5);
                const result = await resp.json();
                if (isStaleFetch(gen)) return;

                if (result.error) {
                    showError(result.error);
                    await showWelcome();
                    return;
                }

                if (result.success) {
                    currentMd5 = md5;
                    currentFileName = result.file_name || md5;
                    document.title = 'SO-CRATES - ' + currentFileName;
                    const urlParams = new URLSearchParams(window.location.search);
                    urlParams.set('file', md5);
                    const newUrl = window.location.pathname + '?' + urlParams.toString();
                    if (window.location.href !== window.location.origin + newUrl) {
                        history.replaceState({}, '', newUrl);
                    }
                    
                    allEvents = [];
                    baseAllEvents = [];
                    truncatedTypes.clear();
                    eventTypes = [];
                    currentFilters = {};
                    currentSearch = [];
                    resetPagination();
                    hiddenAggregations = new Set();
                    tabDataCache = {};
                    clearAnalysisContainers();
                    document.getElementById('searchInput').value = '';
                    
                    showLoading('Loading events...');
                    
                    const statsResp = await fetch('/api/stats?md5=' + md5 + '&t=' + Date.now());
                    const statsData = await statsResp.json();
                    if (isStaleFetch(gen)) return;
                    eventStats = statsData.counts;
                    baseEventStats = {...eventStats};

                    const types = sortEventTypes(Object.keys(baseEventStats).filter(t => t !== 'stats' && t !== 'all'));
                    // eventTypes should not include 'all' - it's added separately by buildStats()
                    eventTypes = types;

                    const { min: rangeMin, max: rangeMax } = statsData.date_range;
                    const dateDisplay = rangeMin && rangeMin === rangeMax
                        ? rangeMin.slice(0, 19)
                        : `${rangeMin?.slice(0, 19) || ''} to ${rangeMax?.slice(0, 19) || ''}`;

                    // Fetch analysis metadata for routing (supports ZIP uploads)
                    const statusResp = await fetch('/api/status?md5=' + md5 + '&t=' + Date.now());
                    const analysisStatus = await statusResp.json();
                    const detectedType = analysisStatus.meta?.detected_type || detectFileType(currentFileName);
                    
                    // Update filename to extracted inner name if available
                    if (analysisStatus.meta?.extracted) {
                        currentFileName = analysisStatus.meta.extracted;
                    }
                    
                    const isPcap = detectedType === 'pcap';
                    const isLogFile = detectedType === 'log';
                    const isFileOnly = !isPcap;
                    
                    if (isFileOnly) {
                        document.body.classList.add('file-analysis');
                    } else {
                        document.body.classList.remove('file-analysis');
                    }
                    
                    document.getElementById('appHeaderFilename').innerHTML = `${FILE_ICON_SVG}${escapeHtml(currentFileName)}`;
                    document.getElementById('appHeaderMeta').innerHTML = `
                        <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap;">${FOLDER_ICON_SVG}${escapeHtml(currentMd5)}</span>
                        <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap;">${CALENDAR_ICON_SVG}${escapeHtml(dateDisplay)}</span>
                    `;
                    document.getElementById('appHeaderRight').innerHTML = renderGearMenu();
                    updateThemeMenu();
                    showAnalysisUI();
                    updateFilterBarVisibility();
                    
                    if (isFileOnly) {
                        document.getElementById('sections').innerHTML = '';
                        const statsGrid = document.getElementById('statsGrid');
                        if (statsGrid) {
                            statsGrid.innerHTML = '';
                            statsGrid.style.display = 'none';
                        }
                        tabDataCache = {};

                        if (isLogFile) {
                            isLogAnalysisMode = true;
                            const statsGrid = document.getElementById('statsGrid');
                            if (statsGrid) statsGrid.style.display = '';
        
                            (async () => {
                                try {
                                    const counts = await _fetchLogAnalysisCounts('');
                                    baseEventStats = counts;
                                    await _renderLogAnalysisView(counts);
                                } catch(e) {
                                    console.error('Failed to load log analysis:', e);
                                    document.getElementById('sections').innerHTML = '<div class="log-events-section"><h3>📋 Log Events</h3><div class="no-matches">Error loading log events</div></div>';
                                }
                            })();
                        } else {
                            // Binary file analysis: unified view with search + aggregations + file info + YARA table
                            await ensureBinaryEventsBatch();
                            baseAllEvents = allEvents;
                            buildBinaryAnalysisView(allEvents);
                        }
                    } else {

                        isLogAnalysisMode = false;
                        // currentFilters was just reset to {} above, so this is
                        // guaranteed to take computeFilteredStats' fast,
                        // fetch-free eventStats path (not ensureCappedBatch).
                        buildStats(await computeFilteredStats());
                        // PCAP analysis: full layout
                        buildSections();
                        const sankeyPanel = document.getElementById('sankeyPanel');
                        if (sankeyPanel) sankeyPanel.style.display = '';
                        if (eventTypes[0]) {
                            // Must be awaited: loadTabData's own fetchEventsPage call
                            // captures the shared fetchGeneration counter, and the
                            // updateSankeyDiagram() call below also bumps it - firing
                            // loadTabData without awaiting it left the two racing,
                            // silently dropping the row table's render (stuck on
                            // "Loading..."). loadTabData already ends by updating the
                            // Sankey diagram itself for this type, so no separate call
                            // is needed here in this branch.
                            await loadTabData(eventTypes[0]);
                        } else if (sankeyPanel) {
                            await updateSankeyDiagram();
                        }
                        
                        const aggContainer = document.getElementById('aggregations');
                        if (aggContainer) {
                            if (advancedMode) {
                                await buildAggregationsSectionAll();
                            } else {
                                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                            }
                        }
                    }
                    
                    hideLoading();
                    
                    // Reset URL field for next analysis
                    const urlInput = document.getElementById('pcapUrl');
                    if (urlInput) {
                        urlInput.value = lastSampleUrl;
                    }
                }
            } catch(err) {
                console.error('loadAnalysis error:', err);
                console.error('loadAnalysis error stack:', err.stack);
                console.error('loadAnalysis error name:', err.name);
                hideLoading();
                showError('Failed to load analysis: ' + (err.message || 'Unknown error'));
            }
        }
        
        function loadSampleUrl(url) {
            closeHelpModal();
            lastSampleUrl = url;
            document.getElementById('pcapUrl').value = url;
            loadFromUrl();
        }

        async function loadFromUrl() {
            const urlInput = document.getElementById('pcapUrl');
            const url = urlInput.value.trim();
            
            if (!url) {
                showError('Please enter a URL');
                return;
            }
            
            // Remember this URL for future resets
            lastSampleUrl = url;
            
            showLoading('Downloading file... (0s)');
            const downloadStart = Date.now();
            let downloadInterval = setInterval(() => {
                const elapsedSec = Math.floor((Date.now() - downloadStart) / 1000);
                showLoading(`Downloading file... (${elapsedSec}s)`);
            }, 1000);

            try {
                const resp = await fetch('/api/load-url', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url, maxUploadSize: getUserMaxUploadSizeMB() * 1024 * 1024})
                });
                const result = await resp.json();
                clearInterval(downloadInterval);

                if (result.status === 'processing') {
                    await checkStatus(result.md5, result.phase || 'network');
                    urlInput.value = lastSampleUrl;
                } else if (result.status === 'ready') {
                    hideLoading();
                    await loadAnalysis(result.md5);
                    urlInput.value = lastSampleUrl;
                } else {
                    hideLoading();
                    showError(result.error || 'Unknown error');
                }
            } catch(err) {
                clearInterval(downloadInterval);
                hideLoading();
                showError(err.message);
            }
        }
        
        async function uploadPcap(droppedFile) {
            const fileInput = document.getElementById('pcapUpload');
            const file = droppedFile || fileInput.files[0];
            if (!file) return;

            showLoading('Uploading file... (0s)');
            const uploadStart = Date.now();
            let uploadInterval = setInterval(() => {
                const elapsedSec = Math.floor((Date.now() - uploadStart) / 1000);
                showLoading(`Uploading file... (${elapsedSec}s)`);
            }, 1000);

            const formData = new FormData();
            formData.append('pcap', file);

            try {
                const resp = await fetch('/api/upload', {
                    method: 'POST',
                    headers: {'X-Max-Upload-Size': String(getUserMaxUploadSizeMB() * 1024 * 1024)},
                    body: formData
                });
                const result = await resp.json();
                clearInterval(uploadInterval);

                if (!resp.ok || result.error) {
                    hideLoading();
                    showError(result.error || 'Upload failed');
                    fileInput.value = '';
                    return;
                }

                if (result.status === 'ready') {
                    hideLoading();
                    await loadAnalysis(result.md5);
                } else if (result.status === 'processing') {
                    await checkStatus(result.md5, result.phase || 'network');
                }
            } catch(err) {
                clearInterval(uploadInterval);
                hideLoading();
                showError(err.message);
            }
            
            fileInput.value = '';
        }
        
        function handleDragOver(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('dropZone').classList.add('drop-zone-active');
        }
        
        function handleDragLeave(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('dropZone').classList.remove('drop-zone-active');
        }
        
        function handleDrop(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('dropZone').classList.remove('drop-zone-active');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                uploadPcap(files[0]);
            }
        }
        
        async function checkStatus(md5, initialPhase = 'network') {
            const phaseMessages = {
                'network': 'Analyzing network traffic...',
                'files': 'Analyzing files...',
                'importing': 'Importing data...',
                'logs': 'Analyzing log file...'
            };
            
            const startTime = Date.now();
            let currentPhase = initialPhase;
            let elapsedInterval = null;
            
            // Show initial message immediately
            showLoading(`${phaseMessages[currentPhase]} (0s)`);
            
            // Local timer updates elapsed time every 1s without hitting the server
            elapsedInterval = setInterval(() => {
                const elapsedSec = Math.floor((Date.now() - startTime) / CONFIG.POLLING_INTERVAL_MS);
                const msg = phaseMessages[currentPhase] || 'Analyzing file...';
                showLoading(`${msg} (${elapsedSec}s)`);
            }, CONFIG.POLLING_INTERVAL_MS);
            
            for (let i = 0; i < CONFIG.MAX_POLLING_ATTEMPTS; i++) {
                await new Promise(r => setTimeout(r, 2000));
                
                try {
                    const resp = await fetch('/api/check-status', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({md5: md5})
                    });
                    const result = await resp.json();
                    
                    if (result.status === 'error') {
                        clearInterval(elapsedInterval);
                        hideLoading();
                        showError(result.message || 'Analysis failed');
                        return;
                    }

                    if (result.status === 'ready') {
                        clearInterval(elapsedInterval);
                        hideLoading();
                        await loadAnalysis(md5);
                        return;
                    }
                    
                    if (result.status === 'processing') {
                        if (result.phase) {
                            currentPhase = result.phase;
                        }
                    }
                } catch(err) {
                    console.error('Status check error:', err);
                }
            }
            
            clearInterval(elapsedInterval);
            hideLoading();
            showError('Analysis timed out. The file may be very large or analysis may have encountered an error.');
        }
        
        let pendingDelete = null;
        let pendingReanalyze = null;
        
        function openDeleteAnalysis(md5, name) {
            pendingDelete = { md5, name };
            document.getElementById('deleteFileName').textContent = name;
            document.getElementById('deleteConfirmModal').classList.add('active');
        }
        
        function closeDeleteModal() {
            pendingDelete = null;
            document.getElementById('deleteConfirmModal').classList.remove('active');
        }
        
        function handleDeleteBackdropClick(event) {
            if (event.target.id === 'deleteConfirmModal') {
                closeDeleteModal();
            }
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('errorModal').classList.add('active');
        }
        
        function closeErrorModal() {
            document.getElementById('errorModal').classList.remove('active');
        }
        
        async function confirmDelete() {
            if (!pendingDelete) return;
            
            const { md5, name } = pendingDelete;
            pendingDelete = null;
            document.getElementById('deleteConfirmModal').classList.remove('active');
            
            try {
                const resp = await fetch('/api/delete-analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ md5: md5 }),
                });
                const result = await resp.json();
                if (result.success) {
                    if (currentMd5 === md5) {
                        currentMd5 = '';
                        eventStats = {};
                        baseEventStats = {};
                        tabDataCache = {};
                    }
                    bumpFetchGeneration();
                    showWelcome();
                } else {
                    showError(result.error || 'Could not delete');
                }
            } catch(err) {
                showError(err.message);
            }
        }

        let pendingDeleteAllCount = 0;
        
        function openDeleteAllAnalyses(count) {
            pendingDeleteAllCount = count;
            document.getElementById('deleteAllCount').textContent = count;
            document.getElementById('deleteAllConfirmModal').classList.add('active');
        }
        
        function closeDeleteAllModal() {
            pendingDeleteAllCount = 0;
            document.getElementById('deleteAllConfirmModal').classList.remove('active');
        }
        
        function handleDeleteAllBackdropClick(event) {
            if (event.target.id === 'deleteAllConfirmModal') {
                closeDeleteAllModal();
            }
        }
        
        async function confirmDeleteAll() {
            if (!pendingDeleteAllCount) return;
            pendingDeleteAllCount = 0;
            document.getElementById('deleteAllConfirmModal').classList.remove('active');
            
            try {
                const resp = await fetch('/api/delete-all-analyses', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({}),
                });
                const result = await resp.json();
                if (result.success) {
                    currentMd5 = '';
                    eventStats = {};
                    baseEventStats = {};
                    tabDataCache = {};
                    bumpFetchGeneration();
                    showWelcome();
                } else {
                    showError(result.error || 'Could not delete analyses');
                }
            } catch(err) {
                showError(err.message);
            }
        }
        
        async function openReanalyzeModal(md5, name) {
            let phase = 'files';
            try {
                const resp = await fetch('/api/status?md5=' + md5 + '&t=' + Date.now());
                const status = await resp.json();
                const detectedType = status.meta?.detected_type || detectFileType(name);
                if (detectedType === 'log') phase = 'logs';
                else if (detectedType === 'pcap') phase = 'network';
            } catch(err) {
                // Fallback to filename-based detection if status API fails
                const detectedType = detectFileType(name);
                if (detectedType === 'log') phase = 'logs';
                else if (detectedType === 'pcap') phase = 'network';
            }
            pendingReanalyze = { md5, name, phase };
            document.getElementById('reanalyzeFileName').textContent = name;
            document.getElementById('reanalyzeConfirmModal').classList.add('active');
        }
        
        function closeReanalyzeModal() {
            pendingReanalyze = null;
            document.getElementById('reanalyzeConfirmModal').classList.remove('active');
        }
        
        function handleReanalyzeBackdropClick(event) {
            if (event.target.id === 'reanalyzeConfirmModal') {
                closeReanalyzeModal();
            }
        }
        
        async function confirmReanalyze() {
            if (!pendingReanalyze) return;
            const { md5, name, phase } = pendingReanalyze;
            pendingReanalyze = null;
            closeReanalyzeModal();
            
            showLoading('Re-analyzing ' + name + '...');
            try {
                const resp = await fetch('/api/reanalyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({md5: md5})
                });
                const result = await resp.json();
                if (result.error) {
                    hideLoading();
                    showError(result.error);
                    return;
                }
                if (result.status === 'processing') {
                    await checkStatus(md5, phase || 'network');
                } else {
                    hideLoading();
                }
            } catch(err) {
                hideLoading();
                showError(err.message);
            }
        }
        
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (diagramMode && currentMd5) {
                    updateSankeyDiagram();
                }
            }, CONFIG.SEARCH_DEBOUNCE_MS);
        });

        async function init() {
            try {
                // Initialize theme state, code-rain background, and favicon.
                updateThemeMenu();
                updateCodeRain();
                updateFavicon();

                // Fetch and display version from server
                try {
                    const verResp = await fetch('/api/version');
                    if (verResp.ok) {
                        const verData = await verResp.json();
                        const link = document.getElementById('footerVersionLink');
                        if (link && verData.version) {
                            link.textContent = 'SO-CRATES ' + verData.version;
                        }
                    }
                } catch(verErr) {
                    // Ignore version fetch errors — footer shows placeholder
                }

                // Check for file query parameter (backward compatible with ?pcap=)
                const urlParams = new URLSearchParams(window.location.search);
                const fileMd5 = urlParams.get('file') || urlParams.get('pcap');
                
                if (fileMd5) {
                    await loadAnalysis(fileMd5);
                } else {
                    await showWelcome();
                }
            } catch(err) {
                console.error('Init error:', err);
                
            }
        }
        
        init().catch(err => {
            console.error('Init error:', err);
            console.error('Init error stack:', err.stack);
            console.error('Init error names:', err.name);
        });
