from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API LoadTube está online 🚀"}

# 1️⃣ Listar formatos (vídeo e áudio)
@app.post("/formats")
async def get_formats(request: Request):
    data = await request.json()
    url = data.get("url")

    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info["formats"]:
            entry = {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "type": "audio" if f.get("vcodec") == "none" else "video",
                "resolution": f.get("resolution") or f"{f.get('width')}x{f.get('height')}" if f.get("height") else "audio only",
                "filesize": f.get("filesize")
            }
            formats.append(entry)
    return JSONResponse(content=formats)

# 2️⃣ Download em formato escolhido (vídeo ou áudio)
@app.post("/download")
async def download_media(request: Request):
    data = await request.json()
    url = data.get("url")
    format_id = data.get("format_id", "best")

    ydl_opts = {
        "format": format_id,
        "quiet": True,
    }

    def generate():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]

            with requests.get(stream_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

    # Se for áudio, muda o tipo de mídia
    media_type = "audio/mpeg" if format_id.startswith("audio") else "video/mp4"

    return StreamingResponse(generate(), media_type=media_type)
