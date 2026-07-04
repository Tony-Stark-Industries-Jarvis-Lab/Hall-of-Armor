// ═══════════════════════════════════════════════════════════
//  Stark Industries — Multi-Agent HQ   |   main.js
//  SSE streaming — non-blocking, real-time agent highlighting
// ═══════════════════════════════════════════════════════════

const AGENTS = {
  code: { label: "Code Expert", color: "#4a9eff" },
  general: { label: "General Expert", color: "#ff8c42" },
  writer: { label: "Writer Expert", color: "#9b59b6" },
  architecte: { label: "Architect", color: "#ffd700" },
  developpeur: { label: "Developer", color: "#00d4ff" },
  reviseur: { label: "Reviewer", color: "#ff4455" },
  testeur: { label: "Tester", color: "#00ff88" },
  editeur: { label: "Editor", color: "#ff9500" },
};

const questionInput = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");
const chatOutput = document.getElementById("chat-output");

function clearAllStates() {
  document.querySelectorAll(".workstation").forEach((ws) => {
    ws.classList.remove("thinking", "done", "routing");
  });
}

function triggerRoutingAnimation() {
  document.querySelectorAll(".workstation").forEach((ws) => {
    ws.classList.add("routing");
  });
  setTimeout(() => {
    document.querySelectorAll(".workstation").forEach((ws) => {
      ws.classList.remove("routing");
    });
  }, 400);
}

function triggerCodeTeamAnimation() {
  document.querySelectorAll(".code-team-floor .workstation").forEach((ws) => {
    ws.classList.add("routing");
  });
  setTimeout(() => {
    document.querySelectorAll(".code-team-floor .workstation").forEach((ws) => {
      ws.classList.remove("routing");
    });
  }, 1800);
}

function setAgentThinking(agentKey) {
  clearAllStates();
  const ws = document.getElementById(`ws-${agentKey}`);
  if (ws) ws.classList.add("thinking");
}

function setAgentDone(agentKey) {
  clearAllStates();
  const ws = document.getElementById(`ws-${agentKey}`);
  if (ws) {
    ws.classList.add("done");
    setTimeout(() => ws.classList.remove("done"), 4000);
  }
}

function addMessage(type, text, agentKey = null) {
  const div = document.createElement("div");
  div.className = `msg ${type}`;

  if (agentKey && AGENTS[agentKey]) {
    const badge = document.createElement("span");
    badge.className = "agent-badge";
    badge.textContent = AGENTS[agentKey].label;
    badge.style.backgroundColor = AGENTS[agentKey].color;
    div.appendChild(badge);
    div.appendChild(document.createTextNode(" "));
  }

  div.appendChild(document.createTextNode(text));
  chatOutput.appendChild(div);
  chatOutput.scrollTop = chatOutput.scrollHeight;
  return div;
}

function createStreamingMessage(agentKey) {
  const div = document.createElement("div");
  div.className = "msg agent streaming";

  const badge = document.createElement("span");
  badge.className = "agent-badge";
  badge.textContent = AGENTS[agentKey]?.label ?? agentKey;
  badge.style.backgroundColor = AGENTS[agentKey]?.color ?? "#888";
  div.appendChild(badge);

  const textSpan = document.createElement("span");
  textSpan.className = "stream-text";
  div.appendChild(textSpan);

  const cursor = document.createElement("span");
  cursor.className = "stream-cursor";
  cursor.textContent = "█";
  div.appendChild(cursor);

  chatOutput.appendChild(div);
  chatOutput.scrollTop = chatOutput.scrollHeight;
  return { div, textSpan, cursor };
}

function appendToken(elements, token) {
  elements.textSpan.textContent += token;
  chatOutput.scrollTop = chatOutput.scrollHeight;
}

function finalizeMessage(elements) {
  elements.cursor.remove();
  elements.div.classList.remove("streaming");
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;

  sendBtn.disabled = true;
  sendBtn.textContent = "...";
  questionInput.disabled = true;
  questionInput.value = "";

  addMessage("user", question);
  triggerRoutingAnimation();

  let agentKey = null;
  let streamElems = null;
  let sseBuffer = "";
  const pipelineMessages = {};

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      sseBuffer += decoder.decode(value, { stream: true });
      const lines = sseBuffer.split("\n");
      sseBuffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        let event;
        try {
          event = JSON.parse(line.slice(6));
        } catch {
          continue;
        }

        switch (event.type) {
          case "routing":
            agentKey = event.agent;
            if (agentKey === "vibe_code") {
              triggerCodeTeamAnimation();
              addMessage("system", "⚡ Code Team activated — multi-agent pipeline in progress...");
            } else {
              streamElems = createStreamingMessage(agentKey);
              setAgentThinking(agentKey);
            }
            break;

          case "token":
            if (streamElems) appendToken(streamElems, event.text);
            break;

          case "file":
            addMessage("system", `📄 File saved: ${event.path}`);
            break;

          case "done":
            if (agentKey === "vibe_code") {
              document.querySelectorAll(".code-team-floor .workstation").forEach((ws) => {
                ws.classList.remove("thinking", "done", "routing");
              });
              addMessage("system", "✅ Code Team pipeline finished.");
            } else {
              if (streamElems) finalizeMessage(streamElems);
              setAgentDone(agentKey);
            }
            break;

          case "pipeline_agent": {
            const pipeWs = document.getElementById(`ws-${event.agent}`);
            if (event.phase === "start") {
              pipelineMessages[event.agent] = createStreamingMessage(event.agent);
              if (pipeWs) {
                pipeWs.classList.remove("thinking", "done", "routing");
                pipeWs.classList.add("thinking");
              }
            } else if (event.phase === "done") {
              if (pipelineMessages[event.agent]) {
                finalizeMessage(pipelineMessages[event.agent]);
              }
              if (pipeWs) {
                pipeWs.classList.remove("thinking");
                pipeWs.classList.add("done");
                setTimeout(() => pipeWs.classList.remove("done"), 3000);
              }
            }
            break;
          }

          case "pipeline_token":
            if (pipelineMessages[event.agent]) {
              appendToken(pipelineMessages[event.agent], event.text);
            }
            break;

          case "editor_plan":
            openFileManagerModal(event.plan_id, event.files);
            break;

          case "error":
            clearAllStates();
            if (streamElems) finalizeMessage(streamElems);
            addMessage("error", `⚠ ${event.message}`);
            break;
        }
      }
    }
  } catch (err) {
    clearAllStates();
    if (streamElems) finalizeMessage(streamElems);
    addMessage("error", `⚠ Error while applying the plan: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "SEND ►";
    questionInput.disabled = false;
    questionInput.focus();
  }
}

sendBtn.addEventListener("click", sendQuestion);

questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
});

(async () => {
  try {
    const res = await fetch("/api/agents");
    const agents = await res.json();
    console.group("Stark Industries — Available agents");
    agents.forEach((a) => console.log(`[${a.key}] ${a.description}`));
    console.groupEnd();
  } catch {
    /* non-critical */
  }
})();

const fileManagerModal = document.getElementById("file-manager-modal");
const modalFileList = document.getElementById("modal-file-list");
const modalApplyBtn = document.getElementById("modal-apply-btn");
const modalCancelBtn = document.getElementById("modal-cancel-btn");
const modalCloseBtn = document.getElementById("modal-close-btn");

function openFileManagerModal(planId, files) {
  modalFileList.innerHTML = "";

  if (!files || files.length === 0) {
    addMessage("system", "ℹ️ The Editor did not find any files to create.");
    return;
  }

  files.forEach((file) => {
    const isExisting = file.exists;
    const row = document.createElement("div");
    row.className = "file-row";
    row.dataset.path = file.path;

    row.innerHTML = `
      <div class="file-row-top">
        <span class="file-path">${file.path}</span>
        <span class="file-badge ${isExisting ? "existing" : "new"}">
          ${isExisting ? "⚠ EXISTING" : "✦ NEW"}
        </span>
      </div>
      <div class="file-actions">
        ${isExisting ? `
          <label><input type="radio" name="action-${CSS.escape(file.path)}" value="replace" checked> Replace</label>
          <label><input type="radio" name="action-${CSS.escape(file.path)}" value="merge"> Merge</label>
          <label><input type="radio" name="action-${CSS.escape(file.path)}" value="skip"> Skip</label>
        ` : `
          <label><input type="radio" name="action-${CSS.escape(file.path)}" value="create" checked> Create</label>
          <label><input type="radio" name="action-${CSS.escape(file.path)}" value="skip"> Skip</label>
        `}
      </div>
    `;
    modalFileList.appendChild(row);
  });

  fileManagerModal.dataset.planId = planId;
  fileManagerModal.classList.remove("hidden");
}

function closeFileManagerModal() {
  fileManagerModal.classList.add("hidden");
  modalFileList.innerHTML = "";
}

async function applyEditorPlan() {
  const planId = fileManagerModal.dataset.planId;
  const rows = modalFileList.querySelectorAll(".file-row");
  const actions = {};

  rows.forEach((row) => {
    const path = row.dataset.path;
    const checked = row.querySelector('input[type="radio"]:checked');
    actions[path] = checked ? checked.value : "skip";
  });

  modalApplyBtn.disabled = true;
  modalApplyBtn.textContent = "...";

  try {
    const res = await fetch("/api/editor/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan_id: planId, actions }),
    });
    const data = await res.json();

    closeFileManagerModal();

    const wsEditeur = document.getElementById("ws-editeur");
    if (wsEditeur) {
      wsEditeur.classList.add("done");
      setTimeout(() => wsEditeur.classList.remove("done"), 4000);
    }

    const written = data.results.filter((r) => r.status !== "skipped" && r.status !== "error");
    const skipped = data.results.filter((r) => r.status === "skipped");
    const errors = data.results.filter((r) => r.status === "error");

    if (written.length) {
      addMessage("system", `✅ ${written.length} file(s) written: ${written.map((r) => r.path).join(", ")}`);
    }
    if (skipped.length) {
      addMessage("system", `⏭ ${skipped.length} file(s) skipped.`);
    }
    if (errors.length) {
      addMessage("error", `⚠ Errors: ${errors.map((r) => r.message || r.path).join(", ")}`);
    }
  } catch (err) {
    addMessage("error", `⚠ Error while applying the plan: ${err.message}`);
  } finally {
    modalApplyBtn.disabled = false;
    modalApplyBtn.textContent = "APPLY ►";
  }
}

modalApplyBtn.addEventListener("click", applyEditorPlan);
modalCancelBtn.addEventListener("click", closeFileManagerModal);
modalCloseBtn.addEventListener("click", closeFileManagerModal);
fileManagerModal.addEventListener("click", (e) => {
  if (e.target === fileManagerModal) closeFileManagerModal();
});
