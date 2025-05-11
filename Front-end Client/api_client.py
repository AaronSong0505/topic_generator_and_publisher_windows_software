import requests

API_BASE_URL = 'http://127.0.0.1:8000'  # 根据实际后端地址调整


def start_emulator():
    resp = requests.post(f'{API_BASE_URL}/emulator/start')
    return resp.json()


def stop_emulator():
    resp = requests.post(f'{API_BASE_URL}/emulator/stop')
    return resp.json()


def get_emulator_status():
    resp = requests.get(f'{API_BASE_URL}/emulator/status')
    return resp.json() 