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
    quality = data.get("quality", "best")  # valor padrão = melhor qualidade

    # Mapeamento de qualidades para yt-dlp
    quality_map = {
        "audio": "bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "best": "best"
    }

    ydl_opts = {
        "format": quality_map.get(quality, "best"),
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

    # Ajustar o tipo de mídia dependendo da escolha
    media_type = "audio/mpeg" if quality == "audio" else "video/mp4"
    return StreamingResponse(generate(), media_type=media_type)
