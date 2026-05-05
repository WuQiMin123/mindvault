"""
B站字幕可行性深入测试
"""

import httpx
import asyncio
import json

BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}


async def get_video_info(bvid: str):
    """获取视频全部信息"""
    async with httpx.AsyncClient(timeout=30.0) as c:
        vr = await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=BROWSER)
        if vr.status_code != 200:
            return {"error": f"HTTP {vr.status_code}"}
        vd = vr.json()
        if vd["code"] != 0:
            return {"error": f"biz {vd['code']}: {vd.get('message','')}"}

        data = vd["data"]
        cid = data["cid"]
        title = data["title"]
        desc = data.get("desc", "")
        duration = data.get("duration", 0)

        # 取 player/v2 (字幕信息在这里)
        sr = await c.get(
            f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}",
            headers=BROWSER,
        )
        sub_info = {"subtitles": [], "ai_subtitle": None}
        if sr.status_code == 200:
            sd = sr.json()
            player = sd.get("data", {})
            sub_info = {
                "subtitles": player.get("subtitle", {}).get("subtitles", []),
                "ai_subtitle": player.get("subtitle", {}).get("ai_subtitle"),
            }

        # 尝试触发 AI 字幕生成
        gen_result = None
        if not sub_info["subtitles"] and not sub_info.get("ai_subtitle"):
            gen_result = await try_generate_ai_subtitle(c, bvid, cid)

        return {
            "bvid": bvid,
            "title": title,
            "desc_len": len(desc),
            "desc_preview": desc[:200],
            "duration": duration,
            "sub_info": {
                "manual_subs": len(sub_info["subtitles"]),
                "ai_subtitle": bool(sub_info.get("ai_subtitle")),
            },
            "generate_result": gen_result,
        }


async def try_generate_ai_subtitle(c, bvid: str, cid: int):
    """尝试触发B站AI字幕生成"""
    # 方法1: 请求生成
    endpoints = [
        f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}&platform=web&ai_subtitle=true",
    ]
    for url in endpoints:
        try:
            r = await c.get(url, headers=BROWSER)
            if r.status_code == 200:
                data = r.json()
                ai = data.get("data", {}).get("subtitle", {}).get("ai_subtitle", {})
                if ai and ai.get("text"):
                    return f"found at {url[:60]}"
                return {"try": url[:60], "ai_subtitle_found": False, "code": data.get("code")}
        except Exception as e:
            return {"try": url[:60], "error": str(e)}
    return None


async def main():
    # 已知有字幕的视频（B站官方/机构账号通常会上传字幕）
    test_bvids = [
        "BV1GJ411x7Ht",  # 知名UP主
        "BV1AW98BoE6a",  # 热门
        "BV1BM9fB8Eds",
        "BV1YERYBDEnu",
        "BV16p9UBgEhT",
        "BV1GrRFBoEko",
        # 尝试带编号的视频
        "BV1xx411c7mD",  # 经典老番
        "BV1s5411K7kE",
    ]

    for bvid in test_bvids:
        print(f"\n--- {bvid} ---")
        info = await get_video_info(bvid)
        print(json.dumps(info, ensure_ascii=False, indent=2))

    print("\n\n结论：")
    print("如果 AI 字幕无法通过 API 触发生成，替代方案:")
    print("  方案A: 标题 + 简介 + 评论作为内容 (轻量)")
    print("  方案B: yt-dlp 下载视频 + Whisper 本地转文字 (重量)")
    print("  方案C: 使用B站必选API (需要cookie/sessdata)")


if __name__ == "__main__":
    asyncio.run(main())
