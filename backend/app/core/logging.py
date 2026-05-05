"""日志配置：标准 logging + 按日分目录 + 自动清理旧日志"""

import logging
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings

LOG_FORMAT = "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    # 避免重复添加 handler（热重载时）
    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # 文件输出：log/YYYY-MM-DD/mindvault.log
    base = Path(settings.log_dir)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = base / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "mindvault.log"

    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 清理超过 7 天的日志
    _clean_old_logs(base)

    # 抑制 httpx 的请求日志
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("日志初始化完成 | %s", log_path)


def _clean_old_logs(log_dir: Path, days: int = 7) -> None:
    cutoff = datetime.now() - timedelta(days=days)
    if not log_dir.exists():
        return
    for entry in log_dir.iterdir():
        if entry.is_dir():
            try:
                dir_date = datetime.strptime(entry.name, "%Y-%m-%d")
                if dir_date < cutoff:
                    shutil.rmtree(entry)
            except ValueError:
                continue
