import json
import re
from pathlib import Path
from datetime import datetime

from core.hash_manager import HashManager


CLASS_NAMES = {
    0: "Other",
    1: "Scout",
    2: "Sniper",
    3: "Soldier",
    4: "Demoman",
    5: "Medic",
    6: "Heavy",
    7: "Pyro",
    8: "Spy",
    9: "Engineer",
}


class DemoAnalyzer:
    """
    TF2 Demo 数据分析器。

    Rust Parser：
        DEM → JSON

    Analyzer：
        JSON → 标准化比赛数据

    标准化数据包含：
        demo_hash         文件 SHA-256（去重）
        demo_name         文件名
        match_time        比赛时间
        map_name          地图
        players           玩家列表（含职业、PlayerSummary、死亡事件统计）
        deaths            死亡事件
        rounds            回合
        chat              聊天
        raw_json          原始 JSON（存档用）
    """

    def __init__(self):

        self.hash_manager = HashManager()


    # ========================================================
    # 主分析入口
    # ========================================================

    def analyze(
        self,
        data: dict,
        demo_path=None
    ):
        """
        分析 Rust Parser 输出。

        参数：
            data:
                Rust Parser 返回的 JSON

            demo_path:
                原始 DEM 文件路径

        返回：
            dict
                标准化后的比赛数据
        """

        if not isinstance(data, dict):

            raise ValueError(
                "Parser 数据必须是 dict"
            )


        demo_path = (
            Path(demo_path)
            if demo_path
            else None
        )


        # ----------------------------------------------------
        # 基础数据
        # ----------------------------------------------------

        header = data.get(
            "header",
            {}
        )

        users = data.get(
            "users",
            {}
        )

        player_summaries = data.get(
            "playerSummaries",
            {}
        )

        deaths = data.get(
            "deaths",
            []
        )

        rounds = data.get(
            "rounds",
            []
        )

        chat = data.get(
            "chat",
            []
        )


        # ----------------------------------------------------
        # SHA-256
        # ----------------------------------------------------

        demo_hash = (
            self.hash_manager.calculate(
                demo_path
            )
            if demo_path
            else ""
        )


        # ----------------------------------------------------
        # 玩家
        # ----------------------------------------------------

        players = {}

        for user_id, user in users.items():

            try:
                uid = int(user_id)

            except (ValueError, TypeError):
                uid = user.get(
                    "userId",
                    0
                )

            # ---------------------------------------------
            # 职业
            # ---------------------------------------------

            classes = {}

            for class_id, count in user.get(
                    "classes",
                    {}
            ).items():

                try:
                    cid = int(class_id)

                except (ValueError, TypeError):
                    continue

                classes[cid] = {
                    "class_name": CLASS_NAMES.get(
                        cid,
                        f"Unknown({cid})"
                    ),
                    "use_count": count
                }

            # ---------------------------------------------
            # PlayerSummary
            # ---------------------------------------------

            summary = player_summaries.get(
                str(uid),
                {}
            )

            players[uid] = {

                "user_id": uid,

                "steam_id": user.get(
                    "steamId",
                    ""
                ),

                "player_name": user.get(
                    "name",
                    "Unknown"
                ),

                "team": user.get(
                    "team",
                    "unknown"
                ),

                "classes": classes,

                # -----------------------------------------
                # 官方 PlayerSummary
                # -----------------------------------------

                "points": summary.get(
                    "points",
                    0
                ),

                "scoreboard_kills": summary.get(
                    "kills",
                    0
                ),

                "scoreboard_deaths": summary.get(
                    "deaths",
                    0
                ),

                "scoreboard_assists": summary.get(
                    "assists",
                    0
                ),

                "buildings_destroyed": summary.get(
                    "buildings_destroyed",
                    0
                ),

                "captures": summary.get(
                    "captures",
                    0
                ),

                "defenses": summary.get(
                    "defenses",
                    0
                ),

                "dominations": summary.get(
                    "dominations",
                    0
                ),

                "revenges": summary.get(
                    "revenges",
                    0
                ),

                "ubercharges": summary.get(
                    "ubercharges",
                    0
                ),

                "headshots": summary.get(
                    "headshots",
                    0
                ),

                "teleports": summary.get(
                    "teleports",
                    0
                ),

                "healing": summary.get(
                    "healing",
                    0
                ),

                "backstabs": summary.get(
                    "backstabs",
                    0
                ),

                "bonus_points": summary.get(
                    "bonus_points",
                    0
                ),

                "support": summary.get(
                    "support",
                    0
                ),

                "damage_dealt": summary.get(
                    "damage_dealt",
                    0
                ),

                # -----------------------------------------
                # 后面根据 death_events 计算
                # -----------------------------------------

                "event_kills": 0,
                "event_deaths": 0,
                "event_assists": 0,
            }

        # ----------------------------------------------------
        # Death Events
        #
        # 只作为事件统计保存，不覆盖 PlayerSummary。
        # ----------------------------------------------------

        for death in deaths:

            killer = death.get(
                "killer"
            )

            victim = death.get(
                "victim"
            )

            assister = death.get(
                "assister"
            )

            # Killer
            if (
                    killer is not None
                    and killer != 0
                    and killer in players
            ):
                players[killer][
                    "event_kills"
                ] += 1

            # Victim
            if (
                    victim is not None
                    and victim in players
            ):
                players[victim][
                    "event_deaths"
                ] += 1

            # Assister
            if (
                    assister is not None
                    and assister in players
            ):
                players[assister][
                    "event_assists"
                ] += 1

        # ----------------------------------------------------
        # 最后一回合的胜者
        # ----------------------------------------------------

        winner = None

        if rounds:

            winner = rounds[-1].get(
                "winner"
            )

        # ----------------------------------------------------
        # 时间
        # ----------------------------------------------------

        match_time = self.extract_time(
            demo_path
        )

        # ----------------------------------------------------
        # 最终结果
        # ----------------------------------------------------

        return {

            "demo_hash": demo_hash,

            "demo_name": (
                demo_path.name
                if demo_path
                else ""
            ),

            "match_time": match_time,

            "map_name": header.get(
                "map",
                "unknown"
            ),

            "recorder": header.get(
                "nick",
                ""
            ),

            "duration": header.get(
                "duration",
                0
            ),

            "ticks": header.get(
                "ticks",
                0
            ),

            "frames": header.get(
                "frames",
                0
            ),

            "protocol": header.get(
                "protocol",
                0
            ),

            "winner": winner,

            "player_count": len(
                players
            ),

            "kill_count": len(
                deaths
            ),

            "players": list(
                players.values()
            ),

            "deaths": deaths,

            "rounds": rounds,

            "chat": chat,

            "start_tick": data.get(
                "startTick",
                0
            ),

            "interval_per_tick": data.get(
                "intervalPerTick",
                0
            ),

            "pauses": data.get(
                "pauses",
                []
            ),

            "raw_json": json.dumps(
                data,
                ensure_ascii=False
            )
        }


    # ========================================================
    # 从文件名提取比赛时间
    # ========================================================

    @staticmethod
    def extract_time(demo_path):

        if demo_path is None:
            return ""

        filename = demo_path.stem

        pattern = (
            r"(\d{4}-\d{2}-\d{2}_"
            r"\d{2}-\d{2}-\d{2})"
        )

        match = re.search(
            pattern,
            filename
        )

        if match:

            try:

                return datetime.strptime(
                    match.group(1),
                    "%Y-%m-%d_%H-%M-%S"
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            except ValueError:
                pass

        return datetime.fromtimestamp(
            demo_path.stat().st_mtime
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
