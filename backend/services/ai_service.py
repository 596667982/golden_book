"""Unified AI service supporting multiple providers via OpenAI-compatible API."""
import base64
import json
import re
from typing import Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import AIConfig


def _is_anthropic(config: AIConfig) -> bool:
    return config.provider == "anthropic"


def _get_openai_client(config: AIConfig) -> AsyncOpenAI:
    kwargs = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return AsyncOpenAI(**kwargs)


def _get_anthropic_client(config: AIConfig) -> AsyncAnthropic:
    kwargs = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    # Add custom headers required by some proxies
    kwargs["default_headers"] = {
        "x-channel-id": "12",
        "User-Agent": "claude-cli/2.1.15 (external cli)"
    }
    return AsyncAnthropic(**kwargs)


async def _chat(config: AIConfig, messages: list[dict], max_tokens: int) -> str:
    """Unified chat call, returns text content."""
    if _is_anthropic(config):
        client = _get_anthropic_client(config)
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = []
        for m in messages:
            content = m["content"]
            # Handle multimodal content (list of parts)
            if isinstance(content, list):
                parts = []
                for part in content:
                    if part["type"] == "image_url":
                        url = part["image_url"]["url"]
                        # data:image/jpeg;base64,<data>
                        media_type, b64data = url.split(";base64,")
                        media_type = media_type.split("data:")[1]
                        parts.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": b64data},
                        })
                    else:
                        parts.append({"type": "text", "text": part["text"]})
                anthropic_messages.append({"role": m["role"], "content": parts})
            else:
                anthropic_messages.append({"role": m["role"], "content": content})

        resp = await client.messages.create(
            model=config.model_name,
            max_tokens=max_tokens,
            messages=anthropic_messages,
        )
        return resp.content[0].text
    else:
        client = _get_openai_client(config)
        resp = await client.chat.completions.create(
            model=config.model_name,
            messages=messages,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content


async def get_active_config(db: AsyncSession) -> Optional[AIConfig]:
    result = await db.execute(select(AIConfig).where(AIConfig.is_active == True))
    return result.scalar_one_or_none()


async def test_connection(config: AIConfig) -> dict:
    request_params = {
        "provider": config.provider,
        "base_url": config.base_url,
        "model": config.model_name,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5,
    }
    try:
        text = await _chat(config, [{"role": "user", "content": "hi"}], max_tokens=5)
        return {"ok": True, "response": text, "request": request_params}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "detail": str(e), "request": request_params}


def _encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


PARSE_QUESTIONS_PROMPT = """请仔细分析这张练习题图片，提取所有题目。
返回严格的JSON格式，不要有任何额外文字：
{
  "questions": [
    {
      "order_num": 1,
      "content": "题目内容",
      "question_type": "single|multi|fill|subjective",
      "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
      "score": 2
    }
  ]
}
说明：
- single=单选题, multi=多选题, fill=填空/计算题, subjective=主观/问答题
- options 仅选择题有，其他为 null
- score 默认为 1 分，如题目标注了分值则使用标注值
- 保持题目原文，不要修改"""

PARSE_ANSWERS_PROMPT = """请仔细分析这张答案图片，提取所有题目的答案。
返回严格的JSON格式，不要有任何额外文字：
{
  "answers": [
    {
      "order_num": 1,
      "correct_answer": "答案内容"
    }
  ]
}
说明：
- order_num 对应题目编号
- correct_answer 填写标准答案，选择题填选项字母如 "A" 或 "AB"
- 如果答案图片中没有某题答案，correct_answer 填 null"""


async def parse_exercise_image(image_bytes: bytes, db: AsyncSession) -> list[dict]:
    config = await get_active_config(db)
    if not config:
        raise ValueError("未配置可用的 AI 模型，请先在设置中配置并激活")

    b64 = _encode_image(image_bytes)
    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": PARSE_QUESTIONS_PROMPT},
        ],
    }]
    raw = await _chat(config, messages, max_tokens=4096)
    return _extract_json(raw).get("questions", [])


async def parse_answer_image(image_bytes: bytes, db: AsyncSession) -> list[dict]:
    config = await get_active_config(db)
    if not config:
        raise ValueError("未配置可用的 AI 模型，请先在设置中配置并激活")

    b64 = _encode_image(image_bytes)
    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": PARSE_ANSWERS_PROMPT},
        ],
    }]
    raw = await _chat(config, messages, max_tokens=2048)
    return _extract_json(raw).get("answers", [])


def _extract_json(text: str) -> dict:
    """Extract JSON from AI response, handling markdown code blocks."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}
