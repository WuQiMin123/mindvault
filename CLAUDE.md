# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## MindVault 项目规则

### 技术栈
- 后端: Python 3.12 / FastAPI (async) / SQLAlchemy (async) / aiosqlite
- 前端: Next.js 16 (App Router) / React 19 / Tailwind CSS 4 / shadcn/ui
- 浏览器插件: Manifest V3 (Chrome/Edge)
- AI: OpenAI 兼容 API (DeepSeek / Claude)
- 工程: Docker / pytest / ruff / GitHub Actions

### 常用命令
```bash
make dev-backend    # 启动后端（8001 端口）
make dev-frontend   # 启动前端（3000 端口）
make test           # 运行测试
make lint           # 代码检查
make format         # 自动格式化
make seed           # 填充演示数据
```

### 开发节奏
- 一次只做一个 phase，不做 scope creep
- 先 spike 验证可行性，再做详细设计，然后编码
- 每个 phase 有明确边界和交付物，不"顺便修一下"

### API 设计规范
- 响应在所有数据变更完成后构建，不在变更前构建
- async SQLAlchemy 中 session expire 后不 lazy load 关联属性
- 每个端点覆盖 loading / empty / error 三种状态

### 错误处理
- 不捕不知道该怎么处理的异常 —— catch 块只是 pass 或 print 说明调用方不需要处理它
- LLM API key 为空时降级跳过 AI 处理，不带着假 key 去撞墙
- 启动时 lifespan 中做配置自检，提前暴露问题

### 浏览器插件 (Manifest V3)
- Content script 不依赖页面 JS 上下文（`window.__INITIAL_STATE__` 等）
- 优先从 URL / DOM / 公开 API 获取信息
- `chrome.storage.session` 在 content script 中不可用 —— 用 `sendMessage` 中转
- 跨域请求需要在 manifest 中声明 `host_permissions`

### v1.1 开发范围（当前）
- **P0**: 数据导出 + 前端 loading/empty/error 状态补齐
- **P1**: 移动端 Web 响应式（Tailwind breakpoint，不引入额外依赖）
- **P2**: 移动端 App (Expo)
- **P3**: 批量操作 + 测试覆盖
- 明确排除：多用户/JWT、PostgreSQL 迁移、向量检索/RAG、离线模式
