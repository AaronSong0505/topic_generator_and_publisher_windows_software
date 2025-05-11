# llm-agent

本模块通过RPA自动化方式访问豆包网页，自动生成小红书文案和图片生成提示词。

## 主要功能
- 提供RESTful接口，接收发帖主题需求，自动化操作豆包网页，返回文案和图片提示词。

## 接口说明
- POST /llm_generate
  - 输入参数：{"topic": "健身"}
  - 返回：{"copy": "...生成的小红书文案...", "prompt": "...生成的图片提示词..."}

## 依赖
- fastapi
- selenium
- pydantic
- uvicorn

## 运行方法
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 启动服务（需本地有chromedriver，或设置CHROMEDRIVER_PATH环境变量）：
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```