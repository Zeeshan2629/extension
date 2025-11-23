// chatbot/static/app.js
document.addEventListener("DOMContentLoaded", () => {
  // DOM handles (may be null for some pages)
  const form = document.getElementById("uploadForm");
  const uploadResponse = document.getElementById("uploadResponse");
  const chatArea = document.getElementById("chatArea");
  const currentFile = document.getElementById("currentFile");
  const chatLog = document.getElementById("chatLog");
  const questionInput = document.getElementById("questionInput");
  const askBtn = document.getElementById("askBtn");
  const fileList = document.getElementById("fileList");
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = document.getElementById("themeIcon");
  const body = document.body;
  const sidebar = document.getElementById("sidebar");
  const hamburger = document.getElementById("hamburger");
  const overlay = document.getElementById("overlay");

  // safe-guards
  const safe = (el) => el !== null && el !== undefined;

  // Helper: determine "mobile" breakpoint used by CSS
  const isMobileViewport = () => window.innerWidth <= 900;

  // ---------- SIDEBAR CONTROL ----------
  // We'll set both a class AND explicit inline transform to ensure visible state.
  function showSidebar() {
    if (!safe(sidebar)) return;
    sidebar.classList.add("visible");
    // inline style for immediate effect (overrides conflicting CSS)
    sidebar.style.transform = "translateX(0)";
    overlay?.classList.add("show");
    document.documentElement.classList.add("sidebar-open"); // used in CSS to dim content on mobile
    setHamburger(true);
    if (isMobileViewport()) localStorage.setItem("sidebarState", "open");
  }

  function hideSidebar() {
    if (!safe(sidebar)) return;
    // On mobile hide by moving left; on desktop we keep it visible by default,
    // but allow explicit hide if user toggles.
    const translate = isMobileViewport() ? "translateX(-270px)" : "translateX(-270px)";
    sidebar.classList.remove("visible");
    sidebar.style.transform = translate;
    overlay?.classList.remove("show");
    document.documentElement.classList.remove("sidebar-open");
    setHamburger(false);
    if (isMobileViewport()) localStorage.setItem("sidebarState", "closed");
  }

  function toggleSidebar() {
    if (!safe(sidebar)) return;
    // determine current visible state using computed style (works even if CSS overrides)
    const currentlyVisible = sidebar.classList.contains("visible") || getComputedStyle(sidebar).transform !== "none" && !getComputedStyle(sidebar).transform.includes("-270");
    if (currentlyVisible) hideSidebar();
    else showSidebar();
  }

  function setHamburger(open) {
    if (!safe(hamburger)) return;
    hamburger.textContent = open ? "✖" : "☰";
    hamburger.setAttribute("aria-expanded", open ? "true" : "false");
  }

  // Initialize sidebar state from localStorage
  (function initSidebarState() {
    if (!safe(sidebar)) return;
    // On desktop we prefer sidebar shown by default.
    if (!isMobileViewport()) {
      sidebar.classList.add("visible");
      sidebar.style.transform = "translateX(0)";
      setHamburger(true);
      overlay?.classList.remove("show");
      document.documentElement.classList.remove("sidebar-open");
      return;
    }
    // mobile: restore persisted state
    const saved = localStorage.getItem("sidebarState") || "closed";
    if (saved === "open") showSidebar();
    else hideSidebar();
  })();

  // Hamburger click
  if (safe(hamburger)) {
    hamburger.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSidebar();
    });
  }

  // overlay click closes sidebar
  if (safe(overlay)) {
    overlay.addEventListener("click", () => {
      hideSidebar();
    });
  }

  // Keep state consistent on resize
  window.addEventListener("resize", () => {
    // If desktop now, ensure sidebar visible and overlay hidden
    if (!isMobileViewport()) {
      sidebar?.classList.add("visible");
      sidebar && (sidebar.style.transform = "translateX(0)");
      overlay?.classList.remove("show");
      document.documentElement.classList.remove("sidebar-open");
      setHamburger(true);
    } else {
      // mobile: follow saved state
      const saved = localStorage.getItem("sidebarState") || "closed";
      if (saved === "open") showSidebar();
      else hideSidebar();
    }
  });

  // ---------- THEME TOGGLE ----------
  if (safe(themeToggle) && safe(themeIcon)) {
    const savedTheme = localStorage.getItem("theme") || "dark";
    if (savedTheme === "light") body.classList.add("light-mode");
    themeIcon.textContent = savedTheme === "light" ? "🌞" : "🌙";

    themeToggle.addEventListener("click", () => {
      const isLight = body.classList.toggle("light-mode");
      const theme = isLight ? "light" : "dark";
      localStorage.setItem("theme", theme);
      themeIcon.textContent = theme === "light" ? "🌞" : "🌙";
      themeIcon.classList.add("spin");
      setTimeout(() => themeIcon.classList.remove("spin"), 450);
    });
  }

  // ---------- SMALL UTILITIES ----------
  function scrollToBottom() {
    if (!safe(chatLog)) return;
    chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: "smooth" });
  }

  async function typeEffect(el, txt, speed = 12) {
    if (!safe(el)) return;
    el.innerHTML = "";
    for (let i = 0; i < txt.length; i++) {
      el.innerHTML += txt.charAt(i);
      if (i % 6 === 0) scrollToBottom();
      await new Promise((r) => setTimeout(r, speed));
    }
  }

  const escapeHtml = (s) => s.replace(/[&<"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", '"': "&quot;", "'": "&#39;" })[m]);

  // ---------- LOAD USER FILES (sidebar) ----------
  async function loadUserFiles() {
    if (!safe(fileList)) return;
    try {
      const res = await fetch("/user_files");
      if (!res.ok) { fileList.innerHTML = "<li class='no-files'>No files (error)</li>"; return; }
      const files = await res.json();
      fileList.innerHTML = "";
      if (!files.length) { fileList.innerHTML = "<li class='no-files'>No files yet</li>"; return; }
      files.forEach((f) => {
        const li = document.createElement("li");
        li.title = f;
        li.textContent = f;
        li.addEventListener("click", () => loadChatHistory(f));
        fileList.appendChild(li);
      });
    } catch (err) {
      console.error("loadUserFiles error:", err);
      fileList.innerHTML = "<li class='no-files'>Error loading files</li>";
    }
  }
  loadUserFiles();

  // ---------- UPLOAD HANDLER ----------
  form?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fileInput = document.getElementById("fileInput");
    if (!fileInput || !fileInput.files.length) {
      if (uploadResponse) uploadResponse.innerHTML = "<p style='color:red;'>Please select a PDF file.</p>";
      return;
    }
    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    if (uploadResponse) uploadResponse.innerHTML = "<p>⏳ Uploading and indexing...</p>";

    try {
      const res = await fetch("/upload", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) {
        if (uploadResponse) uploadResponse.innerHTML = `<p style="color:red;">Error: ${data.error || data.message}</p>`;
        return;
      }
      if (uploadResponse) uploadResponse.innerHTML = `<p><strong>${data.message}</strong></p><p>Chunks indexed: ${data.chunk_count}</p><pre>${data.preview}</pre>`;
      if (safe(currentFile)) currentFile.textContent = data.filename;
      if (safe(chatArea)) chatArea.style.display = "block";
      if (safe(chatLog)) chatLog.innerHTML = "";
      await loadChatHistory(data.filename);
      await loadUserFiles();
      if (isMobileViewport()) hideSidebar(); // close sidebar after upload on mobile
    } catch (err) {
      if (uploadResponse) uploadResponse.innerHTML = `<p style="color:red;">${err.message}</p>`;
    }
  });

  // ---------- LOAD CHAT HISTORY ----------
  async function loadChatHistory(filename) {
    if (!filename) return;
    if (safe(currentFile)) currentFile.textContent = filename;
    if (safe(chatLog)) chatLog.innerHTML = "";
    if (safe(chatArea)) chatArea.style.display = "block";

    try {
      const res = await fetch(`/history/${encodeURIComponent(filename)}`);
      if (!res.ok) return;
      const msgs = await res.json();
      msgs.forEach((m) => appendChat(m.role === "user" ? "You" : "Assistant", m.message));
      // mark active file in list
      if (safe(fileList)) {
        [...fileList.children].forEach((li) => {
          if (li.textContent === filename) li.classList.add("active");
          else li.classList.remove("active");
        });
      }
      if (isMobileViewport()) hideSidebar();
    } catch (err) {
      console.error("loadChatHistory error:", err);
    }
  }

  // ---------- CHAT SUBMIT ----------
  askBtn?.addEventListener("click", async () => {
    const q = (questionInput?.value || "").trim();
    if (!q) return;
    // find the filename from UI if not tracked
    const filename = currentFile?.textContent || null;
    if (!filename) { alert("Please upload or select a file first."); return; }

    appendChat("You", q);
    if (questionInput) questionInput.value = "";
    const thinking = appendChat("Assistant", "⏳ Thinking...");

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, question: q }),
      });
      const data = await res.json();
      removeElement(thinking);
      if (!res.ok) { appendChat("Assistant", `Error: ${data.error || "Unknown error"}`); return; }
      const msgEl = appendChat("Assistant", "");
      await typeEffect(msgEl.querySelector(".bubble-text"), data.answer || "[no answer]", 10);
      if (data.context_used?.length) {
        const cites = data.context_used.map((c, i) => `▸ [${i + 1}] score=${(c.score||0).toFixed(4)}`).join("\n");
        const citeEl = appendChat("Assistant", `Citations:\n${cites}`);
        if (citeEl) citeEl.style.opacity = "0.7";
      }
    } catch (err) {
      removeElement(thinking);
      appendChat("Assistant", `Error: ${err.message}`);
    }
  });

  // ---------- UI helpers ----------
  function appendChat(who, text) {
    if (!safe(chatLog)) return document.createElement("div");
    const msg = document.createElement("div");
    msg.className = `chat-message ${who.toLowerCase()}`;
    msg.innerHTML = `<div class="bubble"><strong>${who}:</strong><div class="bubble-text">${escapeHtml(text)}</div></div>`;
    chatLog.appendChild(msg);
    msg.style.opacity = "0";
    msg.style.transform = "translateY(6px)";
    setTimeout(() => { msg.style.opacity = "1"; msg.style.transform = "translateY(0)"; }, 30);
    scrollToBottom();
    return msg;
  }
});
