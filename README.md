# Pytube API (FastAPI + yt-dlp)

API simples para baixar vídeos do YouTube usando **FastAPI** + **yt-dlp**.

## 🚀 Rodar localmente
```bash
# criar ambiente virtual (opcional)
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# instalar dependências
pip install -r requirements.txt

# rodar servidor
uvicorn main:app --reload