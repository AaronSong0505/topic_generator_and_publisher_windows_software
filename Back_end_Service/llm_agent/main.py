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
from selenium.common.exceptions import NoSuchElementException

app = FastAPI()

class LLMRequest(BaseModel):
    topic: str
    debug: bool = False  # 新增debug参数，前端可传递

class LLMResponse(BaseModel):
    copy: str
    prompt: str

DOUBAO_URL = "https://www.doubao.com/chat/?channel=bing_sem&source=dbweb_bing_sem_xhs_cpc_pinp_hexin_05&keywordid=77241076291699&msclkid=ad2e454f72001b521c002d6f0d4f804c"

# 生成文案的提示
COPY_PROMPT_TEMPLATE = "我现在想在小红书上发布一个和{topic}相关的内容，请你帮我以小红书的风格的文案。要求：1.记住这个文案可以直接发布不需要调整。2.不要生成额外的描述。3.不要开启你的ai写作模式"
# 生成图片提示词的提示
PROMPT_PROMPT_TEMPLATE = "请你根据提供的文案和我的需求，生成适用于文生图任务的大模型提示词。要求：1.只生成提示词。2.不要生成额外的描述。"

# 自动安装chromedriver
chromedriver_autoinstaller.install()


# RPA主流程

def wait_llm_reply_complete(driver, old_count, max_wait=60, debug=False, stable_time=2, last_input=None):
    import datetime
    interval = 0.5
    waited = 0
    last_msgs = []
    last_time = time.time()
    while waited < max_wait:
        time.sleep(interval)
        waited += interval
        new_msgs = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="message_text_content"]')
        send_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="chat_input_send_button"]')
        # 过滤掉与last_input相同的内容
        new_texts = [msg.text for msg in new_msgs[old_count:] if last_input is None or msg.text.strip() != last_input.strip()]
        is_disabled = send_btn.get_attribute('aria-disabled') == 'true' or send_btn.get_attribute('disabled') == 'true' or 'semi-button-disabled' in send_btn.get_attribute('class')
        # 1. 优先判断suggest_message_list 或 after_message_download_desktop_button
        suggest_list = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="suggest_message_list"]')
        after_download_btn = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="after_message_download_desktop_button"]')
        if debug:
            print(f"[DEBUG] waited={waited}, new_texts={new_texts}, suggest_list_count={len(suggest_list)}, after_download_btn_count={len(after_download_btn)}, is_disabled={is_disabled}")
        if (suggest_list or after_download_btn) and len(new_texts) > 0:
            if debug:
                print("[DEBUG] 检测到suggest_message_list或after_message_download_desktop_button，回复已结束")
            return "\n".join(new_texts)
        # 2. 兼容内容稳定性判断
        if is_disabled and len(new_texts) > 0:
            if new_texts == last_msgs:
                if time.time() - last_time > stable_time:
                    if debug:
                        print("[DEBUG] 内容稳定但未检测到suggest_message_list或after_message_download_desktop_button，继续等待...")
            else:
                last_msgs = new_texts
                last_time = time.time()
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"debug_page_{now}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(f"debug_page_{now}.png")
    raise Exception(f"未检测到新回复完成，已等待{max_wait}秒")

def send_doubao_message(driver, message, wait_time=15, debug=False, max_wait=60, max_retry=2):
    # 每次都重新查找输入框
    input_box = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[data-testid="chat_input_input"]'))
    )
    input_box.clear()
    input_box.send_keys(message)
    if debug:
        print(f"[DEBUG] 已输入内容: {message}")
    time.sleep(0.5)

    # 精确定位深度思考按钮
    try:
        deep_btn = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="use-deep-thinking-switch-btn"]/button[contains(@title,"深度思考")]'))
        )
    except Exception as e:
        all_btns = driver.find_elements(By.TAG_NAME, 'button')
        print('[DEBUG] 页面所有按钮：')
        for btn in all_btns:
            print(btn.text)
        # 异常时保存页面快照
        import datetime
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"debug_page_{now}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot(f"debug_page_{now}.png")
        raise Exception('未找到"深度思考"按钮，请检查网页结构或定位表达式')
    if debug:
        print("[DEBUG] 找到深度思考按钮")
    # 判断是否已激活
    if 'active-s41p1Y' not in deep_btn.get_attribute('class'):
        deep_btn.click()
        if debug:
            print("[DEBUG] 点击深度思考按钮")
        time.sleep(0.5)

    # 发送前获取old_count
    old_msgs = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="message_text_content"]')
    old_count = len(old_msgs)

    # 重新查找发送按钮
    send_btn = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="chat_input_send_button"]'))
    )
    is_disabled = send_btn.get_attribute('aria-disabled') == 'true' or send_btn.get_attribute('disabled') == 'true' or 'semi-button-disabled' in send_btn.get_attribute('class')
    if not is_disabled:
        send_btn.click()
        if debug:
            print("[DEBUG] 点击发送按钮")
        time.sleep(1)
    else:
        raise Exception("发送按钮不可用")

    if debug:
        print("[DEBUG] 发送后等待LLM回复10秒")
    time.sleep(10)

    for retry in range(max_retry):
        try:
            return wait_llm_reply_complete(driver, old_count, max_wait=max_wait, debug=debug, last_input=message)
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