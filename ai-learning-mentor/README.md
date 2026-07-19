# AI Learning Mentor

A working prototype of the AI Learning Mentor agent from the Lean Canvas / SDG 4 project.
Flask backend + HTML/CSS/JS frontend, powered by the Groq API. Two features:

- **Doubt Chat** — conversational, step-by-step help with academic questions, personalised
  to the student's name, grade, subject and language.
- **Study Planner** — generates a day-by-day study plan from subject, topics, days available
  and hours/day.

---

## 1. Project structure

```
mentor-app/
├── app.py               # Flask backend (routes + Groq calls)
├── requirements.txt
├── Procfile              # tells Render how to start the app
├── render.yaml            # optional one-click Render blueprint
├── .env.example           # copy to .env locally, never commit .env
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

---

## 2. Running locally on Windows 7

Windows 7 can't run modern Python (3.9+ dropped Win7 support), so use the
**last Python release that still supports Windows 7: Python 3.8.10**.

1. **Install Python 3.8.10**
   Download the "Windows x86-64 executable installer" from:
   `https://www.python.org/downloads/release/python-3810/`
   During install, tick **"Add Python 3.8 to PATH"**.

2. **Open Command Prompt in the project folder** and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Add your Groq API key.**
   Copy `.env.example` to `.env` and paste your key:
   ```
   copy .env.example .env
   ```
   Then edit `.env` in Notepad so it reads:
   ```
   GROQ_API_KEY=gsk_your_real_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

5. **Run the app:**
   ```
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

If `pip install` fails on `groq` or `gunicorn`, run
`python -m pip install --upgrade pip` first, then retry.

---

## 3. Deploying to Render (to keep it live)

1. **Push this folder to a GitHub repository** (Render deploys from GitHub/GitLab).
   ```
   git init
   git add .
   git commit -m "AI Learning Mentor"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
   `.env` is already in `.gitignore` — your API key won't be pushed.

2. **Create the service on Render:**
   - Go to [render.com](https://render.com) → **New +** → **Web Service**.
   - Connect your GitHub repo.
   - Render should auto-detect Python. If not, set manually:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free is fine to start.

3. **Add your environment variable:**
   - In the service's **Environment** tab, add:
     - `GROQ_API_KEY` = your actual Groq key
     - `GROQ_MODEL` = `llama-3.3-70b-versatile` (or another Groq model)

4. **Deploy.** Render builds and gives you a live URL like
   `https://ai-learning-mentor.onrender.com`.

   (If you'd rather use the included `render.yaml` blueprint: on Render choose
   **New + → Blueprint**, point it at the repo, and it will read `render.yaml`
   automatically — you'll just be prompted to paste in `GROQ_API_KEY`.)

**Note:** on Render's free tier, the service sleeps after 15 minutes of no
traffic and takes ~30-50 seconds to wake up on the next request — this is
normal and not a bug in the app.

---

## 4. Getting a Groq API key

1. Go to `https://console.groq.com`
2. Sign in → **API Keys** → **Create API Key**
3. Copy the key (starts with `gsk_...`) into your `.env` (local) or Render's
   environment variables (deployed).

---

## 5. Customising

- **Mentor persona / behaviour:** edit `build_system_prompt()` in `app.py`.
- **Study plan formatting:** edit `STUDY_PLAN_SYSTEM_PROMPT` in `app.py`.
- **Model:** change `GROQ_MODEL` — see available models at
  `https://console.groq.com/docs/models`.
- **Colours/branding:** edit the CSS variables at the top of `static/style.css`.

## 6. Known limitations (good to mention in your concept note)

- No database yet — chat history and profile live only in the browser
  (`localStorage` for profile, in-memory array for chat), so nothing persists
  across devices or is tracked centrally.
- No authentication — anyone with the link can use it.
- No rate limiting — a public Render URL could rack up Groq API usage if shared
  widely; fine for a class demo, worth adding for real deployment.
