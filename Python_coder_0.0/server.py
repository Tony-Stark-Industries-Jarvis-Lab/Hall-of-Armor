from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from pathlib import Path
import json
import re
import app as agents_module

# ==============================================================================
# Flask app
# ==============================================================================

BASE_DIR   = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = BASE_DIR / "asset office"

flask_app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


# ── Routes ────────────────────────────────────────────────────────────────────

@flask_app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


@flask_app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve images from the 'asset office/' directory."""
    return send_from_directory(str(ASSETS_DIR), filename)


@flask_app.route("/api/agents", methods=["GET"])
def get_agents():
    """Return the list of available agents."""
    agents = [
        {"key": key, "description": desc}
        for key, desc in agents_module.AGENT_DESCRIPTIONS.items()
    ]
    return jsonify(agents)


@flask_app.route("/api/chat", methods=["POST"])
def chat():
    """
        SSE (Server-Sent Events) endpoint.
        The client receives events as they arrive:
            1. {"type":"routing","agent":"code"}   ← as soon as routing is decided
            2. {"type":"token","text":"..."}        ← each response token
            3. {"type":"file","path":"..."}         ← only for the writer agent
            4. {"type":"done"}                      ← end of the stream
    """
    data     = request.get_json(force=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "The question cannot be empty."}), 400

    def generate():
        try:
            # Phase 1: routing
            agent_key = agents_module.route_question(question)
            yield f"data: {json.dumps({'type': 'routing', 'agent': agent_key})}\n\n"

            # Phase 2a: vibe_code pipeline
            if agent_key == "vibe_code":
                for step in agents_module.run_vibe_code_pipeline(question):
                    yield f"data: {json.dumps(step)}\n\n"

            # Phase 2b: standard agent (streaming)
            else:
                full_tokens: list[str] = []
                for token in agents_module.stream_expert(agent_key, question):
                    full_tokens.append(token)
                    yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"

                # Save a file for the writer agent
                if agent_key == "writer":
                    content = "".join(full_tokens)
                    slug = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", question.strip())[:50].strip("_")
                    filepath = agents_module.OUTPUT_DIR / f"{slug}.txt"
                    agents_module.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                    filepath.write_text(content, encoding="utf-8")
                    yield f"data: {json.dumps({'type': 'file', 'path': str(filepath)})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@flask_app.route("/api/editor/apply", methods=["POST"])
def editor_apply():
    """
        Apply the Editor's file plan.
        Body: {
      "plan_id": "uuid",
      "actions": {"chemin/fichier.py": "create"|"replace"|"merge"|"skip", ...}
    }
    """
    data     = request.get_json(force=True) or {}
    plan_id  = data.get("plan_id", "").strip()
    actions  = data.get("actions", {})

    if not plan_id:
        return jsonify({"error": "Missing plan_id."}), 400

    results = agents_module.apply_editor_plan(plan_id, actions)
    return jsonify({"results": results})


# ==============================================================================
# Entry point
# ==============================================================================

if __name__ == "__main__":
    STATIC_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("  Stark Industries — Web Interface")
    print("  -> http://127.0.0.1:5000")
    print("=" * 60)
    flask_app.run(debug=False, port=5000, threaded=True)
