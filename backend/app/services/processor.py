"""AI 处理管线：摘要 + 打标签"""

import json
import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    async def generate_summary(self, content: str) -> str:
        if not settings.llm_api_key:
            return ""
        if len(content) < 100:
            logger.warning("内容过短（%d 字符），跳过 AI 摘要", len(content))
            return ""
        resp = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "请用一到两句话概括以下内容的核心要点。"},
                {"role": "user", "content": content[:8000]},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        summary = resp.choices[0].message.content or ""
        if not summary:
            logger.warning("AI 返回空摘要 | content_len=%d | model=%s", len(content), settings.llm_model)
        return summary

    async def suggest_tags(self, content: str) -> list[str]:
        if not settings.llm_api_key:
            return []
        if len(content) < 100:
            logger.warning("内容过短（%d 字符），跳过 AI 打标签", len(content))
            return []
        resp = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "请分析以下内容，给出 1-3 个中文标签（JSON 数组格式）。"
                        "标签要能概括内容的主题和领域。直接返回数组，不要额外文字。"
                    ),
                },
                {"role": "user", "content": content[:4000]},
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or "[]"

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("AI 标签返回解析失败: %s", text[:200])
            return []
