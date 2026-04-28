"""
SalonAI Agent — Prototype
AI scheduling + client comms for independent hair salon owners
"""

import streamlit as st
import openai
from datetime import datetime, date
import os

# ── Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="SalonAI Agent", page_icon="✂️", layout="wide")

openai.api_key = os.environ.get("OPENAI_API_KEY", "")

# ── Prompt helpers ──────────────────────────────────────────────────────
SYSTEM_SALON = """You are SalonAI — an AI assistant for independent hair salon owners.
You help with:
- Smart scheduling suggestions (reduce no-shows, optimize day flow)
- Client follow-up messages (reminders, re-book prompts)
- Social media content (Instagram captions, hashtags)
- Daily/weekly task lists based on appointment flow

Be warm, practical, and concise. Speak like a helpful salon manager, not a tech bro.
Tone: friendly, professional, encouraging."""
SYSTEM_MSG = {"role": "system", "content": SYSTEM_SALON}

def ask_gpt(user_msg: str, context: str = "") -> str:
    if not openai.api_key:
        return "⚠️ OpenAI API key not set. Add OPENAI_API_KEY to your Streamlit secrets."
    messages = [SYSTEM_MSG]
    if context:
        messages.append({"role": "user", "content": context + "\n\n" + user_msg})
    else:
        messages.append({"role": "user", "content": user_msg})
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# ── Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Schedule Assistant",
    "💬 Client Messages",
    "📱 Social Content",
    "✅ Daily Tasks",
])

# ── Tab 1: Schedule Assistant ─────────────────────────────────────────
with tab1:
    st.header("📅 Schedule Assistant")
    st.caption("Paste your appointments for today — get smart suggestions to reduce no-shows and optimize flow.")

    appointments = st.text_area(
        "Paste today's appointments",
        placeholder="Example:\n9:00 AM — Maria S. (balayage, new client)\n10:30 AM — Jen L. (cut + blowdry, returning)\n12:00 PM — Blocked\n2:00 PM — Tom R. (colour retouch)\n3:30 PM — Rosa K. (cut only)",
        height=180,
    )

    if st.button("Get Suggestions", icon="💡"):
        if appointments.strip():
            with st.spinner("Thinking..."):
                prompt = f"""Today's appointments:
{appointments}

Based on this schedule, give me:
1. Any scheduling red flags (gaps, overload, conflicts)
2. Suggestions to reduce no-shows (who might need a reminder, optimal reminder timing)
3. Flow optimization tips (order of services, buffer suggestions)
4. Quick wins to improve today's efficiency

Be specific and actionable. Keep it under 300 words."""
                result = ask_gpt(prompt)
            st.success("Here's what I found:")
            st.markdown(result)
        else:
            st.warning("Paste some appointments first!")

    with st.expander("💡 Tips for better suggestions"):
        st.markdown("""
- **Include times, client names, and services** — the more detail, the better
- **Note any patterns** — chronic late-comers, first-time clients, large groups
- **Mention past no-shows** — I can flag who might need a reminder
        """)

# ── Tab 2: Client Messages ─────────────────────────────────────────────
with tab2:
    st.header("💬 Client Message Composer")
    st.caption("Pre-built templates + AI personalizer — craft the perfect reminder or re-book message.")

    msg_type = st.selectbox("What do you need?", [
        "— Select —",
        "Appointment Reminder (24hr before)",
        "Appointment Reminder (1hr before)",
        "Re-book after service",
        "Thanks for your referral!",
        "No-show / late cancellation follow-up",
    ])

    client_name = st.text_input("Client name", placeholder="e.g. Maria")
    service = st.text_input("Service they had / booked", placeholder="e.g. balayage + cut")
    custom_note = st.text_area("Anything personal to add? (optional)", placeholder="e.g. 'Loved the depth in your colour last time!'")

    if st.button("Generate Message", icon="✍️"):
        if msg_type == "— Select —":
            st.warning("Select a message type first!")
        elif not client_name.strip():
            st.warning("Enter a client name first!")
        else:
            with st.spinner("Crafting your message..."):
                prompt = f"""Write a client message for a hair salon.

Client: {client_name}
Service: {service}
Personal touch to include: {custom_note or 'none'}
Message type: {msg_type}

Write it in the tone of a friendly, professional salon — warm but not overly casual.
Keep it under 150 words. Make it feel personal, not automated.
Format as plain text (no emojis or keep them minimal)."""
                result = ask_gpt(prompt)
            st.success("Here's your message:")
            st.text_area("Copy below:", value=result, height=120, label_visibility="collapsed", key="msg_output")
            st.caption("💡 Tip: BCC yourself when sending bulk to avoid looking like spam.")

    with st.expander("📋 Message Templates"):
        st.markdown("""
**24hr Reminder:**
"Hi [Name]! Just a quick reminder — your [service] is tomorrow at [time]. We look forward to seeing you! Reply to confirm or reschedule."

**Re-book:**
"Hi [Name]! Your [service] looked amazing — thanks for coming in! To keep your colour/mind that fresh, book your next visit at [link]. See you soon!"

**No-show follow-up:**
"Hi [Name] — we missed you for your [service] today! No worries if something came up — just let us know and we can find another time. We'd love to see you back soon."
        """)

# ── Tab 3: Social Content ──────────────────────────────────────────────
with tab3:
    st.header("📱 Social Content Generator")
    st.caption("Enter the service or look — get a catchy Instagram caption + hashtags.")

    service_input = st.text_input(
        "Service or look",
        placeholder="e.g. Balayage on dark hair, coral tones, sun-kissed"
    )
    style_vibe = st.selectbox("Vibe", ["Any", "Professional / Salon Brand", "Trendy / Avant-garde", "Warm / Personal", "Bold / Promo"])

    if st.button("Generate Caption", icon="📸"):
        if not service_input.strip():
            st.warning("Enter a service or look first!")
        else:
            with st.spinner("Creating content..."):
                prompt = f"""Generate an Instagram caption for a hair salon post.

Service / Look described: {service_input}
Desired vibe: {style_vibe}

Include:
- A catchy opening line (hook)
- 2-3 sentences describing the look
- A soft call-to-action (book / DM / link in bio)

Then add 8-12 relevant hashtags on a new line.

Keep the caption under 150 words. Conversational, warm, professional.
"""
                result = ask_gpt(prompt)
            st.success("Here's your content:")
            st.markdown(result)
            st.caption("💡 Tip: Mix it up — the same prompt gives different results each time. Run it twice and pick your favourite!")

# ── Tab 4: Daily Tasks ──────────────────────────────────────────────────
with tab4:
    st.header("✅ Daily / Weekly Task List")
    st.caption("Tell me your appointments or salon setup — get a prioritized to-do list.")

    task_context = st.text_area(
        "What's happening at your salon today / this week?",
        placeholder="Example:\nToday: 5 clients, 2 new. 1 colour correction walk-in possible.\nWe just switched booking software.\nI haven't posted on social in 3 days.\nSupplies arrive Wednesday.",
        height=150,
    )

    if st.button("Generate Task List", icon="📋"):
        if not task_context.strip():
            st.warning("Describe your salon day first!")
        else:
            with st.spinner("Prioritizing your day..."):
                prompt = f"""Based on this salon situation, give me a prioritized daily/weekly task list:

{task_context}

Prioritize:
- High-value tasks first (revenue-generating, client-retaining)
- Break down big tasks into bite-size steps
- Include time estimates where useful
- Flag anything urgent (within 24hrs)

Format as a clear numbered list. Keep it practical and realistic.
Maximum 10 tasks. Be specific."""
                result = ask_gpt(prompt)
            st.success("Your prioritized list:")
            st.markdown(result)

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("✂️ SalonAI Agent")
    st.caption("AI assistant for independent hair salon owners")
    st.divider()
    st.markdown("**What it does:**")
    st.markdown("✅ Smart scheduling suggestions\n✅ Client message composer\n✅ Social media captions\n✅ Daily task lists")
    st.divider()
    st.markdown(f"**Built:** {date.today().strftime('%B %d, %Y')}")
    st.caption("Prototype v1.0 — $19/mo coming soon")

# ── Footer ─────────────────────────────────────────────────────────────
st.divider()
st.caption("SalonAI Agent Prototype · Built with Streamlit + GPT-4o-mini · $19/mo launch Q2 2026")
