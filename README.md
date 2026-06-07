# AI 美甲试戴与智能运营系统

这是一个用于快速演示的 AI 美甲试戴与智能运营系统 MVP。项目包含 FastAPI 后端、React 前端、款式库、手图库、商家推荐、服务需求确认单、运营看板、AI 文案接口，以及双图分割美甲试戴 Pipeline。

当前目标是保证演示链路完整可运行。系统保留 mock 降级能力，不实现真实登录、支付、预约、地图和模型训练。

## 技术栈

后端：

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- JSON 文件存储
- pytest
- Pillow / numpy / opencv-python
- inference-sdk，用于 Roboflow 指甲分割

前端：

- Vite
- React
- TypeScript
- lucide-react
- 通过 `VITE_API_BASE_URL` 调用后端

## 项目结构

```text
nail_auto/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── data/
│   │   ├── uploads/
│   │   └── outputs/
│   ├── tests/
│   ├── scripts/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── .env.example
├── frontend/
├── docs/
├── try_qwen_models.py
└── README.md
```

## 当前已实现能力

### 1. 基础后端服务

- FastAPI 应用入口。
- CORS 跨域支持。
- 静态文件挂载：
  - `/uploads`
  - `/outputs`
  - `/static`
- 健康检查：

```http
GET /health
```

返回示例：

```json
{
  "status": "ok",
  "service": "nail-ai-backend"
}
```

### 2. 款式库

接口：

```http
GET /api/styles
GET /api/styles/{style_id}
```

数据文件：

```text
backend/app/data/styles.json
```

说明：

- 款式库格式是 JSON 元数据 + 图片 URL。
- 兼容旧字段和合作方字段。
- 旧字段：`id`、`name`、`image_url`。
- 合作方字段：`style_id`、`style_name`、`image_path`。
- `image_url` / `image_path` 同时用于前端展示和 AI 试戴参考图。

### 3. 手图库

接口：

```http
GET /api/hands
GET /api/hands/{hand_id}
```

数据文件：

```text
backend/app/data/hands.json
```

当前手图库为 Demo 数据，包含手图 URL、肤色标签和手型标签。

### 4. 旧版单图试戴接口

接口：

```http
POST /api/tryon
```

请求类型：

```text
multipart/form-data
```

字段：

```text
hand_image: file
style_id: string
user_id: string，可选，默认 demo_user
```

当前行为：

- 保留接口，避免破坏已有前端或文档契约。
- 上传手图保存到 `/uploads`。
- 结果图保存到 `/outputs`。
- 自动记录一条 `tryon` 行为。
- 该接口目前仍以 mock 为主，不是当前主推荐试戴链路。

### 5. 双图分割美甲试戴接口

接口：

```http
POST /api/nail-tryon
```

这是当前主推荐试戴链路，前端试戴流程已经切到该接口。

请求类型：

```text
multipart/form-data
```

支持两种输入方式。

方式一：前端只传用户手图和款式 ID：

```text
target_hand_image: file
style_id: string
provider: qwen | openai | doubao | mock，可选
model_name: string，可选
```

后端会根据 `style_id` 查询 `styles.json`，下载或复制款式图作为参考图。

方式二：手动传两张图：

```text
target_hand_image: file
style_hand_image: file
provider: qwen | openai | doubao | mock，可选
model_name: string，可选
```

Pipeline：

```text
target hand image
style reference image
-> 目标手图指甲分割
-> target_nail_mask.png
-> 款式参考图指甲分割
-> style_nail_mask.png
-> style_nails_only.png
-> image_ai_service.edit_image(...)
-> final_tryon_result.png
```

返回示例：

```json
{
  "success": true,
  "message": "nail try-on generated successfully",
  "data": {
    "session_id": "nail_tryon_xxx",
    "result_image_url": "/uploads/nail_tryon/nail_tryon_xxx/final_tryon_result.png",
    "target_mask_url": "/uploads/nail_tryon/nail_tryon_xxx/target_nail_mask.png",
    "style_mask_url": "/uploads/nail_tryon/nail_tryon_xxx/style_nail_mask.png",
    "style_reference_url": "/uploads/nail_tryon/nail_tryon_xxx/style_nails_only.png",
    "provider": "qwen",
    "model_name": "qwen-image-edit-plus",
    "segmentation_provider": "roboflow"
  }
}
```

说明：

- 已实现目标手图 mask 生成。
- 已实现款式参考图指甲区域提取。
- 已实现 mock 图像编辑降级。
- `IMAGE_AI_MODE=real` 时会尝试调用真实图像编辑 provider。
- provider 调用失败、Key 缺失或返回异常时，自动回退到 mock 结果，保证演示链路不中断。

### 6. 真实图像编辑 provider

真实图像编辑通过 `backend/app/services/image_ai_service.py` 统一适配，不在 router 中直接绑定具体模型。

已预留并实现调用分发：

| provider | 默认模型 | Key |
|---|---|---|
| `qwen` | `qwen-image-edit-plus` | `QWEN_API_KEY` |
| `openai` | `gpt-image-1` | `OPENAI_API_KEY` 或 `IMAGE_AI_API_KEY` |
| `doubao` | `doubao-seededit-3-0-i2i-250628` | `ARK_API_KEY` |
| `mock` | 本地 mask 颜色迁移 | 不需要 Key |

当前本地建议默认使用 Qwen：

```env
IMAGE_AI_MODE=real
NAIL_TRYON_DEFAULT_EDIT_PROVIDER=qwen
QWEN_API_KEY=你的百炼 API Key
```

注意：

- Qwen 和 OpenAI 的真实调用代码已接入，但需要真实 Key 和账号权限才能验证最终效果。
- 豆包 SeedEdit3.0 通过火山方舟 Ark 配置接入，实际模型 ID 如与控制台不同，请用 `DOUBAO_IMAGE_MODEL` 覆盖。
- 不会把任何真实 API Key 写入代码、README、测试或 `.env.example`。

### 7. Roboflow 指甲分割

当前 Roboflow 调用方式与官方示例一致：

```python
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="..."
)

result = CLIENT.infer(your_image.jpg, model_id="fingernail-segmentation-yy1l7/3")
```

项目中的封装位置：

```text
backend/app/services/segmentation/roboflow_fingernail.py
```

API Key 填写位置：

```env
ROBOFLOW_API_KEY=你的 Roboflow API Key
ROBOFLOW_API_URL=https://serverless.roboflow.com
ROBOFLOW_MODEL_ID=fingernail-segmentation-yy1l7/3
```

未配置 `ROBOFLOW_API_KEY` 或调用失败时，系统使用 mock 分割。

### 8. AI 文案与运营建议

接口：

```http
POST /api/ai/report
POST /api/ai/promotion
POST /api/ai/advice
```

当前文本生成通过 `backend/app/services/llm_service.py` 多模型适配层接入。

已实现：

- mock 文案降级。
- Qwen 文本调用分支。
- 默认文本模型：`qwen3.7-plus`。

建议配置：

```env
LLM_MODE=real
LLM_PROVIDER=qwen
LLM_MODEL=qwen3.7-plus
QWEN_API_KEY=你的百炼 API Key
```

如果 `qwen3.7-plus` 在你的百炼账号中不可用，请将 `LLM_MODEL` 改成控制台可调用的模型名。

### 9. 用户行为记录

接口：

```http
POST /api/events
GET /api/events
```

支持事件类型：

```text
view_style
select_style
tryon
favorite
save_result
book
```

数据文件：

```text
backend/app/data/events.json
```

### 10. 商家与推荐

商家接口：

```http
GET /api/merchants
GET /api/merchants/{merchant_id}
```

推荐接口：

```http
POST /api/recommend/merchants
```

当前行为：

- 使用 `backend/app/data/merchants.json` 中的 Demo 商家数据。
- 根据款式标签、颜色、元素、用户偏好和商家能力做 mock 排序。
- 不接真实地图。
- 不做真实预约。
- 不做支付。

### 11. 服务需求确认单

接口：

```http
POST /api/confirmation
GET /api/confirmation/{confirmation_id}
```

当前行为：

- 校验款式是否存在。
- 校验商家是否存在。
- 生成 mock 服务需求确认单。
- 不代表真实预约。
- 不涉及支付。

### 12. 运营看板

基础看板：

```http
GET /api/analytics/dashboard
```

平台运营看板：

```http
GET /api/analytics/platform-dashboard
```

数据来源：

```text
backend/app/data/events.json
backend/app/data/behavior_metrics.json
backend/app/data/preference_events.json
backend/app/data/merchants.json
```

平台看板返回内容包括：

- 款式热度排行。
- 用户偏好趋势。
- 商家能力概览。
- 供需预警。
- AI 运营建议。

## 前端功能

前端目录：

```text
frontend/
```

已实现：

- 款式浏览。
- 上传用户手图。
- 调用 `/api/nail-tryon` 生成试戴结果。
- 图像模型切换：
  - Qwen Image Edit Plus
  - OpenAI GPT Image
  - Doubao SeedEdit3.0
- 试戴结果展示。
- 商家推荐。
- 服务需求确认单。
- 用户偏好流程。
- 运营后台页面。
- 平台运营看板。

前端 API 基地址：

```text
VITE_API_BASE_URL=http://localhost:8000
```

如不配置，前端默认请求本地 `http://localhost:8000`。

## 环境变量

后端本地配置文件建议使用：

```text
backend/.env
```

从模板复制：

```powershell
cd E:\AAA_NEED\nail_auto
Copy-Item backend/.env.example backend/.env
```

关键配置说明：

| 变量 | 作用 | 推荐值 |
|---|---|---|
| `SERVICE_NAME` | 服务名称 | `nail-ai-backend` |
| `CORS_ORIGINS` | 前端跨域来源 | 本地可用 `*` |
| `IMAGE_AI_MODE` | 图像 AI 模式 | `mock` 或 `real` |
| `NAIL_TRYON_DEFAULT_EDIT_PROVIDER` | 默认图像编辑模型 | `qwen` |
| `QWEN_API_KEY` | 百炼 Qwen 图像和文本 Key | 填你的真实 Key |
| `QWEN_IMAGE_MODEL` | Qwen 图像编辑模型 | `qwen-image-edit-plus` |
| `QWEN_IMAGE_API_URL` | Qwen 图像接口地址 | 保持默认 |
| `OPENAI_API_KEY` | OpenAI Key | 使用 OpenAI 时填写 |
| `OPENAI_IMAGE_MODEL` | OpenAI 图像模型 | `gpt-image-1` |
| `ARK_API_KEY` | 火山方舟 Key | 使用豆包时填写 |
| `ARK_BASE_URL` | 火山方舟 API 地址 | `https://ark.cn-beijing.volces.com/api/v3` |
| `DOUBAO_IMAGE_MODEL` | 豆包图像编辑模型 | 以控制台实际 ID 为准 |
| `LLM_MODE` | 文本生成模式 | `mock` 或 `real` |
| `LLM_PROVIDER` | 文本模型 provider | `qwen` |
| `LLM_MODEL` | 文本模型名 | `qwen3.7-plus` |
| `QWEN_TEXT_API_URL` | Qwen 文本接口地址 | 保持默认 |
| `ROBOFLOW_API_KEY` | Roboflow 分割 Key | 填你的真实 Key |
| `ROBOFLOW_API_URL` | Roboflow API 地址 | `https://serverless.roboflow.com` |
| `ROBOFLOW_MODEL_ID` | Roboflow 模型 ID | `fingernail-segmentation-yy1l7/3` |
| `NAIL_TRYON_MASK_DILATE_PX` | mask 膨胀像素 | `2` |
| `NAIL_TRYON_MASK_FEATHER_PX` | mask 羽化像素 | `1` |
| `NAIL_TRYON_DEBUG_OUTPUT` | 是否输出中间图 | 本地建议 `true` |

Qwen 优先的本地配置示例：

```env
IMAGE_AI_MODE=real
NAIL_TRYON_DEFAULT_EDIT_PROVIDER=qwen
LLM_MODE=real
LLM_PROVIDER=qwen
LLM_MODEL=qwen3.7-plus
QWEN_API_KEY=你的百炼 API Key
ROBOFLOW_API_KEY=你的 Roboflow API Key
```

豆包 SeedEdit3.0 额外配置：

```env
ARK_API_KEY=你的火山方舟 API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_IMAGE_MODEL=控制台中的 SeedEdit3.0 模型 ID
```

不要把真实 Key 写入 `.env.example`，也不要提交 `.env`。

## 本地运行

### 后端

```powershell
cd E:\AAA_NEED\nail_auto\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### 前端

```powershell
cd E:\AAA_NEED\nail_auto\frontend
npm install
npm run dev
```

默认访问 Vite 输出的本地地址，常见为：

```text
http://localhost:3000
```

## Docker 运行

当前 `backend/docker-compose.yml` 已配置为读取：

```yaml
env_file:
  - .env
```

因此 Docker 启动前需要确保存在：

```text
backend/.env
```

启动：

```powershell
cd E:\AAA_NEED\nail_auto\backend
docker compose up -d --build
```

查看状态：

```powershell
docker compose ps
```

停止：

```powershell
docker compose down
```

## 测试

后端测试：

```powershell
cd E:\AAA_NEED\nail_auto\backend
python -m pytest -q
```

Windows 临时目录权限异常时可使用：

```powershell
python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp
```

前端构建：

```powershell
cd E:\AAA_NEED\nail_auto\frontend
npm run build
```

最近一次验证结果：

```text
backend pytest: 23 passed
frontend build: success
```

## 命令行试戴 Demo

准备两张图片：

```text
hand.png   目标用户手图
style.png  款式参考图
```

运行：

```powershell
cd E:\AAA_NEED\nail_auto
python backend/scripts/run_nail_tryon_demo.py --target hand.png --style style.png --provider qwen --output backend/app/outputs/nail_tryon_demo/final_tryon_result.png
```

输出产物：

```text
target_nail_mask.png
style_nail_mask.png
style_nails_only.png
final_tryon_result.png
```

## 独立 Qwen 模型验证脚本

根目录有一个独立脚本：

```text
try_qwen_models.py
```

用途：

- 单独验证 `qwen-image-edit-plus`。
- 单独验证 `qwen3.7-plus`。
- 不读取当前后端配置。
- 不导入项目代码。
- API Key 需要手动填在脚本顶部。

运行：

```powershell
python try_qwen_models.py
```

该脚本只用于模型可用性验证，不属于正式后端 provider 架构。

## 数据文件

主要数据位于：

```text
backend/app/data/
```

当前数据文件：

```text
styles.json              款式库
hands.json               手图库
merchants.json           Demo 商家数据
events.json              用户行为数据
behavior_metrics.json    Demo 运营指标
preference_events.json   Demo 偏好趋势
confirmations.json       服务需求确认单
tryon_records.json       试戴记录预留
preferences.json         用户偏好数据
```

说明：

- 当前没有数据库。
- JSON 文件存储适合 MVP 演示，不适合高并发生产环境。
- 商家、行为、偏好、运营指标均为 Demo/mock 数据。

## 已实现接口列表

```http
GET  /health

GET  /api/styles
GET  /api/styles/{style_id}

GET  /api/hands
GET  /api/hands/{hand_id}

POST /api/tryon
POST /api/nail-tryon

POST /api/events
GET  /api/events

GET  /api/analytics/dashboard
GET  /api/analytics/platform-dashboard

POST /api/ai/report
POST /api/ai/promotion
POST /api/ai/advice

GET  /api/merchants
GET  /api/merchants/{merchant_id}

POST /api/recommend/merchants

POST /api/confirmation
GET  /api/confirmation/{confirmation_id}
```

## 当前未实现内容

### 用户系统

未实现：

- 登录。
- 注册。
- Token。
- 权限。
- 用户鉴权。
- Session 管理。

### 交易和预约

未实现：

- 真实预约。
- 支付。
- 订单。
- 退款。
- 商家排班。
- 档期管理。

### 地图和距离

未实现：

- 真实地图。
- 经纬度定位。
- 实时距离计算。
- 门店定位。

当前商家距离字段是 mock 数据。

### 数据库

未实现数据库持久化。当前使用 JSON 文件，不适合高并发和多人同时写入。

### 生产级能力

未实现：

- 上传文件清理任务。
- 图片安全审核。
- 请求限流。
- 异步任务队列。
- 生产日志追踪。
- 监控告警。
- CI/CD。
- 多环境部署策略。

### 真实 AI 效果验证

代码层面已接入 Qwen/OpenAI/Doubao 图像编辑分发和 Qwen 文本分支，但真实效果取决于：

- API Key 是否有效。
- 账号是否开通对应模型。
- 模型名称是否与控制台一致。
- provider 返回结构是否与当前解析逻辑一致。
- 网络是否允许访问外部模型 API。

任何真实 provider 失败都会 fallback 到 mock，以保证演示不中断。

## 推荐后续开发顺序

1. 使用真实 `ROBOFLOW_API_KEY` 验证指甲分割质量。
2. 使用 Qwen 作为默认 provider 验证 `/api/nail-tryon` 真实试戴效果。
3. 对豆包 SeedEdit3.0 按火山方舟控制台实际模型 ID 修正配置。
4. 根据真实 provider 返回格式补强图片 URL / base64 解析。
5. 给前端增加 provider 调用失败时的调试信息展示。
6. 增加上传文件大小、格式和安全检查。
7. 引入数据库替换 JSON 文件。
8. 再考虑登录、真实预约、支付和地图能力。
