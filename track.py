from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from urllib.parse import urlparse
import json
import base64
import os
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
LOG_FILE = "video_access.log"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)

def get_client_ip(request: Request):
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def write_log(data: dict):
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

@app.post("/log")
async def log_api(request: Request):
    try:
        body = await request.json()
        raw = body.get("p")                      # ✅ FIXED
        decoded = base64.b64decode(raw).decode("utf-8")
        decoded = decoded.replace("x9A@1", "", 1)
        data = json.loads(decoded)
    except Exception:
        data = {}

    log_data = {
    "ip": get_client_ip(request),
    "host": request.headers.get("host"),
    
    "diamond_id": data.get("d"),
    "full_url": data.get("u"),
    "referrer": data.get("r"),
    }
    write_log(log_data)
    print(log_data)

    return JSONResponse({"status": "ok"})
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "track:app",
        host="0.0.0.0",
        port=5484,
        reload=False
    )
