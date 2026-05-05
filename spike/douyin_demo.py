"""
抖音内容提取 Demo — yt-dlp 获取简介 + 下载视频

管线: 抖音链接 → yt-dlp 提取信息(标题+简介) → 下载视频到本地
      简介作为正文内容，不进行语音转文字

用法:
  1. 浏览器打开 douyin.com 并登录
  2. F12 → Console → 输入 document.cookie 复制全部
  3. export DOUYIN_COOKIE="sessionid=xxx; passport_csrf_token=yyy"
     python douyin_demo.py "https://v.douyin.com/xxxxx/"
"""
import sys, os, subprocess, json, re, tempfile
from http.cookiejar import MozillaCookieJar

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "douyin_videos")


def make_cookie_file(cookie_str: str) -> str:
    """把 document.cookie 格式的字符串转成 Netscape 格式的 cookie 文件"""
    jar = MozillaCookieJar()
    # 解析 "key=value; key2=value2" 格式
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" not in pair:
            continue
        name, value = pair.split("=", 1)
        # 添加一个适用于 .douyin.com 的 cookie
        jar.set_cookie(
            __import__("http.cookiejar", fromlist=["Cookie"]).Cookie(
                version=0, name=name.strip(), value=value.strip(),
                port=None, port_specified=False,
                domain=".douyin.com", domain_specified=True, domain_initial_dot=False,
                path="/", path_specified=True,
                secure=False, expires=None, discard=True,
                comment=None, comment_url=None,
                rest={},
            )
        )
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    jar.save(tmp.name)
    return tmp.name


def parse_ytdlp_output(output: str) -> dict:
    """Parse yt-dlp output, handling possible warnings before JSON"""
    lines = output.strip().split("\n")
    # Find the first line that looks like JSON
    for line in lines:
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    return {}


def main():
    if len(sys.argv) < 2:
        url = input("粘贴抖音链接: ").strip()
    else:
        url = sys.argv[1]

    cookie_str = os.environ.get("DOUYIN_COOKIE", "")
    if not cookie_str:
        cookie_str = input("请粘贴 douyin.com 的 Cookie (留空则无登录态): ").strip()

    cookie_file = make_cookie_file(cookie_str) if cookie_str else None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  抖音内容提取 Demo")
    print(f"  链接: {url[:60]}")
    print(f"  登录态: {'有' if cookie_str else '无'}")
    print(f"  保存目录: {DOWNLOAD_DIR}")
    print(f"{'='*60}")

    # Step 1: 获取视频信息
    print(f"\n==> 步骤 1: 获取视频信息...")
    cmd = ["yt-dlp", "--dump-json", "--no-download", "--no-playlist", url]
    if cookie_file:
        cmd = ["yt-dlp", "--cookies", cookie_file,
               "--dump-json", "--no-download", "--no-playlist", url]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        print(f"  [失败] 获取信息失败")
        print(f"  {result.stderr[:500]}")
        return

    info = parse_ytdlp_output(result.stdout)
    if not info:
        print(f"  [失败] 无法解析视频信息")
        print(f"  stdout: {result.stdout[:300]}")
        print(f"  stderr: {result.stderr[:300]}")
        return

    title = info.get("title", "(无标题)")
    desc = info.get("description", "") or ""
    duration = info.get("duration", 0)
    uploader = info.get("uploader", "") or info.get("channel", "") or ""
    vid = info.get("id", "")

    print(f"  标题: {title}")
    print(f"  作者: {uploader}")
    print(f"  时长: {duration} 秒")
    print(f"  简介: {desc[:200] if desc else '(空)'}")

    # Step 2: 下载视频
    print(f"\n==> 步骤 2: 下载视频...")
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]
    video_path = os.path.join(DOWNLOAD_DIR, f"{vid}_{safe_title}.mp4")

    dl_cmd = [
        "yt-dlp",
        "-f", "best[filesize<100M]",
        "-o", video_path,
        "--no-playlist",
        "--print", "after_move:filepath",
        url,
    ]
    if cookie_file:
        dl_cmd = [
            "yt-dlp", "--cookies", cookie_file,
            "-f", "best[filesize<100M]",
            "-o", video_path,
            "--no-playlist",
            "--print", "after_move:filepath",
            url,
        ]

    result = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"  [失败] 下载失败: {result.stderr[:300]}")
        print(f"  [重试] 无限制重试...")
        dl_cmd = [
            "yt-dlp", "--cookies", cookie_file,
            "-f", "best",
            "-o", video_path,
            "--no-playlist",
            url,
        ] if cookie_file else [
            "yt-dlp", "-f", "best",
            "-o", video_path, "--no-playlist", url,
        ]
        result = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        actual_path = result.stdout.strip().split("\n")[-1]
        if os.path.exists(actual_path):
            size_mb = os.path.getsize(actual_path) / (1024 * 1024)
            print(f"  [OK] 下载完成: {size_mb:.1f} MB")
            print(f"       保存至: {actual_path}")
        else:
            print(f"  [OK] 下载完成")
    else:
        print(f"  [失败] 下载失败: {result.stderr[:200]}")

    # Step 3: 输出结果
    print(f"\n{'='*60}")
    print(f"  结果: {title}")
    print(f"  来源: douyin / {uploader}")
    if desc:
        print(f"  简介: {len(desc)} 字")
        quality = "*****" if len(desc) >= 200 else "***" if len(desc) >= 50 else "*"
        print(f"  质量: {quality}")
        print(f"\n{'-'*40}")
        print(desc[:1000])
        if len(desc) > 1000:
            print(f"\n... (共 {len(desc)} 字)")
    else:
        print(f"  简介: (空) - 质量: *")
    print(f"{'='*60}")

    # 清理临时 cookie 文件
    if cookie_file:
        os.unlink(cookie_file)


if __name__ == "__main__":
    main()
