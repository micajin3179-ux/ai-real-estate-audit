import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import (
    init_db,
    create_lead,
    get_lead,
    get_leads,
    update_lead_status,
    create_call,
    get_call,
    get_calls_for_lead,
    complete_call,
)
from ai_voice import run_ai_qualification

BASE_DIR = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="AI Real Estate Transformation Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.post("/api/leads")
async def api_create_lead(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    agency: str = Form(None),
    role: str = Form(None),
    interest: str = Form(None),
    source: str = Form("demo"),
):
    lead = await create_lead(
        name=name,
        phone=phone,
        email=email,
        agency=agency,
        role=role,
        interest=interest,
        source=source,
    )
    return JSONResponse({"success": True, "lead": lead})


@app.get("/api/leads")
async def api_get_leads(limit: int = 100, offset: int = 0):
    leads = await get_leads(limit=limit, offset=offset)
    return {"leads": leads}


@app.get("/api/leads/{lead_id}")
async def api_get_lead(lead_id: int):
    lead = await get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    calls = await get_calls_for_lead(lead_id)
    return {"lead": lead, "calls": calls}


@app.post("/api/leads/{lead_id}/call")
async def api_start_call(lead_id: int):
    lead = await get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    call = await create_call(lead_id, status="in_progress")
    await update_lead_status(lead_id, "calling")

    # Run qualification synchronously for the demo (in production, hand off to async worker)
    result = await run_ai_qualification(lead)

    transcript_json = json.dumps(result["transcript"], indent=2)
    await complete_call(
        call_id=call["id"],
        transcript=transcript_json,
        summary=result["summary"],
        outcome=result["outcome"],
    )

    new_status = "qualified" if result["qualified"] else "needs_review"
    await update_lead_status(
        lead_id=lead_id,
        status=new_status,
        qualified=result["qualified"],
        notes=result["summary"],
        call_transcript=transcript_json,
    )

    return {
        "success": True,
        "call_id": call["id"],
        "lead_id": lead_id,
        "qualified": result["qualified"],
        "outcome": result["outcome"],
        "summary": result["summary"],
        "transcript": result["transcript"],
    }


@app.get("/api/calls/{call_id}")
async def api_get_call(call_id: int):
    call = await get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"call": call}


@app.get("/api/leads/{lead_id}/call-stream")
async def api_call_stream(lead_id: int):
    """Server-sent events stream of a simulated AI voice call."""
    lead = await get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    call = await create_call(lead_id, status="in_progress")
    await update_lead_status(lead_id, "calling")

    transcript_lines = []

    async def event_stream():
        async def live_update(text):
            transcript_lines.append(text)
            yield f"data: {json.dumps({'type': 'transcript', 'text': text})}\n\n"

        result = await run_ai_qualification(lead, live_updates=live_update)

        transcript_json = json.dumps(result["transcript"], indent=2)
        await complete_call(
            call_id=call["id"],
            transcript=transcript_json,
            summary=result["summary"],
            outcome=result["outcome"],
        )

        new_status = "qualified" if result["qualified"] else "needs_review"
        await update_lead_status(
            lead_id=lead_id,
            status=new_status,
            qualified=result["qualified"],
            notes=result["summary"],
            call_transcript=transcript_json,
        )

        yield f"data: {json.dumps({'type': 'done', 'call_id': call['id'], 'qualified': result['qualified'], 'outcome': result['outcome'], 'summary': result['summary']})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)