# AI Real Estate Transformation — Lead-to-CRM Demo

This is a working prototype for Jay Ho's **AI Real Estate Transformation** offer. It demonstrates the first module: a lead capture form, AI voice qualification, and CRM dashboard.

## What it does

1. **Landing page** — captures real estate agency/brokerage lead info.
2. **CRM storage** — saves leads to SQLite.
3. **AI voice qualification** — simulates an AI phone call that asks qualifying questions and scores the lead.
4. **CRM dashboard** — shows leads, qualification status, and call transcripts.

## Run it locally

```bash
cd ai-real-estate-demo
uv run python main.py
```

Then open:
- Landing page: http://localhost:8000/
- CRM dashboard: http://localhost:8000/dashboard

## Architecture

- **Backend:** FastAPI + SQLite (async via `aiosqlite`)
- **Frontend:** plain HTML/CSS/JS
- **AI voice:** simulated in `ai_voice.py` — replace with Bland, Retell, Vapi, or Twilio in production

## Production swap-outs

Replace the simulated `run_ai_qualification()` in `ai_voice.py` with a real provider:

- **Bland AI** (`bland.ai`) — phone calls via API
- **Retell AI** (`retellai.com`) — voice agents
- **Vapi** (`vapi.ai`) — voice AI infrastructure
- **Twilio + OpenAI realtime** — custom voice pipeline

Connect the CRM to:
- GoHighLevel
- Follow Up Boss
- kvCORE
- LionDesk
- HubSpot

## API endpoints

| Method | Endpoint | Description |
|--------|----------|---------------|
| GET | `/` | Landing page with lead form |
| GET | `/dashboard` | CRM dashboard |
| POST | `/api/leads` | Submit a new lead |
| GET | `/api/leads` | List leads |
| GET | `/api/leads/{id}` | Get lead + calls |
| POST | `/api/leads/{id}/call` | Run AI qualification call |
| GET | `/api/leads/{id}/call-stream` | Stream the call via SSE |
| GET | `/api/calls/{id}` | Get call record |

## Next steps

1. Add real AI voice provider integration.
2. Add SMS/email follow-up sequences.
3. Connect to a real CRM via webhooks or API.
4. Add Stripe billing for setup fees + retainers.
5. Add agency onboarding checklist and reporting dashboard.
6. Deploy to Vercel / Render / Railway for live demos.