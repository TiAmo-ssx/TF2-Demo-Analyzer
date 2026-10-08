import socket
import threading
import webbrowser

from flask import Flask

from config.config import (
    WEB_HOST,
    WEB_DEFAULT_PORT,
    TEMPLATE_DIR,
    STATIC_DIR,
)

from web.routes import register_routes


# ============================================================
# 创建 Flask App
# ============================================================

def create_app():
    """
    创建 Flask 应用。

    template_folder / static_folder 指向程序资源目录，
    这样 PyInstaller 打包后也能找到模板和静态文件。
    """

    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
    )

    register_routes(app)

    return app


# ============================================================
# 空闲端口查找
# ============================================================

def find_free_port(start_port=None):
    """
    从 start_port 开始，依次尝试，返回第一个可用端口。
    """

    start_port = start_port or WEB_DEFAULT_PORT

    for port in range(start_port, start_port + 100):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            try:
                s.bind((WEB_HOST, port))
                return port

            except OSError:
                continue

    raise RuntimeError(
        f"找不到可用端口（{start_port} ~ {start_port + 99}）"
    )


# ============================================================
# 启动服务器
# ============================================================

def start_server(port=None, open_browser=True):
    """
    在后台线程启动 Flask 服务器。

    参数：
        port:
            指定端口；None 则自动查找空闲端口

        open_browser:
            True 则自动打开浏览器

    返回：
        str
            访问地址，例如 http://127.0.0.1:8765
    """

    app = create_app()

    actual_port = port or find_free_port()

    url = f"http://{WEB_HOST}:{actual_port}"

    thread = threading.Thread(
        target=lambda: app.run(
            host=WEB_HOST,
            port=actual_port,
            debug=False,
            use_reloader=False
        ),
        daemon=True,
    )

    thread.start()

    if open_browser:
        webbrowser.open(url)

    return url
