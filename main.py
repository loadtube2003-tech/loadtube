from fastapi import FastAPI, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API LoadTube está online 🚀"}

# Download via GET (ex.: https://seusite.com/download?url=YOUTUBE_URL)
@app.get("/download")
def download_video_get(url: str = Query(..., description="URL do vídeo")):
    return stream_video(url)

# Download via POST (ex.: body JSON = {"url": "YOUTUBE_URL"})
@app.post("/download")
async def download_video_post(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse({"error": "URL não fornecida"}, status_code=400)
    return stream_video(url)

def stream_video(url: str):
    ydl_opts = {
        "format": "best",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info["url"]
        ext = info.get("ext", "mp4")  # tenta adivinhar a extensão
        mime_type = f"video/{ext}"

    def generate():
        with requests.get(stream_url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

    return StreamingResponse(generate(), media_type=mime_type)
