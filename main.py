import os
import time
import pygame
import tempfile
import multiprocessing
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Pygame 초기화 함수
def init_pygame():
    pygame.init()
    pygame.mixer.init()

# MIDI 파일 재생 함수
def play_midi_file(midi_filename, volume):
    init_pygame()
    pygame.mixer.music.set_volume(volume)
    try:
        pygame.mixer.music.load(midi_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except pygame.error as e:
        print(f"파일을 재생하는 동안 오류가 발생했습니다: {e}")

# MIDI 파일 재생을 위한 엔드포인트
def create_play_midi_endpoint(name):
    @app.post(f"/{name}")
    async def play_midi(file: UploadFile, volume: float = 0.5):
        if not file.filename.endswith((".mid", ".midi")):
            raise HTTPException(status_code=400, detail="Invalid file type. Only .mid and .midi files are allowed.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_file:
            tmp_file.write(file.file.read())
            midi_filename = tmp_file.name

        p = multiprocessing.Process(target=play_midi_file, args=(midi_filename, volume))
        p.start()
        return JSONResponse(content={"message": f"{file.filename} 파일이 재생됩니다."})

# 엔드포인트 생성
create_play_midi_endpoint("piano")
create_play_midi_endpoint("guitar")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
