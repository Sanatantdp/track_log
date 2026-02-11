from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import base64
import json
import httpx
from datetime import datetime

app = FastAPI()

WEBHOOK_URL = "https://geography-deemed-what-les.trycloudflare.com/receive-log" 

def get_client_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


@app.post("/log")
async def log_api(request: Request):
    try:
        body = await request.json()
        raw = body.get("p")
        decoded = base64.b64decode(raw).decode("utf-8")
        decoded = decoded.replace("x9A@1", "", 1)
        data = json.loads(decoded)
    except Exception:
        data = {}

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": get_client_ip(request),
        "full_url": data.get("u"),
        "referrer": data.get("r"),
    }

    # Call second API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(WEBHOOK_URL, json=log_data)

        if response.status_code == 200:
            return JSONResponse({"status": "ok"})
        else:
            return JSONResponse(
                {"status": "failed", "reason": "Webhook error"},
                status_code=500
            )

    except Exception as e:
        return JSONResponse(
            {"status": "failed", "error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "track:app",
        host="0.0.0.0",
        port=5484,
        reload=False
    )
