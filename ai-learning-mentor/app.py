import os
from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def build_system_prompt(profile):
    """Builds a personalised system prompt for the mentor based on the
    student's profile (sent from the frontend, kept client-side only)."""
    name = (profile or {}).get("name") or "there"
    grade = (profile or {}).get("grade") or "unspecified grade/level"
    subject = (profile or {}).get("subject") or "general subjects"
    language = (profile or {}).get("language") or "English"

    return (
        "You are Nova, a warm, patient AI Learning Mentor for school and "
        "college students. You are talking to a student named {name}, "
        "studying at the {grade} level, currently focused on {subject}. "
        "Reply in {language} unless the student switches language.\n\n"
        "How you help:\n"
        "- Resolve doubts clearly, step by step, with simple examples.\n"
        "- Never just give a final answer to a problem-solving question "
        "without showing the reasoning, so the student actually learns.\n"
        "- Check understanding briefly before moving on for multi-step topics.\n"
        "- Keep tone encouraging and never condescending.\n"
        "- Keep answers focused and not overly long unless the student asks "
        "for a deep explanation.\n"
        "- If asked something outside academics/studying, gently steer back "
        "to how you can help with learning, but you can still be friendly.\n"
    ).format(name=name, grade=grade, subject=subject, language=language)


STUDY_PLAN_SYSTEM_PROMPT = (
    "You are an expert academic study planner. Produce practical, specific, "
    "day-by-day study plans. Always format the plan as a clean markdown table "
    "or clearly labelled day-by-day list (Day 1, Day 2, ...), with concrete "
    "tasks per day, not vague advice. End with exactly two short motivational "
    "tips relevant to the plan."
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "groq_configured": bool(GROQ_API_KEY)})


@app.route("/api/chat", methods=["POST"])
def chat():
    if client is None:
        return jsonify({"error": "GROQ_API_KEY is not configured on the server."}), 500

    data = request.get_json(force=True) or {}
    messages = data.get("messages", [])
    profile = data.get("profile", {})

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    system_prompt = build_system_prompt(profile)
    groq_messages = [{"role": "system", "content": system_prompt}]

    # keep only the last 16 turns to stay within context / cost limits
    for m in messages[-16:]:
        role = m.get("role")
        content = m.get("content", "")
        if role in ("user", "assistant") and content:
            groq_messages.append({"role": role, "content": content})

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=groq_messages,
            temperature=0.6,
            max_tokens=800,
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the frontend
        return jsonify({"error": str(exc)}), 502


@app.route("/api/study-plan", methods=["POST"])
def study_plan():
    if client is None:
        return jsonify({"error": "GROQ_API_KEY is not configured on the server."}), 500

    data = request.get_json(force=True) or {}
    subject = data.get("subject", "").strip()
    topics = data.get("topics", "").strip()
    days = data.get("days", "7")
    hours = data.get("hours", "2")
    level = data.get("level", "").strip()

    if not subject:
        return jsonify({"error": "Subject is required."}), 400

    user_prompt = (
        "Create a {days}-day study plan.\n"
        "Subject: {subject}\n"
        "Topics to cover: {topics}\n"
        "Available study time: {hours} hours per day\n"
        "Student level: {level}\n"
    ).format(
        days=days,
        subject=subject,
        topics=topics or "cover the core syllabus for this subject",
        hours=hours,
        level=level or "not specified",
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": STUDY_PLAN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=1400,
        )
        plan = completion.choices[0].message.content
        return jsonify({"plan": plan})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
