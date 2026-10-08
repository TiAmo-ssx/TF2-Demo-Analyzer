import os
import sys
from pathlib import Path


# ============================================================
# 基础路径（程序资源）
# ============================================================

def get_base_dir() -> Path:
    """
    获取程序资源目录（parse_demo.exe / templates / static 所在目录）。

    开发环境：
        返回项目根目录

    PyInstaller：
        返回 _MEIPASS（数据文件解压目录）
        onedir 下是 dist/App/_internal，
        onefile 下是临时解压目录。
    """

    if getattr(sys, "frozen", False):

        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


# ============================================================
# 用户数据目录（数据库 / JSON / 日志）
# ============================================================

def get_data_dir() -> Path:
    """
    获取用户数据目录。

    开发环境：
        项目内 workspace/

    发布环境（PyInstaller）：
        %LOCALAPPDATA%/TF2-Demo-Analyzer/

    这样即使把程序放到 Program Files，
    普通用户也能写入数据库和日志。
    """

    if getattr(sys, "frozen", False):

        local_appdata = os.environ.get(
            "LOCALAPPDATA",
            str(Path.home() / "AppData" / "Local")
        )

        return Path(local_appdata) / "TF2-Demo-Analyzer"

    return BASE_DIR / "workspace"


DATA_DIR = get_data_dir()

# 兼容旧命名
WORKSPACE_DIR = DATA_DIR


# ============================================================
# Rust Demo Parser
# ============================================================

PARSER_PATH = (
    BASE_DIR
    / "resources"
    / "parser"
    / "parse_demo.exe"
)


# ============================================================
# Workspace 子目录
# ============================================================

DATABASE_DIR = (
    DATA_DIR
    / "database"
)


JSON_DIR = (
    DATA_DIR
    / "json"
)


LOG_DIR = (
    DATA_DIR
    / "logs"
)


DATABASE_PATH = (
    DATABASE_DIR
    / "tf_demo.db"
)


# ============================================================
# Flask Web 资源（templates / static）
# ============================================================

WEB_DIR = (
    BASE_DIR
    / "web"
)


TEMPLATE_DIR = (
    WEB_DIR
    / "templates"
)


STATIC_DIR = (
    WEB_DIR
    / "static"
)


WEB_HOST = "127.0.0.1"

WEB_DEFAULT_PORT = 8765


# ============================================================
# 其他配置
# ============================================================

SUPPORTED_DEMO_EXTENSION = ".dem"


# ============================================================
# 初始化目录
# ============================================================

def ensure_directories():
    """
    创建程序运行所需要的目录。
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    JSON_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
