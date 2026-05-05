"""
全平台可行性验证 v4
"""

import httpx
import asyncio
import json
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}


async def bilibili_test():
    print("\n===== [1] B站: 标题+简介 =====")
    results = []
    async with httpx.AsyncClient(timeout=30.0) as c:
        b_headers = {**HEADERS, "Referer": "https://www.bilibili.com/"}
        try:
            # B站搜索
            sr = await c.get(
                "https://api.bilibili.com/x/web-interface/search/type",
                params={"search_type": "video", "keyword": "AI", "page": 1},
                headers=b_headers,
            )
            print(f"  搜索API状态: {sr.status_code}")
            if sr.status_code == 200:
                sd = sr.json()
                print(f"  搜索API返回码: {sd.get('code')}")
                videos = sd.get("data", {}).get("result", [])
                print(f"  视频数量: {len(videos)}")

                for v in videos[:5]:
                    bvid = v["bvid"]
                    vr = await c.get(
                        f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
                        headers=b_headers,
                    )
                    if vr.status_code != 200:
                        continue
                    vd = vr.json()
                    if vd["code"] != 0:
                        continue
                    d = vd["data"]
                    results.append({
                        "source": "bilibili",
                        "bvid": bvid,
                        "title": d["title"],
                        "desc_len": len(d.get("desc", "")),
                        "desc": d.get("desc", "")[:200],
                    })
            else:
                print(f"  搜索失败: {sr.text[:200]}")
        except Exception as e:
            print(f"  搜索异常: {e}")
            results.append({"source": "bilibili", "error": str(e)})

    return results


async def zhihu_test():
    print("\n===== [2] 知乎: 文章页 =====")
    results = []
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as c:
        for url in [
            "https://zhuanlan.zhihu.com/p/2016598051163218226",
        ]:
            try:
                r = await c.get(url, headers=HEADERS)
                print(f"  知乎 {url[:40]} -> {r.status_code}")
                result = {"source": "zhihu", "url": url[:50], "status": r.status_code}

                if r.status_code == 200:
                    result["body_len"] = len(r.text)
                    # 检测是否是真正的文章页 (而非验证页)
                    soup = BeautifulSoup(r.text, "html.parser")
                    title = soup.find("title")
                    result["title"] = title.get_text()[:100] if title else "N/A"
                    # 看正文长度
                    body = soup.find("body")
                    result["body_text_len"] = len(body.get_text(strip=True)) if body else 0
                    result["has_article"] = "article" in r.text
                else:
                    result["preview"] = r.text[:200]
                results.append(result)
            except Exception as e:
                print(f"  知乎异常: {e}")
                results.append({"source": "zhihu", "error": str(e)})
    return results


async def general_test():
    print("\n===== [3] 通用网页 =====")
    results = []
    async with httpx.AsyncClient(timeout=15.0) as c:
        for name, url in [
            ("B站首页", "https://www.bilibili.com"),
            ("百度", "https://www.baidu.com"),
        ]:
            try:
                r = await c.get(url, headers=HEADERS)
                print(f"  {name} -> {r.status_code}")
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.find("title")
                title_text = title.get_text()[:80] if title else "N/A"
                ps = soup.find_all("p")
                text = "\n".join(p.get_text(strip=True) for p in ps if p.get_text(strip=True))
                results.append({
                    "source": "general",
                    "name": name,
                    "status": r.status_code,
                    "title": title_text,
                    "p_count": len([p for p in ps if p.get_text(strip=True)]),
                    "text_len": len(text),
                    "preview": text[:200],
                })
            except Exception as e:
                print(f"  {name} 异常: {e}")
                results.append({"source": "general", "name": name, "error": str(e)})
    return results


async def main():
    print("=" * 50)
    for name, fn in [("B站", bilibili_test()), ("知乎", zhihu_test()), ("通用", general_test())]:
        result = await fn
        print(f"\n{name} 结果:")
        for r in result:
            print(f"  {json.dumps(r, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
