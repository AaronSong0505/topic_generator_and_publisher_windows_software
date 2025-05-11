全自动小红书文案生成与发布设计方案

---

## 一、整体架构梳理

你的项目已经实现了“前后端分离+多Agent模块化”的设计思路，建议继续保持这种结构，具体如下：

```
/
├── Back-end Service/
│   ├── llm-agent/                # 文案与提示词生成
│   ├── image-generator-agent/    # 图片生成
│   ├── publisher-agent/          # 自动化发布
│   └── state-management-agent/   # 流程与状态管理
├── Front-end Client/             # Windows前端
├── Env-auto-install/             # 自动化环境安装
├── requirements.txt              # 统一依赖管理
```

---

## 二、各模块设计建议

### 1. Back-end Service

- 每个Agent建议都实现为独立的FastAPI子应用，便于解耦和后续独立部署/扩展。
- 主服务负责API聚合、任务调度、日志与状态管理。
- 各Agent之间通过内部API或消息队列（如Redis、RabbitMQ）通信，提升并发与解耦能力。

#### 1.1 llm-agent
- 负责与大模型API对接，生成小红书文案和图片生成提示词。
- 支持多种大模型API切换（如豆包、OpenAI等）。
- 提供RESTful接口，接收前端或主服务的请求，返回文案/提示词。

#### 1.2 image-generator-agent
- 负责调用AI图片生成API，根据提示词生成图片。
- 支持多种图片风格、分辨率参数。
- 图片生成后存储于本地或云端，并返回图片URL/路径。

#### 1.3 publisher-agent
- 负责与安卓模拟器（如MuMu、夜神等）交互，通过ADB+Appium/Poco自动化操作小红书App完成发帖。
- 支持任务队列，自动重试与异常处理。
- 可扩展支持多App自动化发布。

#### 1.4 state-management-agent
- 负责任务流编排（如文案→图片→发布），状态追踪与回溯。
- 提供任务流API，供前端查询任务进度、历史记录等。
- 支持任务暂停、重试、终止等操作。

### 2. Front-end Client

- 建议采用PyQt5/PySide2开发，便于与Python后端集成。
- 主要功能：任务配置、进度展示、日志查看、模拟器控制（启动/关闭）、结果展示。
- 通过HTTP API与后端通信。

### 3. Env-auto-install

- 统一收集所有依赖到根目录`requirements.txt`，并在Env-auto-install目录下编写自动化安装脚本（如install.bat/install.sh）。
- 脚本内容包括：Python依赖安装、安卓模拟器安装、ADB与Appium环境配置等。
- 提供一键检测与修复功能，提升用户体验。

---

## 三、开发流程建议

1. 优先完善各Agent的API接口与核心功能，确保后端服务可用。
2. 前端开发可同步进行，先实现基础的任务配置与进度展示。
3. 完善自动化环境安装脚本，确保新环境可一键部署。
4. 各模块开发完成后，重点测试整体流程的自动化闭环。
5. 持续完善文档，便于后续维护和团队协作。

---

## 四、补充建议

- 每个Agent目录下建议都包含独立的`readme.md`和`requirements.txt`，便于单独开发和测试。
- 主目录下的`requirements.txt`收集所有依赖，供一键安装。
- 日志与异常处理建议统一规范，便于排查问题。
- 可考虑引入Docker进行环境隔离和部署（后续可选）。

