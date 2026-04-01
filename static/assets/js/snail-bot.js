(function () {
  "use strict";

  const widget = document.getElementById("snail-bot-widget");
  if (!widget) {
    return;
  }

  const toggle = document.getElementById("snail-bot-toggle");
  const panel = document.getElementById("snail-bot-panel");
  const closeButton = document.getElementById("snail-bot-close");
  const messages = document.getElementById("snail-bot-messages");
  const suggestions = document.querySelectorAll(".snail-bot-chip");
  const form = document.getElementById("snail-bot-form");
  const input = document.getElementById("snail-bot-input");
  const sendButton = document.getElementById("snail-bot-send");
  const assistantName = widget.dataset.assistantName || "Snail Bot";
  const greeting =
    widget.dataset.greeting ||
    "Assalamualaikum. Ask me about Rashid Zada's profile, skills, services, projects, experience, or contact details.";
  const chatUrl = widget.dataset.chatUrl;

  let hasBootMessage = false;
  let isSending = false;

  function setPanelState(open) {
    widget.classList.toggle("is-open", open);
    panel.hidden = !open;
    panel.setAttribute("aria-hidden", open ? "false" : "true");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      ensureGreeting();
      input.focus();
    }
  }

  function scrollMessagesToEnd() {
    messages.scrollTop = messages.scrollHeight;
  }

  function createMessageBubble(role, content, modeLabel) {
    const wrapper = document.createElement("article");
    wrapper.className = `snail-bot-message snail-bot-message-${role}`;

    const meta = document.createElement("div");
    meta.className = "snail-bot-message-meta";
    meta.textContent = role === "assistant" ? assistantName : "You";

    if (modeLabel) {
      const badge = document.createElement("span");
      badge.className = "snail-bot-mode-badge";
      badge.textContent = modeLabel;
      meta.appendChild(badge);
    }

    const bubble = document.createElement("div");
    bubble.className = "snail-bot-bubble";
    bubble.textContent = content;

    wrapper.appendChild(meta);
    wrapper.appendChild(bubble);
    return wrapper;
  }

  function appendMessage(role, content, modeLabel) {
    messages.appendChild(createMessageBubble(role, content, modeLabel));
    scrollMessagesToEnd();
  }

  function ensureGreeting() {
    if (hasBootMessage) {
      return;
    }
    appendMessage("assistant", greeting, "profile");
    hasBootMessage = true;
  }

  function setSendingState(sending) {
    isSending = sending;
    form.classList.toggle("is-loading", sending);
    sendButton.disabled = sending;
    input.disabled = sending;
  }

  async function sendMessage(message) {
    const trimmed = (message || "").trim();
    if (!trimmed || isSending) {
      return;
    }

    ensureGreeting();
    appendMessage("user", trimmed);
    input.value = "";
    input.style.height = "";
    setSendingState(true);

    const typingMessage = createMessageBubble("assistant", "Typing...", "");
    typingMessage.classList.add("snail-bot-message-typing");
    messages.appendChild(typingMessage);
    scrollMessagesToEnd();

    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ message: trimmed }),
      });
      const payload = await response.json();
      typingMessage.remove();

      if (!response.ok || !payload.ok) {
        appendMessage(
          "assistant",
          "Snail Bot could not answer right now. Please try again with a profile-related question.",
          "error"
        );
        return;
      }

      const reply = payload.data || {};
      const modeLabel =
        reply.mode === "deepseek"
          ? "ai"
          : reply.mode === "guard"
            ? "profile only"
            : "local";
      appendMessage("assistant", reply.message || greeting, modeLabel);
    } catch (error) {
      typingMessage.remove();
      appendMessage(
        "assistant",
        "Snail Bot is temporarily unavailable. Please ask again in a moment.",
        "error"
      );
    } finally {
      setSendingState(false);
      input.focus();
    }
  }

  toggle.addEventListener("click", function () {
    setPanelState(!widget.classList.contains("is-open"));
  });

  closeButton.addEventListener("click", function () {
    setPanelState(false);
  });

  document.addEventListener("click", function (event) {
    if (!widget.classList.contains("is-open")) {
      return;
    }
    if (!widget.contains(event.target)) {
      setPanelState(false);
    }
  });

  suggestions.forEach(function (button) {
    button.addEventListener("click", function () {
      setPanelState(true);
      sendMessage(button.textContent || "");
    });
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(input.value);
  });

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(input.value);
    }
  });

  input.addEventListener("input", function () {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 112) + "px";
  });
})();
