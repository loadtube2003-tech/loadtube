from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

# CORS (permitindo qualquer origem - ajuste em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOADS_PATH = "downloads"
os.makedirs(DOWNLOADS_PATH, exist_ok=True)

# Configurações do yt-dlp
YDL_OPTS = {
    "outtmpl": os.path.join(DOWNLOADS_PATH, "%(title)s.%(ext)s"),
    "format": "best[ext=mp4]",
    "noplaylist": True
}

def _download_now(url: str):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return os.path.basename(filename)

def _get_filename_from_url(url: str):
    with yt_dlp.YoutubeDL({**YDL_OPTS}) as ydl:
        info = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info)
        return os.path.basename(filename)

@app.get("/download")
def download_video(url: str):
    """Download síncrono - espera o vídeo baixar antes de responder"""
    try:
        filename = _download_now(url)
        return {"status": "success", "file": filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/download_async")
def download_video_async(url: str, background_tasks: BackgroundTasks):
    """Download assíncrono - inicia em background e responde antes de terminar"""
    try:
        filename = _get_filename_from_url(url)
        background_tasks.add_task(_download_now, url)
        return {"status": "processing", "file": filename, "message": "Download iniciado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/get_file")
def get_file(file: str):
    """Retorna o arquivo baixado se existir"""
    file_path = os.path.join(DOWNLOADS_PATH, file)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=file)
    return {"status": "error", "message": "Arquivo não encontrado"}