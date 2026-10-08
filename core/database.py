import sqlite3
from contextlib import closing
from pathlib import Path

from config.config import DATABASE_PATH


class Database:
    """
    SQLite 数据库。

    负责：
        标准化比赛数据
          ↓
        SQLite 表
        matches / match_players / player_classes /
        death_events / weapon_stats / rounds / chat / raw_data

    以及：
        按 demo_hash 去重
        单局战报查询
    """

    def __init__(self, db_path=None):

        self.db_path = Path(
            db_path
            if db_path
            else DATABASE_PATH
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.init_database()


    # ========================================================
    # 数据库连接
    # ========================================================

    def get_connection(self):

        conn = sqlite3.connect(
            self.db_path,
            timeout=30
        )

        # 开启外键约束
        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        return conn


    # ========================================================
    # 初始化数据库
    # ========================================================

    def init_database(self):

        with closing(self.get_connection()) as conn:

            cursor = conn.cursor()

            # ---------------------------------------------
            # matches
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demo_hash TEXT NOT NULL UNIQUE,
                    demo_name TEXT NOT NULL,
                    match_time TEXT,
                    map_name TEXT,
                    recorder TEXT,
                    duration REAL DEFAULT 0,
                    ticks INTEGER DEFAULT 0,
                    frames INTEGER DEFAULT 0,
                    protocol INTEGER DEFAULT 0,
                    winner TEXT,
                    player_count INTEGER DEFAULT 0,
                    kill_count INTEGER DEFAULT 0,
                    start_tick INTEGER DEFAULT 0,
                    interval_per_tick REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ---------------------------------------------
            # match_players
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    steam_id TEXT,
                    player_name TEXT,
                    team TEXT,

                    -- 官方 PlayerSummary
                    points INTEGER DEFAULT 0,
                    scoreboard_kills INTEGER DEFAULT 0,
                    scoreboard_deaths INTEGER DEFAULT 0,
                    scoreboard_assists INTEGER DEFAULT 0,
                    buildings_destroyed INTEGER DEFAULT 0,
                    captures INTEGER DEFAULT 0,
                    defenses INTEGER DEFAULT 0,
                    dominations INTEGER DEFAULT 0,
                    revenges INTEGER DEFAULT 0,
                    ubercharges INTEGER DEFAULT 0,
                    headshots INTEGER DEFAULT 0,
                    teleports INTEGER DEFAULT 0,
                    healing INTEGER DEFAULT 0,
                    backstabs INTEGER DEFAULT 0,
                    bonus_points INTEGER DEFAULT 0,
                    support INTEGER DEFAULT 0,
                    damage_dealt INTEGER DEFAULT 0,

                    -- Death Event 统计
                    event_kills INTEGER DEFAULT 0,
                    event_deaths INTEGER DEFAULT 0,
                    event_assists INTEGER DEFAULT 0,

                    FOREIGN KEY (match_id)
                        REFERENCES matches(id)
                        ON DELETE CASCADE,

                    UNIQUE (match_id, user_id)
                )
            """)

            # ---------------------------------------------
            # player_classes
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_player_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    class_name TEXT NOT NULL,
                    use_count INTEGER DEFAULT 0,
                    FOREIGN KEY (match_player_id)
                        REFERENCES match_players(id)
                        ON DELETE CASCADE,
                    UNIQUE (match_player_id, class_id)
                )
            """)

            # ---------------------------------------------
            # death_events
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS death_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    weapon TEXT,
                    victim_user_id INTEGER,
                    assister_user_id INTEGER,
                    killer_user_id INTEGER,
                    tick INTEGER DEFAULT 0,
                    FOREIGN KEY (match_id)
                        REFERENCES matches(id)
                        ON DELETE CASCADE
                )
            """)

            # ---------------------------------------------
            # weapon_stats
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weapon_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_player_id INTEGER NOT NULL,
                    weapon TEXT NOT NULL,
                    kills INTEGER DEFAULT 0,
                    FOREIGN KEY (match_player_id)
                        REFERENCES match_players(id)
                        ON DELETE CASCADE,
                    UNIQUE (match_player_id, weapon)
                )
            """)

            # ---------------------------------------------
            # rounds
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    winner TEXT,
                    length REAL DEFAULT 0,
                    end_tick INTEGER DEFAULT 0,
                    FOREIGN KEY (match_id)
                        REFERENCES matches(id)
                        ON DELETE CASCADE,
                    UNIQUE (match_id, round_number)
                )
            """)

            # ---------------------------------------------
            # chat
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    kind TEXT,
                    player_name TEXT,
                    message TEXT,
                    tick INTEGER DEFAULT 0,
                    FOREIGN KEY (match_id)
                        REFERENCES matches(id)
                        ON DELETE CASCADE
                )
            """)

            # ---------------------------------------------
            # raw_data
            # ---------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL UNIQUE,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (match_id)
                        REFERENCES matches(id)
                        ON DELETE CASCADE
                )
            """)

            # ---------------------------------------------
            # 索引
            # ---------------------------------------------

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_match_time
                ON matches(match_time)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_map_name
                ON matches(map_name)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_players_steam_id
                ON match_players(steam_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deaths_killer
                ON death_events(killer_user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deaths_victim
                ON death_events(victim_user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deaths_weapon
                ON death_events(weapon)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_weapon_stats_weapon
                ON weapon_stats(weapon)
            """)

            conn.commit()


    # ========================================================
    # 查询 Demo 是否已经存在
    # ========================================================

    def exists_by_hash(self, demo_hash):

        with closing(self.get_connection()) as conn:

            cursor = conn.execute(
                """
                SELECT id
                FROM matches
                WHERE demo_hash = ?
                LIMIT 1
                """,
                (demo_hash,)
            )

            row = cursor.fetchone()

            return row is not None


    # ========================================================
    # 根据 Hash 获取比赛 ID
    # ========================================================

    def get_match_id_by_hash(self, demo_hash):

        with closing(self.get_connection()) as conn:

            cursor = conn.execute(
                """
                SELECT id
                FROM matches
                WHERE demo_hash = ?
                LIMIT 1
                """,
                (demo_hash,)
            )

            row = cursor.fetchone()

            if row:
                return row[0]

            return None


    # ========================================================
    # 保存一场完整比赛
    # ========================================================

    def save_match(self, match):

        conn = self.get_connection()

        try:

            cursor = conn.cursor()

            # ---------------------------------------------
            # 1. 插入比赛
            # ---------------------------------------------

            cursor.execute("""
                INSERT INTO matches (
                    demo_hash, demo_name, match_time, map_name,
                    recorder, duration, ticks, frames, protocol,
                    winner, player_count, kill_count,
                    start_tick, interval_per_tick
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match["demo_hash"],
                match["demo_name"],
                match["match_time"],
                match["map_name"],
                match["recorder"],
                match["duration"],
                match["ticks"],
                match["frames"],
                match["protocol"],
                match["winner"],
                match["player_count"],
                match["kill_count"],
                match["start_tick"],
                match["interval_per_tick"],
            ))

            match_id = cursor.lastrowid

            # ---------------------------------------------
            # 2. 玩家
            # ---------------------------------------------

            for player in match["players"]:

                cursor.execute("""
                    INSERT INTO match_players (
                        match_id, user_id, steam_id, player_name, team,
                        points, scoreboard_kills, scoreboard_deaths,
                        scoreboard_assists,
                        buildings_destroyed, captures, defenses,
                        dominations, revenges, ubercharges, headshots,
                        teleports, healing, backstabs, bonus_points,
                        support, damage_dealt,
                        event_kills, event_deaths, event_assists
                    )
                    VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?
                    )
                """, (
                    match_id,
                    player["user_id"],
                    player["steam_id"],
                    player["player_name"],
                    player["team"],
                    player["points"],
                    player["scoreboard_kills"],
                    player["scoreboard_deaths"],
                    player["scoreboard_assists"],
                    player["buildings_destroyed"],
                    player["captures"],
                    player["defenses"],
                    player["dominations"],
                    player["revenges"],
                    player["ubercharges"],
                    player["headshots"],
                    player["teleports"],
                    player["healing"],
                    player["backstabs"],
                    player["bonus_points"],
                    player["support"],
                    player["damage_dealt"],
                    player["event_kills"],
                    player["event_deaths"],
                    player["event_assists"],
                ))

                match_player_id = cursor.lastrowid

                # -----------------------------------------
                # 3. 职业
                # -----------------------------------------

                for class_id, class_data in player[
                    "classes"
                ].items():

                    cursor.execute("""
                        INSERT INTO player_classes (
                            match_player_id, class_id,
                            class_name, use_count
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        match_player_id,
                        class_id,
                        class_data["class_name"],
                        class_data["use_count"],
                    ))

            # ---------------------------------------------
            # 4. 死亡事件
            # ---------------------------------------------

            weapon_kills = {}

            for death in match["deaths"]:

                weapon = death.get("weapon")
                victim = death.get("victim")
                assister = death.get("assister")
                killer = death.get("killer")
                tick = death.get("tick", 0)

                cursor.execute("""
                    INSERT INTO death_events (
                        match_id, weapon, victim_user_id,
                        assister_user_id, killer_user_id, tick
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    match_id,
                    weapon,
                    victim,
                    assister,
                    killer,
                    tick,
                ))

                # -----------------------------------------
                # 武器击杀统计
                # -----------------------------------------

                if (
                        killer is not None
                        and killer != 0
                        and weapon
                ):

                    key = (killer, weapon)

                    weapon_kills[key] = (
                        weapon_kills.get(key, 0) + 1
                    )

            # ---------------------------------------------
            # 5. weapon_stats
            # ---------------------------------------------

            player_db_ids = {}

            rows = cursor.execute("""
                SELECT id, user_id
                FROM match_players
                WHERE match_id = ?
            """, (match_id,)).fetchall()

            for row in rows:

                player_db_ids[row[1]] = row[0]

            for (user_id, weapon), kills in weapon_kills.items():

                match_player_id = player_db_ids.get(user_id)

                if match_player_id is None:
                    continue

                cursor.execute("""
                    INSERT INTO weapon_stats (
                        match_player_id, weapon, kills
                    )
                    VALUES (?, ?, ?)
                """, (
                    match_player_id,
                    weapon,
                    kills,
                ))

            # ---------------------------------------------
            # 6. rounds
            # ---------------------------------------------

            for index, round_data in enumerate(
                match["rounds"],
                start=1
            ):

                cursor.execute("""
                    INSERT INTO rounds (
                        match_id, round_number, winner,
                        length, end_tick
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    match_id,
                    index,
                    round_data.get("winner"),
                    round_data.get("length", 0),
                    round_data.get("end_tick", 0),
                ))

            # ---------------------------------------------
            # 7. chat
            # ---------------------------------------------

            for message in match["chat"]:

                cursor.execute("""
                    INSERT INTO chat (
                        match_id, kind, player_name, message, tick
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    match_id,
                    message.get("kind", ""),
                    message.get("from", ""),
                    message.get("text", ""),
                    message.get("tick", 0),
                ))

            # ---------------------------------------------
            # 8. 原始 JSON
            # ---------------------------------------------

            cursor.execute("""
                INSERT INTO raw_data (match_id, json_data)
                VALUES (?, ?)
            """, (
                match_id,
                match["raw_json"],
            ))

            # ---------------------------------------------
            # 9. 提交事务
            # ---------------------------------------------

            conn.commit()

            return match_id

        except Exception:

            conn.rollback()

            raise

        finally:

            conn.close()


    # ========================================================
    # 获取单局完整战报
    # ========================================================

    def get_match_report(self, match_id):

        conn = self.get_connection()

        try:

            cursor = conn.cursor()

            # ---------------------------------------------
            # 1. 比赛基本信息
            # ---------------------------------------------

            cursor.execute("""
                SELECT
                    id, demo_hash, demo_name, match_time,
                    map_name, recorder, duration, ticks,
                    frames, protocol, winner, player_count,
                    kill_count, start_tick, interval_per_tick,
                    created_at
                FROM matches
                WHERE id = ?
            """, (match_id,))

            match_row = cursor.fetchone()

            if match_row is None:
                return None

            match = {
                "id": match_row[0],
                "demo_hash": match_row[1],
                "demo_name": match_row[2],
                "match_time": match_row[3],
                "map_name": match_row[4],
                "recorder": match_row[5],
                "duration": match_row[6],
                "ticks": match_row[7],
                "frames": match_row[8],
                "protocol": match_row[9],
                "winner": match_row[10],
                "player_count": match_row[11],
                "kill_count": match_row[12],
                "start_tick": match_row[13],
                "interval_per_tick": match_row[14],
                "created_at": match_row[15],
                "red": [],
                "blue": [],
                "team_stats": {},
                "rounds": [],
                "chat": [],
                "death_events": [],
            }

            # ---------------------------------------------
            # 2. 查询所有玩家
            # ---------------------------------------------

            cursor.execute("""
                SELECT
                    id, user_id, steam_id, player_name, team,
                    points, scoreboard_kills, scoreboard_deaths,
                    scoreboard_assists,
                    buildings_destroyed, captures, defenses,
                    dominations, revenges, ubercharges, headshots,
                    teleports, healing, backstabs, bonus_points,
                    support, damage_dealt,
                    event_kills, event_deaths, event_assists
                FROM match_players
                WHERE match_id = ?
                ORDER BY team, points DESC, scoreboard_kills DESC
            """, (match_id,))

            player_rows = cursor.fetchall()

            # ---------------------------------------------
            # 3. 玩家数据
            # ---------------------------------------------

            for row in player_rows:

                player = {
                    "id": row[0],
                    "user_id": row[1],
                    "steam_id": row[2],
                    "player_name": row[3],
                    "team": row[4],
                    "points": row[5],
                    "scoreboard_kills": row[6],
                    "scoreboard_deaths": row[7],
                    "scoreboard_assists": row[8],
                    "buildings_destroyed": row[9],
                    "captures": row[10],
                    "defenses": row[11],
                    "dominations": row[12],
                    "revenges": row[13],
                    "ubercharges": row[14],
                    "headshots": row[15],
                    "teleports": row[16],
                    "healing": row[17],
                    "backstabs": row[18],
                    "bonus_points": row[19],
                    "support": row[20],
                    "damage_dealt": row[21],
                    "event_kills": row[22],
                    "event_deaths": row[23],
                    "event_assists": row[24],
                    "classes": [],
                    "weapons": [],
                }

                # -----------------------------------------
                # 查询职业
                # -----------------------------------------

                cursor.execute("""
                    SELECT class_id, class_name, use_count
                    FROM player_classes
                    WHERE match_player_id = ?
                    ORDER BY use_count DESC
                """, (player["id"],))

                for class_row in cursor.fetchall():

                    player["classes"].append({
                        "class_id": class_row[0],
                        "class_name": class_row[1],
                        "use_count": class_row[2],
                    })

                # -----------------------------------------
                # 查询武器
                # -----------------------------------------

                cursor.execute("""
                    SELECT weapon, kills
                    FROM weapon_stats
                    WHERE match_player_id = ?
                    ORDER BY kills DESC
                """, (player["id"],))

                for weapon_row in cursor.fetchall():

                    player["weapons"].append({
                        "weapon": weapon_row[0],
                        "kills": weapon_row[1],
                    })

                # -----------------------------------------
                # 按队伍保存
                # -----------------------------------------

                if player["team"].lower() == "red":
                    match["red"].append(player)

                elif player["team"].lower() == "blue":
                    match["blue"].append(player)

            # ---------------------------------------------
            # 4. 计算双方总数据
            # ---------------------------------------------

            for team_name, players in [
                ("red", match["red"]),
                ("blue", match["blue"]),
            ]:

                stats = {
                    "player_count": len(players),
                    "points": 0,
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "damage_dealt": 0,
                    "healing": 0,
                    "captures": 0,
                    "defenses": 0,
                    "dominations": 0,
                    "revenges": 0,
                    "ubercharges": 0,
                    "headshots": 0,
                    "teleports": 0,
                    "backstabs": 0,
                    "buildings_destroyed": 0,
                    "bonus_points": 0,
                    "support": 0,
                }

                for player in players:

                    stats["points"] += player["points"]
                    stats["kills"] += player["scoreboard_kills"]
                    stats["deaths"] += player["scoreboard_deaths"]
                    stats["assists"] += player["scoreboard_assists"]
                    stats["damage_dealt"] += player["damage_dealt"]
                    stats["healing"] += player["healing"]
                    stats["captures"] += player["captures"]
                    stats["defenses"] += player["defenses"]
                    stats["dominations"] += player["dominations"]
                    stats["revenges"] += player["revenges"]
                    stats["ubercharges"] += player["ubercharges"]
                    stats["headshots"] += player["headshots"]
                    stats["teleports"] += player["teleports"]
                    stats["backstabs"] += player["backstabs"]
                    stats["buildings_destroyed"] += (
                        player["buildings_destroyed"]
                    )
                    stats["bonus_points"] += player["bonus_points"]
                    stats["support"] += player["support"]

                match["team_stats"][team_name] = stats

            # ---------------------------------------------
            # 5. 回合
            # ---------------------------------------------

            cursor.execute("""
                SELECT round_number, winner, length, end_tick
                FROM rounds
                WHERE match_id = ?
                ORDER BY round_number
            """, (match_id,))

            for row in cursor.fetchall():

                match["rounds"].append({
                    "round_number": row[0],
                    "winner": row[1],
                    "length": row[2],
                    "end_tick": row[3],
                })

            # ---------------------------------------------
            # 6. 聊天
            # ---------------------------------------------

            cursor.execute("""
                SELECT kind, player_name, message, tick
                FROM chat
                WHERE match_id = ?
                ORDER BY tick
            """, (match_id,))

            for row in cursor.fetchall():

                match["chat"].append({
                    "kind": row[0],
                    "player_name": row[1],
                    "message": row[2],
                    "tick": row[3],
                })

            # ---------------------------------------------
            # 7. 死亡事件
            # ---------------------------------------------

            cursor.execute("""
                SELECT weapon, victim_user_id,
                       assister_user_id, killer_user_id, tick
                FROM death_events
                WHERE match_id = ?
                ORDER BY tick
            """, (match_id,))

            for row in cursor.fetchall():

                match["death_events"].append({
                    "weapon": row[0],
                    "victim_user_id": row[1],
                    "assister_user_id": row[2],
                    "killer_user_id": row[3],
                    "tick": row[4],
                })

            return match

        finally:

            conn.close()
