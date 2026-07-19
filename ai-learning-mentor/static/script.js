// ---------- Tab switching ----------
const tabButtons = document.querySelectorAll(".tab-btn");
const panels = document.querySelectorAll(".panel");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
  });
});

// ---------- Profile persistence ----------
const profileFields = ["p-name", "p-grade", "p-subject", "p-language"];
profileFields.forEach((id) => {
  const el = document.getElementById(id);
  const saved = localStorage.getItem(id);
  if (saved) el.value = saved;
  el.addEventListener("input", () => localStorage.setItem(id, el.value));
});

function getProfile() {
  return {
    name: document.getElementById("p-name").value.trim(),
    grade: document.getElementById("p-grade").value.trim(),
    subject: document.getElementById("p-subject").value.trim(),
    language: document.getElementById("p-language").value.trim(),
  };
}

// ---------- Chat ----------
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

let history = [];

function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = "msg " + role;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage("user", text);
  history.push({ role: "user", content: text });
  chatInput.value = "";
  chatSend.disabled = true;

  const thinkingBubble = appendMessage("assistant", "Thinking...");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history, profile: getProfile() }),
    });
    const data = await res.json();

    if (!res.ok) {
      thinkingBubble.parentElement.classList.add("error");
      thinkingBubble.textContent = "Error: " + (data.error || "Something went wrong.");
      return;
    }

    thinkingBubble.textContent = data.reply;
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    thinkingBubble.parentElement.classList.add("error");
    thinkingBubble.textContent = "Network error — please try again.";
  } finally {
    chatSend.disabled = false;
  }
});

// ---------- Study Planner ----------
const planForm = document.getElementById("plan-form");
const planOutput = document.getElementById("plan-output");
const planGenerate = document.getElementById("plan-generate");

planForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  planGenerate.disabled = true;
  planOutput.textContent = "Generating your plan...";
  planOutput.classList.add("loading");

  const payload = {
    subject: document.getElementById("pl-subject").value.trim(),
    days: document.getElementById("pl-days").value,
    hours: document.getElementById("pl-hours").value,
    topics: document.getElementById("pl-topics").value.trim(),
    level: document.getElementById("pl-level").value.trim(),
  };

  try {
    const res = await fetch("/api/study-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    planOutput.classList.remove("loading");
    if (!res.ok) {
      planOutput.textContent = "Error: " + (data.error || "Something went wrong.");
      return;
    }
    planOutput.textContent = data.plan;
  } catch (err) {
    planOutput.classList.remove("loading");
    planOutput.textContent = "Network error — please try again.";
  } finally {
    planGenerate.disabled = false;
  }
});
