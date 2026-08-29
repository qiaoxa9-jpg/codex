# IC Research Copilot

面向 Digital IC / ASIC / SoC 的可运行研究与工程知识平台 MVP。它不是 ChatGPT 克隆：后端先分类问题，再执行混合检索与证据重排；答案以结构化 section 返回，每个主要结论只能绑定 Evidence Context 中真实存在的 `source_id`。

## 当前已完成

- Next.js + TypeScript + Tailwind CSS + shadcn/ui 风格组件；支持深色/浅色模式。
- 全站中文/English 自由切换，选择会保存到浏览器，并支持 `?lang=zh` / `?lang=en` 分享语言状态。
- `/research` 三栏研究工作台：分类/检索轨迹、结构化答案、可点击 Evidence Card。
- `/papers` 联合 Semantic Scholar Academic Graph API 与 Crossref REST API；失败时按 provider 显式降级。
- `/paper/[id]` 从选定上游提供方重新获取论文详情，不根据标题补写摘要。
- `/encyclopedia` 可检索 IC 概念与关系入口。
- FastAPI 模块：`query_analyzer.py`、`retriever.py`、`paper_retriever.py`、`industry_retriever.py`、`concept_retriever.py`、`reranker.py`、`answer_generator.py`、`citation_validator.py`、`research_agent.py`、`engineering_agent.py`。
- PostgreSQL/pgvector 数据模型，覆盖 users、papers、authors、paper_authors、documents、document_chunks、industry_sources、concepts、concept_relations、solutions、questions、answers、citations、collections。
- Alembic 初始 migration、Redis/PostgreSQL/前后端 Docker Compose、后端测试与 100 题 Digital IC 评测集。

## 证据边界

开发模式内置少量可核验的官方 CDC 资料，目的是让没有数据库/API key 的环境也能实际运行 Research 主链路。内置资料不是通用知识库：若相关性不足，API 返回：

> 当前知识库中没有足够可靠证据支持这一结论。

论文检索只使用上游 API 返回字段。Crossref 是元数据注册库，不等同于全文库；OpenAlex、arXiv、PDF Reader 与大规模 ingestion 预留到下一迭代。

## 本地运行

当前机器若没有 Docker，可分别启动后端和前端。

### 1. 后端

```powershell
cd D:\codex\科研\projects\ic-research-copilot\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

打开 `http://localhost:8000/docs` 查看 API。Research 工程模式使用内置证据，不依赖 PostgreSQL；数据库在持久化/ingestion 阶段启用。

### 2. 前端

```powershell
cd D:\codex\科研\projects\ic-research-copilot\frontend
npm.cmd install
npm.cmd run dev
```

打开 `http://localhost:3000`。默认后端地址为 `http://localhost:8000/api/v1`。

### 3. 完整容器栈

复制 `.env.example` 为 `.env`，按需填写 key，然后：

```powershell
docker compose up --build
docker compose exec backend alembic upgrade head
```

本机当前是否安装 Docker 与项目配置无关；若 `docker` 命令不存在，使用上面的双进程方式。

## 可选 LLM

不配置 `LLM_API_KEY` 时，CDC 示例使用可审计的确定性模板。配置兼容 `/chat/completions` 的模型服务后，系统会把 Evidence Context 发送给模型；输出必须为结构化 JSON，并在返回前通过 `citation_validator.py`。任何越界 `source_id` 都会触发安全回退。

```env
LLM_API_KEY=...
LLM_BASE_URL=https://your-provider.example/v1
LLM_MODEL=your-model
```

## 测试

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

前端：

```powershell
cd frontend
npm.cmd run typecheck
npm.cmd run build
```

评测集在 `tests/evaluation/ic_questions.json`，共 100 题，覆盖 RTL、CDC、RDC、STA、Synthesis、Verification、Low Power、DFT、Physical Design、Architecture。

## API

- `GET /api/v1/health`
- `POST /api/v1/research/ask`
- `GET /api/v1/papers/search?q=...`
- `GET /api/v1/papers/detail?source=...&paper_id=...`
- `GET /api/v1/concepts`
- `GET /api/v1/concepts/{id}`

## 下一阶段

1. ingestion worker：PDF section detection、chunking、embedding 与 pgvector 写入。
2. PostgreSQL BM25（或独立检索服务）+ pgvector 真正并行召回，Redis 查询缓存。
3. OpenAlex/arXiv provider、去重与论文版本聚合。
4. 将 APB-UART/UVM 项目转成可引用的内部工程案例，并补 STA/RDC/DFT 等领域种子库。
5. ingestion/source governance 后再开放大规模 LLM 生成，避免“页面先于证据库”。
