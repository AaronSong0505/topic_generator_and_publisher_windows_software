import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import chromedriver_autoinstaller

app = FastAPI()

class LLMRequest(BaseModel):
    topic: str
    debug: bool = False  # 新增debug参数，前端可传递

class LLMResponse(BaseModel):
    copy: str
    prompt: str

DOUBAO_URL = "https://www.doubao.com/chat/?channel=bing_sem&source=dbweb_bing_sem_xhs_cpc_pinp_hexin_05&keywordid=77241076291699&msclkid=ad2e454f72001b521c002d6f0d4f804c"

# 生成文案的提示
COPY_PROMPT_TEMPLATE = "我现在想在小红书上发布一个和{topic}相关的内容，请你帮我以小红书的风格生成合适的文案"
# 生成图片提示词的提示
PROMPT_PROMPT_TEMPLATE = "请你根据提供的文案和我的需求，生成适用于文生图任务的大模型提示词"

# 自动安装chromedriver
chromedriver_autoinstaller.install()

# RPA主流程

def wait_llm_reply_complete(driver, old_count, max_wait=60, debug=False):
    interval = 0.5
    waited = 0
    last_text = None
    while waited < max_wait:
        time.sleep(interval)
        waited += interval
        new_msgs = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="message_text_content"]')
        send_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="chat_input_send_button"]')
        if send_btn.get_attribute('aria-disabled') == 'true':
            if new_msgs:
                if debug:
                    print(f"[DEBUG] 检测到发送按钮变灰，回复已生成完毕: {new_msgs[-1].text}")
                # 如果消息数量有增加，或内容有变化，都返回
                if len(new_msgs) > old_count or (last_text is not None and new_msgs[-1].text != last_text):
                    return new_msgs[-1].text
                last_text = new_msgs[-1].text
    raise Exception(f"未检测到新回复完成，已等待{max_wait}秒")

def send_doubao_message(driver, message, wait_time=15, debug=False, max_wait=60, max_retry=2):
    # 定位输入框
    input_box = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[data-testid="chat_input_input"]'))
    )
    input_box.clear()
    input_box.send_keys(message)
    if debug:
        print(f"[DEBUG] 已输入内容: {message}")
    time.sleep(0.5)  # 输入后等待

    # 等待"深度思考"按钮出现并可点击
    try:
        deep_btn = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(.,"深度思考")]'))
        )
    except Exception as e:
        all_btns = driver.find_elements(By.TAG_NAME, 'button')
        print('[DEBUG] 页面所有按钮：')
        for btn in all_btns:
            print(btn.text)
        raise Exception('未找到"深度思考"按钮，请检查网页结构或定位表达式')
    if debug:
        print("[DEBUG] 找到深度思考按钮")
    if 'active-s41p1Y' not in deep_btn.get_attribute('class'):
        deep_btn.click()
        if debug:
            print("[DEBUG] 点击深度思考按钮")
        time.sleep(0.5)  # 点击后等待

    # 输入内容后，等待发送按钮可点击
    send_btn = WebDriverWait(driver, wait_time).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="chat_input_send_button"]'))
    )
    if send_btn.get_attribute('aria-disabled') == 'false':
        send_btn.click()
        if debug:
            print("[DEBUG] 点击发送按钮")
        time.sleep(1)  # 发送后等待
    else:
        raise Exception("发送按钮不可用")

    # 发送后先sleep(10)，再进入轮询
    if debug:
        print("[DEBUG] 发送后等待LLM回复10秒")
    time.sleep(10)

    # 等待新回复且发送按钮变灰
    for retry in range(max_retry):
        old_msgs = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="message_text_content"]')
        try:
            return wait_llm_reply_complete(driver, len(old_msgs), max_wait=max_wait, debug=debug)
        except Exception as e:
            if debug:
                print(f"[DEBUG] 第{retry+1}次等待{max_wait}秒未获取到新回复完成，准备重试...")
    raise Exception(f"未检测到新回复完成，已重试{max_retry}次，每次等待{max_wait}秒")

@app.post("/llm_generate", response_model=LLMResponse)
def llm_generate(req: LLMRequest):
    chrome_options = Options()
    debug = getattr(req, 'debug', False)
    if not debug:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(DOUBAO_URL)
        # 生成文案
        copy_prompt = COPY_PROMPT_TEMPLATE.format(topic=req.topic)
        copy_text = send_doubao_message(driver, copy_prompt, debug=debug)
        # 生成图片提示词
        prompt_text = send_doubao_message(driver, PROMPT_PROMPT_TEMPLATE, debug=debug)
        return LLMResponse(copy=copy_text, prompt=prompt_text)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 