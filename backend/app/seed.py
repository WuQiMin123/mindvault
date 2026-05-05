"""Seed the database with demo data."""

import asyncio
import hashlib

from sqlalchemy import select

from app.database import async_session, init_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag

TAGS = ["AI", "前端", "后端", "工具", "学习", "B站", "待处理"]

LINKS = [
    {
        "title": "FastAPI 异步编程详解",
        "content": "FastAPI 支持异步请求处理，可以使用 async/await 语法编写高效的 API 端点。依赖注入系统支持异步初始化，数据库会话可以在请求生命周期内共享。SQLAlchemy 异步驱动 aiosqlite 提供了完整的异步数据库操作支持。使用 BackgroundTasks 可以在返回响应后执行后台任务，非常适合处理需要长时间运行的操作如内容抓取和 AI 处理。",
        "url": "https://example.com/fastapi-async",
        "source": "web",
        "tags": ["后端", "学习"],
    },
    {
        "title": "Next.js App Router 深入理解",
        "content": "Next.js 13 引入了基于 React Server Components 的 App Router。App Router 使用文件系统路由，支持布局嵌套、加载状态和错误处理。服务端组件默认在服务端渲染，减少客户端 JavaScript 体积。客户端组件可以在需要交互时使用。App Router 还支持流式渲染和数据缓存，大幅提升页面加载性能。",
        "url": "https://example.com/nextjs-app-router",
        "source": "web",
        "tags": ["前端", "学习"],
    },
    {
        "title": "React 19 新特性介绍",
        "content": "React 19 引入了 Actions API，简化了表单处理和数据提交。新的 use() hook 可以直接在渲染中读取 Promise 和 Context。Server Components 正式稳定，支持服务端渲染和客户端交互的无缝组合。React 19 还改进了 Suspense 和并发特性，提供了更好的用户体验和开发体验。",
        "url": "https://example.com/react-19",
        "source": "web",
        "tags": ["前端"],
    },
    {
        "title": "B站 — 深度学习入门到精通",
        "content": "本课程从零开始讲解深度学习基础知识，包括神经网络原理、反向传播算法、常见的激活函数和损失函数。课程涵盖 CNN 卷积神经网络在图像识别中的应用，RNN 循环神经网络在序列数据处理中的优势。通过实际项目演练，帮助学习者掌握 PyTorch 框架的使用。",
        "url": "https://www.bilibili.com/video/BV1GJ411x7FH",
        "source": "bilibili",
        "tags": ["AI", "B站", "学习"],
    },
    {
        "title": "Tailwind CSS 最佳实践",
        "content": "Tailwind CSS 是一个实用优先的 CSS 框架，通过原子化类名快速构建自定义界面。使用 Tailwind 可以避免命名 CSS 类的困扰，减少样式冲突。搭配设计系统使用，可以保证设计一致性。配合 shadcn/ui 组件库，可以快速搭建美观的 React 应用界面。",
        "url": "https://example.com/tailwind-best-practices",
        "source": "web",
        "tags": ["前端", "工具"],
    },
    {
        "title": "Python 异步编程模式",
        "content": "Python 的 asyncio 库提供了基于事件循环的并发编程能力。async/await 语法让异步代码看起来像同步代码一样直观。常见的异步编程模式包括：使用 asyncio.gather 并行执行多个协程、使用 asyncio.Queue 实现生产者消费者模式、使用 semaphore 控制并发数。",
        "url": "https://example.com/python-async",
        "source": "web",
        "tags": ["后端", "学习"],
    },
    {
        "title": "AI 编程助手对比评测",
        "content": "对比了市面上主流的 AI 编程助手：GitHub Copilot 在代码补全方面表现出色，支持多种 IDE 和语言。Cursor 作为 AI-first IDE，提供了深度集成的 AI 辅助编程体验。Claude 在代码理解和重构方面有独特优势。DeepSeek 作为国产方案，性价比较高，特别适合中文开发场景。",
        "url": "https://example.com/ai-coding-tools",
        "source": "web",
        "tags": ["AI", "工具"],
    },
    {
        "title": "B站 — 系统设计面试指南",
        "content": "系统设计面试是高级工程师面试中的重要环节。常见的面试题目包括：设计短链接系统、设计消息队列、设计分布式缓存、设计社交信息流。解题思路通常包括：明确需求、估算容量、设计数据模型、定义 API 接口、讨论架构细节。重点考察候选人的架构设计思维和 trade-off 分析能力。",
        "url": "https://www.bilibili.com/video/BV1Qa4y1s7xR",
        "source": "bilibili",
        "tags": ["后端", "B站", "学习"],
    },
    {
        "title": "Web 性能优化清单",
        "content": "前端性能优化 Checklist：使用 Lighthouse 进行性能审计。图片优化包括 WebP 格式、懒加载和响应式图片。JavaScript 优化包括代码分割、tree-shaking 和懒加载。CSS 优化包括减少重排重绘、使用 contain 属性。缓存策略包括 Service Worker、CDN 缓存和浏览器缓存。核心 Web 指标包括 LCP、FID、CLS。",
        "url": "https://example.com/web-perf",
        "source": "web",
        "tags": ["前端", "工具"],
    },
    {
        "title": "Docker 容器化部署指南",
        "content": "Docker 通过容器化技术简化了应用部署流程。Dockerfile 定义了应用的构建过程，docker-compose 编排多容器应用。多阶段构建可以减小最终镜像体积。健康检查确保服务可用性。日志管理使用容器日志驱动。数据持久化使用 volumes 或 bind mounts。",
        "url": "https://example.com/docker-deploy",
        "source": "web",
        "tags": ["后端", "工具", "学习"],
    },
]


async def seed():
    await init_db()
    async with async_session() as db:
        # 创建标签
        tag_map = {}
        for name in TAGS:
            result = await db.execute(select(Tag).where(Tag.name == name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                await db.flush()
            tag_map[name] = tag.id
            print(f"  标签: {name}")

        # 创建链接
        for data in LINKS:
            link = Link(
                url=data["url"],
                title=data["title"],
                content=data["content"],
                raw_content=data["content"],
                source=data["source"],
                status="completed",
                content_hash=hashlib.md5(data["content"].encode()).hexdigest(),
            )
            db.add(link)
            await db.flush()

            for tag_name in data.get("tags", []):
                tid = tag_map.get(tag_name)
                if tid:
                    await db.execute(
                        link_tag.insert().values(link_id=link.id, tag_id=tid)
                    )

            print(f"  链接: {data['title']}")

        await db.commit()
        print(f"\n完成! 创建了 {len(TAGS)} 个标签, {len(LINKS)} 条内容")


if __name__ == "__main__":
    asyncio.run(seed())
