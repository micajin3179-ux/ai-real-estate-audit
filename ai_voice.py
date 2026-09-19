import asyncio
from datetime import datetime

# Simulated AI voice qualification flow.
# In production, replace this with a real provider like Bland, Retell, or Vapi.

QUALIFICATION_QUESTIONS = [
    "Are you currently running Facebook or Instagram ads for your listings?",
    "How many agents are in your office or brokerage?",
    "What's your biggest frustration with lead follow-up right now?",
    "Would you be interested in an AI system that qualifies and books appointments automatically?",
]

POSITIVE_KEYWORDS = ["yes", "yeah", "sure", "interested", "definitely", "absolutely", "book", "appointment", "help", "frustrated", "waste", "missing", "slow"]
NEGATIVE_KEYWORDS = ["no", "not", "never", "stop", "remove", "don\'t call", "do not call", "wrong number"]


def simulate_lead_response(question: str) -> str:
    """Simulate what a lead might say. Replace with real transcription in production."""
    lowered = question.lower()
    if "running" in lowered:
        return "Yeah, we run some ads, but the follow-up is terrible."
    if "agents" in lowered:
        return "We have about twelve agents."
    if "frustration" in lowered:
        return "Leads come in and nobody calls them fast enough. We lose a lot."
    if "interested" in lowered:
        return "Yes, that sounds exactly like what we need."
    return "Okay, tell me more."


def score_transcript(transcript: list[dict]) -> dict:
    """Score the simulated conversation for qualification."""
    full_text = " ".join([turn["text"] for turn in transcript]).lower()
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in full_text)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in full_text)

    score = positive_count - negative_count * 2
    qualified = score >= 3

    if negative_count >= 2:
        outcome = "not_interested"
    elif qualified:
        outcome = "qualified_booked"
    else:
        outcome = "follow_up_needed"

    summary_parts = []
    if "ads" in full_text or "facebook" in full_text or "instagram" in full_text:
        summary_parts.append("Currently running Meta ads.")
    if any(kw in full_text for kw in ["twelve", "10", "15", "20", "30", "50", "agents", "brokerage", "office"]):
        summary_parts.append("Multi-agent office or brokerage.")
    if any(kw in full_text for kw in ["follow-up", "follow up", "terrible", "lose", "fast", "slow", "nobody", "frustration"]):
        summary_parts.append("Pain point around lead follow-up speed.")
    if qualified:
        summary_parts.append("Expressed strong interest in AI qualification.")

    summary = " ".join(summary_parts) if summary_parts else "Initial conversation completed."

    return {
        "qualified": qualified,
        "outcome": outcome,
        "summary": summary,
        "score": score,
    }


async def run_ai_qualification(lead: dict, live_updates=None):
    """
    Run a simulated AI voice qualification call.
    `live_updates` is an optional async callback(text) to stream transcript lines.
    Returns a dict with transcript, summary, outcome, qualified.
    """
    transcript = []

    # AI greeting
    greeting = f"Hi {lead.get('name', 'there')}, this is Alex from the AI Real Estate team. I saw you were interested in help with listing ads and lead follow-up. Do you have a quick minute?"
    transcript.append({"speaker": "AI", "text": greeting, "time": datetime.utcnow().isoformat()})
    if live_updates:
        await live_updates(f"AI: {greeting}")
    await asyncio.sleep(1)

    # Lead simulated response
    lead_response = "Yes, I have a minute."
    transcript.append({"speaker": "Lead", "text": lead_response, "time": datetime.utcnow().isoformat()})
    if live_updates:
        await live_updates(f"Lead: {lead_response}")
    await asyncio.sleep(0.8)

    for question in QUALIFICATION_QUESTIONS:
        transcript.append({"speaker": "AI", "text": question, "time": datetime.utcnow().isoformat()})
        if live_updates:
            await live_updates(f"AI: {question}")
        await asyncio.sleep(1.2)

        response = simulate_lead_response(question)
        transcript.append({"speaker": "Lead", "text": response, "time": datetime.utcnow().isoformat()})
        if live_updates:
            await live_updates(f"Lead: {response}")
        await asyncio.sleep(1)

    # AI close
    close = "Thanks for your time. I’ll have our team send you a short audit showing how we can plug this into your office this week."
    transcript.append({"speaker": "AI", "text": close, "time": datetime.utcnow().isoformat()})
    if live_updates:
        await live_updates(f"AI: {close}")
    await asyncio.sleep(0.8)

    result = score_transcript(transcript)
    return {
        "transcript": transcript,
        "summary": result["summary"],
        "outcome": result["outcome"],
        "qualified": result["qualified"],
        "score": result["score"],
    }