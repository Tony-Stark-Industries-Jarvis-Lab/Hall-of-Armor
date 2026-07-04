import json
import re
import uuid
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

# ==============================================================================
# Configuration
# ==============================================================================

MODEL = "qwen2.5-coder:1.5b"
OLLAMA_HOST = "http://127.0.0.1:11434"
OUTPUT_DIR = Path(__file__).parent / "outputs"  # output directory for the writer agent

# ==============================================================================
# Core LLM call
# ==============================================================================

def call_ollama(system_prompt: str, user_message: str) -> str:
  """Send a message to Ollama and return the final response text."""
  payload = {
    "model": MODEL,
    "messages": [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_message},
    ],
    "stream": False,
  }
  request = urlrequest.Request(
    f"{OLLAMA_HOST}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
  )
  try:
    with urlrequest.urlopen(request, timeout=120) as response:
      data = json.loads(response.read().decode("utf-8"))
  except urlerror.URLError as exc:
    raise RuntimeError(
      f"Unable to reach Ollama at {OLLAMA_HOST}. Start the Ollama service first "
      f"and make sure the {MODEL} model is available. Original error: {exc}"
    ) from exc
  return data["message"]["content"].strip()

def call_ollama_stream(system_prompt: str, user_message: str):
  """Stream the response token by token."""
  payload = {
    "model": MODEL,
    "messages": [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_message},
    ],
    "stream": True,
  }
  request = urlrequest.Request(
    f"{OLLAMA_HOST}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
  )
  try:
    with urlrequest.urlopen(request, timeout=120) as response:
      for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if not line:
          continue
        chunk = json.loads(line)
        token = chunk.get("message", {}).get("content", "")
        if token:
          yield token
  except urlerror.URLError as exc:
    raise RuntimeError(f"Unable to reach Ollama at {OLLAMA_HOST}: {exc}") from exc

# Token limits per pipeline agent (output only)
_PIPELINE_CAPS = {
  "architecte": 500,
  "developpeur": 1800,
  "reviseur":  300,
  "testeur":   280,
  "editeur":   2200,
}

# Model used by each pipeline agent (defaults to the global MODEL)
_PIPELINE_MODELS = {
  "developpeur": MODEL,
  "reviseur":  MODEL,
  "testeur":   MODEL,
  "editeur":   MODEL,
}

def _stream_fast(agent_key: str, user_message: str):
  """
  Fast streaming for the pipeline:
  - per-agent model (_PIPELINE_MODELS)
  - /no_think keeps the response focused and bounded
  - num_predict keeps generation tightly bounded
  """
  model = _PIPELINE_MODELS.get(agent_key, MODEL)
  payload = {
    "model": model,
    "messages": [
      {"role": "system", "content": VIBE_CODE_AGENT_PROMPTS[agent_key]},
      {"role": "user",  "content": f"/no_think\n{user_message}"},
    ],
    "stream": True,
    "options": {"num_predict": _PIPELINE_CAPS.get(agent_key, 800)},
  }
  request = urlrequest.Request(
    f"{OLLAMA_HOST}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
  )
  try:
    with urlrequest.urlopen(request, timeout=120) as response:
      for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if not line:
          continue
        chunk = json.loads(line)
        token = chunk.get("message", {}).get("content", "")
        if token:
          yield token
  except urlerror.URLError as exc:
    raise RuntimeError(f"Unable to reach Ollama at {OLLAMA_HOST}: {exc}") from exc

# ==============================================================================
# Expert Agents
# ==============================================================================

def expert_code(question: str) -> str:
  """Specialized agent for programming and software development."""
  system_prompt = (
    "You are an expert in software development. "
    "You answer programming questions precisely, "
    "with code examples when relevant. "
    "You cover all languages and paradigms."
  )
  return call_ollama(system_prompt, question)

def expert_generalist(question: str) -> str:
  """General-purpose agent for all other questions."""
  system_prompt = (
    "You are a well-rounded and curious general assistant. "
    "You answer clearly, concisely, and pedagogically "
    "to any question that is not specifically about code."
  )
  return call_ollama(system_prompt, question)

def expert_writer(question: str) -> str:
  """Writer agent: generates text and saves it to a .txt file."""
  system_prompt = (
    "You are an expert in writing and written communication. "
    "You are asked to produce a structured text (introduction, body, conclusion) "
    "on the provided topic. Be clear, professional, and concise."
  )
  content = call_ollama(system_prompt, question)

  # Build a clean filename from the question text
  slug = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", question.strip())[:50].strip("_")
  filename = f"{slug}.txt"

  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  filepath = OUTPUT_DIR / filename

  filepath.write_text(content, encoding="utf-8")
  print(f"[Writer Agent] File saved: {filepath}")

  return content

# ==============================================================================
# Available agent registry
# Add a new entry here to extend the architecture.
# ==============================================================================

AGENTS: dict[str, callable] = {
  "code":  expert_code,
  "general": expert_generalist,
  "writer": expert_writer,
  # "vibe_code" is added after _vibe_code_cli is defined (see below)
}

# System prompts shared by the CLI and streaming modes
AGENT_SYSTEM_PROMPTS: dict[str, str] = {
  "code": (
    "You are an expert in software development. "
    "You answer programming questions precisely, "
    "with code examples when relevant. "
    "You cover all languages and paradigms."
  ),
  "general": (
    "You are a well-rounded and curious general assistant. "
    "You answer clearly, concisely, and pedagogically "
    "to any question that is not specifically about code."
  ),
  "writer": (
    "You are an expert in writing and written communication. "
    "You are asked to produce a structured text (introduction, body, conclusion) "
    "on the provided topic. Be clear, professional, and concise."
  ),
}

# User-facing descriptions
AGENT_DESCRIPTIONS: dict[str, str] = {
  "code":   "Code Expert   — explains, debugs, and answers programming questions.",
  "general":  "General Expert — science, culture, history, current events, and general advice.",
  "writer":  "Writer Expert  — writes structured text and saves it in outputs/.",
  "vibe_code": "Vibe Code Team — Architect→Developer→Reviewer→Tester→Editor pipeline.",
}

# ==============================================================================
# Vibe Code Pipeline — 4 agents in sequence
# ==============================================================================

VIBE_CODE_AGENT_PROMPTS: dict[str, str] = {
  "architecte": (
    "You are an expert in software design. Your mission is to analyze the user request, "
    "break the problem into numbered atomic tasks, and establish a clear implementation strategy. "
    "You do not code; you direct. You must always check dependencies before approving a plan. "
    "Be precise and structured."
  ),
  "developpeur": (
    "You are an expert developer, rigorous and pragmatic. Your role is to write clean, "
    "modular, and commented code. You follow the Architect's plan exactly. You prioritize "
    "readability and error handling. You produce only code, no filler. Write only functional "
    "code with concise comments."
  ),
  "reviseur": (
    "You are an expert in cybersecurity and code optimization (Code Reviewer). Your mission "
    "is to review the Developer's code before it is tested. You hunt for logic flaws, algorithmic "
    "inefficiencies, and syntax mistakes. You are uncompromising. If you find a flaw, list it clearly. "
    "If the code is correct, start your response with '✅ CODE APPROVED'."
  ),
  "testeur": (
    "You are a QA engineer (Quality Assurance). Your mission is to analyze the provided code, "
    "simulate its execution mentally, and verify that it meets expectations. You identify edge cases, "
    "potential errors, and missing pieces. If everything is correct, start with '✅ TESTS PASSED'. "
    "Otherwise, list the failures precisely with context."
  ),
  "editeur": (
    "You are the project's Editor. You receive the finalized code and must break down which files "
    "to create or modify. For each file, use EXACTLY this format:\n"
    "---FILE: chemin/relatif/au/projet.ext---\n"
    "[full file content here]\n"
    "---END---\n"
    "Use paths relative to the project root. "
    "Generate only the files strictly necessary for the code to work. "
    "Propose a clean and logical file tree."
  ),
}

# Temporary storage for Editor plans (UUID key -> list of operations)
_editor_plans: dict[str, list[dict]] = {}
PROJECT_ROOT = Path(__file__).parent

def parse_file_operations(editor_output: str) -> list[dict]:
  """Parse the Editor's structured output into a list of file operations."""
  ops = []
  pattern = re.compile(r"---FILE:\s*(.+?)---\n(.*?)---END---", re.DOTALL)
  for match in pattern.finditer(editor_output):
    path_str = match.group(1).strip()
    content = match.group(2).rstrip("\n")
    ops.append({"path": path_str, "content": content})
  return ops

def _store_editor_plan(file_ops: list[dict]) -> str:
  """Store the Editor operations and return a UUID plan_id."""
  plan_id = str(uuid.uuid4())
  _editor_plans[plan_id] = file_ops
  return plan_id

def apply_editor_plan(plan_id: str, actions: dict[str, str]) -> list[dict]:
  """
  Apply the file operations from a plan.
  actions = {path: "create" | "replace" | "merge" | "skip"}
  Returns the per-file result list.
  """
  file_ops = _editor_plans.pop(plan_id, [])
  results = []

  for op in file_ops:
    rel_path = op["path"]
    content = op["content"]
    action  = actions.get(rel_path, "create")

    if action == "skip":
      results.append({"path": rel_path, "status": "skipped"})
      continue

    # Safety: resolve the path and ensure it stays inside the project
    full_path = (PROJECT_ROOT / rel_path).resolve()
    try:
      full_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
      results.append({"path": rel_path, "status": "error",
              "message": "Path outside the project root — rejected."})
      continue

    if action == "merge" and full_path.exists():
      existing = full_path.read_text(encoding="utf-8")
      merge_prompt = (
        f"Merge these two versions of the file '{rel_path}' intelligently.\n"
        f"Keep the best parts of both. Return ONLY the merged content.\n\n"
        f"=== EXISTING VERSION ===\n{existing}\n\n"
        f"=== NEW VERSION ===\n{content}"
      )
      content = call_ollama(VIBE_CODE_AGENT_PROMPTS["editeur"], merge_prompt)

    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"[EDITOR] ✅ {action.upper()} -> {rel_path}")
    results.append({"path": rel_path, "status": action})

  return results

def run_vibe_code_pipeline(user_request: str):
  """
  Multi-agent pipeline for vibe coding.
  Yields structured event dicts that can be sent as SSE.
  Order: Architect -> [Developer ↔ Reviewer] max 2 rounds -> Tester -> Architect (green light) -> Editor.
  """
  review = ""

  # Phase 1: Architect — analysis and plan
  print(f"\n{'='*60}")
  print(f"[ARCHITECT] Breaking down the request...")
  yield {"type": "pipeline_agent", "agent": "architecte", "phase": "start"}

  arch_prompt = (
    f"Analyze this development request and produce a structured implementation plan "
    f"with numbered atomic tasks and the technical dependencies to check:\n\n"
    f"{user_request}"
  )
  plan_tokens: list[str] = []
  for token in _stream_fast("architecte", arch_prompt):
    plan_tokens.append(token)
    print(token, end="", flush=True)
    yield {"type": "pipeline_token", "agent": "architecte", "text": token}
  plan = "".join(plan_tokens)
  print(f"\n[ARCHITECT] Plan established ({len(plan_tokens)} tokens).")
  yield {"type": "pipeline_agent", "agent": "architecte", "phase": "done"}

  # Phase 2: Developer + Reviewer (1 iteration, correction if rejected)
  # Context trim: cap the plan to avoid huge inputs
  plan_short = plan[:1500]
  code = ""
  for iteration in range(2):
    if iteration == 0:
      dev_prompt = (
        f"Request:\n{user_request}\n\n"
        f"Plan:\n{plan_short}\n\n"
        f"Write the complete and functional code."
      )
    else:
      dev_prompt = (
        f"Request:\n{user_request}\n\n"
        f"Reviewer issues:\n{review[:600]}\n\n"
        f"Previous code:\n{code[:2000]}\n\n"
        f"Fix only the listed problems."
      )
      print(f"\n[DEVELOPER] Writing code (iteration {iteration + 1})...")
    yield {"type": "pipeline_agent", "agent": "developpeur", "phase": "start"}

    code_tokens: list[str] = []
    for token in _stream_fast("developpeur", dev_prompt):
      code_tokens.append(token)
      print(token, end="", flush=True)
      yield {"type": "pipeline_token", "agent": "developpeur", "text": token}
    code = "".join(code_tokens)
    print(f"\n[DEVELOPER] Code produced ({len(code_tokens)} tokens).")
    yield {"type": "pipeline_agent", "agent": "developpeur", "phase": "done"}

    # Reviewer
    review_prompt = f"Plan:\n{plan_short}\n\nCode to review:\n{code[:2500]}"
    print(f"\n[REVIEWER] Review in progress...")
    yield {"type": "pipeline_agent", "agent": "reviseur", "phase": "start"}

    review_tokens: list[str] = []
    for token in _stream_fast("reviseur", review_prompt):
      review_tokens.append(token)
      print(token, end="", flush=True)
      yield {"type": "pipeline_token", "agent": "reviseur", "text": token}
    review = "".join(review_tokens)
    print(f"\n[REVIEWER] Review complete.")
    yield {"type": "pipeline_agent", "agent": "reviseur", "phase": "done"}

    # Stop once the code is approved
    if "✅" in review or any(kw in review.lower() for kw in [
      "approved", "code approved", "no issues", "no issue", "lgtm", "looks good"
    ]):
      print("[REVIEWER] ✅ Code approved, moving to tester.")
      break

  # Phase 3: Tester
  test_prompt = (
    f"Request:\n{user_request}\n\n"
    f"Code to test:\n{code[:2500]}\n\n"
    f"Simulate the execution and validate it."
  )
  print(f"\n[TESTER] Tests in progress...")
  yield {"type": "pipeline_agent", "agent": "testeur", "phase": "start"}

  test_tokens: list[str] = []
  for token in _stream_fast("testeur", test_prompt):
    test_tokens.append(token)
    print(token, end="", flush=True)
    yield {"type": "pipeline_token", "agent": "testeur", "text": token}
  test_result = "".join(test_tokens)
  print(f"\n[TESTER] Tests complete.")
  yield {"type": "pipeline_agent", "agent": "testeur", "phase": "done"}

  # Phase 4: Architect — final green light
  final_prompt = (
    f"Request: {user_request}\n\n"
    f"Produced code (excerpt):\n{code[:1200]}\n\n"
    f"Tests: {test_result[:400]}\n\n"
    f"Summarize in at most 5 lines what was implemented and how to use it."
  )
  print(f"\n[ARCHITECT] Final validation...")
  yield {"type": "pipeline_agent", "agent": "architecte", "phase": "start"}

  for token in _stream_fast("architecte", final_prompt):
    print(token, end="", flush=True)
    yield {"type": "pipeline_token", "agent": "architecte", "text": token}
  print(f"\n[ARCHITECT] Green light given.")
  yield {"type": "pipeline_agent", "agent": "architecte", "phase": "done"}

  # Phase 5: Editor — file plan generation
  editor_prompt = (
    f"Request: {user_request}\n\n"
    f"Final code:\n{code[:3000]}\n\n"
    f"Generate the files to create using the format ---FILE: path--- [content] ---END---"
  )
  print(f"\n[EDITOR] Generating the file plan...")
  yield {"type": "pipeline_agent", "agent": "editeur", "phase": "start"}

  editor_tokens: list[str] = []
  for token in _stream_fast("editeur", editor_prompt):
    editor_tokens.append(token)
    print(token, end="", flush=True)
    yield {"type": "pipeline_token", "agent": "editeur", "text": token}
  editor_output = "".join(editor_tokens)
  print(f"\n[EDITOR] Plan generated.")
  yield {"type": "pipeline_agent", "agent": "editeur", "phase": "done"}

  # Parse the file operations and check whether they already exist
  file_ops = parse_file_operations(editor_output)
  project_root = Path(__file__).parent
  for op in file_ops:
    op["exists"] = (project_root / op["path"]).is_file()

  if file_ops:
    # Store the plan so /api/editor/apply can access it
    plan_id = _store_editor_plan(file_ops)
    yield {
      "type": "editor_plan",
      "plan_id": plan_id,
      "files": [{"path": op["path"], "exists": op["exists"]} for op in file_ops],
    }

  print(f"{'='*60}")
  print(f"[PIPELINE] Finished.")

def _vibe_code_cli(question: str) -> str:
  """Synchronous CLI wrapper — the pipeline prints everything to the terminal."""
  for _ in run_vibe_code_pipeline(question):
    pass
  return "[Vibe-code pipeline finished — see the logs above]"

# Add after definition to avoid forward reference issues
# route_question sorts by key length, so dict order does not matter
AGENTS["vibe_code"] = _vibe_code_cli

# ==============================================================================
# Router Agent
# ==============================================================================

ROUTER_SYSTEM_PROMPT = """You are a router agent. Your only role is to read the user's question and decide which expert should answer it.

The available experts are:
- "vibe_code": develop, create, implement, write a program, function, script, or application (new code production).
- "code": explain code, answer programming questions, debug existing code.
- "general": all other questions (science, culture, history, current events, advice, etc.).
- "writer": when the user explicitly asks for a text, document, report, letter, or summary.

Reply ONLY with the matching keyword: either "vibe_code", "code", "general", or "writer".
Do not add any explanation, punctuation, or extra text."""

def route_question(question: str) -> str:
  """Routing only — returns the agent key without calling the expert."""
  print(f"\n[Router] Question received: {question[:80]}{'...' if len(question) > 80 else ''}")
  print("[Router] Analysis in progress...")
  raw = call_ollama(ROUTER_SYSTEM_PROMPT, question).strip().lower()
  # Exact match first, then substring search starting with the longest keys
  if raw in AGENTS:
    chosen = raw
  else:
    chosen = next(
      (key for key in sorted(AGENTS.keys(), key=len, reverse=True) if key in raw),
      "general",
    )
  print(f"[Router] -> Delegating to: '{chosen}'")
  return chosen

def stream_expert(agent_key: str, question: str):
  """Generate the expert response token by token, with terminal logging."""
  print(f"[{agent_key.upper()}] Generation in progress...")
  system_prompt = AGENT_SYSTEM_PROMPTS[agent_key]
  token_count = 0
  for token in call_ollama_stream(system_prompt, question):
    token_count += 1
    print(token, end="", flush=True)
    yield token
  print(f"\n[{agent_key.upper()}] Finished ({token_count} tokens).")

def router_agent(question: str) -> str:
  """
  Analyze the question, choose the right expert, and return its answer.
  Used by the interactive CLI mode.
  """
  print(f"\n[Router] Analyzing the question...")
  chosen_key = route_question(question)

  print(f"[Router] -> Delegating to agent: '{chosen_key}'")
  print("-" * 60)

  return AGENTS[chosen_key](question), chosen_key

# ==============================================================================
# Affichage des agents disponibles
# ==============================================================================

def print_agents() -> None:
  print("\nAvailable agents:")
  for key, description in AGENT_DESCRIPTIONS.items():
    print(f" [{key}] {description}")
  print()

# ==============================================================================
# Boucle interactive
# ==============================================================================

def interactive_mode() -> None:
  """Ask questions in a loop until the user types 'quit'."""
  print_agents()
  print("Ask your questions (type 'quit' or leave empty to stop).")
  print("-" * 60)

  while True:
    try:
      question = input("\nYour question: ").strip()
    except (EOFError, KeyboardInterrupt):
      print("\nGoodbye!")
      break

    if not question or question.lower() in {"exit", "quit", "stop"}:
      print("Goodbye!")
      break

    answer, agent_key = router_agent(question)
    print(f"\n[Agent: {agent_key}]")
    print(f"\nAnswer:\n{answer}")
    print("=" * 60)

# ==============================================================================
# Entry point
# ==============================================================================

if __name__ == "__main__":
  print("=" * 60)
  print(" Stark Industries — Local Multi-Agent System")
  print(f" Model: {MODEL}")
  print("=" * 60)

  interactive_mode()
