# AI 美甲试戴与智能运营系统后端

这是两天内交付的 FastAPI 后端 MVP，使用 JSON 文件存储，默认 mock 模式可完整演示款式库、试戴、行为记录、运营看板和 AI 文案链路。

## 本地启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

- 健康检查：http://localhost:8000/health
- Swagger 文档：http://localhost:8000/docs
- 前端联调 Base URL：http://localhost:8000

## Docker 启动

```bash
cd backend
docker compose up --build
```

后台启动：

```bash
docker compose up -d --build
```

查看状态：

```bash
docker compose ps
```

## 环境变量

默认可直接使用 `.env.example`，不需要真实 API Key。

```text
SERVICE_NAME=nail-ai-backend
CORS_ORIGINS=*
IMAGE_AI_MODE=mock
IMAGE_AI_API_KEY=
OPENAI_IMAGE_MODEL=gpt-image-1
QWEN_IMAGE_MODEL=qwen-image-edit-plus
QWEN_IMAGE_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
DOUBAO_IMAGE_MODEL=doubao-seededit-3-0-i2i-250628
ARK_API_KEY=
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODE=mock
LLM_PROVIDER=
LLM_MODEL=qwen3.7-plus
QWEN_TEXT_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
OPENAI_API_KEY=
GEMINI_API_KEY=
QWEN_API_KEY=
DEEPSEEK_API_KEY=
ROBOFLOW_API_KEY=
```

说明：

- `IMAGE_AI_MODE=mock`：AI 试戴复制原图作为结果图。
- `IMAGE_AI_MODE=real`：预留真实图像生成/编辑模型调用，失败自动降级 mock。
- `LLM_MODE=mock`：AI 文本接口返回稳定 mock 文案。
- `LLM_MODE=real`：通过 `llm_service.py` 多模型适配层调用真实供应商，配置缺失或调用失败自动降级 mock。

不要把真实 API Key 写入代码、文档或测试数据。

## API 列表

### GET `/health`

服务健康检查。

### GET `/api/styles`

获取美甲款式列表。

### GET `/api/styles/{style_id}`

获取单个美甲款式，不存在返回 `404`。

### POST `/api/events`

记录用户行为。

```json
{
  "user_id": "demo_user",
  "style_id": "style_001",
  "event_type": "tryon"
}
```

支持的 `event_type`：

```text
view_style
select_style
tryon
favorite
save_result
book
```

### GET `/api/events`

获取用户行为列表。

### GET `/api/analytics/dashboard`

获取运营看板数据，包括今日试戴次数、今日用户数、热门款式、热门标签、冷门款式和推荐主推款式。

### POST `/api/tryon`

AI 美甲试戴 mock 接口，使用 `multipart/form-data`。

字段：

```text
hand_image: file
style_id: string
user_id: string，可选，默认 demo_user
```

### POST `/api/ai/report`

生成运营日报。

```json
{
  "date": "2026-06-02"
}
```

### POST `/api/ai/promotion`

生成推广文案。

```json
{
  "style_id": "style_001",
  "channel": "xiaohongshu"
}
```

### POST `/api/ai/advice`

生成用户适配建议。

```json
{
  "style_id": "style_001"
}
```

## 前端联调

前端请求地址：

```text
http://localhost:8000
```

CORS 默认允许跨域。前端可直接调用 `/api/styles` 获取款式，再用 `/api/tryon` 上传图片并传入 `style_id`。

上传示例：

```bash
curl -F "style_id=style_001" -F "user_id=demo_user" -F "hand_image=@hand.png" http://localhost:8000/api/tryon
```

返回的图片 URL 是相对路径，例如：

```text
/uploads/tryon_xxx_original.png
/outputs/tryon_xxx_result.png
```

前端展示时拼接 Base URL 即可。

## 官方数据与 Demo 数据

- 官方真实数据来自根目录 `data.xlsx`。
- 官方数据只包含手图 URL 和款式图 URL。
- `hands.json` 和 `styles.json` 基于官方 URL 生成。
- `merchants.json`、`behavior_metrics.json`、`preference_events.json`、`tryon_records.json` 是 Demo mock 数据。
- 当前不接真实地图、不做登录、不做支付、不做真实预约。

## 对齐新增 API

### GET `/api/hands`

获取官方手图列表。

### GET `/api/hands/{hand_id}`

获取单个手图，不存在返回 `404`。

### GET `/api/merchants`

获取 Demo mock 商家能力列表。

### GET `/api/merchants/{merchant_id}`

获取单个商家能力，不存在返回 `404`。

### POST `/api/recommend/merchants`

根据用户手图、款式和偏好推荐商家。

```json
{
  "user_id": "demo_user",
  "hand_id": "hand_001",
  "style_id": "style_001",
  "preferences": ["还原度", "性价比"]
}
```

### POST `/api/confirmation`

生成服务需求确认单，不代表真实预约。

```json
{
  "user_id": "demo_user",
  "hand_id": "hand_001",
  "style_id": "style_001",
  "merchant_id": "merchant_001",
  "preferences": ["还原度", "性价比"],
  "tryon_result_url": "/outputs/result_001.png"
}
```

### GET `/api/analytics/platform-dashboard`

获取平台运营看板，包含款式热度、偏好趋势、商家能力、供需提醒和 mock 运营建议。

## 前端推荐调用顺序

用户端：

```text
GET /api/hands
GET /api/styles
POST /api/tryon
POST /api/ai/advice
POST /api/recommend/merchants
POST /api/confirmation
POST /api/events
```

运营端：

```text
GET /api/analytics/platform-dashboard
POST /api/ai/report
POST /api/ai/promotion
```

字段兼容：

- 款式接口保留 `id/name/image_url`。
- 款式接口同时返回 `style_id/style_name/image_path`。
- `image_url` 和 `image_path` 默认使用官方增强后款式图 URL。
- `original_url` 保留官方原始款式图 URL。

## Mock 模式

当前 MVP 默认 mock：

- AI 试戴：保存上传图，并复制到 `outputs` 作为结果图。
- AI 文本：返回稳定文案，不请求真实 LLM。
- 配置缺失、Key 缺失、供应商不可用或调用失败都不会导致演示链路中断。

## LLM 多模型适配

文本生成统一通过 `app/services/llm_service.py`，router 不直接调用任何具体供应商 SDK 或 API。

预留供应商：

- OpenAI / GPT：`LLM_PROVIDER=openai`，Key 从 `OPENAI_API_KEY` 读取。
- Gemini：`LLM_PROVIDER=gemini`，Key 从 `GEMINI_API_KEY` 读取。
- Qwen：`LLM_PROVIDER=qwen`，Key 从 `QWEN_API_KEY` 读取。
- DeepSeek：`LLM_PROVIDER=deepseek`，Key 从 `DEEPSEEK_API_KEY` 读取。

真实模式还需要设置：

```text
LLM_MODE=real
LLM_PROVIDER=openai
LLM_MODEL=your-model-name
```

如果供应商、模型名或 API Key 缺失，系统自动返回 mock 文案。

## 常见问题

### Docker 拉取镜像失败

先确认 Docker Desktop 已启动，并且本机能访问 Docker Hub。也可以先手动拉取 `python:3.11-slim`。

### `/api/tryon` 返回 422

确认请求类型是 `multipart/form-data`，字段名必须是 `hand_image` 和 `style_id`。

### `style_id` 返回 404

确认 `style_id` 存在于 `app/data/styles.json`。

### AI 没有生成真实试戴图

这是当前 MVP 的默认行为。`IMAGE_AI_MODE=mock` 会复制原图，真实图像生成能力已通过 `image_ai_service.py` 预留。

### LLM Key 没配置是否能演示

可以。默认 `LLM_MODE=mock`，即使切到 real 但缺少 Key，也会自动降级 mock。

## 测试

```bash
cd backend
python -m pytest -q
```

## Nail Try-On 双图分割试戴

新增接口：

```text
POST /api/nail-tryon
```

请求类型为 `multipart/form-data`：

```text
target_hand_image: 第一张目标手部照片
style_hand_image: 第二张带美甲款式的手部照片
provider: 可选，默认 openai
model_name: 可选
```

该流程会分别生成 `target_nail_mask.png`、`style_nail_mask.png`、`style_nails_only.png` 和 `final_tryon_result.png`。未配置 `ROBOFLOW_API_KEY` 时使用 mock 分割，配置后使用 Roboflow 指甲分割模型。

命令行 demo：

```bash
python backend/scripts/run_nail_tryon_demo.py --target hand.png --style style.png --provider openai --output backend/app/outputs/nail_tryon_demo/final_tryon_result.png
```

## 前端融合说明

前端代码位于仓库根目录 `frontend`，使用 Vite + React。

```bash
cd ../frontend
npm install
npm run dev
```

前端通过 `VITE_API_BASE_URL=http://localhost:8000` 调用后端，默认已在
`frontend/.env.example` 中预留。当前用户端已接入款式列表、上传试戴、AI
建议、商家推荐和确认单接口；运营端已接入平台看板和 AI 日报接口。
 
## 运营端 Demo mock 数据

`GET /api/analytics/platform-dashboard` 已接入 `app/data/` 下的 Demo 数据文件：

- `behavior_metrics.json`：聚合生成运营总览和款式热度榜。
- `preference_events.json`：统计用户偏好趋势。
- `merchants.json`：返回商家能力画像，并参与供需匹配提醒。
- `events.json`：保留为用户行为链路 Demo 数据源。

接口会返回 `overview`、`style_heat_ranking`、`preference_trends`、`merchant_capabilities`、`supply_demand_alerts`、`ai_suggestion` 和 `mock: true`，即使 Demo 文件缺失也会保持稳定 JSON。
