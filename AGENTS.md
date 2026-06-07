# AGENTS.md

## 项目目标

本项目是一个两天内完成的 AI 美甲试戴与智能运营系统后端。

核心目标是快速交付可运行 MVP，而不是实现复杂企业级架构。

## 技术栈

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- JSON 文件存储
- Docker
- pytest

## 开发原则

1. 优先保证功能可运行。
2. 不要引入复杂依赖。
3. 不要实现真实登录、权限、支付、预约系统。
4. 不要训练模型。
5. AI 图像生成和文本生成都必须支持 mock 模式。
6. LLM 文本生成必须通过多模型适配层接入，不允许业务接口直接绑定 GPT、Gemini、Qwen、DeepSeek 等任一具体模型。
7. 所有接口必须返回稳定 JSON。
8. 所有接口必须支持前端跨域访问。
9. 每完成一个任务，必须更新 `docs/06_CODEX_TASKS.md` 的完成状态。
10. 每完成一个任务，必须运行测试或至少运行启动检查。
11. 不允许删除已有文档。
12. 不允许随意改变 API 字段名，除非同步更新 `docs/03_API_CONTRACT.md`。
13. 如果真实 AI API 不可用，必须使用 mock 返回，保证演示链路不中断。
14. 不允许把任何真实 API Key 写入代码、文档或测试数据。

## 后端目录结构要求

后端目录必须尽量保持如下结构：

```text
backend
├── app
│   ├── main.py
│   ├── core
│   │   ├── config.py
│   │   └── cors.py
│   ├── routers
│   │   ├── health.py
│   │   ├── styles.py
│   │   ├── tryon.py
│   │   ├── events.py
│   │   ├── analytics.py
│   │   └── ai.py
│   ├── services
│   │   ├── style_service.py
│   │   ├── event_service.py
│   │   ├── analytics_service.py
│   │   ├── image_ai_service.py
│   │   └── llm_service.py
│   ├── schemas
│   │   └── dto.py
│   ├── data
│   │   ├── styles.json
│   │   └── events.json
│   ├── uploads
│   └── outputs
├── tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 任务执行规则

每次执行任务时，请按以下格式输出结果：

```text
已完成：

- ...

修改文件：

- ...

本地验证：

- ...

下一步建议：

- ...
```
