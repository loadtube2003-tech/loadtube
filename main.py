from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
import re

app = FastAPI()

# DURANTE TESTES: permite qualquer origem. Em produção troque para a URL do Lovable.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API LoadTube está online 🚀"}

@app.get("/download")
def download_get(url: str = Query(..., description="URL do vídeo do YouTube")):
    return stream_video(url)

@app.post("/download")
async def download_post(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    return stream_video(url)

def _safe_filename(s: str) -> str:
    return re.sub(r'[^\w\-_\. ]', '_', s).strip()

def stream_video(url: str):
    ydl_opts = {"format": "best", "quiet": True}

    # pega info / URL do stream sem baixar
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info.get("url")
        ext = info.get("ext", "mp4")
        title = info.get("title") or "video"
        filename = f"{_safe_filename(title)}.{ext}"

    if not stream_url:
        raise HTTPException(status_code=500, detail="Could not obtain stream URL from yt-dlp")

    def generate():
        with requests.get(stream_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

    return StreamingResponse(
        generate(),
        media_type=f"video/{ext}",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
