"""
SalonAI Agent — FastAPI version for Vercel deployment
"""

import os
import openai

# ── Load .env if present (local dev fallback) ────────────────────────
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)

# ── FastAPI setup ────────────────────────────────────────────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="SalonAI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── GPT Helper ────────────────────────────────────────────────────────
SYSTEM_SALON = """You are SalonAI — an AI assistant for independent hair salon owners.
You help with:
- Smart scheduling suggestions (reduce no-shows, optimize day flow)
- Client follow-up messages (reminders, re-book prompts)
- Social media content (Instagram captions, hashtags)
- Daily/weekly task lists based on appointment flow

Be warm, practical, and concise. Speak like a helpful salon manager, not a tech bro.
Tone: friendly, professional, encouraging."""

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
print(f"[SalonAI] api_key present: {bool(openai.api_key)}, len={len(openai.api_key) if openai.api_key else 0}", flush=True)

def ask_gpt(user_msg: str) -> str:
    if not openai.api_key:
        return "⚠️ OpenAI API key not configured. Set OPENAI_API_KEY in Vercel project env vars."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_SALON},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ── Routes ───────────────────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("index.html")

@app.get("/health")
def health():
    return {"status": "ok", "api_key_configured": bool(openai.api_key)}

class ScheduleRequest(BaseModel):
    appointments: str

@app.post("/api/schedule")
def api_schedule(req: ScheduleRequest):
    prompt = f"""Today's appointments:
{req.appointments}

Based on this schedule, give me:
1. Any scheduling red flags (gaps, overload, conflicts)
2. Suggestions to reduce no-shows (who might need a reminder, optimal reminder timing)
3. Flow optimization tips (order of services, buffer suggestions)
4. Quick wins to improve today's efficiency

Be specific and actionable. Keep it under 300 words."""
    return {"result": ask_gpt(prompt)}

class MessageRequest(BaseModel):
    msg_type: str
    client_name: str
    service: str
    custom_note: str = ""

@app.post("/api/message")
def api_message(req: MessageRequest):
    prompt = f"""Write a client message for a hair salon.

Client: {req.client_name}
Service: {req.service}
Personal touch to include: {req.custom_note or 'none'}
Message type: {req.msg_type}

Write it in the tone of a friendly, professional salon — warm but not overly casual.
Keep it under 150 words. Make it feel personal, not automated."""
    return {"result": ask_gpt(prompt)}

class SocialRequest(BaseModel):
    service: str
    vibe: str = "Any"

@app.post("/api/social")
def api_social(req: SocialRequest):
    prompt = f"""Generate an Instagram caption for a hair salon post.

Service / Look described: {req.service}
Desired vibe: {req.vibe}

Include:
- A catchy opening line (hook)
- 2-3 sentences describing the look
- A soft call-to-action (book / DM / link in bio)

Then add 8-12 relevant hashtags on a new line.

Keep the caption under 150 words. Conversational, warm, professional."""
    return {"result": ask_gpt(prompt)}

class TaskRequest(BaseModel):
    context: str

@app.post("/api/tasks")
def api_tasks(req: TaskRequest):
    prompt = f"""Based on this salon situation, give me a prioritized daily/weekly task list:

{req.context}

Prioritize:
- High-value tasks first (revenue-generating, client-retaining)
- Break down big tasks into bite-size steps
- Include time estimates where useful
- Flag anything urgent (within 24hrs)

Format as a clear numbered list. Maximum 10 tasks. Be specific."""
    return {"result": ask_gpt(prompt)}
