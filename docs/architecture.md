# MindVault 项目文档

## 定位

发链接/写笔记 → AI 自动处理 → 标签归档 → 聚合总结 → 搜索检索 → 多端同步

对标 Mem.ai / Omnivore，针对国内平台优化，支持网页 + 手机端数据互通。

## 当前状态

Phase 0-3 已完成。后端 API、AI 管线、Web 前端均可运行。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI (async) + SQLAlchemy + SQLite |
| Web 前端 | Next.js 16 + Tailwind v4 + shadcn/ui |
| 移动端 | Expo (React Native) — 排期中 |
| 数据库 | SQLite (计划迁移 PostgreSQL) |
| 认证 | JWT (python-jose + passlib) — 待实现 |
| LLM | OpenAI 兼容 API (DeepSeek) |

## 架构决策

- **不做离线同步**：所有端实时请求 API，服务端唯一真实数据源
- **不做向量检索**：ILIKE 全文搜索足够，知识库量级无需 RAG
- **移动端统一 API**：Expo 直接复用 Web 端的 API 调用层

## 当前功能

- 链接/文本内容摄入
- B站字幕抓取、知乎内容抓取（Cookie 辅助）
- AI 摘要生成 + 自动打标签（DeepSeek）
- 手动补充内容（抓取失败时）
- 标签 CRUD、标签聚合总结
- 全文搜索、列表筛选
- 已读状态管理

## 运行方式

```bash
# 后端
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001

# Web 前端
cd frontend && npx next dev --port 3000
```

## 环境变量

### backend/.env
```env
# 必填
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash

# 可选
LOG_LEVEL=INFO
LOG_DIR=../log
```

### frontend/.env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

## 未来计划

1. Phase 5: 浏览器插件（Manifest V3）
2. Phase 4: 多用户 + PostgreSQL 迁移
3. Phase 6: 移动端 Expo
