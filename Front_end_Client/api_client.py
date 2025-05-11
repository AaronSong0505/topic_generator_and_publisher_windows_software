import requests

API_BASE_URL = 'http://127.0.0.1:8000'  # 根据实际后端地址调整
LLM_AGENT_URL = 'http://127.0.0.1:8001'  # llm_agent服务地址


def start_emulator():
    resp = requests.post(f'{API_BASE_URL}/emulator/start')
    return resp.json()


def stop_emulator():
    resp = requests.post(f'{API_BASE_URL}/emulator/stop')
    return resp.json()


def get_emulator_status():
    resp = requests.get(f'{API_BASE_URL}/emulator/status')
    return resp.json()


def generate_xhs_copy_and_prompt(topic, debug=False):
    resp = requests.post(f'{LLM_AGENT_URL}/llm_generate', json={"topic": topic, "debug": debug}, timeout=120)
    return resp.json() 