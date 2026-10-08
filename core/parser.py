import json
import subprocess
from pathlib import Path

from config.config import PARSER_PATH


class DemoParser:
    """
    TF2 Demo Rust Parser 封装类。

    负责：
        DEM文件
          ↓
        parse_demo.exe
          ↓
        JSON
          ↓
        Python dict
    """

    def __init__(self, parser_path=None):

        self.parser_path = Path(
            parser_path
            if parser_path
            else PARSER_PATH
        )


    # ========================================================
    # 检查解析器
    # ========================================================

    def check_parser(self):
        """
        检查 Rust Parser 是否存在。
        """

        if not self.parser_path.exists():

            raise FileNotFoundError(
                f"找不到 Rust Demo Parser：\n"
                f"{self.parser_path}"
            )


        if not self.parser_path.is_file():

            raise FileNotFoundError(
                f"Parser 路径不是文件：\n"
                f"{self.parser_path}"
            )


        return True


    # ========================================================
    # 解析 DEM
    # ========================================================

    def parse(self, demo_path):
        """
        解析一个 DEM 文件。

        参数：
            demo_path:
                DEM文件路径

        返回：
            dict
                Rust Parser 输出的 JSON 数据
        """

        demo_path = Path(demo_path)


        # ----------------------------------------------------
        # 检查 DEM
        # ----------------------------------------------------

        if not demo_path.exists():

            raise FileNotFoundError(
                f"DEM 文件不存在：\n"
                f"{demo_path}"
            )


        if not demo_path.is_file():

            raise ValueError(
                f"DEM 路径不是文件：\n"
                f"{demo_path}"
            )


        if demo_path.suffix.lower() != ".dem":

            raise ValueError(
                f"不是 DEM 文件：\n"
                f"{demo_path}"
            )


        # ----------------------------------------------------
        # 检查 Parser
        # ----------------------------------------------------

        self.check_parser()


        # ----------------------------------------------------
        # 调用 Rust Parser
        # ----------------------------------------------------

        command = [
            str(self.parser_path),
            str(demo_path)
        ]


        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

        except Exception as e:

            raise RuntimeError(
                f"启动 Rust Parser 失败：{e}"
            )


        # ----------------------------------------------------
        # 检查返回码
        # ----------------------------------------------------

        if result.returncode != 0:

            stderr = (
                result.stderr.strip()
                if result.stderr
                else "未知错误"
            )

            raise RuntimeError(
                "Rust Demo Parser 解析失败\n\n"
                f"DEM：{demo_path.name}\n\n"
                f"错误信息：\n{stderr}"
            )


        # ----------------------------------------------------
        # 获取 JSON
        # ----------------------------------------------------

        output = result.stdout.strip()


        if not output:

            raise RuntimeError(
                "Rust Parser 没有返回任何数据"
            )


        # ----------------------------------------------------
        # JSON解析
        # ----------------------------------------------------

        try:

            data = json.loads(output)

        except json.JSONDecodeError as e:

            raise RuntimeError(
                "Rust Parser 返回的数据不是合法 JSON。\n\n"
                f"错误位置：{e}\n\n"
                f"Parser 输出：\n{output[:2000]}"
            )


        return data
