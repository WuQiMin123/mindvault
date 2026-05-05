"""启动脚本 — 修正 sys.path 后启动 uvicorn"""

import sys
from pathlib import Path

# 确保当前目录在路径最前面，避免被其他项目 .pth 文件污染
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
