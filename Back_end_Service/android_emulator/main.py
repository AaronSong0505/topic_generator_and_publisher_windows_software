from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import psutil
import os
import traceback

app = FastAPI()

# 允许跨域，便于前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MuMu模拟器主程序路径（请根据实际安装路径调整）
MUMU_PATH = r"D:\Program Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe"
MUMU_PROCESS_NAME = "MuMuPlayer.exe"

@app.post("/emulator/start")
def start_emulator():
    print(f"[DEBUG] MUMU_PATH: {MUMU_PATH}")
    # 检查是否已启动
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == MUMU_PROCESS_NAME:
            return {"status": "running", "msg": "模拟器已在运行"}
    try:
        subprocess.Popen([MUMU_PATH])
        return {"status": "starting", "msg": "已发送启动指令"}
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] {tb}")
        return {"status": "error", "msg": f"{e}\n{tb}"}

@app.post("/emulator/stop")
def stop_emulator():
    killed = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == MUMU_PROCESS_NAME:
            proc.kill()
            killed = True
    if killed:
        return {"status": "stopped", "msg": "已发送关闭指令"}
    else:
        return {"status": "not_running", "msg": "模拟器未在运行"}

@app.get("/emulator/status")
def emulator_status():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == MUMU_PROCESS_NAME:
            return {"status": "running"}
    return {"status": "stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 