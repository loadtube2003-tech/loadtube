from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API LoadTube está online 🚀"}

@app.post("/download")
async def download_video(request: Request):
    data = await request.json()
    url = data.get("url")

    ydl_opts = {
        "format": "best",
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

    return StreamingResponse(generate(), media_type="video/mp4")
