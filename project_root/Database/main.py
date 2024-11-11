from fastapi import FastAPI, File, UploadFile
import shutil
from pathlib import Path

app = FastAPI()

uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_path = uploads_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully"}