import re
from pathlib import Path
from datetime import datetime

from core.parser import DemoParser
from core.analyzer import DemoAnalyzer
from core.database import Database


class DemoRenamer:
    """
    DEM 文件重命名。

    规则：
        文件名
          ↓
        {时间戳} [{地图名}].dem
    """

    @staticmethod
    def extract_timestamp(demo_path):

        filename = demo_path.stem

        pattern = (
            r"(\d{4}-\d{2}-\d{2}_"
            r"\d{2}-\d{2}-\d{2})"
        )

        match = re.search(pattern, filename)

        if match:
            return match.group(1)

        timestamp = datetime.fromtimestamp(
            demo_path.stat().st_mtime
        )

        return timestamp.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

    @staticmethod
    def get_map_name(data):

        return data.get(
            "header",
            {}
        ).get(
            "map",
            "unknown_map"
        )

    @staticmethod
    def sanitize_name(name):

        return re.sub(
            r'[<>:"/\\|?*]',
            "_",
            str(name)
        )

    def rename(self, demo_path, data):
        """
        重命名 DEM 文件，返回新路径。
        如果文件名已经符合规则，则不处理。
        """

        demo_path = Path(demo_path)

        timestamp = self.extract_timestamp(demo_path)

        map_name = self.sanitize_name(
            self.get_map_name(data)
        )

        new_name = f"{timestamp} [{map_name}].dem"

        new_path = demo_path.parent / new_name

        if demo_path.resolve() == new_path.resolve():
            return demo_path

        # 如果目标已经存在，避免覆盖
        if new_path.exists():

            counter = 2

            while True:

                new_name = (
                    f"{timestamp} [{map_name}] "
                    f"({counter}).dem"
                )

                new_path = demo_path.parent / new_name

                if not new_path.exists():
                    break

                counter += 1

        demo_path.rename(new_path)

        return new_path


class TaskManager:
    """
    批量任务管理。

    负责整条处理链：
        DEM
          ↓
        Rust Parser (DemoParser)
          ↓
        分析 (DemoAnalyzer)
          ↓
        SHA-256 去重 (Database)
          ↓
        入库 (Database.save_match)
    """

    def __init__(
        self,
        parser=None,
        analyzer=None,
        database=None,
        renamer=None,
        auto_rename=False
    ):

        self.parser = parser or DemoParser()

        self.analyzer = analyzer or DemoAnalyzer()

        self.database = database or Database()

        self.renamer = renamer or DemoRenamer()

        self.auto_rename = auto_rename


    # ========================================================
    # 事件回调
    # ========================================================

    @staticmethod
    def _emit(on_event, stage, **kwargs):
        """
        安全触发事件回调（on_event 可选）。
        """

        if on_event:
            on_event({"stage": stage, **kwargs})


    # ========================================================
    # 处理单个 DEM
    # ========================================================

    def process_demo(self, demo_path, on_event=None):
        """
        处理一个 DEM 文件。

        参数：
            demo_path:
                DEM 文件路径

            on_event:
                可选回调，在每个阶段触发：
                    on_event({"stage": ..., ...})

                stage 取值：
                    parse       开始解析
                    analyze     开始分析（Parser 完成）
                    save        开始入库（Analyzer 完成）
                    ok          保存成功
                    duplicate   已存在
                    error       失败

        返回：
            dict
                {
                    "demo_path": str,
                    "demo_name": str,
                    "status": "ok" | "duplicate" | "error",
                    "match_id": int | None,
                    "message": str,
                }
        """

        demo_path = Path(demo_path)

        result = {
            "demo_path": str(demo_path),
            "demo_name": demo_path.name,
            "status": "error",
            "match_id": None,
            "message": "",
        }

        name = demo_path.name

        # ----------------------------------------------------
        # 检查文件
        # ----------------------------------------------------

        if not demo_path.exists():

            result["message"] = "文件不存在"

            self._emit(
                on_event,
                "error",
                demo_name=name,
                message=result["message"]
            )

            return result

        if demo_path.suffix.lower() != ".dem":

            result["message"] = "不是 .dem 文件"

            self._emit(
                on_event,
                "error",
                demo_name=name,
                message=result["message"]
            )

            return result

        # ----------------------------------------------------
        # 解析
        # ----------------------------------------------------

        self._emit(on_event, "parse", demo_name=name)

        try:

            data = self.parser.parse(demo_path)

        except Exception as e:

            result["message"] = f"解析失败：{e}"

            self._emit(
                on_event,
                "error",
                demo_name=name,
                message=result["message"]
            )

            return result

        # ----------------------------------------------------
        # 分析
        # ----------------------------------------------------

        self._emit(on_event, "analyze", demo_name=name)

        try:

            match = self.analyzer.analyze(
                data,
                demo_path
            )

        except Exception as e:

            result["message"] = f"分析失败：{e}"

            self._emit(
                on_event,
                "error",
                demo_name=name,
                message=result["message"]
            )

            return result

        # ----------------------------------------------------
        # SHA-256 去重
        # ----------------------------------------------------

        demo_hash = match["demo_hash"]

        existing_match_id = (
            self.database.get_match_id_by_hash(
                demo_hash
            )
        )

        if existing_match_id is not None:

            result["status"] = "duplicate"

            result["match_id"] = existing_match_id

            result["message"] = (
                f"已存在，match_id={existing_match_id}"
            )

            self._emit(
                on_event,
                "duplicate",
                demo_name=name,
                match_id=existing_match_id
            )

            return result

        # ----------------------------------------------------
        # 入库
        # ----------------------------------------------------

        self._emit(on_event, "save", demo_name=name)

        try:

            match_id = self.database.save_match(match)

        except Exception as e:

            result["message"] = f"入库失败：{e}"

            self._emit(
                on_event,
                "error",
                demo_name=name,
                message=result["message"]
            )

            return result

        result["status"] = "ok"

        result["match_id"] = match_id

        result["message"] = f"保存成功，match_id={match_id}"

        self._emit(
            on_event,
            "ok",
            demo_name=name,
            match_id=match_id
        )

        # ----------------------------------------------------
        # 重命名（可选）
        # ----------------------------------------------------

        if self.auto_rename:

            try:

                new_path = self.renamer.rename(
                    demo_path,
                    data
                )

                result["demo_path"] = str(new_path)

                result["demo_name"] = new_path.name

            except Exception as e:

                result["message"] += f"（重命名失败：{e}）"

        return result


    # ========================================================
    # 批量处理
    # ========================================================

    def process_demos(
        self,
        demo_paths,
        on_progress=None,
        on_event=None
    ):
        """
        批量处理多个 DEM。

        参数：
            demo_paths:
                DEM 文件路径列表

            on_progress:
                可选回调，签名：
                    on_progress(index, total, demo_path, result)

            on_event:
                可选回调，透传给 process_demo

        返回：
            list[dict]
                每个文件的处理结果
        """

        demo_paths = list(demo_paths)

        total = len(demo_paths)

        results = []

        for index, demo_path in enumerate(
            demo_paths,
            start=1
        ):

            result = self.process_demo(
                demo_path,
                on_event=on_event
            )

            results.append(result)

            if on_progress:

                on_progress(
                    index,
                    total,
                    demo_path,
                    result
                )

        return results
