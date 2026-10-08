import sqlite3

from flask import render_template, request, redirect, url_for

from config.config import DATABASE_PATH

from utils.i18n import (
    LANGUAGES,
    DEFAULT_LANG,
    TRANSLATIONS,
    get_text,
)


# ============================================================
# 数据库
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_match_ids():
    conn = get_db()

    rows = conn.execute("""
        SELECT id, demo_name, map_name, match_time
        FROM matches
        ORDER BY match_time DESC, id DESC
    """).fetchall()

    conn.close()
    return rows


def get_match_data(match_id):
    conn = get_db()

    # --------------------------------------------------------
    # 比赛基本信息
    # --------------------------------------------------------

    match = conn.execute("""
        SELECT *
        FROM matches
        WHERE id = ?
    """, (match_id,)).fetchone()

    if match is None:
        conn.close()
        return None

    # --------------------------------------------------------
    # 玩家
    # --------------------------------------------------------

    players = conn.execute("""
        SELECT *
        FROM match_players
        WHERE match_id = ?
        ORDER BY
            CASE
                WHEN team = 'red' THEN 0
                WHEN team = 'blue' THEN 1
                ELSE 2
                END,
            points DESC,
            scoreboard_kills DESC
    """, (match_id,)).fetchall()

    # --------------------------------------------------------
    # 职业
    # --------------------------------------------------------

    classes = conn.execute("""
        SELECT match_player_id, class_id, class_name, use_count
        FROM player_classes
        WHERE match_player_id IN (
            SELECT id FROM match_players WHERE match_id = ?
        )
        ORDER BY use_count DESC
    """, (match_id,)).fetchall()

    # --------------------------------------------------------
    # 武器
    # --------------------------------------------------------

    weapons = conn.execute("""
        SELECT match_player_id, weapon, kills
        FROM weapon_stats
        WHERE match_player_id IN (
            SELECT id FROM match_players WHERE match_id = ?
        )
        ORDER BY kills DESC
    """, (match_id,)).fetchall()

    # --------------------------------------------------------
    # 回合
    # --------------------------------------------------------

    rounds = conn.execute("""
        SELECT *
        FROM rounds
        WHERE match_id = ?
        ORDER BY round_number
    """, (match_id,)).fetchall()

    # --------------------------------------------------------
    # 组装玩家数据
    # --------------------------------------------------------

    player_list = []

    for player in players:
        player = dict(player)

        player["classes"] = []
        player["weapons"] = []

        for cls in classes:
            if cls["match_player_id"] == player["id"]:
                player["classes"].append({
                    "name": cls["class_name"],
                    "count": cls["use_count"]
                })

        for weapon in weapons:
            if weapon["match_player_id"] == player["id"]:
                player["weapons"].append({
                    "name": weapon["weapon"],
                    "kills": weapon["kills"]
                })

        player_list.append(player)

    # --------------------------------------------------------
    # RED / BLU 汇总
    # --------------------------------------------------------

    metric_fields = [
        "points",
        "scoreboard_kills",
        "scoreboard_deaths",
        "scoreboard_assists",
        "damage_dealt",
        "healing",
        "captures",
        "defenses",
        "dominations",
        "revenges",
        "ubercharges",
        "headshots",
        "teleports",
        "backstabs",
        "buildings_destroyed",
    ]

    teams = {
        "red": {
            "name": "RED",
            "players": [],
            "totals": {field: 0 for field in metric_fields}
        },
        "blue": {
            "name": "BLU",
            "players": [],
            "totals": {field: 0 for field in metric_fields}
        },
        "other": {
            "name": "OTHER",
            "players": [],
            "totals": {field: 0 for field in metric_fields}
        }
    }

    for player in player_list:
        team = player.get("team", "other")

        if team not in teams:
            team = "other"

        teams[team]["players"].append(player)

        for field in metric_fields:
            value = player.get(field)

            if value is None:
                value = 0

            teams[team]["totals"][field] += value

    # --------------------------------------------------------
    # 玩家图表数据 + 玩家卡片数据
    # --------------------------------------------------------

    chart_players = []

    for player in player_list:

        chart_players.append({
            "id": player["id"],
            "name": player["player_name"],
            "team": player.get("team", "other"),

            "kills": player.get("scoreboard_kills", 0) or 0,
            "deaths": player.get("scoreboard_deaths", 0) or 0,
            "assists": player.get("scoreboard_assists", 0) or 0,

            "points": player.get("points", 0) or 0,

            "damage": player.get("damage_dealt", 0) or 0,
            "healing": player.get("healing", 0) or 0,

            "captures": player.get("captures", 0) or 0,
            "defenses": player.get("defenses", 0) or 0,

            "headshots": player.get("headshots", 0) or 0,
            "backstabs": player.get("backstabs", 0) or 0,

            "ubercharges": player.get("ubercharges", 0) or 0,

            "buildings": player.get("buildings_destroyed", 0) or 0,

            "teleports": player.get("teleports", 0) or 0,

            "dominations": player.get("dominations", 0) or 0,

            "revenges": player.get("revenges", 0) or 0,

            "bonus_points": player.get("bonus_points", 0) or 0,

            "support": player.get("support", 0) or 0,

            "classes": player["classes"],

            "weapons": player["weapons"]
        })

    # --------------------------------------------------------
    # 队伍图表数据
    # --------------------------------------------------------

    team_chart = {
        "labels": ["RED", "BLU"],
        "points": [
            teams["red"]["totals"]["points"],
            teams["blue"]["totals"]["points"]
        ],
        "kills": [
            teams["red"]["totals"]["scoreboard_kills"],
            teams["blue"]["totals"]["scoreboard_kills"]
        ],
        "deaths": [
            teams["red"]["totals"]["scoreboard_deaths"],
            teams["blue"]["totals"]["scoreboard_deaths"]
        ],
        "assists": [
            teams["red"]["totals"]["scoreboard_assists"],
            teams["blue"]["totals"]["scoreboard_assists"]
        ],
        "damage": [
            teams["red"]["totals"]["damage_dealt"],
            teams["blue"]["totals"]["damage_dealt"]
        ],
        "healing": [
            teams["red"]["totals"]["healing"],
            teams["blue"]["totals"]["healing"]
        ],
        "captures": [
            teams["red"]["totals"]["captures"],
            teams["blue"]["totals"]["captures"]
        ],
        "defenses": [
            teams["red"]["totals"]["defenses"],
            teams["blue"]["totals"]["defenses"]
        ]
    }

    conn.close()

    return {
        "match": dict(match),
        "players": player_list,
        "chart_players": chart_players,
        "teams": teams,
        "team_chart": team_chart,
        "rounds": [dict(r) for r in rounds]
    }


# ============================================================
# 比赛管理
# ============================================================

# 可排序列（白名单，防止 SQL 注入）
SORTABLE_COLUMNS = {
    "id": "id",
    "demo_name": "demo_name",
    "map_name": "map_name",
    "match_time": "match_time",
    "player_count": "player_count",
    "duration": "duration",
}


def get_all_matches(search=None, sort="id", order="desc"):
    """
    列出所有比赛（可选按关键词搜索、按列排序）。
    """

    conn = get_db()

    sql = """
        SELECT id, demo_name, map_name, match_time,
               player_count, kill_count, duration, winner
        FROM matches
    """

    params = []

    keyword = (search or "").strip()

    if keyword:

        like = f"%{keyword}%"

        sql += """
            WHERE demo_name LIKE ?
               OR map_name LIKE ?
               OR match_time LIKE ?
        """

        params = [like, like, like]

    sort_col = SORTABLE_COLUMNS.get(sort, "id")

    direction = "ASC" if str(order).lower() == "asc" else "DESC"

    sql += f" ORDER BY {sort_col} {direction}, id DESC"

    rows = conn.execute(sql, params).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def delete_matches(match_ids):
    """
    删除比赛及其关联数据（外键级联）。

    返回删除数量。
    """

    match_ids = [int(i) for i in match_ids]

    if not match_ids:
        return 0

    conn = get_db()

    try:

        placeholders = ",".join("?" for _ in match_ids)

        cursor = conn.execute(
            f"DELETE FROM matches WHERE id IN ({placeholders})",
            match_ids
        )

        conn.commit()

        return cursor.rowcount

    finally:

        conn.close()


# ============================================================
# Flask 路由
# ============================================================

def register_routes(app):


    def current_lang():
        lang = request.cookies.get("lang", DEFAULT_LANG)
        if lang not in LANGUAGES:
            lang = DEFAULT_LANG
        return lang


    @app.context_processor
    def inject_i18n():

        lang = current_lang()

        def t(key, **kwargs):
            return get_text(lang, key, **kwargs)

        return {
            "lang": lang,
            "languages": LANGUAGES,
            "t": t,
            "translations": TRANSLATIONS.get(
                lang,
                TRANSLATIONS[DEFAULT_LANG]
            ),
        }


    @app.route("/set_lang")
    def set_lang():

        lang = request.args.get("lang", DEFAULT_LANG)

        if lang not in LANGUAGES:
            lang = DEFAULT_LANG

        next_url = request.args.get("next") or "/"

        resp = redirect(next_url)

        resp.set_cookie(
            "lang",
            lang,
            max_age=60 * 60 * 24 * 365
        )

        return resp


    @app.route("/")
    def index():

        match_ids = get_match_ids()

        if not match_ids:

            lang = current_lang()

            return (
                f"<h2>{get_text(lang, 'no_data_yet')}</h2>"
            )

        selected_id = request.args.get("match_id")

        if selected_id:
            try:
                selected_id = int(selected_id)
            except ValueError:
                selected_id = match_ids[0]["id"]
        else:
            selected_id = match_ids[0]["id"]

        data = get_match_data(selected_id)

        return render_template(
            "dashboard.html",
            match_ids=match_ids,
            selected_id=selected_id,
            data=data
        )


    @app.route("/manage")
    def manage():

        search = request.args.get("search", "")

        sort = request.args.get("sort", "id")

        order = request.args.get("order", "desc")

        deleted = request.args.get("deleted", "")

        matches = get_all_matches(
            search,
            sort=sort,
            order=order
        )

        return render_template(
            "manage.html",
            matches=matches,
            search=search,
            sort=sort,
            order=order,
            deleted=deleted
        )


    @app.route("/manage/delete", methods=["POST"])
    def manage_delete():

        match_ids = request.form.getlist("match_ids")

        single = request.form.get("match_id")

        if single:
            match_ids = [single]

        count = delete_matches(match_ids)

        return redirect(
            url_for("manage", deleted=count)
        )
