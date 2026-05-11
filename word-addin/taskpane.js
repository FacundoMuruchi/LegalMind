const API_URL = "http://127.0.0.1:8000/chat";
const HEALTH_URL = "http://127.0.0.1:8000/health";

const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chat-form");
const inputEl = document.querySelector("#message-input");
const sendButtonEl = document.querySelector("#send-button");
const newChatButtonEl = document.querySelector("#new-chat");
const statusDotEl = document.querySelector("#status-dot");
const statusTextEl = document.querySelector("#status-text");

let threadId = getOrCreateThreadId();

Office.onReady(() => {
  setStatus("Checking graph", "pending");
  checkHealth();
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = inputEl.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  inputEl.value = "";
  resizeInput();
  setBusy(true);
  const typingEl = appendTypingMessage();

  try {
    setStatus("Reading document", "pending");
    const documentText = await getDocumentText();
    setStatus("Thinking with contract", "pending");

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        thread_id: threadId,
        document_text: documentText,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "The graph returned an error.");
    }

    typingEl.remove();
    appendMessage("assistant", payload.response);
    setStatus("Graph connected", "ready");
  } catch (error) {
    typingEl.remove();
    appendMessage("error", error.message);
    setStatus("Graph unavailable", "error");
  } finally {
    setBusy(false);
    inputEl.focus();
  }
});

inputEl.addEventListener("input", resizeInput);

inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

newChatButtonEl.addEventListener("click", () => {
  threadId = createThreadId();
  localStorage.setItem("legal-graph-thread-id", threadId);
  messagesEl.replaceChildren();
  appendMessage("assistant", "New conversation ready.");
  inputEl.focus();
});

async function checkHealth() {
  try {
    const response = await fetch(HEALTH_URL);
    if (!response.ok) {
      throw new Error("Health check failed.");
    }
    setStatus("Graph connected", "ready");
  } catch {
    setStatus("Start FastAPI on port 8000", "error");
  }
}

async function getDocumentText() {
  if (!window.Word || !Word.run) {
    return "";
  }

  return Word.run(async (context) => {
    const body = context.document.body;
    body.load("text");
    await context.sync();
    return body.text || "";
  });
}

function appendMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const text = document.createElement("p");
  text.textContent = content;
  article.append(text);

  messagesEl.append(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendTypingMessage() {
  const article = document.createElement("article");
  article.className = "message assistant";
  article.setAttribute("aria-label", "Graph is responding");

  const dots = document.createElement("div");
  dots.className = "typing";
  dots.setAttribute("aria-hidden", "true");

  for (let index = 0; index < 3; index += 1) {
    dots.append(document.createElement("span"));
  }

  article.append(dots);
  messagesEl.append(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return article;
}

function setBusy(isBusy) {
  sendButtonEl.disabled = isBusy;
  inputEl.disabled = isBusy;
  newChatButtonEl.disabled = isBusy;
}

function setStatus(text, state) {
  statusTextEl.textContent = text;
  statusDotEl.className = `status-dot ${state}`;
}

function resizeInput() {
  inputEl.style.height = "auto";
  inputEl.style.height = `${inputEl.scrollHeight}px`;
}

function getOrCreateThreadId() {
  const stored = localStorage.getItem("legal-graph-thread-id");
  if (stored) {
    return stored;
  }

  const next = createThreadId();
  localStorage.setItem("legal-graph-thread-id", next);
  return next;
}

function createThreadId() {
  if (crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `word-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
