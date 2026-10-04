with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Header with Interactive Endpoint Switcher & Hardware Badge
old_hdr_indicators = """      <!-- Live Indicators -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 bg-dark-900/80 px-3 py-1.5 rounded-lg border border-dark-700 text-xs">
          <span id="server-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-gray-400">Endpoint:</span>
          <span id="server-url-display" class="font-mono text-gray-200">http://127.0.0.1:8080</span>
        </div>
        <div class="flex items-center gap-2 bg-dark-900/80 px-3 py-1.5 rounded-lg border border-dark-700 text-xs">
          <span class="text-gray-400">Modus:</span>
          <span id="model-name-display" class="font-mono text-emerald-300 font-semibold">Gemma-4 + mmproj</span>
        </div>
        <div class="flex items-center gap-1.5 bg-purple-950/60 px-2.5 py-1.5 rounded-lg border border-purple-500/40 text-xs">
          <span class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
          <span class="text-purple-300 font-mono font-bold text-[11px]">v3.1 (2-Stufen-Übersetzer)</span>
        </div>
        <div class="flex items-center gap-2 bg-dark-900/80 px-2.5 py-1.5 rounded-lg border border-dark-700 text-xs font-mono text-cyan-300">
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span id="clock-display">--:--:--</span>
        </div>"""

new_hdr_indicators = """      <!-- Live Indicators & Dynamic Endpoint Switcher -->
      <div class="flex items-center gap-2.5 flex-wrap">
        
        <!-- Interactive Endpoint Switcher -->
        <div class="flex items-center gap-2 bg-dark-900/90 px-3 py-1.5 rounded-xl border border-dark-700 text-xs shadow-inner">
          <span id="server-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span class="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Endpoint:</span>
          
          <!-- Port Switcher Buttons -->
          <div class="flex items-center gap-1 bg-dark-950 p-0.5 rounded-lg border border-dark-800">
            <button id="btn-port-8080" title="Auf Port 8080 wechseln" class="px-2 py-0.5 rounded text-[11px] font-mono font-bold transition bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 cursor-pointer">
              8080
            </button>
            <button id="btn-port-8081" title="Auf Port 8081 wechseln" class="px-2 py-0.5 rounded text-[11px] font-mono font-bold transition text-gray-400 hover:text-gray-200 border border-transparent cursor-pointer">
              8081
            </button>
          </div>

          <span id="server-url-display" class="font-mono text-gray-300 text-[11px] hidden xl:inline">http://127.0.0.1:8080</span>
          
          <!-- Manual Reconnect / Refresh Button -->
          <button id="btn-check-server" title="Endpoint jetzt prüfen & verbinden" class="px-2 py-0.5 rounded bg-dark-800 hover:bg-dark-700 text-gray-300 hover:text-white border border-dark-700 hover:border-gray-500 transition cursor-pointer flex items-center gap-1 text-[11px] font-mono">
            <svg id="refresh-icon" class="w-3 h-3 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Prüfen</span>
          </button>
        </div>

        <!-- Hardware & Model Detection (CPU vs GPU) -->
        <div class="flex items-center gap-2 bg-dark-900/90 px-3 py-1.5 rounded-xl border border-dark-700 text-xs">
          <span id="hardware-mode-badge" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
            <span>⚡ GPU</span>
          </span>
          <span id="model-name-display" class="font-mono text-gray-200 font-semibold text-xs truncate max-w-[160px]">Gemma-4 + mmproj</span>
        </div>

        <div class="flex items-center gap-2 bg-dark-900/80 px-2.5 py-1.5 rounded-lg border border-dark-700 text-xs font-mono text-cyan-300">
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span id="clock-display">--:--:--</span>
        </div>"""

if old_hdr_indicators in text:
    text = text.replace(old_hdr_indicators, new_hdr_indicators, 1)
    print("Updated header with interactive Endpoint Switcher & Hardware Badge.")
else:
    print("WARNING: old_hdr_indicators not found.")

# 2. Update serverUrl declaration & add Endpoint state
old_server_url = "    const serverUrl = 'http://127.0.0.1:8080/v1/chat/completions';"
new_server_url = """    let currentBaseUrl = localStorage.getItem('llama_endpoint_base') || 'http://127.0.0.1:8080';
    let isServerOnline = false;
    let activeModelName = null;
    let activeInferenceAbort = null;

    function getCompletionsUrl() {
      return `${currentBaseUrl.replace(/\\/+$/, '')}/v1/chat/completions`;
    }"""

if old_server_url in text:
    text = text.replace(old_server_url, new_server_url, 1)
    print("Replaced static serverUrl with dynamic getCompletionsUrl().")
else:
    print("WARNING: old_server_url not found.")

# 3. Update checkServerHealth & Endpoint event listeners
old_check_health_section = """    let activeModelName = null;

    // Check server props and active model name dynamically
    async function checkServerHealth() {
      try {
        const res = await fetch('http://127.0.0.1:8080/props');
        if (res.ok) {
          const props = await res.json();
          const hasAudio = props.modalities && props.modalities.audio;
          document.getElementById('server-dot').className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
          document.getElementById('server-url-display').textContent = `http://127.0.0.1:8080 (Audio: ${hasAudio ? 'AKTIV' : 'AUS'})`;
        }

        const mRes = await fetch('http://127.0.0.1:8080/v1/models');
        if (mRes.ok) {
          const mData = await mRes.json();
          const mName = mData.models?.[0]?.name || mData.data?.[0]?.id;
          if (mName) {
            activeModelName = mName;
            const modelLabel = document.getElementById('model-name-display');
            if (modelLabel) {
              modelLabel.textContent = mName.replace('.gguf', '');
            }
          }
        }
      } catch (e) {
        document.getElementById('server-dot').className = "w-2.5 h-2.5 rounded-full bg-amber-500";
        document.getElementById('server-url-display').textContent = "http://127.0.0.1:8080 (Offline?)";
      }
    }
    checkServerHealth();"""

new_check_health_section = """    // --- Dynamic Continuous Server Health & Endpoint Inspector ---
    async function checkServerHealth(isManual = false) {
      const dotEl = document.getElementById('server-dot');
      const urlEl = document.getElementById('server-url-display');
      const modeEl = document.getElementById('model-name-display');
      const hwBadge = document.getElementById('hardware-mode-badge');
      const refreshIcon = document.getElementById('refresh-icon');

      if (refreshIcon && isManual) refreshIcon.classList.add('animate-spin');

      const base = currentBaseUrl.replace(/\\/+$/, '');
      try {
        const ctrl = new AbortController();
        const timeoutId = setTimeout(() => ctrl.abort(), 1200);

        const res = await fetch(`${base}/props`, { signal: ctrl.signal });
        clearTimeout(timeoutId);

        if (res.ok) {
          const props = await res.json();
          isServerOnline = true;
          const hasAudio = props.modalities && props.modalities.audio;
          const modelPath = props.model_path || props.model_alias || "";
          const isCpu = modelPath.toLowerCase().includes('cpu') || modelPath.toLowerCase().includes('dll_cpu');

          activeModelName = props.model_alias || (props.models?.[0]?.name) || null;

          if (dotEl) dotEl.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
          if (urlEl) urlEl.textContent = base;

          if (hwBadge) {
            if (isCpu) {
              hwBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1 shadow-sm";
              hwBadge.innerHTML = `<span>🐢 CPU</span>`;
            } else {
              hwBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 shadow-sm";
              hwBadge.innerHTML = `<span>⚡ GPU (CUDA)</span>`;
            }
          }

          if (modeEl) {
            const shortName = (props.model_alias || "Gemma-4").replace('.gguf', '');
            modeEl.textContent = `${shortName} (Audio: ${hasAudio ? 'AKTIV' : 'AUS'})`;
          }

          updatePortButtonStyles();
          return true;
        } else {
          throw new Error(`HTTP ${res.status}`);
        }
      } catch (err) {
        isServerOnline = false;
        if (dotEl) dotEl.className = "w-2.5 h-2.5 rounded-full bg-red-500";
        if (urlEl) urlEl.textContent = `${base} (Offline)`;
        if (modeEl) modeEl.textContent = "-- Server offline --";
        if (hwBadge) {
          hwBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-500/20 text-red-300 border border-red-500/40 flex items-center gap-1 shadow-sm";
          hwBadge.innerHTML = `<span>🔴 OFFLINE</span>`;
        }

        // If an active request is hanging on a dead server, abort it immediately to unblock UI!
        if (activeInferenceAbort) {
          activeInferenceAbort.abort();
          activeInferenceAbort = null;
          const tel = document.getElementById('telemetry-latency');
          if (tel && tel.textContent.includes('Gemma verarbeitet')) {
            tel.textContent = "⚠️ Server wurde getrennt/beendet";
          }
          const tStat = document.getElementById('trans-audio-status');
          if (tStat && tStat.textContent.includes('Gemma')) {
            tStat.textContent = "⚠️ Server offline";
          }
        }

        updatePortButtonStyles();
        return false;
      } finally {
        if (refreshIcon && isManual) {
          setTimeout(() => refreshIcon.classList.remove('animate-spin'), 300);
        }
      }
    }

    function switchEndpoint(newBase) {
      currentBaseUrl = newBase;
      localStorage.setItem('llama_endpoint_base', newBase);
      updatePortButtonStyles();
      checkServerHealth(true);
    }

    function updatePortButtonStyles() {
      const btn8080 = document.getElementById('btn-port-8080');
      const btn8081 = document.getElementById('btn-port-8081');
      const is8080 = currentBaseUrl.includes('8080');

      if (btn8080) {
        btn8080.className = is8080
          ? "px-2 py-0.5 rounded text-[11px] font-mono font-bold transition bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 cursor-pointer"
          : "px-2 py-0.5 rounded text-[11px] font-mono font-bold transition text-gray-400 hover:text-gray-200 border border-transparent cursor-pointer";
      }
      if (btn8081) {
        btn8081.className = !is8080
          ? "px-2 py-0.5 rounded text-[11px] font-mono font-bold transition bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 cursor-pointer"
          : "px-2 py-0.5 rounded text-[11px] font-mono font-bold transition text-gray-400 hover:text-gray-200 border border-transparent cursor-pointer";
      }
    }

    // Endpoint Button Listeners
    const btn8080El = document.getElementById('btn-port-8080');
    if (btn8080El) btn8080El.addEventListener('click', () => switchEndpoint('http://127.0.0.1:8080'));

    const btn8081El = document.getElementById('btn-port-8081');
    if (btn8081El) btn8081El.addEventListener('click', () => switchEndpoint('http://127.0.0.1:8081'));

    const btnCheckEp = document.getElementById('btn-check-server');
    if (btnCheckEp) btnCheckEp.addEventListener('click', () => checkServerHealth(true));

    // Continuous background health polling every 1.5 seconds!
    checkServerHealth(true);
    setInterval(() => checkServerHealth(false), 1500);"""

if old_check_health_section in text:
    text = text.replace(old_check_health_section, new_check_health_section, 1)
    print("Replaced checkServerHealth with continuous inspector & endpoint switcher.")
else:
    print("WARNING: old_check_health_section not found.")

with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved index.html.")
