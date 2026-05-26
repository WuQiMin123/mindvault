# MindVault

个人知识库系统 — 写笔记/插件提取 → 标签归档 → 搜索检索。v0.2.0

## 功能

- **手动输入** — 纯文本/笔记快速保存，支持从已有标签选择或当场创建新标签
- **浏览器插件** — 选中网页文本右键保存（Chrome/Edge），B站视频字幕自动提取
- **标签管理** — 自定义标签，多对多关联，标签内聚合总结
- **全文搜索** — 关键词搜索 + 标签组合筛选，分页展示
- **数据导出** — JSON 完整备份 / Markdown ZIP 打包
- **Web 端** — Next.js 仪表盘，浏览、编辑、搜索一体化

## 快速开始

### 本地开发

```bash
# 1. 安装后端依赖
make install-backend

# 2. 配置环境变量
cp backend/.env.example backend/.env  # 编辑填入 LLM_API_KEY

# 3. 启动后端（默认 8001 端口）
make dev-backend

# 4. 新终端，启动前端（默认 3000 端口）
make dev-frontend
```

然后访问 `http://localhost:3000`。

### 演示数据

```bash
make seed
```

会在数据库中创建 7 个标签和 10 条示例内容，方便试用。

### Docker 部署

```bash
# 构建并启动
LLM_API_KEY=your-key-here make docker-up

# 查看日志
make docker-logs
```

访问 `http://localhost:3000`。后端 API 在 `http://localhost:8000`。

### 浏览器插件

`browser-plugin/` 目录是一个 Manifest V3 的 Chrome/Edge 插件。

1. 打开 `edge://extensions`（或 `chrome://extensions`）
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"，选择 `browser-plugin/` 目录
4. 在任意网页选中文本 → 右键"保存到 MindVault"（或 Ctrl+Shift+V）
5. 在 B站视频页面点击插件图标 → 自动提取字幕保存
6. 弹出窗口中可从已有标签选择或创建新标签

## 项目结构

```
mindvault/
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── api/v1/           # REST API 路由
│       │   ├── ingest.py     #   POST /ingest/text
│       │   ├── links.py      #   GET/PATCH/DELETE /links
│       │   ├── tags.py       #   GET/POST/PUT/DELETE /tags
│       │   ├── search.py     #   GET /search
│       │   ├── export.py     #   GET /export/json|markdown
│       │   └── router.py     #   路由聚合
│       ├── models/           # SQLAlchemy 数据模型
│       ├── schemas/          # Pydantic 请求/响应模型
│       ├── config.py         # 配置（pydantic-settings）
│       ├── database.py       # 数据库引擎与会话
│       ├── main.py           # 应用入口
│       └── seed.py           # 演示数据脚本
├── frontend/                 # Next.js Web 端
│   ├── src/app/              # App Router 页面
│   │   ├── page.tsx          #   仪表盘
│   │   ├── ingest/           #   提交页面
│   │   ├── tags/             #   标签页面
│   │   ├── links/            #   内容详情
│   │   └── search/           #   搜索页面
│   └── src/lib/              # 工具库
├── browser-plugin/           # Chrome/Edge 插件
│   ├── manifest.json
│   ├── content.js            # B站字幕提取
│   ├── background.js         # 右键菜单 & 消息中转
│   ├── popup.html / popup.js # 弹出窗口（支持已有标签选择）
│   └── options.html / .js    # 配置页
├── docs/                     # 设计文档
├── docker-compose.yml        # Docker 编排
├── Dockerfile                # 后端容器镜像
└── Makefile                  # 常用命令
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ingest/text` | 保存纯文本/笔记 |
| GET | `/api/v1/links` | 内容列表（分页） |
| GET | `/api/v1/links/{id}` | 内容详情 |
| PATCH | `/api/v1/links/{id}` | 修改内容 |
| DELETE | `/api/v1/links/{id}` | 删除内容 |
| PATCH | `/api/v1/links/{id}/read-status` | 切换已读/未读 |
| GET | `/api/v1/tags` | 标签列表 |
| POST | `/api/v1/tags` | 创建标签 |
| PUT | `/api/v1/tags/{id}` | 更新标签 |
| DELETE | `/api/v1/tags/{id}` | 删除标签 |
| PUT | `/api/v1/links/{link_id}/tags` | 批量设置链接标签 |
| GET | `/api/v1/tags/{id}/summary` | 标签聚合总结 |
| GET | `/api/v1/search?q=keyword&tag=1` | 搜索（关键词+标签筛选） |
| GET | `/api/v1/export/json` | 导出全部数据为 JSON |
| GET | `/api/v1/export/markdown` | 导出全部数据为 Markdown ZIP |

完整 API 文档见 [`docs/API接口设计.md`](docs/API接口设计.md)。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 / FastAPI / SQLAlchemy (async) |
| 数据库 | SQLite (WAL 模式) |
| Web 前端 | Next.js 16 / Tailwind CSS 4 / shadcn/ui |
| 浏览器插件 | Manifest V3 / Chrome/Edge |
| 工程 | Docker / pytest / ruff |

## 开发

```bash
# 运行测试
make test

# 代码检查
make lint

# 自动格式化
make format
```

## 路线图

- [x] 后端核心 API + 搜索 (v0.1.0)
- [x] 内容摄入 + 浏览器插件 (v0.1.0)
- [x] Web 前端 (v0.1.0)
- [x] 输入简化：聚焦插件 + 手动文本 (v0.2.0)
- [x] 标签交互升级：已有标签选择 + 当场创建 (v0.2.0)
- [ ] 移动端 (Expo)
- [ ] 多用户 + JWT 认证 + PostgreSQL