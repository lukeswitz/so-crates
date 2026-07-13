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
            const jsEscaped = String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
            return escapeHtml(jsEscaped);
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
            dark: { label: 'Dark Mode', icon: '<svg class="theme-icon-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>' },
            light: { label: 'Light Mode', icon: '<svg class="theme-icon-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>' },
            hacker: { label: 'Hacker Mode', icon: '<svg class="theme-icon-hacker" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="6 9 10 12 6 15"/><line x1="12" y1="15" x2="18" y2="15"/></svg>' },
        };

        function getCurrentTheme() {
            return document.documentElement.getAttribute('data-theme') || 'dark';
        }

        function setTheme(themeName) {
            const valid = Object.prototype.hasOwnProperty.call(THEMES, themeName);
            if (!valid) return;
            const html = document.documentElement;
            if (themeName === 'dark') {
                html.removeAttribute('data-theme');
            } else {
                html.setAttribute('data-theme', themeName);
            }
            localStorage.setItem('socrates-theme', themeName);
            updateThemeMenu();
            updateCodeRain();
            updateFavicon();
        }

        function toggleTheme() {
            const order = ['dark', 'light', 'hacker'];
            const current = getCurrentTheme();
            const nextIndex = (order.indexOf(current) + 1) % order.length;
            setTheme(order[nextIndex]);
        }

        function updateThemeMenu() {
            // Menu items are rendered in HTML; this hook is available for
            // future dynamic menu generation.
        }

        // Subtle code-rain background for Hacker Mode.
        let codeRainCtx = null;
        let codeRainCols = [];
        let codeRainFontSize = 14;
        let codeRainAnimationId = null;
        let codeRainLastDraw = 0;
        const codeRainChars = '0123456789ABCDEFｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ';

        function resizeCodeRain() {
            const canvas = document.getElementById('codeRain');
            if (!canvas) return;
            const dpr = window.devicePixelRatio || 1;
            canvas.width = window.innerWidth * dpr;
            canvas.height = window.innerHeight * dpr;
            codeRainCtx = canvas.getContext('2d');
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
            link.href = getCurrentTheme() === 'hacker' ? 'static/favicon-hacker.svg' : 'static/favicon.svg';
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
            if (dropdown) dropdown.classList.toggle('active');
        }

        function closeMenu() {
            const dropdown = document.getElementById('appHeaderMenuDropdown');
            if (dropdown) dropdown.classList.remove('active');
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
                filealerts: '#e91e63',
                fileinfo: '#9c27b0',
                flow: '#bc8cff',
                ftp: '#00bcd4',
                http: '#ffa726',
                log: '#b0b0b0',
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
            FILE_ALERT: {
                bg: '#e91e6322',
                text: 'var(--file-alert-text)',
            },
        };
        const CONFIG = {
            MAX_QUERY_LIMIT: 10000,
            MAX_TYPE_QUERY_LIMIT: 5000,
            MAX_POLLING_ATTEMPTS: 120,
            POLLING_INTERVAL_MS: 1000,
            TLS_ISSUER_MAX_LENGTH: 30,
            AGGREGATION_TOP_N: 10,
            SEARCH_DEBOUNCE_MS: 300,
            SANKEY_BOTTOM_MARGIN: 60,
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
        const WELCOME_HELP_CONTENT = `
            <p style="color: var(--text-muted); font-size: 0.95rem;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Maximum file size is 1000MB.
            </p>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 15px;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> Processing may take a minute or two depending on the size of the file.
            </p>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 15px;">
                <span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span> File types supported:
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.9rem; color: var(--text-primary);">
                <thead>
                    <tr style="border-bottom: 1px solid var(--bg-hover);">
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 18%;">File Type</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 40%;">File Extensions</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 18%;">Engine</th>
                        <th style="text-align: left; padding: 8px 12px; color: var(--text-muted); font-weight: 600; width: 24%;">Ruleset</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid var(--bg-tertiary); background: rgba(255, 107, 107, 0.05);">
                        <td style="padding: 8px 12px;"><strong style="color: var(--welcome-red);">Packet Capture</strong></td>
                        <td style="padding: 8px 12px;">.pcap, .pcapng, .cap, .trace</td>
                        <td style="padding: 8px 12px;">Suricata</td>
                        <td style="padding: 8px 12px;">Emerging Threats Open</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--bg-tertiary); background: rgba(255, 167, 38, 0.05);">
                        <td style="padding: 8px 12px;"><strong style="color: var(--welcome-orange);">Logs</strong></td>
                        <td style="padding: 8px 12px;">.evtx, .json, .jsonl, .csv, .xml, .log</td>
                        <td style="padding: 8px 12px;">Zircolite</td>
                        <td style="padding: 8px 12px;">SigmaHQ</td>
                    </tr>
                    <tr style="background: rgba(255, 202, 40, 0.05);">
                        <td style="padding: 8px 12px;"><strong style="color: var(--welcome-yellow);">Binary / Other</strong></td>
                        <td style="padding: 8px 12px;">.exe, .dll, .elf, .pdf, etc.</td>
                        <td style="padding: 8px 12px;">YARA</td>
                        <td style="padding: 8px 12px;">YARA Forge</td>
                    </tr>
                </tbody>
            </table>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 8px; margin-bottom: 0;">
                Any of the above file types can be uploaded inside a .zip archive to automatically extract and analyze the first supported file found.
            </p>
        `;
        let lastSampleUrl = DEFAULT_SAMPLE_URL;
        function yaraTagBadgeHtml(tag) {
            const t = (tag || '').toUpperCase();
            let bg, text;
            if (['RANSOMWARE','TROJAN','BACKDOOR','MALWARE','BOTNET'].includes(t)) {
                bg = '#ff6b6b22'; text = 'var(--tag-red-text)';
            } else if (['STORMBAMBOO','CHARMINGKITTEN','TURLA','LAZARUS','PLATINUM','HATMAN','CHARMINGCYPRESS','INKYPINE','INKYSQUID','EVILBAMBOO','TRANSPARENTJASMINE','UTA0040','WHEELEDASH'].includes(t)) {
                bg = '#ba68c822'; text = 'var(--tag-purple-text)';
            } else if (t.startsWith('CVE_')) {
                bg = '#ffa72622'; text = 'var(--tag-orange-text)';
            } else if (['FILE','MEMORY','SCRIPT','LOG'].includes(t)) {
                bg = '#42a5f522'; text = 'var(--tag-blue-text)';
            } else if (['INFO','UTILITY','HIGHVOL'].includes(t)) {
                bg = '#9e9e9e22'; text = 'var(--tag-gray-text)';
            } else {
                bg = '#66bb6a22'; text = 'var(--tag-green-text)';
            }
            return `<span class="badge" style="background:${bg};color:${text};margin-right:4px;">${escapeHtml(tag)}</span>`;
        }

        function buildStreamUrl(endpoint, src, sport, dst, dport) {
            const md5Param = currentMd5 ? `&md5=${encodeURIComponent(currentMd5)}` : '';
            return `/api/${endpoint}?src=${encodeURIComponent(src)}&sport=${encodeURIComponent(sport)}&dst=${encodeURIComponent(dst)}&dport=${encodeURIComponent(dport)}${md5Param}`;
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
            const sectionId = `section-${eventType}`;
            const sectionEl = document.getElementById(sectionId);
            const qParam = currentSearch.length > 0 ? currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('') : '';
            
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
                if (allEvents.length === 0) {
                    try {
                        const resp = await fetch(`/api/events?md5=${currentMd5}&limit=${CONFIG.MAX_TYPE_QUERY_LIMIT}${qParam}&t=${Date.now()}`);
                        allEvents = await resp.json();
                    } catch(e) {
                        console.error('Failed to load all events:', e);
                    }
                }
                if (sectionEl) buildAllEvents();
                if (sectionEl && advancedMode) buildAggregationsSectionAll();
                updateFilterBarVisibility();
                updateSankeyDiagram();
                return;
            }

            if (isLogAnalysisMode && eventType === 'log') {
                const events = tabDataCache['log'] || [];
                const filtered = getFilteredLogEvents(events);
                if (sectionEl) buildLogSectionContent(sectionId, filtered);
                if (advancedMode) buildLogAggregations(filtered, sectionId);
                updateFilterBarVisibility();
                return;
            }

            if (isLogAnalysisMode && eventType === 'sigmaalert') {
                let alerts = tabDataCache['sigmaalert'] || [];
                if (!tabDataCache['sigmaalert']) {
                    try {
                        const resp = await fetch(`/api/sigma-alerts?md5=${currentMd5}&limit=5000${qParam}&t=${Date.now()}`);
                        alerts = await resp.json();
                        tabDataCache['sigmaalert'] = alerts;
                    } catch(e) {
                        console.error('Failed to load sigma alerts:', e);
                    }
                }
                const filtered = getFilteredSigmaAlerts(alerts);
                if (sectionEl) buildSigmaAlertSectionContent(sectionId, filtered);
                if (advancedMode) buildSigmaAlertAggregations(filtered, sectionId);
                updateFilterBarVisibility();
                return;
            }

            if (tabDataCache[eventType]) {
                sections[eventType] = tabDataCache[eventType];
                const filtered = getFilteredEvents(sectionId, tabDataCache[eventType], eventType);
                if (advancedMode && sectionEl) {
                    buildAggregationsSection(eventType, filtered);
                    buildSection(eventType, tabDataCache[eventType]);
                } else if (sectionEl) {
                    buildSection(eventType, tabDataCache[eventType]);
                }
                updateFilterBarVisibility();
                updateSankeyDiagram();
                return;
            }
            
            try {
                const resp = await fetch(`/api/events?md5=${currentMd5}&type=${eventType}&limit=${CONFIG.MAX_QUERY_LIMIT}${qParam}&t=${Date.now()}`);
                const events = await resp.json();
                tabDataCache[eventType] = events;
                
                sections[eventType] = events;
                const filtered = getFilteredEvents(sectionId, events, eventType);
                if (advancedMode) {
                    if (sectionEl) {
                        buildAggregationsSection(eventType, filtered);
                    }
                }
                if (sectionEl) buildSection(eventType, events);
                updateFilterBarVisibility();
                updateSankeyDiagram();
            } catch(e) {
                console.error('Failed to load tab data:', e);
                if (sectionEl) {
                    sectionEl.innerHTML = `<div class="section-header">${typeLabels[eventType] || eventType.toUpperCase()}</div><div class="loading">Error loading data</div>`;
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
                    const asciiDiv = detailRow.querySelector('[id^="ascii-"]');
                    if (asciiDiv) {
                        const id = asciiDiv.id;
                        const parts = id.replace('ascii-', '').split('-');
                        if (parts.length >= 4) {
                            const srcIp = parts[0];
                            const srcPort = parts[1];
                            const dstIp = parts[2];
                            const dstPort = parts[3];
                            const pre = asciiDiv.querySelector('.ascii-transcript');
                            if (pre && !pre.innerHTML) {
                                pre.innerHTML = '<div style="color:var(--text-muted);padding:10px 0;display:flex;align-items:center;gap:8px;"><span class="ascii-loading"></span>Loading ASCII transcript...</div>';
                                loadAsciiTranscript(srcIp, srcPort, dstIp, dstPort, pre);
                            }
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
            const wrapper = btn.closest('div[id^="ascii-"]');
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
            const cls = className ? ` class="${className}"` : '';
            const sty = style ? ` style="${style}"` : '';
            return `<span style="color: var(--text-muted);">${escapeHtml(label)}</span><span${cls}${sty}>${innerHtml}</span>`;
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
            return `<span style="color: var(--text-muted); margin-top: 10px; grid-column: 1 / -1; border-bottom: 1px solid var(--bg-hover); padding-bottom: 5px; color: ${color};">${escapeHtml(title)}</span>`;
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
            html += htmlRow('Event Type', `<span class="badge badge-info">${escapeHtml(e.event_type || '')}</span>`);
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
            return `<div id="ascii-${e.src_ip}-${e.src_port}-${e.dest_ip}-${e.dest_port}" style="margin-top: 15px;"><div style="color: var(--text-muted); font-size: 0.85rem; border-bottom: 1px solid var(--bg-hover); padding-bottom: 5px; margin-bottom: 5px;">Payload</div><div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 10px;"><div class="view-tabs"><button class="view-tab active" onclick="switchStreamView('ascii','${srcIpJs}',${e.src_port},'${dstIpJs}',${e.dest_port},this)">ASCII Transcript</button><button class="view-tab" onclick="switchStreamView('hexdump','${srcIpJs}',${e.src_port},'${dstIpJs}',${e.dest_port},this)">Hexdump</button></div><button class="stream-btn" onclick="downloadPcap('${srcIpJs}','${e.src_port}','${dstIpJs}','${e.dest_port}')" style="margin-left: 12px;">Download PCAP</button></div><div class="stream-view-container" style="background: var(--bg-primary); padding: 15px; border-radius: 8px; font-size: 0.8rem; margin: 0;"><div class="ascii-transcript" style="white-space: pre-wrap; overflow-wrap: break-word;"></div><div class="hexdump-content" style="display: none;"></div></div></div>`;
        }

        function renderAlertDetails(e) {
            let html = htmlSection('Alert Details', COLORS.EVENT.alert);
            html += htmlRowText('Signature', e.alert?.signature);
            html += htmlRow('Category', `<span class="badge badge-danger">${escapeHtml(e.alert?.category || '')}</span>`);
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
            html += htmlRowText('Query Name', e.dns?.rrname, 'mono');
            html += htmlRowText('Query Type', e.dns?.rrtype);
            if (e.dns?.answers) {
                html += htmlRowText('Answers', e.dns.answers.map(a => a.rdata).join(', '), 'mono');
            }
            return html;
        }

        function renderHttpDetails(e) {
            let html = htmlSection('HTTP Details', COLORS.EVENT.http);
            html += htmlRow('Method', `<span class="badge badge-info">${escapeHtml(e.http?.http_method || '')}</span>`);
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
            html += htmlRow('Version', `<span class="badge badge-info">${escapeHtml(e.tls?.version || '')}</span>`);
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
            html += htmlRowText('Type', e.anomaly?.type);
            html += htmlRowText('Message', e.anomaly?.message);
            return html;
        }

        function renderFileAlertDetails(e) {
            const fa = e.filealerts || {};
            let html = htmlRow('Rule', `<span class="badge" style="background:${COLORS.FILE_ALERT.bg};color:${COLORS.FILE_ALERT.text}">${escapeHtml(fa.rule_name || '')}</span>`);
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
                    html += htmlRow('Rule', `<span class="badge" style="background:${COLORS.FILE_ALERT.bg};color:${COLORS.FILE_ALERT.text}">${escapeHtml(m.filealerts?.rule_name || '')}</span>`);
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
            http: renderHttpDetails,
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
        
        
        function sortTable(table, colIndex, th) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => !r.classList.contains('detail-row'));
            const asc = !th.classList.contains('sort-asc');
            
            table.querySelectorAll('th').forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
                const arrow = h.querySelector('.sort-arrow');
                if (arrow) arrow.textContent = '';
            });
            
            th.classList.add(asc ? 'sort-asc' : 'sort-desc');
            let arrow = th.querySelector('.sort-arrow');
            if (!arrow) {
                arrow = document.createElement('span');
                arrow.className = 'sort-arrow';
                th.appendChild(arrow);
            }
            arrow.textContent = asc ? '▲' : '▼';
            
            rows.sort((a, b) => {
                let aVal = a.children[colIndex]?.textContent?.trim() || '';
                let bVal = b.children[colIndex]?.textContent?.trim() || '';
                
                if (!isNaN(aVal) && !isNaN(bVal) && aVal !== '' && bVal !== '') {
                    return asc ? parseFloat(aVal) - parseFloat(bVal) : parseFloat(bVal) - parseFloat(aVal);
                }
                return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            });
            
            const fragment = document.createDocumentFragment();
            rows.forEach(row => {
                fragment.appendChild(row);
                const detailRow = row.nextElementSibling;
                if (detailRow && detailRow.classList.contains('detail-row')) {
                    fragment.appendChild(detailRow);
                }
            });
            tbody.appendChild(fragment);
        }
        
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'TH') {
                const th = e.target;
                // Skip if cursor is default (non-sortable table)
                if (window.getComputedStyle(th).cursor === 'default') return;
                const table = th.closest('table');
                const thead = th.closest('thead');
                const index = Array.from(thead.querySelectorAll('th')).indexOf(th);
                sortTable(table, index, th);
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
            document.getElementById('appHeaderRight').innerHTML = `
                <div class="app-header-menu">
                    <button class="app-header-menu-btn" onclick="toggleMenu()" title="Menu" id="appHeaderMenuBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.17 15a1.65 1.65 0 0 0-1.51-1H2a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.17 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.17a1.65 1.65 0 0 0 1-1.51V2a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                    </button>
                    <div class="app-header-menu-dropdown" id="appHeaderMenuDropdown">
                        <div class="app-header-menu-item theme-header">Theme</div>
                        <button class="app-header-menu-item" onclick="setTheme('dark'); closeMenu();">
                            <span><svg class="theme-icon-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg></span>
                            <span>Dark Mode</span>
                        </button>
                        <button class="app-header-menu-item" onclick="setTheme('light'); closeMenu();">
                            <span><svg class="theme-icon-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg></span>
                            <span>Light Mode</span>
                        </button>
                        <button class="app-header-menu-item" onclick="setTheme('hacker'); closeMenu();">
                            <span><svg class="theme-icon-hacker" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="6 9 10 12 6 15"/><line x1="12" y1="15" x2="18" y2="15"/></svg></span>
                            <span>Hacker Mode</span>
                        </button>
                        <div class="app-header-menu-sep"></div>
                        <button class="app-header-menu-item" onclick="showHelpModal(); closeMenu();">
                            <span><svg class="theme-icon-help" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span>
                            <span>Help</span>
                        </button>
                    </div>
                </div>`;
        }

        function shouldShowHelpModal() {
            if (localStorage.getItem('socrates_hideHelp') === 'true') return false;
            if (sessionStorage.getItem('socrates_helpShown') === 'true') return false;
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
                modalBody.innerHTML = WELCOME_HELP_CONTENT;
                checkboxContainer.style.display = 'flex';
                checkbox.checked = localStorage.getItem('socrates_hideHelp') !== 'true';
                helpModal.classList.add('wide');
            } else {
                modalTitle.textContent = 'Analysis Help';
                const isLogFile = currentFileName && /\.(evtx|json|jsonl|csv|xml|log)$/i.test(currentFileName);
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
                sessionStorage.setItem('socrates_helpShown', 'true');
                if (!document.getElementById('helpShowAgain').checked) {
                    localStorage.setItem('socrates_hideHelp', 'true');
                } else {
                    localStorage.removeItem('socrates_hideHelp');
                }
            }
        }

        function handleHelpBackdropClick(event) {
            if (event.target === document.getElementById('helpModal')) {
                closeHelpModal();
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
                        `<div style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--bg-hover);">
                            <a href="?file=${a.md5}" onclick="event.preventDefault(); loadAnalysis('${a.md5}');" style="color: var(--accent); text-decoration: none; flex: 1;">${FOLDER_ICON_SVG}${escapeHtml(a.name)}</a>
                            <button data-md5="${a.md5}" data-name="${escapeHtml(a.name)}" data-action="reanalyze" style="background: var(--bg-hover); border: none; color: var(--accent); cursor: pointer; font-size: 1rem; padding: 4px 10px; border-radius: 6px; margin-right: 4px;" title="Re-analyze">${REFRESH_ICON_SVG}</button>
                            <button class="previous-analysis-delete" data-md5="${a.md5}" data-name="${escapeHtml(a.name)}" data-action="delete" style="background: var(--bg-hover); border: none; cursor: pointer; font-size: 1rem; padding: 4px 10px; border-radius: 6px;" title="Delete">${DELETE_ICON_SVG}</button>
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
                ? `<button class="previous-analysis-delete-all" onclick="openDeleteAllAnalyses(${previousAnalysisCount})" style="background: var(--bg-hover); border: none; cursor: pointer; font-size: 0.8rem; padding: 4px 10px; border-radius: 6px;" title="Delete all previous analyses">Delete All</button>`
                : '';
            
            document.getElementById('inputBoxes').innerHTML = `
                <div style="max-width: 900px; margin: 0 auto;">
                    <div style="display: flex; flex-direction: column; gap: 20px; margin-bottom: 20px;">
                        <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--bg-hover); width: 100%; box-sizing: border-box;">
                            <div style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; margin-bottom: 15px; font-weight: 600;">${DOWN_ARROW_ICON_SVG} Select a sample file, import a file from URL, or import a file from your local system</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 15px;">
                                <div class="sample-card sample-card-red" onclick="loadSampleUrl('https://www.malware-traffic-analysis.net/2026/02/03/2026-02-03-GuLoader-for-AgentTesla-style-infection-with-FTP-data-exfil.pcap.zip')">
                                    <span class="sample-label sample-red">Sample pcap file</span>
                                </div>
                                <div class="sample-card sample-card-orange" onclick="loadSampleUrl('https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES/raw/refs/heads/master/Defense%20Evasion/apt10_jjs_sideloading_prochollowing_persist_as_service_sysmon_1_7_8_13.evtx')">
                                    <span class="sample-label sample-orange">Sample log file</span>
                                </div>
                                <div class="sample-card sample-card-yellow" onclick="loadSampleUrl('https://secure.eicar.org/eicar.com')">
                                    <span class="sample-label sample-yellow">Sample binary file</span>
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
                                <input type="text" id="pcapUrl" value="https://www.malware-traffic-analysis.net/2026/02/03/2026-02-03-GuLoader-for-AgentTesla-style-infection-with-FTP-data-exfil.pcap.zip" onfocus="this.value=''" onkeydown="if(event.key==='Enter')loadFromUrl()" style="background: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--bg-hover); padding: 8px 12px; border-radius: 4px; font-size: 0.95rem; flex: 1;">
                                <button onclick="loadFromUrl()" style="background: var(--accent); color: var(--bg-primary); padding: 8px 20px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 0.95rem; border: none;">Go</button>
                            </div>
                            <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 15px;">— OR —</div>
                            <input type="file" id="pcapUpload" onchange="uploadPcap()" style="display: none;">
                            <div id="dropZone" style="background: var(--bg-primary); color: var(--accent); padding: 20px; border-radius: 4px; cursor: pointer; font-size: 0.95rem; border: 2px dashed var(--bg-hover); text-align: center; transition: border-color 0.2s, background 0.2s;"
                                 ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)"
                                 onclick="document.getElementById('pcapUpload').click()">
                                 <div style="font-size: 1.5rem; margin-bottom: 8px;"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><polyline points="2 13 6 9 10 13"></polyline></svg></div>
                                 <div>Choose file or drag and drop here</div>
                             </div>
                         </div>
                     </div>
                      <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--bg-hover);">
                          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                              <div style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; font-weight: 600;">${FOLDER_OPEN_ICON_SVG} Previous Analyses</div>
                              ${deleteAllButtonHtml}
                          </div>
                         <div id="previousAnalysesList">${previousHtml}</div>
                     </div>
                    <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 1px solid var(--bg-hover); margin-top: 20px;">
                        <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 10px; text-align: center;">SO-CRATES provides basic analysis. Need more advanced functionality?<br>Take a look at the full <a href="https://securityonion.net" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-weight: 600;">Security Onion</a> platform available in a free Community Edition!<br>If you need enterprise features, consider upgrading to <a href="https://securityonion.com/pro" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-weight: 600;">Security Onion Pro</a>!</div>
                        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                            <thead>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <th style="text-align: left; padding: 10px; color: var(--text-muted); font-size: 0.8rem; text-transform: none; cursor: default;">Feature</th>
                                    <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">SO-CRATES</th>
                                    <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">Security Onion</th>
                                    <th style="text-align: center; padding: 10px; color: var(--text-bright); font-size: 0.8rem; text-transform: none; cursor: default;">Security Onion Pro</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Import Files</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Investigate Alerts</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Slice and Dice Metadata</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Pivot to ASCII Transcript</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Download Carved PCAP</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Airgap / Offline Deployment</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Analyze Live Traffic</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Production Deployments</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Distributed Deployments</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Endpoint Visibility</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
                                    <td style="padding: 8px 10px; color: var(--text-primary); font-size: 0.85rem;">Log Management</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--bg-hover-light);">-</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                    <td style="text-align: center; padding: 8px 10px; color: var(--badge-success-text);">${CHECKMARK_ICON_SVG}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid var(--bg-hover);">
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
            // Easter egg: type "31337" anywhere outside of input fields to activate Hacker Mode.
            const tag = e.target.tagName;
            const isTyping = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.target.isContentEditable;
            if (!isTyping && e.key.length === 1) {
                keyBuffer += e.key.toLowerCase();
                if (keyBuffer.length > 5) {
                    keyBuffer = keyBuffer.slice(-5);
                }
                if (keyBuffer === '31337') {
                    e.preventDefault();
                    setTheme('hacker');
                    showEasterEggMessage('Hacker Mode activated. Welcome to the elite.');
                    keyBuffer = '';
                }
            }
        });

        function showEasterEggMessage(message) {
            const toast = document.createElement('div');
            toast.textContent = message;
            toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: var(--bg-secondary); color: var(--accent); border: 1px solid var(--accent); padding: 12px 20px; border-radius: 6px; font-family: inherit; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: opacity 0.5s;';
            document.body.appendChild(toast);
            setTimeout(function() {
                toast.style.opacity = '0';
                setTimeout(function() { toast.remove(); }, 500);
            }, 2000);
        }
        
        // Single delegated listener for advanced toggle (prevents memory leak from repeated loadAnalysis calls)
        function toggleDiagram() {
            diagramMode = !diagramMode;
            updateSankeyDiagram();
        }
        
        function toggleAggregations() {
            advancedMode = !advancedMode;
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            if (!visibleSection) {
                // Binary analysis mode: no tab sections, rebuild aggregations directly
                const fileAlerts = allEvents.filter(e => e.event_type === 'filealerts');
                const filtered = fileAlerts.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        if (extractValue(e, col, -1) !== val) return false;
                    }
                    return true;
                });
                if (advancedMode) {
                    hiddenAggregations = new Set();
                    buildBinaryAggregations(filtered);
                } else {
                    const aggContainer = document.getElementById('aggregations');
                    if (aggContainer) aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                }
                return;
            }
            const eventType = visibleSection.id.replace('section-', '');
            if (advancedMode) {
                hiddenAggregations = new Set();
                if (eventType === 'all') {
                    buildAggregationsSectionAll();
                } else if (isLogAnalysisMode && eventType === 'log') {
                    const events = tabDataCache['log'] || [];
                    const filtered = getFilteredLogEvents(events);
                    buildLogAggregations(filtered, visibleSection.id);
                } else if (isLogAnalysisMode && eventType === 'sigmaalert') {
                    const alerts = tabDataCache['sigmaalert'] || [];
                    const filtered = getFilteredSigmaAlerts(alerts);
                    buildSigmaAlertAggregations(filtered, visibleSection.id);
                } else {
                    const events = tabDataCache[eventType] || sections[eventType] || [];
                    const filtered = getFilteredEvents(visibleSection.id, events, eventType);
                    buildAggregationsSection(eventType, filtered);
                }
            } else {
                const aggContainer = document.getElementById('aggregations');
                if (aggContainer) {
                    aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                }
            }
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

            capColumn(0, 50);
            capColumn(1, 50);
            capColumn(2, 50);

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
            const events = tabDataCache[eventType] || sections[eventType] || [];
            return getFilteredEvents(visibleSection.id, events, eventType);
        }

        function updateSankeyDiagram() {
            const sankeyPanel = document.getElementById('sankeyPanel');
            if (!sankeyPanel) return;
            sankeyPanel.innerHTML = '';

            if (!diagramMode) {
                sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▸ Sankey Diagram</div>';
                return;
            }
            const events = getSankeyEvents();
            if (!events || events.length === 0) {
                sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▾ Sankey Diagram</div>';
                return;
            }
            sankeyPanel.innerHTML = '<div class="section-toggle-bar" onclick="toggleDiagram()">▾ Sankey Diagram</div><div class="sankey-content"></div>';
            const svgContainer = sankeyPanel.querySelector('.sankey-content');
            const data = buildSankeyData(events);
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
                default:
                    return ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port'];
            }
        }
        
        function buildRowForEvent(e) {
            const ts = (e.timestamp || '').slice(0, 19);
            const etype = e.event_type || '';
            const proto = e.proto || '';
            const srcIp = e.src_ip || '';
            const srcPort = e.src_port || '';
            const dstIp = e.dest_ip || '';
            const dstPort = e.dest_port || '';
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
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td>${escapeHtml(sig)}</td><td><span class="badge badge-danger">${escapeHtml(cat)}</span></td><td><span class="badge" style="background:${sevColor}33;color:${sevColor}">Sev ${sev}</span></td></tr>`;
                    break;
                case 'dns':
                    const rrname = e.dns?.rrname || '';
                    const rrtype = e.dns?.rrtype || '';
                    colSpan = 8;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td class="mono">${escapeHtml(rrname)}</td><td><span class="badge badge-info">${escapeHtml(rrtype)}</span></td></tr>`;
                    break;
                case 'http':
                    const method = e.http?.http_method || '';
                    const host = e.http?.hostname || '';
                    const url = e.http?.url || '';
                    const status = e.http?.status || '';
                    const ua = (e.http?.http_user_agent || '').slice(0, CONFIG.TLS_ISSUER_MAX_LENGTH);
                    const statusBadge = status && parseInt(status) < 400 ? 'badge-success' : status && parseInt(status) < 500 ? 'badge-warning' : 'badge-danger';
                    colSpan = 11;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td><span class="badge badge-info">${escapeHtml(method)}</span></td><td class="mono">${escapeHtml(host)}</td><td class="mono">${escapeHtml(url)}</td><td>${escapeHtml(ua)}</td><td><span class="badge ${statusBadge}">${escapeHtml(String(status))}</span></td></tr>`;
                    break;
                case 'tls':
                    const sni = e.tls?.sni || '-';
                    const version = e.tls?.version || '-';
                    const subject = (e.tls?.subject || '-').slice(0, 40);
                    let issuer = e.tls?.issuerdn || '-';
                    if (issuer && issuer.includes('CN=')) issuer = issuer.split('CN=')[1].split(',')[0];
                    colSpan = 10;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td class="mono">${escapeHtml(sni)}</td><td><span class="badge badge-info">${escapeHtml(version)}</span></td><td class="mono">${escapeHtml(subject)}</td><td class="mono">${escapeHtml(issuer.slice(0, CONFIG.TLS_ISSUER_MAX_LENGTH))}</td></tr>`;
                    break;
                case 'flow':
                    const pktsTs = e.flow?.pkts_toserver || 0;
                    const pktsTc = e.flow?.pkts_toclient || 0;
                    const bytesTs = e.flow?.bytes_toserver || 0;
                    const bytesTc = e.flow?.bytes_toclient || 0;
                    const state = e.flow?.state || '';
                    const alerted = e.flow?.alerted || false;
                    const alertedBadge = alerted ? 'badge-danger' : 'badge-success';
                    const alertedText = alerted ? 'Yes' : 'No';
                    colSpan = 12;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td>${escapeHtml(String(pktsTs.toLocaleString()))}</td><td>${escapeHtml(String(pktsTc.toLocaleString()))}</td><td>${escapeHtml(String(bytesTs.toLocaleString()))}</td><td>${escapeHtml(String(bytesTc.toLocaleString()))}</td><td>${escapeHtml(state)}</td><td><span class="badge ${alertedBadge}">${escapeHtml(alertedText)}</span></td></tr>`;
                    break;
                case 'fileinfo':
                    const filename = e.fileinfo?.filename || '';
                    colSpan = 7;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td class="mono">${escapeHtml(filename)}</td></tr>`;
                    break;
                case 'filealerts':
                    const fa = e.filealerts || {};
                    const ruleName = fa.rule_name || 'N/A';
                    const tagsHtml = (fa.tags || []).map(t => yaraTagBadgeHtml(t)).join('');
                    colSpan = 8;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><span class="badge" style="background:${COLORS.FILE_ALERT.bg};color:${COLORS.FILE_ALERT.text}">${escapeHtml(ruleName)}</span></td><td>${tagsHtml}</td></tr>`;
                    break;
                default:
                    colSpan = 6;
                    row = `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td></tr>`;
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

        function buildBinaryYaraTable(events) {
            const columns = ['Rule Name', 'Tags', 'Author'];
            const sorted = [...events].sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

            let filteredEvents = sorted;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sorted.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        if (extractValue(e, col, -1) !== val) return false;
                    }
                    return true;
                });
            }

            const rows = filteredEvents.map(e => {
                const fa = e.filealerts || {};
                const ruleName = fa.rule_name || 'N/A';
                const tagsHtml = (fa.tags || []).map(t => yaraTagBadgeHtml(t)).join('');
                const author = fa.author || '';
                const formatted = formatEvent(e);
                return `<tr onclick="toggleRow(this)"><td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><span class="badge" style="background:${COLORS.FILE_ALERT.bg};color:${COLORS.FILE_ALERT.text}">${escapeHtml(ruleName)}</span></td><td>${tagsHtml}</td><td>${escapeHtml(author)}</td></tr><tr class="detail-row"><td colspan="3"><div class="detail-content">${formatted}</div></td></tr>`;
            });

            let html = '<div class="section-content">';
            if (rows.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else if (rows.length === 0) {
                html += '<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;">No YARA matches found</div>';
            } else {
                html += '<table><thead><tr>';
                columns.forEach(h => html += `<th>${h}</th>`);
                html += '</tr></thead><tbody>';
                rows.forEach(r => html += r);
                html += '</tbody></table>';
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
            const filteredAlerts = fileAlerts.filter(e => {
                for (const [col, val] of Object.entries(currentFilters)) {
                    if (extractValue(e, col, -1) !== val) return false;
                }
                return true;
            });
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
            const safeDetailId = escapeHtml(String(detailId));
            const totalCols = 2 + (columns ? columns.length : 0); // Time + [cols] + Detail

            let row = `<tr onclick="toggleLogRow(this, '${safeDetailId}')">`;
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
            row += `<tr class="detail-row" id="${safeDetailId}"><td colspan="${totalCols}"><div class="log-detail-panel">${detailHtml}</div></td></tr>`;
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
            const sevClass = `sigma-severity-${sev.replace(/[^a-z]/g, '')}`;
            const ruleTitle = escapeHtml(alert.rule_title || 'Unknown');
            const ruleId = escapeHtml(alert.rule_id || '');
            const timestamp = escapeHtml(alert.timestamp || '');
            const logsource = escapeHtml(alert.logsource || '');

            let mitreHtml = '';
            try {
                const techniques = JSON.parse(alert.mitre_techniques || '[]');
                mitreHtml = techniques.map(t => {
                    const tid = t.replace(/^attack\./i, '').toUpperCase();
                    return `<a href="https://attack.mitre.org/techniques/${encodeURIComponent(tid)}/" target="_blank" rel="noopener noreferrer" class="mitre-tag">${escapeHtml(tid)}</a>`;
                }).join('');
            } catch(e) {
                mitreHtml = '';
            }

            const detailId = 'sigma-detail-' + (alert.id || Math.random().toString(36).substr(2, 9));
            const safeDetailId = escapeHtml(String(detailId));

            let row = `<tr onclick="toggleSigmaRow(this, '${safeDetailId}')">`;
            row += `<td class="timestamp">${timestamp}</td>`;
            row += `<td><span class="badge ${sevClass}">${escapeHtml(sev.toUpperCase())}</span></td>`;
            row += `<td><strong>${ruleTitle}</strong>${ruleId ? '<br><span style="color:var(--text-muted);font-size:0.8rem;">' + ruleId + '</span>' : ''}</td>`;
            row += `<td>${mitreHtml}</td>`;
            row += `<td>${logsource}</td>`;
            row += '</tr>';

            const detailHtml = formatSigmaAlertDetail(alert);
            row += `<tr class="detail-row" id="${safeDetailId}"><td colspan="5"><div class="log-detail-panel">${detailHtml}</div></td></tr>`;
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

        function getFilteredLogEvents(events) {
            if (Object.keys(currentFilters).length === 0) return events;
            return events.filter(e => {
                for (const [col, val] of Object.entries(currentFilters)) {
                    let extracted = '';
                    if (col === 'Time') {
                        extracted = (e.timestamp || '').slice(0, 19);
                    } else if (col === 'Detail') {
                        extracted = getLogEventSmartDetail(_parseLogEventJson(e));
                    } else {
                        const field = _getFieldForLabel(col);
                        extracted = getLogColumnValue(e, field);
                    }
                    if (extracted !== val) return false;
                }
                return true;
            });
        }

        function getFilteredSigmaAlerts(alerts) {
            if (Object.keys(currentFilters).length === 0) return alerts;
            return alerts.filter(a => {
                for (const [col, val] of Object.entries(currentFilters)) {
                    let extracted = '';
                    switch(col) {
                        case 'Severity': extracted = a.severity || ''; break;
                        case 'Rule': extracted = a.rule_title || ''; break;
                        case 'MITRE Technique': {
                            try {
                                const techniques = JSON.parse(a.mitre_techniques || '[]');
                                extracted = techniques.map(t => t.replace(/^attack\./i, '').toUpperCase()).join(', ');
                            } catch(e) { extracted = ''; }
                            break;
                        }
                        case 'Log Source': extracted = a.logsource || ''; break;
                        case 'Timestamp': extracted = a.timestamp || ''; break;
                        default: {
                            // Dynamic column from original_log
                            try {
                                const logObj = JSON.parse(a.original_log || '{}');
                                if (logObj && typeof logObj === 'object') {
                                    const field = _getFieldForLabel(col);
                                    extracted = String(logObj[field] || '');
                                }
                            } catch(e) { extracted = ''; }
                        }
                    }
                    if (extracted !== val) return false;
                }
                return true;
            });
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
                const columns = discoverLogColumns(events);
                html += '<div style="overflow-x:auto;"><table><thead><tr>';
                html += '<th>Time</th>';
                columns.forEach(c => { html += `<th>${escapeHtml(c.label)}</th>`; });
                html += '<th>Detail</th>';
                html += '</tr></thead><tbody>';
                events.forEach(evt => { html += buildLogEventRow(evt, columns); });
                html += '</tbody></table></div>';
            }
            html += '</div>';
            container.innerHTML = html;
        }

        function buildSigmaAlertSectionContent(sectionId, alerts) {
            const container = document.getElementById(sectionId);
            if (!container) return;
            let html = '<div class="section-content">';
            if (alerts.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else if (alerts.length === 0) {
                html += '<div class="no-matches">No Sigma alerts detected</div>';
            } else {
                html += '<table><thead><tr>';
                html += '<th>Timestamp</th><th>Severity</th><th>Rule</th><th>MITRE Technique</th><th>Log Source</th>';
                html += '</tr></thead><tbody>';
                alerts.forEach(alert => { html += buildSigmaAlertRow(alert); });
                html += '</tbody></table>';
            }
            html += '</div>';
            container.innerHTML = html;
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
            let html = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content"><div class="agg-grid">';
            for (const col of aggCols) {
                if (hiddenAggregations.has(sectionId + ':' + col)) continue;
                const colCounts = counts[col];
                const entries = Object.entries(colCounts).sort((a, b) => b[1] - a[1]).slice(0, CONFIG.AGGREGATION_TOP_N);
                if (entries.length === 0) continue;
                html += `<div class="section agg-section" data-col="${escapeHtml(col)}"><div class="section-content"><div class="agg-table">
                    <div class="agg-header"><span>${escapeHtml(col)}</span><button class="agg-close" onclick="hideAggregationTable('${sectionId}', '${escapeJsString(col)}')" title="Hide">&times;</button></div>
                    <table><thead><tr><th style="width:60px;text-align:right;">Count</th><th>Value</th></tr></thead><tbody>`;
                for (const [val, count] of entries) {
                    const escapedVal = escapeHtml(val);
                    html += `<tr class="agg-row" onclick="applyFilter('${sectionId}', '${escapeJsString(col)}', '${escapeJsString(val)}')">
                        <td style="text-align:right;color:var(--text-muted);">${count}</td><td class="agg-cell" title="${escapedVal}">${escapedVal}</td>
                    </tr>`;
                }
                html += '</tbody></table></div></div></div>';
            }
            html += '</div></div></div>';
            aggContainer.innerHTML = html;
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
                let techniques = [];
                try { techniques = JSON.parse(a.mitre_techniques || '[]'); } catch(e) {}
                techniques.forEach(t => {
                    const tid = t.replace(/^attack\./i, '').toUpperCase();
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
            let html = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content"><div class="agg-grid">';
            for (const col of aggCols) {
                if (hiddenAggregations.has(sectionId + ':' + col)) continue;
                const colCounts = counts[col];
                const entries = Object.entries(colCounts).sort((a, b) => b[1] - a[1]).slice(0, CONFIG.AGGREGATION_TOP_N);
                if (entries.length === 0) continue;
                html += `<div class="section agg-section" data-col="${escapeHtml(col)}"><div class="section-content"><div class="agg-table">
                    <div class="agg-header"><span>${escapeHtml(col)}</span><button class="agg-close" onclick="hideAggregationTable('${sectionId}', '${escapeJsString(col)}')" title="Hide">&times;</button></div>
                    <table><thead><tr><th style="width:60px;text-align:right;">Count</th><th>Value</th></tr></thead><tbody>`;
                for (const [val, count] of entries) {
                    const escapedVal = escapeHtml(val);
                    html += `<tr class="agg-row" onclick="applyFilter('${sectionId}', '${escapeJsString(col)}', '${escapeJsString(val)}')">
                        <td style="text-align:right;color:var(--text-muted);">${count}</td><td class="agg-cell" title="${escapedVal}">${escapedVal}</td>
                    </tr>`;
                }
                html += '</tbody></table></div></div></div>';
            }
            html += '</div></div></div>';
            aggContainer.innerHTML = html;
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

            let mitreHtml = '';
            try {
                const techniques = JSON.parse(alert.mitre_techniques || '[]');
                mitreHtml = techniques.map(t => {
                    const tid = t.replace(/^attack\./i, '').toUpperCase();
                    return `<a href="https://attack.mitre.org/techniques/${encodeURIComponent(tid)}/" target="_blank" rel="noopener noreferrer" class="mitre-tag">${escapeHtml(tid)}</a>`;
                }).join('');
            } catch(e) {}
            if (mitreHtml) {
                html += htmlRow('MITRE Techniques', mitreHtml);
            }

            let tagsHtml = '';
            try {
                const tags = JSON.parse(alert.tags || '[]');
                if (tags.length > 0) {
                    tagsHtml = tags.map(t => `<span class="badge badge-info">${escapeHtml(t)}</span>`).join(' ');
                }
            } catch(e) {}
            if (tagsHtml) {
                html += htmlRow('Tags', tagsHtml);
            }

            html += '</div>';
            return html;
        }

        function buildSection(eventType, events) {
            const sorted = [...events].sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));
            const columns = getColumnsForType(eventType);
            const sectionId = `section-${eventType}`;
            
            let filteredEvents = sorted;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sorted.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        const colIndex = columns.indexOf(col);
                        const extracted = extractValue(e, col, colIndex);
                        if (extracted !== val) return false;
                    }
                    return true;
                });
            }
            
            const rows = filteredEvents.map(e => buildRowForEvent(e));
            
            const container = document.getElementById(sectionId);
            if (!container) return;
            
            let html = '<div class="section-content">';
            if (rows.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else {
                html += '<table><thead><tr>';
                columns.forEach(h => html += `<th>${h}</th>`);
                html += '</tr></thead><tbody>';
                rows.forEach(r => html += r);
                html += '</tbody></table>';
            }
            html += '</div>';
            
            try {
                container.innerHTML = html;
            } catch(e) {
                console.error('Failed to render section:', e);
                container.innerHTML = '<div class="loading">Error rendering table</div>';
            }
        }
        
        function buildAggregationsSection(eventType, events) {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;
            
            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }
            
            const sectionId = `section-${eventType}`;
            
            aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + buildAggregationTables(events, eventType) + '</div></div>';
        }
        
        function buildFilterBarHtml() {
            const hasFilters = Object.keys(currentFilters).length > 0;
            if (currentSearch.length === 0 && !hasFilters) return '';

            let html = `<div class="filter-bar"><span class="filter-label">${SEARCH_ICON_SVG} Active:</span>`;
            for (let i = 0; i < currentSearch.length; i++) {
                const term = currentSearch[i];
                html += `<span class="filter-chip">${SEARCH_ICON_SVG} "${escapeHtml(term)}" <span class="filter-chip-remove" onclick="clearSearchTerm(${i})">&times;</span></span>`;
            }
            for (const [col, val] of Object.entries(currentFilters)) {
                html += `<span class="filter-chip">${escapeHtml(col)}: ${escapeHtml(val)} <span class="filter-chip-remove" onclick="clearFilter('${escapeJsString(col)}')">&times;</span></span>`;
            }
            html += '<button class="filter-clear-all" onclick="clearAllFilters()">Clear All</button></div>';
            return html;
        }

        function updateFilterBarVisibility() {
            const filterBarContainer = document.getElementById('filterBarContainer');
            if (!filterBarContainer) return;

            const hasFilters = Object.keys(currentFilters).length > 0;
            if (currentSearch.length > 0 || hasFilters) {
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
            for (const [col, val] of Object.entries(currentFilters)) {
                let extracted;
                if (col === 'Type' || col === 'Detail') {
                    const types = EVENT_TYPE_ICONS;
                    const allColumns = ALL_EVENTS_COLUMNS;
                    const allColIndex = allColumns.indexOf(col);
                    extracted = extractAllValue(event, col, allColIndex);
                } else {
                    extracted = extractValue(event, col, -1);
                }
                if (extracted !== val) return false;
            }
            return true;
        }

        function computeFilteredStats() {
            if (isLogAnalysisMode) {
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
            for (const [col, val] of Object.entries(currentFilters)) {
                let extracted = '';
                switch(col) {
                    case 'Severity': extracted = alert.severity || ''; break;
                    case 'Rule': extracted = alert.rule_title || ''; break;
                    case 'MITRE Technique': {
                        try {
                            const techniques = JSON.parse(alert.mitre_techniques || '[]');
                            extracted = techniques.map(t => t.replace(/^attack\./i, '').toUpperCase()).join(', ');
                        } catch(e) { extracted = ''; }
                        break;
                    }
                    case 'Log Source': extracted = alert.logsource || ''; break;
                    case 'Timestamp': extracted = alert.timestamp || ''; break;
                    default: extracted = '';
                }
                if (extracted !== val) return false;
            }
            return true;
        }

        function buildStats(filteredStats) {
            const grid = document.getElementById('statsGrid');
            const stats = [];
            const hasFilters = Object.keys(currentFilters).length > 0 || currentSearch.length > 0;
            
            eventTypes.forEach(type => {
                const total = baseEventStats[type] || 0;
                let filtered;
                if (type === 'filealerts') {
                    filtered = eventStats[type] || 0;
                } else {
                    filtered = filteredStats ? (filteredStats[type] || 0) : (eventStats[type] || 0);
                }
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
                const countDisplay = hasFilters ? `${s.count} / ${s.total}` : String(s.count);
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
        
        function buildAllEvents() {
            const types = EVENT_TYPE_ICONS;
            const allColumns = ALL_EVENTS_COLUMNS;
            const sectionId = 'section-all';
            const sortedAll = [...allEvents].filter(e => e.event_type !== 'stats').sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));
            
            if (sortedAll.length === 0) return;
            
            let filteredEvents = sortedAll;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sortedAll.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        const colIndex = allColumns.indexOf(col);
                        const extracted = extractAllValue(e, col, colIndex);
                        if (extracted !== val) return false;
                    }
                    return true;
                });
            }
            
            const rows = filteredEvents.map(e => {
                const ts = (e.timestamp || '').slice(0, 19);
                const etype = e.event_type || '';
                const icon = types[etype] || '❓';
                const proto = e.proto || '';
                const srcIp = e.src_ip || '';
                const srcPort = e.src_port || '';
                const dstIp = e.dest_ip || '';
                const dstPort = e.dest_port || '';
                let detail = '';
                if (etype === 'alert') detail = e.alert?.signature || '';
                else if (etype === 'dns') detail = e.dns?.rrname || '';
                else if (etype === 'http') detail = (e.http?.http_method || '') + ' ' + (e.http?.url || '');
                else if (etype === 'tls') detail = e.tls?.sni || '';
                else if (etype === 'flow') detail = `${srcIp}:${srcPort} → ${dstIp}:${dstPort}`;
                else if (etype === 'ftp') detail = e.ftp?.command || '';
                else if (etype === 'anomaly') detail = e.anomaly?.message || '';
                else if (etype === 'fileinfo') detail = e.fileinfo?.filename || '';
                const formatted = formatEvent(e);
                return `<tr onclick="toggleRow(this)"><td class="timestamp">${escapeHtml(ts)}</td><td>${escapeHtml(icon)} ${escapeHtml(etype.toUpperCase())}</td><td><span class="badge badge-info">${escapeHtml(proto)}</span></td><td class="mono">${escapeHtml(srcIp)}</td><td class="mono">${escapeHtml(String(srcPort))}</td><td class="mono">${escapeHtml(dstIp)}</td><td class="mono">${escapeHtml(String(dstPort))}</td><td class="mono">${escapeHtml(detail)}</td></tr><tr class="detail-row"><td colspan="8"><div class="detail-content">${formatted}</div></td></tr>`;
            });
            
            const container = document.getElementById(sectionId);
            let html = '<div class="section-content">';
            if (rows.length === 0 && Object.keys(currentFilters).length > 0) {
                html += EMPTY_FILTER_STATE_HTML;
            } else {
                html += '<table><thead><tr>';
                allColumns.forEach(h => html += `<th>${h}</th>`);
                html += '</tr></thead><tbody>';
                rows.forEach(r => html += r);
                html += '</tbody></table>';
            }
            html += '</div>';
            
            container.innerHTML = html;
        }
        
        function buildAggregationsSectionAll() {
            const aggContainer = document.getElementById('aggregations');
            if (!aggContainer) return;
            
            const types = EVENT_TYPE_ICONS;
            const allColumns = ALL_EVENTS_COLUMNS;
            const sectionId = 'section-all';
            const sortedAll = [...allEvents].filter(e => e.event_type !== 'stats').sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));
            
            let filteredEvents = sortedAll;
            if (Object.keys(currentFilters).length > 0) {
                filteredEvents = sortedAll.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        const colIndex = allColumns.indexOf(col);
                        if (extractAllValue(e, col, colIndex) !== val) return false;
                    }
                    return true;
                });
            }
            
            if (!advancedMode) {
                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                return;
            }
            
            aggContainer.innerHTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▾ Aggregation Tables</div><div class="agg-content">' + buildAggregationTablesAll(filteredEvents, allColumns, types) + '</div></div>';
        }
        
        function extractAllValue(e, col, colIndex) {
            if (col === 'Type') return (e.event_type || '').toUpperCase();
            if (col === 'Command') return e.ftp?.command || '';
            if (col === 'Message') return e.anomaly?.message || '';
            return extractValue(e, col, colIndex);
        }
        
        function buildAggregationTablesCore(events, columns, sectionId, extractFn) {
            if (!events || events.length === 0) return '';
            
            const excludeCols = ['Time'];
            const aggCols = columns.filter(c => !excludeCols.includes(c) && !hiddenAggregations.has(sectionId + ':' + c));
            
            let html = '<div class="agg-grid">';
            
            for (const col of aggCols) {
                const colIndex = columns.indexOf(col);
                const counts = {};
                
                for (const e of events) {
                    const val = extractFn(e, col, colIndex);
                    const key = val || '(empty)';
                    counts[key] = (counts[key] || 0) + 1;
                }
                
                const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, CONFIG.AGGREGATION_TOP_N);
                
                html += `<div class="section agg-section" data-col="${escapeHtml(col)}"><div class="section-content"><div class="agg-table">
                    <div class="agg-header"><span>${escapeHtml(col)}</span><button class="agg-close" onclick="hideAggregationTable('${sectionId}', '${escapeJsString(col)}')" title="Hide">&times;</button></div>
                    <table>
                        <thead><tr><th style="width:60px;text-align:right;">Count</th><th>Value</th></tr></thead>
                        <tbody>`;
                
                for (const [val, count] of sorted) {
                    const escapedVal = escapeHtml(val);
                    const filterVal = val === '(empty)' ? '' : val;
                    html += `<tr class="agg-row" onclick="applyFilter('${sectionId}', '${escapeJsString(col)}', '${escapeJsString(filterVal)}')">
                        <td style="text-align:right;color:var(--text-muted);">${count}</td>
                        <td class="agg-cell" title="${escapedVal}">${escapedVal}</td>
                    </tr>`;
                }
                
                html += `</tbody></table></div></div></div>`;
            }
            
            html += '</div>';
            return html;
        }
        
        function buildAggregationTablesAll(events, columns, types) {
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
                case 'Category': return e.alert?.category || '';
                case 'Severity': return 'Sev ' + (e.alert?.severity || 0);
                case 'Query': return e.dns?.rrname || '';
                case 'Type': return e.dns?.rrtype || '';
                case 'Method': return e.http?.http_method || '';
                case 'Host': return e.http?.hostname || '';
                case 'URL': return e.http?.url || '';
                case 'Status': return String(e.http?.status || '');
                case 'User-Agent': return (e.http?.http_user_agent || '').slice(0, 50);
                case 'SNI / Host': return e.tls?.sni || '-';
                case 'Version': return e.tls?.version || '-';
                case 'Subject': return (e.tls?.subject || '-').slice(0, 40);
                case 'Issuer': return (e.tls?.issuerdn || '-').slice(0, 40);
                case 'Pkts →': return String(e.flow?.pkts_toserver || 0);
                case 'Pkts ←': return String(e.flow?.pkts_toclient || 0);
                case 'Bytes →': return String(e.flow?.bytes_toserver || 0);
                case 'Bytes ←': return String(e.flow?.bytes_toclient || 0);
                case 'State': return e.flow?.state || '';
                case 'Alerted': return e.flow?.alerted ? 'Yes' : 'No';
                case 'Filename': return e.fileinfo?.filename || '';
                case 'Rule Name': return e.filealerts?.rule_name || '';
                case 'Tags': return (e.filealerts?.tags || []).join(', ');
                case 'Author': return e.filealerts?.author || '';
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
                    if (etype === 'dns') return e.dns?.rrname || '';
                    if (etype === 'http') return (e.http?.http_method || '') + ' ' + (e.http?.url || '');
                    if (etype === 'tls') return e.tls?.sni || '';
                    if (etype === 'flow') return `${e.src_ip || ''}:${e.src_port || ''} → ${e.dest_ip || ''}:${e.dest_port || ''}`;
                    if (etype === 'ftp') return e.ftp?.command || '';
                    if (etype === 'anomaly') return e.anomaly?.message || '';
                    if (etype === 'fileinfo') return e.fileinfo?.filename || '';
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
        let sections = {};
        let eventTypes = [];
        let currentMd5 = '';
          let currentFileName = '';
          var currentFilters = {};
          let currentSearch = [];
          var advancedMode = false;
          let diagramMode = true;
          var hiddenAggregations = new Set();
          let baseEventStats = {};
          var isLogAnalysisMode = false;

        const EVENT_TYPE_ICONS = { alert: '🔴', dns: '🟢', http: '🟠', tls: '🔵', flow: '🟣', ftp: '📁', anomaly: '⚠️', fileinfo: '📄', filealerts: '🚨', log: '📋', sigmaalert: '🛡️' };
        const ALL_EVENTS_COLUMNS = ['Time', 'Type', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Detail'];
        const EMPTY_FILTER_STATE_HTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;">${SEARCH_ICON_SVG} No events match the current filters</div>`;
        const AGG_COLLAPSED_HTML = '<div class="agg-panel"><div class="section-toggle-bar" onclick="toggleAggregations()">▸ Aggregation Tables</div></div>';

        function hideAggregationTable(sectionId, col) {
            hiddenAggregations.add(sectionId + ':' + col);
            document.querySelectorAll(`.agg-section[data-col="${col}"]`).forEach(el => {
                el.style.display = 'none';
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

        function refreshCurrentView(sectionId, eventType) {
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
            const events = tabDataCache[eventType] || sections[eventType] || [];
            const filtered = getFilteredEvents(sectionId, events, eventType);
            if (advancedMode) {
                buildAggregationsSection(eventType, filtered);
            }
            buildSection(eventType, events);
        }

        function applyFilters(sectionId, filters) {
            for (const f of filters) {
                currentFilters[f.column] = f.value;
            }
            if (sectionId === 'section-binary') {
                buildBinaryAnalysisView(allEvents);
                updateFilterBarVisibility();
                buildStats(computeFilteredStats());
                return;
            }
            const eventType = sectionId.replace('section-', '');
            refreshCurrentView(sectionId, eventType);
            updateFilterBarVisibility();
            buildStats(computeFilteredStats());
        }

        function clearFilter(columnName) {
            delete currentFilters[columnName];
            const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)');
            if (!visibleSection) {
                // Binary analysis mode
                buildBinaryAnalysisView(allEvents);
                updateFilterBarVisibility();
                buildStats(computeFilteredStats());
                return;
            }
            const eventType = visibleSection.id.replace('section-', '');
            refreshCurrentView(visibleSection.id, eventType);
            updateFilterBarVisibility();
            buildStats(computeFilteredStats());
        }

        function applyFilter(sectionId, columnName, value) {
            applyFilters(sectionId, [{column: columnName, value: value}]);
        }

        async function clearAllFilters() {
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
                const types = EVENT_TYPE_ICONS;
                const allColumns = ALL_EVENTS_COLUMNS;
                return events.filter(e => {
                    for (const [col, val] of Object.entries(currentFilters)) {
                        const colIndex = allColumns.indexOf(col);
                        if (extractAllValue(e, col, colIndex) !== val) return false;
                    }
                    return true;
                });
            }
            
            const columns = getColumnsForType(eventType);
            return events.filter(e => {
                for (const [col, val] of Object.entries(currentFilters)) {
                    const colIndex = columns.indexOf(col);
                    if (extractValue(e, col, colIndex) !== val) return false;
                }
                return true;
            });
        }
        
        async function performSearch() {
            const input = document.getElementById('searchInput');
            const text = input ? input.value.trim() : '';
            if (!text) return;

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
            currentSearch.splice(index, 1);
            updateFilterBarVisibility();
            await refreshAnalysisData();
        }

        async function refreshAnalysisData() {
            if (!currentMd5) return;
            showLoading(currentSearch.length > 0 ? 'Searching...' : 'Loading events...');

            try {
                const qParam = currentSearch.length > 0 ? currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('') : '';

                const [statsResp, baseStatsResp] = await Promise.all([
                    fetch('/api/stats?md5=' + currentMd5 + qParam + '&t=' + Date.now()),
                    fetch('/api/stats?md5=' + currentMd5 + '&t=' + Date.now())
                ]);
                eventStats = await statsResp.json();
                baseEventStats = await baseStatsResp.json();

                const types = sortEventTypes(Object.keys(baseEventStats).filter(t => t !== 'stats' && t !== 'all'));
                eventTypes = types;

                const eventsResp = await fetch('/api/events?md5=' + currentMd5 + '&limit=' + CONFIG.MAX_QUERY_LIMIT + qParam + '&t=' + Date.now());
                allEvents = await eventsResp.json();

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
                        const qParamLocal = currentSearch.length > 0 ? currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('') : '';
                        // Fetch unfiltered baseline
                        const [baseLogResp, baseSigmaResp] = await Promise.all([
                            fetch('/api/events?md5=' + currentMd5 + '&type=log&limit=' + CONFIG.MAX_QUERY_LIMIT + '&t=' + Date.now()),
                            fetch('/api/sigma-alerts?md5=' + currentMd5 + '&limit=5000&t=' + Date.now())
                        ]);
                        const baseLogEvents = await baseLogResp.json();
                        const baseSigmaAlerts = await baseSigmaResp.json();
                        baseEventStats = { log: baseLogEvents.length, sigmaalert: baseSigmaAlerts.length };

                        // Fetch filtered data if search is active
                        let logEvents = baseLogEvents;
                        let sigmaAlerts = baseSigmaAlerts;
                        if (qParamLocal) {
                            const [filteredLogResp, filteredSigmaResp] = await Promise.all([
                                fetch('/api/events?md5=' + currentMd5 + '&type=log&limit=' + CONFIG.MAX_QUERY_LIMIT + qParamLocal + '&t=' + Date.now()),
                                fetch('/api/sigma-alerts?md5=' + currentMd5 + '&limit=5000' + qParamLocal + '&t=' + Date.now())
                            ]);
                            logEvents = await filteredLogResp.json();
                            sigmaAlerts = await filteredSigmaResp.json();
                        }
                        tabDataCache['log'] = logEvents;
                        tabDataCache['sigmaalert'] = sigmaAlerts;
                        allEvents = logEvents;
                        eventStats = { log: logEvents.length, sigmaalert: sigmaAlerts.length };

                        eventTypes = sortEventTypes(Object.keys(baseEventStats));
                        buildStats(computeFilteredStats());
                        buildSections();

                        const defaultType = sigmaAlerts.length > 0 ? 'sigmaalert' : 'log';
                        document.querySelectorAll('.section').forEach(s => s.classList.add('section-hidden'));
                        const defaultSection = document.getElementById('section-' + defaultType);
                        if (defaultSection) defaultSection.classList.remove('section-hidden');
                        loadTabData(defaultType, null);

                        const aggContainer = document.getElementById('aggregations');
                        if (aggContainer) {
                            if (advancedMode) {
                                if (defaultType === 'sigmaalert') {
                                    buildSigmaAlertAggregations(getFilteredSigmaAlerts(sigmaAlerts), 'section-sigmaalert');
                                } else {
                                    buildLogAggregations(getFilteredLogEvents(logEvents), 'section-log');
                                }
                            } else {
                                aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                            }
                        }
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
                    let baseEvents = allEvents;
                    if (qParam) {
                        const baseEventsResp = await fetch('/api/events?md5=' + currentMd5 + '&limit=' + CONFIG.MAX_QUERY_LIMIT + '&t=' + Date.now());
                        baseEvents = await baseEventsResp.json();
                    }
                    baseAllEvents = baseEvents;
                    buildBinaryAnalysisView(allEvents, baseEvents);
                }
            } else {
                document.body.classList.remove('file-analysis');
                isLogAnalysisMode = false;
                const statsGrid = document.getElementById('statsGrid');
                if (statsGrid) statsGrid.style.display = '';
                buildStats(computeFilteredStats());
                
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
                        loadTabData(activeType, null);
                    }
                } else if (eventTypes[0]) {
                    loadTabData(eventTypes[0], null);
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
            try {
                const resp = await fetch('/api/load-analysis?md5=' + md5);
                const result = await resp.json();
                
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
                    sections = {};
                    eventTypes = [];
                    currentFilters = {};
                    currentSearch = [];
                    hiddenAggregations = new Set();
                    tabDataCache = {};
                    clearAnalysisContainers();
                    document.getElementById('searchInput').value = '';
                    
                    showLoading('Loading events...');
                    
                    const statsResp = await fetch('/api/stats?md5=' + md5 + '&t=' + Date.now());
                    eventStats = await statsResp.json();
                    baseEventStats = {...eventStats};
                    
                    const types = sortEventTypes(Object.keys(baseEventStats).filter(t => t !== 'stats' && t !== 'all'));
                    // eventTypes should not include 'all' - it's added separately by buildStats()
                    eventTypes = types;
                    
                    const eventsResp = await fetch('/api/events?md5=' + md5 + '&limit=' + CONFIG.MAX_QUERY_LIMIT + '&t=' + Date.now());
                    allEvents = await eventsResp.json();
                    
                    eventTypes = types;
                    
                    buildStats(computeFilteredStats());
                    
                    // Get date range from non-stats events
                    const mainEvents = allEvents.filter(e => e.event_type !== 'stats');
                    const ts = mainEvents.map(e => e.timestamp).filter(Boolean).sort();
                    const dateDisplay = ts.length > 0 && ts[0] === ts[ts.length - 1]
                        ? ts[0].slice(0, 19)
                        : `${ts[0]?.slice(0, 19) || ''} to ${ts[ts.length-1]?.slice(0, 19) || ''}`;
                    
                    // Fetch analysis metadata for routing (supports ZIP uploads)
                    const statusResp = await fetch('/api/status?md5=' + md5 + '&t=' + Date.now());
                    const analysisStatus = await statusResp.json();
                    const detectedType = analysisStatus.meta?.detected_type ||
                        (currentFileName && /\.(pcap|pcapng|cap|trace)$/i.test(currentFileName) ? 'pcap' :
                         currentFileName && /\.(evtx|json|jsonl|csv|xml|log)$/i.test(currentFileName) ? 'log' : 'binary');
                    
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
                        <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap;">${FOLDER_ICON_SVG}${currentMd5}</span>
                        <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap;">${CALENDAR_ICON_SVG}${dateDisplay}</span>
                    `;
                    document.getElementById('appHeaderRight').innerHTML = `
                        <div class="app-header-menu">
                            <button class="app-header-menu-btn" onclick="toggleMenu()" title="Menu" id="appHeaderMenuBtn">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.17 15a1.65 1.65 0 0 0-1.51-1H2a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.17 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.17a1.65 1.65 0 0 0 1-1.51V2a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                            </button>
                            <div class="app-header-menu-dropdown" id="appHeaderMenuDropdown">
                                <div class="app-header-menu-item theme-header">Theme</div>
                                <button class="app-header-menu-item" onclick="setTheme('dark'); closeMenu();">
                                    <span><svg class="theme-icon-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg></span>
                                    <span>Dark Mode</span>
                                </button>
                                <button class="app-header-menu-item" onclick="setTheme('light'); closeMenu();">
                                    <span><svg class="theme-icon-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg></span>
                                    <span>Light Mode</span>
                                </button>
                                <button class="app-header-menu-item" onclick="setTheme('hacker'); closeMenu();">
                                    <span><svg class="theme-icon-hacker" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="6 9 10 12 6 15"/><line x1="12" y1="15" x2="18" y2="15"/></svg></span>
                                    <span>Hacker Mode</span>
                                </button>
                                <div class="app-header-menu-sep"></div>
                                <button class="app-header-menu-item" onclick="showHelpModal(); closeMenu();">
                                    <span><svg class="theme-icon-help" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span>
                                    <span>Help</span>
                                </button>
                            </div>
                        </div>`;
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
                                    const [logResp, sigmaResp] = await Promise.all([
                                        fetch('/api/events?md5=' + currentMd5 + '&type=log&limit=' + CONFIG.MAX_QUERY_LIMIT + '&t=' + Date.now()),
                                        fetch('/api/sigma-alerts?md5=' + currentMd5 + '&limit=5000&t=' + Date.now())
                                    ]);
                                    const logEvents = await logResp.json();
                                    const sigmaAlerts = await sigmaResp.json();
                                    tabDataCache['log'] = logEvents;
                                    tabDataCache['sigmaalert'] = sigmaAlerts;
                                    allEvents = logEvents;

                                    const logCount = logEvents.length;
                                    const sigmaCount = sigmaAlerts.length;
                                    baseEventStats = { log: logCount, sigmaalert: sigmaCount };
                                    eventStats = { ...baseEventStats };

                                    eventTypes = sortEventTypes(Object.keys(baseEventStats));
                                    buildStats(computeFilteredStats());
                                    buildSections();

                                    const defaultType = sigmaCount > 0 ? 'sigmaalert' : 'log';
                                    document.querySelectorAll('.section').forEach(s => s.classList.add('section-hidden'));
                                    const defaultSection = document.getElementById('section-' + defaultType);
                                    if (defaultSection) defaultSection.classList.remove('section-hidden');
                                    loadTabData(defaultType, null);

                                    const aggContainer = document.getElementById('aggregations');
                                    if (aggContainer) {
                                        if (advancedMode) {
                                            if (defaultType === 'sigmaalert') {
                                                buildSigmaAlertAggregations(getFilteredSigmaAlerts(sigmaAlerts), 'section-sigmaalert');
                                            } else {
                                                buildLogAggregations(getFilteredLogEvents(logEvents), 'section-log');
                                            }
                                        } else {
                                            aggContainer.innerHTML = AGG_COLLAPSED_HTML;
                                        }
                                    }
                                } catch(e) {
                                    console.error('Failed to load log analysis:', e);
                                    document.getElementById('sections').innerHTML = '<div class="log-events-section"><h3>📋 Log Events</h3><div class="no-matches">Error loading log events</div></div>';
                                }
                            })();
                        } else {
                            // Binary file analysis: unified view with search + aggregations + file info + YARA table
                            baseAllEvents = allEvents;
                            buildBinaryAnalysisView(allEvents);
                        }
                    } else {
    
                        isLogAnalysisMode = false;
                        // PCAP analysis: full layout
                        buildSections();
                        if (eventTypes[0]) loadTabData(eventTypes[0]);
                        
                        const sankeyPanel = document.getElementById('sankeyPanel');
                        if (sankeyPanel) {
                            sankeyPanel.style.display = '';
                            updateSankeyDiagram();
                        }
                        
                        const aggContainer = document.getElementById('aggregations');
                        if (aggContainer) {
                            if (advancedMode) {
                                buildAggregationsSectionAll();
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
                    body: JSON.stringify({url: url})
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
                const detectedType = status.meta?.detected_type ||
                    (name && /\.(pcap|pcapng|cap|trace)$/i.test(name) ? 'pcap' :
                     name && /\.(evtx|json|jsonl|csv|xml|log)$/i.test(name) ? 'log' : 'binary');
                if (detectedType === 'log') phase = 'logs';
                else if (detectedType === 'pcap') phase = 'network';
            } catch(err) {
                // Fallback to filename-based detection if status API fails
                const isLogFile = /\.(evtx|json|jsonl|csv|xml|log)$/i.test(name);
                const isPcapFile = /\.(pcap|pcapng|cap|trace)$/i.test(name);
                if (isLogFile) phase = 'logs';
                else if (isPcapFile) phase = 'network';
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
