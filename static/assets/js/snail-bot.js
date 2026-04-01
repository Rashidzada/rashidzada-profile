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
  const countNode = document.getElementById("snail-bot-character-count");
  const assistantName = widget.dataset.assistantName || "Snail Bot";
  const greeting =
    widget.dataset.greeting ||
    "Assalamualaikum. Ask me about Rashid Zada's profile, skills, services, projects, experience, or contact details.";
  const chatUrl = widget.dataset.chatUrl;
  const streamUrl = widget.dataset.streamUrl || chatUrl;

  let hasBootMessage = false;
  let isSending = false;
  const history = [];

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
    bubble.textContent = content || "";

    wrapper.appendChild(meta);
    wrapper.appendChild(bubble);
    return { wrapper, meta, bubble };
  }

  function appendMessage(role, content, modeLabel) {
    const node = createMessageBubble(role, content, modeLabel);
    messages.appendChild(node.wrapper);
    scrollMessagesToEnd();
    return node;
  }

  function ensureGreeting() {
    if (hasBootMessage) {
      return;
    }
    appendMessage("assistant", greeting, "profile");
    history.push({ role: "assistant", content: greeting });
    hasBootMessage = true;
  }

  function setSendingState(sending) {
    isSending = sending;
    form.classList.toggle("is-loading", sending);
    sendButton.disabled = sending;
    input.disabled = sending;
  }

  function updateCounter() {
    if (countNode) {
      countNode.textContent = `${input.value.length}/400`;
    }
  }

  function resizeInput() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 96) + "px";
  }

  function buildModeLabel(mode) {
    if (mode === "deepseek") {
      return "live ai";
    }
    if (mode === "guard") {
      return "profile only";
    }
    return "local";
  }

  function setMessageMode(metaNode, mode) {
    let badge = metaNode.querySelector(".snail-bot-mode-badge");
    if (!badge) {
      badge = document.createElement("span");
      badge.className = "snail-bot-mode-badge";
      metaNode.appendChild(badge);
    }
    badge.textContent = buildModeLabel(mode);
  }

  function setTypingBubble(node) {
    node.wrapper.classList.add("snail-bot-message-typing");
    node.bubble.innerHTML = '<span class="snail-bot-dots"><span></span><span></span><span></span></span>';
  }

  function clearTypingBubble(node) {
    node.wrapper.classList.remove("snail-bot-message-typing");
    if (!node.bubble.dataset.streamingReady) {
      node.bubble.textContent = "";
      node.bubble.dataset.streamingReady = "true";
    }
  }

  async function consumeStream(response, bubbleNode) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let assistantReply = "";

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

      let newlineIndex = buffer.indexOf("\n");
      while (newlineIndex !== -1) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);

        if (line) {
          const event = JSON.parse(line);

          if (event.type === "meta") {
            setMessageMode(bubbleNode.meta, event.mode);
            clearTypingBubble(bubbleNode);
          } else if (event.type === "token") {
            clearTypingBubble(bubbleNode);
            assistantReply += event.content || "";
            bubbleNode.bubble.textContent = assistantReply;
            scrollMessagesToEnd();
          }
        }

        newlineIndex = buffer.indexOf("\n");
      }

      if (done) {
        break;
      }
    }

    return assistantReply.trim();
  }

  async function sendMessage(message) {
    const trimmed = (message || "").trim();
    if (!trimmed || isSending) {
      return;
    }

    ensureGreeting();
    appendMessage("user", trimmed);
    history.push({ role: "user", content: trimmed });

    input.value = "";
    resizeInput();
    updateCounter();
    setSendingState(true);

    const assistantNode = appendMessage("assistant", "", "");
    setTypingBubble(assistantNode);

    try {
      const response = await fetch(streamUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          message: trimmed,
          history: history.slice(-10),
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error("Stream unavailable");
      }

      const assistantReply = await consumeStream(response, assistantNode);
      if (assistantReply) {
        history.push({ role: "assistant", content: assistantReply });
      } else {
        assistantNode.bubble.textContent =
          "Snail Bot could not answer right now. Please try again with a profile-related question.";
        setMessageMode(assistantNode.meta, "guard");
      }
    } catch (error) {
      try {
        const fallbackResponse = await fetch(chatUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({
            message: trimmed,
            history: history.slice(-10),
          }),
        });
        const payload = await fallbackResponse.json();
        clearTypingBubble(assistantNode);

        if (!fallbackResponse.ok || !payload.ok) {
          throw new Error("Fallback failed");
        }

        const reply = payload.data || {};
        setMessageMode(assistantNode.meta, reply.mode);
        assistantNode.bubble.textContent = reply.message || greeting;
        history.push({ role: "assistant", content: assistantNode.bubble.textContent });
      } catch (fallbackError) {
        clearTypingBubble(assistantNode);
        setMessageMode(assistantNode.meta, "guard");
        assistantNode.bubble.textContent =
          "Snail Bot is temporarily unavailable. Please try again in a moment.";
      }
    } finally {
      scrollMessagesToEnd();
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
    resizeInput();
    updateCounter();
  });

  updateCounter();
  resizeInput();
})();
