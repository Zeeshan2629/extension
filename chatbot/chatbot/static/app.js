// chatbot/static/app.js
document.addEventListener("DOMContentLoaded", () => {
  // ----------- DOM ELEMENTS -----------
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

  const safe = (el) => el !== null && el !== undefined;
  const isMobile = () => window.innerWidth <= 900;

  // ==================================================
  // 🍔 SIDEBAR TOGGLE
  // ==================================================
  function setHamburger(open) {
    if (!safe(hamburger)) return;
    hamburger.textContent = open ? "✖" : "☰";
    hamburger.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function showSidebar() {
    if (!safe(sidebar)) return;
    sidebar.classList.add("visible");
    sidebar.style.transform = "translateX(0)";
    overlay?.classList.add("show");
    document.documentElement.classList.add("sidebar-open");
    setHamburger(true);
    if (isMobile()) localStorage.setItem("sidebarState", "open");
  }

  function hideSidebar() {
    if (!safe(sidebar)) return;
    sidebar.classList.remove("visible");
    sidebar.style.transform = "translateX(-270px)";
    overlay?.classList.remove("show");
    document.documentElement.classList.remove("sidebar-open");
    setHamburger(false);
    if (isMobile()) localStorage.setItem("sidebarState", "closed");
  }

  function toggleSidebar() {
    const visible = sidebar.classList.contains("visible");
    visible ? hideSidebar() : showSidebar();
  }

  hamburger?.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleSidebar();
  });
  overlay?.addEventListener("click", hideSidebar);

  // Restore last sidebar state on load
  const savedSidebar = localStorage.getItem("sidebarState") || "closed";
  if (!isMobile()) showSidebar();
  else if (savedSidebar === "open") showSidebar();
  else hideSidebar();

  window.addEventListener("resize", () => {
    if (!isMobile()) showSidebar();
    else hideSidebar();
  });

  // ==================================================
  // 🌗 THEME TOGGLE
  // ==================================================
  if (safe(themeToggle) && safe(themeIcon)) {
    const savedTheme = localStorage.getItem("theme") || "dark";
    if (savedTheme === "light") body.classList.add("light-mode");
    themeIcon.textContent = savedTheme === "light" ? "🌞" : "🌙";

    themeToggle.addEventListener("click", () => {
      const isLight = body.classList.toggle("light-mode");
      const theme = isLight ? "light" : "dark";
      localStorage.setItem("theme", theme);
      themeIcon.textContent = isLight ? "🌞" : "🌙";
      themeIcon.classList.add("spin");
      setTimeout(() => themeIcon.classList.remove("spin"), 400);
    });
  }

  // ==================================================
  // 🧠 CHAT SYSTEM
  // ==================================================
  const escapeHtml = (s) =>
    s.replace(/[&<"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", '"': "&quot;", "'": "&#39;" }[m]));

  function scrollToBottom() {
    if (!safe(chatLog)) return;
    chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: "smooth" });
  }

  async function typeEffect(el, text, speed = 12) {
    if (!safe(el)) return;
    el.innerHTML = "";
    for (let i = 0; i < text.length; i++) {
      el.innerHTML += text.charAt(i);
      if (i % 6 === 0) scrollToBottom();
      await new Promise((r) => setTimeout(r, speed));
    }
  }

  function appendChat(who, text) {
    if (!safe(chatLog)) return;
    const msg = document.createElement("div");
    msg.className = `chat-message ${who.toLowerCase()}`;
    msg.innerHTML = `
      <div class="bubble">
        <strong>${who}:</strong>
        <div class="bubble-text">${escapeHtml(text)}</div>
      </div>`;
    chatLog.appendChild(msg);
    msg.style.opacity = "0";
    msg.style.transform = "translateY(6px)";
    setTimeout(() => {
      msg.style.opacity = "1";
      msg.style.transform = "translateY(0)";
    }, 30);
    scrollToBottom();
    return msg;
  }

  function removeElement(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  // ==================================================
  // 📁 LOAD USER FILES (Sidebar)
  // ==================================================
  async function loadUserFiles() {
    if (!safe(fileList)) return;
    try {
      const res = await fetch("/user_files", { cache: "no-store" });
      const files = await res.json();
      fileList.innerHTML = "";

      if (!files.length) {
        fileList.innerHTML = `<li class="no-files">No files yet</li>`;
        return;
      }

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

  // ==================================================
  // 🧾 UPLOAD HANDLER
  // ==================================================
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    if (!fileInput || !fileInput.files.length) {
      uploadResponse.innerHTML = "<p style='color:red;'>Please select a PDF file.</p>";
      return;
    }

    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    uploadResponse.innerHTML = "<p>⏳ Uploading and indexing...</p>";

    try {
      const res = await fetch("/upload", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) {
        uploadResponse.innerHTML = `<p style='color:red;'>${data.error || "Upload failed"}</p>`;
        return;
      }

      uploadResponse.innerHTML = `
        <p><strong>${data.message}</strong></p>
        <p>Chunks indexed: ${data.chunk_count}</p>
        <pre>${data.preview}</pre>`;
      currentFile.textContent = data.filename;
      chatArea.style.display = "block";
      chatLog.innerHTML = "";
      await loadChatHistory(data.filename);
      await loadUserFiles();
      if (isMobile()) hideSidebar();
    } catch (err) {
      uploadResponse.innerHTML = `<p style='color:red;'>${err.message}</p>`;
    }
  });

  // ==================================================
  // 🧾 LOAD CHAT HISTORY
  // ==================================================
  async function loadChatHistory(filename) {
    if (!filename) return;
    currentFile.textContent = filename;
    chatLog.innerHTML = "";
    chatArea.style.display = "block";

    try {
      const res = await fetch(`/history/${encodeURIComponent(filename)}`, { cache: "no-store" });
      if (!res.ok) return;
      const msgs = await res.json();
      msgs.forEach((m) => appendChat(m.role === "user" ? "You" : "Assistant", m.message));

      [...fileList.children].forEach((li) =>
        li.textContent === filename ? li.classList.add("active") : li.classList.remove("active")
      );
      if (isMobile()) hideSidebar();
    } catch (err) {
      console.error("loadChatHistory error:", err);
    }
  }

  // ==================================================
  // 💬 CHAT REQUEST (⚡ FIXED INSTANT RENDER)
  // ==================================================
  askBtn?.addEventListener("click", () => {
    const q = questionInput.value.trim();
    if (!q) return;
    const filename = currentFile?.textContent;
    if (!filename) {
      alert("Please upload or select a file first.");
      return;
    }

    appendChat("You", q);
    questionInput.value = "";
    const thinking = appendChat("Assistant", "⏳ Thinking...");

    // 🔥 fixed: no await blocking, immediate DOM update
    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Connection: "close" },
      body: JSON.stringify({ filename, question: q }),
    })
      .then((res) => res.json())
      .then((data) => {
        removeElement(thinking);
        if (data.error) {
          appendChat("Assistant", `Error: ${data.error}`);
          return;
        }

        const msgEl = appendChat("Assistant", "");
        typeEffect(msgEl.querySelector(".bubble-text"), data.answer || "[no answer]", 10);

        if (data.context_used?.length) {
          const cites = data.context_used
            .map((c, i) => `▸ [${i + 1}] score=${(c.score || 0).toFixed(4)}`)
            .join("\n");
          const citeEl = appendChat("Assistant", `Citations:\n${cites}`);
          citeEl.style.opacity = "0.7";
        }
      })
      .catch((err) => {
        removeElement(thinking);
        appendChat("Assistant", `Error: ${err.message}`);
      });
  });
});
