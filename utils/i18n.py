# -*- coding: utf-8 -*-
"""
多语言支持（中文 / English / 한국어）。

Web 页面通过 Flask context processor 注入 t() 使用；
模板里的 JS 通过 window.I18N 注入同一份字典。
桌面 GUI 通过 get_text() 直接使用。
"""

import json

from config.config import DATA_DIR


SETTINGS_PATH = DATA_DIR / "settings.json"


LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ko": "한국어",
    "ja": "日本語",
}


DEFAULT_LANG = "zh"


TRANSLATIONS = {

    # ============================================================
    # 中文
    # ============================================================

    "zh": {
        # 通用 / 头部
        "app_subtitle": "单局比赛数据可视化",
        "manage_records": "管理比赛记录",
        "select_match": "选择比赛：",
        "view_report": "查看战报",

        # 比赛信息
        "info_map": "地图",
        "info_time": "比赛时间",
        "info_duration": "比赛时长",
        "info_players": "玩家数",
        "info_deaths": "死亡事件",
        "info_winner": "最后回合",
        "unknown": "未知",

        # 队伍对比
        "team_comparison": "RED vs BLU 总数据",
        "team_players": "玩家",
        "kills": "击杀",
        "deaths": "死亡",
        "assists": "助攻",
        "points": "得分",
        "damage": "伤害",
        "healing": "治疗",
        "captures": "占领",
        "defenses": "防守",

        # 图表
        "charts_title": "玩家数据图表",
        "chart_kda": "玩家 K / D / A",
        "chart_score": "玩家得分",
        "chart_damage": "玩家伤害",
        "chart_healing": "玩家治疗",
        "chart_objective": "玩家占领 / 防守",
        "chart_special": "玩家特殊数据",

        # 玩家表
        "players_detail": "所有玩家详细数据",
        "team": "队伍",
        "player": "玩家",
        "headshots": "爆头",
        "backstabs": "背刺",
        "uber": "Uber",
        "buildings": "建筑",
        "classes": "职业",

        # 回合
        "rounds_title": "回合数据",
        "round_label": "Round",
        "round_length": "时长",
        "seconds": "秒",
        "end_tick": "End Tick",

        # 玩家卡片
        "card_close": "关闭",
        "class_usage": "职业使用",
        "weapon_kills": "武器击杀",
        "k_kills": "KILLS",
        "k_deaths": "DEATHS",
        "k_assists": "ASSISTS",
        "stat_score": "Score",
        "stat_damage": "Damage",
        "stat_healing": "Healing",
        "stat_captures": "Captures",
        "stat_defenses": "Defenses",
        "stat_headshots": "Headshots",
        "stat_backstabs": "Backstabs",
        "stat_uber": "Uber",
        "stat_buildings": "Buildings",
        "stat_teleports": "Teleports",
        "stat_dominations": "Dominations",
        "stat_revenges": "Revenges",
        "team_other": "OTHER",
        "no_class_data": "无职业数据",
        "no_weapon_data": "无武器数据",
        "player_not_found": "找不到玩家数据",
        "player_unknown": "Unknown",

        # 管理页
        "manage_title": "比赛管理",
        "manage_subtitle": "管理历史解析过的 DEM 记录",
        "search_placeholder": "搜索文件名 / 地图 / 时间...",
        "search": "搜索",
        "back_dashboard": "← 返回分析页面",
        "deleted_notice": "已从数据库删除 {n} 条记录（磁盘文件未受影响）",
        "history_count": "历史记录（{n}）",
        "filename": "文件名",
        "actions": "操作",
        "view": "查看",
        "delete": "删除",
        "delete_selected": "删除选中",
        "no_matches": "没有找到比赛记录。",
        "confirm_first": "请先勾选要删除的比赛。",
        "confirm_delete_selected": "确定从数据库删除选中的 {n} 条比赛吗？磁盘文件不会删除。",
        "confirm_delete_one": "确定从数据库删除这条比赛吗？磁盘文件不会删除。",

        # 路由
        "no_data_yet": "数据库中还没有比赛数据",

        # ---- GUI 桌面界面 ----
        "gui_subtitle": "Team Fortress 2 Demo 分析工具",
        "gui_search": "搜索：",
        "gui_clear_search": "清空搜索",
        "gui_add_file": "添加文件",
        "gui_add_folder": "添加文件夹",
        "gui_delete_selected": "删除选中",
        "gui_replace_selected": "替换选中",
        "gui_select_all": "全选",
        "gui_clear_list": "清空列表",
        "gui_open_dashboard": "打开分析页面",
        "gui_manage": "管理比赛",
        "gui_start": "开始解析",
        "gui_files_frame": " DEM 文件（{n}） ",
        "gui_progress_frame": " 解析状态 ",
        "gui_log_frame": " 日志 ",
        "gui_state_idle": "未解析",
        "gui_state_running": "解析中",
        "gui_state_done": "解析完成",
        "gui_idle_hint": "请选择 DEM 文件后点击「开始解析」",
        "gui_progress_line": "正在处理 第 {i} / {n} 个文件",
        "gui_current_file": "当前文件：{name}",
        "gui_current_stage": "当前阶段：{stage}",
        "gui_counter_running": "已完成 {x} / {n}　成功 {d} · 重复 {p} · 失败 {f}",
        "gui_counter_done": "成功：{d} 重复：{p} 失败：{f}",
        "gui_elapsed": "总耗时：{t}",
        "gui_stage_save": "保存数据库",
        "gui_log_added": "已添加 {n} 个 DEM 文件",
        "gui_log_folder_added": "从文件夹添加 {n} 个 DEM 文件",
        "gui_log_deleted": "已删除 {n} 个 DEM 文件",
        "gui_log_replaced": "已替换为 {name}",
        "gui_log_cleared": "已清空 DEM 文件列表",
        "gui_log_parse_start": "开始解析，共 {n} 个 DEM 文件",
        "gui_log_file_start": "开始解析 {name}",
        "gui_log_parser_done": "Parser 完成",
        "gui_log_analyzer_done": "Analyzer 完成",
        "gui_log_saved": "保存成功 match_id={id}",
        "gui_log_duplicate": "已存在 match_id={id}，跳过",
        "gui_log_failed": "失败：{msg}",
        "gui_log_fatal": "严重错误：{msg}",
        "gui_log_server_starting": "正在启动 Web 服务器...",
        "gui_log_dashboard": "分析页面：{url}",
        "gui_log_manage": "管理页面：{url}",
        "gui_log_server_fail": "启动 Web 服务器失败：{e}",
        "gui_lang_changed": "已切换语言：{lang}",
        "gui_msg_title": "提示",
        "gui_msg_no_files": "请先选择至少一个 DEM 文件。",
        "gui_msg_busy": "解析中，请等待完成后再管理文件。",
        "gui_msg_select_delete": "请先在列表中选择要删除的文件。",
        "gui_msg_select_replace": "请先选择要替换的文件。",
        "gui_msg_no_dem_in_folder": "该文件夹中没有找到 DEM 文件。",
        "gui_dialog_open": "选择 TF2 DEM 文件",
        "gui_dialog_replace": "选择替换的 DEM 文件",
        "gui_dialog_folder": "选择 DEM 文件夹",
        "gui_filetype_dem": "TF2 Demo",
        "gui_filetype_all": "所有文件",
    },

    # ============================================================
    # English
    # ============================================================

    "en": {
        "app_subtitle": "Match data visualization",
        "manage_records": "Manage match records",
        "select_match": "Select match:",
        "view_report": "View report",

        "info_map": "Map",
        "info_time": "Match time",
        "info_duration": "Duration",
        "info_players": "Players",
        "info_deaths": "Death events",
        "info_winner": "Last round",
        "unknown": "Unknown",

        "team_comparison": "RED vs BLU Totals",
        "team_players": "Players",
        "kills": "Kills",
        "deaths": "Deaths",
        "assists": "Assists",
        "points": "Points",
        "damage": "Damage",
        "healing": "Healing",
        "captures": "Captures",
        "defenses": "Defenses",

        "charts_title": "Player Charts",
        "chart_kda": "Player K / D / A",
        "chart_score": "Player Score",
        "chart_damage": "Player Damage",
        "chart_healing": "Player Healing",
        "chart_objective": "Player Objectives",
        "chart_special": "Player Special Stats",

        "players_detail": "All Players Detail",
        "team": "Team",
        "player": "Player",
        "headshots": "Headshots",
        "backstabs": "Backstabs",
        "uber": "Uber",
        "buildings": "Buildings",
        "classes": "Classes",

        "rounds_title": "Rounds",
        "round_label": "Round",
        "round_length": "Length",
        "seconds": "s",
        "end_tick": "End Tick",

        "card_close": "Close",
        "class_usage": "Classes",
        "weapon_kills": "Weapon kills",
        "k_kills": "KILLS",
        "k_deaths": "DEATHS",
        "k_assists": "ASSISTS",
        "stat_score": "Score",
        "stat_damage": "Damage",
        "stat_healing": "Healing",
        "stat_captures": "Captures",
        "stat_defenses": "Defenses",
        "stat_headshots": "Headshots",
        "stat_backstabs": "Backstabs",
        "stat_uber": "Uber",
        "stat_buildings": "Buildings",
        "stat_teleports": "Teleports",
        "stat_dominations": "Dominations",
        "stat_revenges": "Revenges",
        "team_other": "OTHER",
        "no_class_data": "No class data",
        "no_weapon_data": "No weapon data",
        "player_not_found": "Player data not found",
        "player_unknown": "Unknown",

        "manage_title": "Match Management",
        "manage_subtitle": "Manage parsed DEM history",
        "search_placeholder": "Search filename / map / time...",
        "search": "Search",
        "back_dashboard": "← Back to dashboard",
        "deleted_notice": "Deleted {n} record(s) from database (disk files unaffected)",
        "history_count": "History ({n})",
        "filename": "Filename",
        "actions": "Actions",
        "view": "View",
        "delete": "Delete",
        "delete_selected": "Delete selected",
        "no_matches": "No matches found.",
        "confirm_first": "Please select matches to delete first.",
        "confirm_delete_selected": "Delete {n} selected match(es) from database? Disk files will not be deleted.",
        "confirm_delete_one": "Delete this match from database? Disk file will not be deleted.",

        "no_data_yet": "No match data in database yet",

        "gui_subtitle": "Team Fortress 2 Demo analysis tool",
        "gui_search": "Search:",
        "gui_clear_search": "Clear search",
        "gui_add_file": "Add files",
        "gui_add_folder": "Add folder",
        "gui_delete_selected": "Delete selected",
        "gui_replace_selected": "Replace selected",
        "gui_select_all": "Select all",
        "gui_clear_list": "Clear list",
        "gui_open_dashboard": "Open dashboard",
        "gui_manage": "Manage matches",
        "gui_start": "Start parsing",
        "gui_files_frame": " DEM files ({n}) ",
        "gui_progress_frame": " Parse status ",
        "gui_log_frame": " Log ",
        "gui_state_idle": "Not parsed",
        "gui_state_running": "Parsing",
        "gui_state_done": "Parse complete",
        "gui_idle_hint": "Select DEM files, then click Start",
        "gui_progress_line": "Processing {i} / {n}",
        "gui_current_file": "Current file: {name}",
        "gui_current_stage": "Current stage: {stage}",
        "gui_counter_running": "Done {x} / {n}  Success {d} · Duplicate {p} · Failed {f}",
        "gui_counter_done": "Success: {d}  Duplicate: {p}  Failed: {f}",
        "gui_elapsed": "Total time: {t}",
        "gui_stage_save": "Save to database",
        "gui_log_added": "Added {n} DEM file(s)",
        "gui_log_folder_added": "Added {n} DEM file(s) from folder",
        "gui_log_deleted": "Deleted {n} DEM file(s)",
        "gui_log_replaced": "Replaced with {name}",
        "gui_log_cleared": "Cleared DEM file list",
        "gui_log_parse_start": "Start parsing {n} DEM file(s)",
        "gui_log_file_start": "Parsing {name}",
        "gui_log_parser_done": "Parser done",
        "gui_log_analyzer_done": "Analyzer done",
        "gui_log_saved": "Saved, match_id={id}",
        "gui_log_duplicate": "Already exists, match_id={id}, skipped",
        "gui_log_failed": "Failed: {msg}",
        "gui_log_fatal": "Fatal: {msg}",
        "gui_log_server_starting": "Starting web server...",
        "gui_log_dashboard": "Dashboard: {url}",
        "gui_log_manage": "Manage page: {url}",
        "gui_log_server_fail": "Failed to start web server: {e}",
        "gui_lang_changed": "Language switched: {lang}",
        "gui_msg_title": "Info",
        "gui_msg_no_files": "Please select at least one DEM file.",
        "gui_msg_busy": "Parsing, please wait before managing files.",
        "gui_msg_select_delete": "Please select files to delete first.",
        "gui_msg_select_replace": "Please select a file to replace first.",
        "gui_msg_no_dem_in_folder": "No DEM files found in this folder.",
        "gui_dialog_open": "Select TF2 DEM files",
        "gui_dialog_replace": "Select replacement DEM file",
        "gui_dialog_folder": "Select DEM folder",
        "gui_filetype_dem": "TF2 Demo",
        "gui_filetype_all": "All files",
    },

    # ============================================================
    # 한국어
    # ============================================================

    "ko": {
        "app_subtitle": "경기 데이터 시각화",
        "manage_records": "경기 기록 관리",
        "select_match": "경기 선택:",
        "view_report": "리포트 보기",

        "info_map": "맵",
        "info_time": "경기 시간",
        "info_duration": "경기 시간",
        "info_players": "플레이어 수",
        "info_deaths": "사망 이벤트",
        "info_winner": "마지막 라운드",
        "unknown": "알 수 없음",

        "team_comparison": "RED vs BLU 총계",
        "team_players": "플레이어",
        "kills": "킬",
        "deaths": "데스",
        "assists": "어시스트",
        "points": "점수",
        "damage": "데미지",
        "healing": "힐",
        "captures": "점령",
        "defenses": "수비",

        "charts_title": "플레이어 차트",
        "chart_kda": "플레이어 K / D / A",
        "chart_score": "플레이어 점수",
        "chart_damage": "플레이어 데미지",
        "chart_healing": "플레이어 힐",
        "chart_objective": "플레이어 점령 / 수비",
        "chart_special": "플레이어 특수 통계",

        "players_detail": "모든 플레이어 상세",
        "team": "팀",
        "player": "플레이어",
        "headshots": "헤드샷",
        "backstabs": "백스탭",
        "uber": "우버",
        "buildings": "건물",
        "classes": "병과",

        "rounds_title": "라운드",
        "round_label": "라운드",
        "round_length": "길이",
        "seconds": "초",
        "end_tick": "종료 틱",

        "card_close": "닫기",
        "class_usage": "병과 사용",
        "weapon_kills": "무기 킬",
        "k_kills": "킬",
        "k_deaths": "데스",
        "k_assists": "어시스트",
        "stat_score": "점수",
        "stat_damage": "데미지",
        "stat_healing": "힐",
        "stat_captures": "점령",
        "stat_defenses": "수비",
        "stat_headshots": "헤드샷",
        "stat_backstabs": "백스탭",
        "stat_uber": "우버",
        "stat_buildings": "건물",
        "stat_teleports": "텔레포트",
        "stat_dominations": "지배",
        "stat_revenges": "복수",
        "team_other": "기타",
        "no_class_data": "병과 데이터 없음",
        "no_weapon_data": "무기 데이터 없음",
        "player_not_found": "플레이어 데이터를 찾을 수 없음",
        "player_unknown": "알 수 없음",

        "manage_title": "경기 관리",
        "manage_subtitle": "파싱된 DEM 기록 관리",
        "search_placeholder": "파일명 / 맵 / 시간 검색...",
        "search": "검색",
        "back_dashboard": "← 대시보드로 돌아가기",
        "deleted_notice": "데이터베이스에서 {n}개의 기록을 삭제했습니다 (디스크 파일은 영향 없음)",
        "history_count": "기록 ({n})",
        "filename": "파일명",
        "actions": "작업",
        "view": "보기",
        "delete": "삭제",
        "delete_selected": "선택 삭제",
        "no_matches": "경기 기록을 찾을 수 없습니다.",
        "confirm_first": "먼저 삭제할 경기를 선택하세요.",
        "confirm_delete_selected": "선택한 {n}개의 경기를 데이터베이스에서 삭제하시겠습니까? 디스크 파일은 삭제되지 않습니다.",
        "confirm_delete_one": "이 경기를 데이터베이스에서 삭제하시겠습니까? 디스크 파일은 삭제되지 않습니다.",

        "no_data_yet": "데이터베이스에 아직 경기 데이터가 없습니다",

        "gui_subtitle": "Team Fortress 2 데모 분석 도구",
        "gui_search": "검색:",
        "gui_clear_search": "검색 지우기",
        "gui_add_file": "파일 추가",
        "gui_add_folder": "폴더 추가",
        "gui_delete_selected": "선택 삭제",
        "gui_replace_selected": "선택 교체",
        "gui_select_all": "전체 선택",
        "gui_clear_list": "목록 비우기",
        "gui_open_dashboard": "대시보드 열기",
        "gui_manage": "경기 관리",
        "gui_start": "파싱 시작",
        "gui_files_frame": " DEM 파일 ({n}) ",
        "gui_progress_frame": " 파싱 상태 ",
        "gui_log_frame": " 로그 ",
        "gui_state_idle": "파싱 전",
        "gui_state_running": "파싱 중",
        "gui_state_done": "파싱 완료",
        "gui_idle_hint": "DEM 파일을 선택한 후 시작을 누르세요",
        "gui_progress_line": "처리 중 {i} / {n}",
        "gui_current_file": "현재 파일: {name}",
        "gui_current_stage": "현재 단계: {stage}",
        "gui_counter_running": "완료 {x} / {n}  성공 {d} · 중복 {p} · 실패 {f}",
        "gui_counter_done": "성공: {d}  중복: {p}  실패: {f}",
        "gui_elapsed": "총 시간: {t}",
        "gui_stage_save": "데이터베이스 저장",
        "gui_log_added": "DEM 파일 {n}개 추가",
        "gui_log_folder_added": "폴더에서 DEM 파일 {n}개 추가",
        "gui_log_deleted": "DEM 파일 {n}개 삭제",
        "gui_log_replaced": "{name}(으)로 교체",
        "gui_log_cleared": "DEM 파일 목록 비움",
        "gui_log_parse_start": "DEM 파일 {n}개 파싱 시작",
        "gui_log_file_start": "{name} 파싱",
        "gui_log_parser_done": "Parser 완료",
        "gui_log_analyzer_done": "Analyzer 완료",
        "gui_log_saved": "저장 완료 match_id={id}",
        "gui_log_duplicate": "이미 존재함 match_id={id}, 건너뜀",
        "gui_log_failed": "실패: {msg}",
        "gui_log_fatal": "치명적 오류: {msg}",
        "gui_log_server_starting": "웹 서버 시작 중...",
        "gui_log_dashboard": "대시보드: {url}",
        "gui_log_manage": "관리 페이지: {url}",
        "gui_log_server_fail": "웹 서버 시작 실패: {e}",
        "gui_lang_changed": "언어 변경됨: {lang}",
        "gui_msg_title": "알림",
        "gui_msg_no_files": "먼저 DEM 파일을 하나 이상 선택하세요.",
        "gui_msg_busy": "파싱 중입니다. 완료 후 파일을 관리하세요.",
        "gui_msg_select_delete": "먼저 삭제할 파일을 선택하세요.",
        "gui_msg_select_replace": "먼저 교체할 파일을 선택하세요.",
        "gui_msg_no_dem_in_folder": "이 폴더에 DEM 파일이 없습니다.",
        "gui_dialog_open": "TF2 DEM 파일 선택",
        "gui_dialog_replace": "교체할 DEM 파일 선택",
        "gui_dialog_folder": "DEM 폴더 선택",
        "gui_filetype_dem": "TF2 데모",
        "gui_filetype_all": "모든 파일",
    },

    # ============================================================
    # 日本語
    # ============================================================

    "ja": {
        "app_subtitle": "試合データ可視化",
        "manage_records": "試合記録を管理",
        "select_match": "試合を選択：",
        "view_report": "レポートを見る",

        "info_map": "マップ",
        "info_time": "試合日時",
        "info_duration": "試合時間",
        "info_players": "プレイヤー数",
        "info_deaths": "キルイベント",
        "info_winner": "最終ラウンド",
        "unknown": "不明",

        "team_comparison": "RED vs BLU 合計",
        "team_players": "プレイヤー",
        "kills": "キル",
        "deaths": "デス",
        "assists": "アシスト",
        "points": "ポイント",
        "damage": "ダメージ",
        "healing": "ヒール",
        "captures": "占拠",
        "defenses": "防衛",

        "charts_title": "プレイヤーチャート",
        "chart_kda": "プレイヤー K / D / A",
        "chart_score": "プレイヤーポイント",
        "chart_damage": "プレイヤーダメージ",
        "chart_healing": "プレイヤーヒール",
        "chart_objective": "プレイヤー占拠 / 防衛",
        "chart_special": "プレイヤー特殊スタッツ",

        "players_detail": "全プレイヤー詳細",
        "team": "チーム",
        "player": "プレイヤー",
        "headshots": "ヘッドショット",
        "backstabs": "バックスタブ",
        "uber": "Uber",
        "buildings": "建物",
        "classes": "クラス",

        "rounds_title": "ラウンド",
        "round_label": "ラウンド",
        "round_length": "長さ",
        "seconds": "秒",
        "end_tick": "End Tick",

        "card_close": "閉じる",
        "class_usage": "クラス使用",
        "weapon_kills": "武器キル",
        "k_kills": "キル",
        "k_deaths": "デス",
        "k_assists": "アシスト",
        "stat_score": "スコア",
        "stat_damage": "ダメージ",
        "stat_healing": "ヒール",
        "stat_captures": "占拠",
        "stat_defenses": "防衛",
        "stat_headshots": "ヘッドショット",
        "stat_backstabs": "バックスタブ",
        "stat_uber": "Uber",
        "stat_buildings": "建物",
        "stat_teleports": "テレポート",
        "stat_dominations": "支配",
        "stat_revenges": "リベンジ",
        "team_other": "その他",
        "no_class_data": "クラスデータなし",
        "no_weapon_data": "武器データなし",
        "player_not_found": "プレイヤーデータが見つかりません",
        "player_unknown": "不明",

        "manage_title": "試合管理",
        "manage_subtitle": "解析済みDEM記録を管理",
        "search_placeholder": "ファイル名 / マップ / 時間で検索...",
        "search": "検索",
        "back_dashboard": "← ダッシュボードに戻る",
        "deleted_notice": "データベースから{n}件の記録を削除しました（ディスクファイルは影響なし）",
        "history_count": "記録（{n}）",
        "filename": "ファイル名",
        "actions": "操作",
        "view": "表示",
        "delete": "削除",
        "delete_selected": "選択を削除",
        "no_matches": "試合記録が見つかりません。",
        "confirm_first": "まず削除する試合を選択してください。",
        "confirm_delete_selected": "選択した{n}件の試合をデータベースから削除しますか？ディスクファイルは削除されません。",
        "confirm_delete_one": "この試合をデータベースから削除しますか？ディスクファイルは削除されません。",

        "no_data_yet": "データベースにまだ試合データがありません",

        "gui_subtitle": "Team Fortress 2 デモ分析ツール",
        "gui_search": "検索：",
        "gui_clear_search": "検索をクリア",
        "gui_add_file": "ファイルを追加",
        "gui_add_folder": "フォルダを追加",
        "gui_delete_selected": "選択を削除",
        "gui_replace_selected": "選択を置換",
        "gui_select_all": "すべて選択",
        "gui_clear_list": "リストをクリア",
        "gui_open_dashboard": "ダッシュボードを開く",
        "gui_manage": "試合を管理",
        "gui_start": "解析開始",
        "gui_files_frame": " DEM ファイル（{n}） ",
        "gui_progress_frame": " 解析ステータス ",
        "gui_log_frame": " ログ ",
        "gui_state_idle": "未解析",
        "gui_state_running": "解析中",
        "gui_state_done": "解析完了",
        "gui_idle_hint": "DEMファイルを選択して「解析開始」を押してください",
        "gui_progress_line": "処理中 {i} / {n}",
        "gui_current_file": "現在のファイル：{name}",
        "gui_current_stage": "現在の段階：{stage}",
        "gui_counter_running": "完了 {x} / {n}　成功 {d} · 重複 {p} · 失敗 {f}",
        "gui_counter_done": "成功：{d} 重複：{p} 失敗：{f}",
        "gui_elapsed": "所要時間：{t}",
        "gui_stage_save": "データベースに保存",
        "gui_log_added": "DEMファイルを{n}件追加",
        "gui_log_folder_added": "フォルダからDEMファイルを{n}件追加",
        "gui_log_deleted": "DEMファイルを{n}件削除",
        "gui_log_replaced": "{name}に置換",
        "gui_log_cleared": "DEMファイルリストをクリア",
        "gui_log_parse_start": "DEMファイル{n}件の解析を開始",
        "gui_log_file_start": "{name}を解析中",
        "gui_log_parser_done": "Parser 完了",
        "gui_log_analyzer_done": "Analyzer 完了",
        "gui_log_saved": "保存完了 match_id={id}",
        "gui_log_duplicate": "既に存在 match_id={id}、スキップ",
        "gui_log_failed": "失敗：{msg}",
        "gui_log_fatal": "致命的エラー：{msg}",
        "gui_log_server_starting": "Webサーバーを起動中...",
        "gui_log_dashboard": "ダッシュボード：{url}",
        "gui_log_manage": "管理ページ：{url}",
        "gui_log_server_fail": "Webサーバーの起動に失敗：{e}",
        "gui_lang_changed": "言語を変更：{lang}",
        "gui_msg_title": "お知らせ",
        "gui_msg_no_files": "まずDEMファイルを1つ以上選択してください。",
        "gui_msg_busy": "解析中です。完了後にファイルを管理してください。",
        "gui_msg_select_delete": "まず削除するファイルを選択してください。",
        "gui_msg_select_replace": "まず置換するファイルを選択してください。",
        "gui_msg_no_dem_in_folder": "このフォルダにDEMファイルがありません。",
        "gui_dialog_open": "TF2 DEMファイルを選択",
        "gui_dialog_replace": "置換するDEMファイルを選択",
        "gui_dialog_folder": "DEMフォルダを選択",
        "gui_filetype_dem": "TF2 デモ",
        "gui_filetype_all": "すべてのファイル",
    },
}


def get_text(lang, key, **kwargs):
    """
    根据语言取文案，支持 {name} 占位符格式化。
    缺失时回退到中文，再回退到 key 本身。
    """

    table = TRANSLATIONS.get(lang) or TRANSLATIONS[DEFAULT_LANG]

    text = table.get(key)

    if text is None:
        text = TRANSLATIONS[DEFAULT_LANG].get(key, key)

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


def load_lang():
    """
    从 settings.json 读取语言，失败回退默认语言。
    """

    try:

        data = json.loads(
            SETTINGS_PATH.read_text(encoding="utf-8")
        )

        lang = data.get("lang")

        if lang in LANGUAGES:
            return lang

    except Exception:
        pass

    return DEFAULT_LANG


def save_lang(lang):
    """
    保存语言到 settings.json。
    """

    try:

        SETTINGS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        SETTINGS_PATH.write_text(
            json.dumps(
                {"lang": lang},
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    except Exception:
        pass
