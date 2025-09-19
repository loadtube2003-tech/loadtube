from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import yt_dlp
import tempfile
import os

app = FastAPI()

@app.get("/download")
def download_video(url: str = Query(..., description="URL do vídeo do YouTube")):
    # Cria arquivo temporário no servidor (só enquanto transmite)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.close()

    ydl_opts = {
        "format": "best",
        "outtmpl": temp_file.name,  # salva temporariamente
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Função para transmitir e apagar o arquivo após envio
    def iterfile():
        with open(temp_file.name, mode="rb") as file:
            yield from file
        os.remove(temp_file.name)  # limpa após enviar

    filename = "video.mp4"
    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
