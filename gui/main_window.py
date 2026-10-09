import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from pathlib import Path

from config.config import (
    ensure_directories
)

from core.task_manager import TaskManager

from utils.i18n import (
    get_text,
    LANGUAGES,
    load_lang,
    save_lang,
)


class MainWindow:
    """
    TF2 Demo Analyzer 主窗口。

    架构：
        Tkinter 主线程（只负责显示）
                ↑ 消息队列
        Worker 线程（负责解析，绝不直接操作 GUI）
    """

    def __init__(self):

        ensure_directories()


        # ====================================================
        # 语言
        # ====================================================

        self.lang = load_lang()


        # ====================================================
        # 主窗口
        # ====================================================

        self.root = tk.Tk()

        self.root.title(
            "TF2 Demo Analyzer"
        )

        self.root.geometry(
            "960x720"
        )

        self.root.minsize(
            820,
            560
        )


        # ====================================================
        # 数据
        # ====================================================

        self.selected_files = []


        self.task_manager = TaskManager()


        self.web_url = None


        # ----------------------------------------------------
        # 文件搜索
        # ----------------------------------------------------

        self.search_text = ""

        self._view_indices = []


        # ----------------------------------------------------
        # Worker -> 主线程 的消息队列
        # ----------------------------------------------------

        self.queue = queue.Queue()


        # 状态机：idle / running / done
        self.state = "idle"


        # 计数器
        self.done_count = 0

        self.dup_count = 0

        self.fail_count = 0


        # 当前进度
        self.current_index = 0

        self.total = 0

        self.current_file = ""

        self.current_stage = ""

        self.last_elapsed = 0


        # ====================================================
        # 创建界面
        # ====================================================

        self.create_widgets()

        self._set_idle()

        self._apply_language()


    # ========================================================
    # 翻译
    # ========================================================

    def _t(self, key, **kwargs):

        return get_text(
            self.lang,
            key,
            **kwargs
        )


    # ========================================================
    # 创建界面
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # 可滚动容器（Canvas + 内部 Frame + 滚动条）
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.canvas.yview
        )

        self.content_frame = tk.Frame(
            self.canvas
        )

        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )

        self._bind_mousewheel()


        # ----------------------------------------------------
        # 标题
        # ----------------------------------------------------

        title = tk.Label(
            self.content_frame,
            text="TF2 Demo Analyzer",
            font=(
                "Microsoft YaHei",
                22,
                "bold"
            )
        )

        title.pack(
            pady=(25, 5)
        )


        self.subtitle_label = tk.Label(
            self.content_frame,
            text="",
            font=(
                "Microsoft YaHei",
                11
            )
        )

        self.subtitle_label.pack(
            pady=(0, 10)
        )


        # ----------------------------------------------------
        # 语言选择
        # ----------------------------------------------------

        lang_frame = tk.Frame(
            self.content_frame
        )

        lang_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 10)
        )


        self.lang_combo = ttk.Combobox(
            lang_frame,
            state="readonly",
            values=list(LANGUAGES.values()),
            width=12
        )

        self.lang_combo.pack(
            side="right"
        )

        self.lang_combo.bind(
            "<<ComboboxSelected>>",
            self._on_lang_change
        )


        # ----------------------------------------------------
        # 文件区域
        # ----------------------------------------------------

        self.file_frame = ttk.LabelFrame(
            self.content_frame,
            text=""
        )

        self.file_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )


        # ----------------------------------------------------
        # 搜索行
        # ----------------------------------------------------

        search_frame = tk.Frame(
            self.file_frame
        )

        search_frame.pack(
            fill="x",
            padx=10,
            pady=(10, 0)
        )


        self.search_label = tk.Label(
            search_frame,
            text="",
            font=(
                "Microsoft YaHei",
                10
            )
        )

        self.search_label.pack(
            side="left"
        )


        self.search_var = tk.StringVar()


        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(
                "Microsoft YaHei",
                10
            )
        )

        search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 5)
        )

        search_entry.bind(
            "<KeyRelease>",
            self._on_search_key
        )


        self.clear_search_button = ttk.Button(
            search_frame,
            text="",
            command=self.clear_search
        )

        self.clear_search_button.pack(
            side="left"
        )


        # ----------------------------------------------------
        # 文件列表
        # ----------------------------------------------------

        list_frame = tk.Frame(
            self.file_frame
        )

        list_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


        self.file_listbox = tk.Listbox(
            list_frame,
            font=(
                "Microsoft YaHei",
                10
            ),
            selectmode=tk.EXTENDED
        )

        self.file_listbox.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.file_listbox.bind(
            "<MouseWheel>",
            self._on_listbox_wheel
        )


        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.file_listbox.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        self.file_listbox.config(
            yscrollcommand=scrollbar.set
        )


        # ----------------------------------------------------
        # 管理按钮
        # ----------------------------------------------------

        manage_frame = tk.Frame(
            self.file_frame
        )

        manage_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )


        self.add_file_button = ttk.Button(
            manage_frame,
            text="",
            command=self.select_files
        )

        self.add_file_button.pack(
            side="left",
            padx=2
        )


        self.add_folder_button = ttk.Button(
            manage_frame,
            text="",
            command=self.select_folder
        )

        self.add_folder_button.pack(
            side="left",
            padx=2
        )


        self.delete_button = ttk.Button(
            manage_frame,
            text="",
            command=self.delete_selected
        )

        self.delete_button.pack(
            side="left",
            padx=2
        )


        self.replace_button = ttk.Button(
            manage_frame,
            text="",
            command=self.replace_selected
        )

        self.replace_button.pack(
            side="left",
            padx=2
        )


        self.select_all_button = ttk.Button(
            manage_frame,
            text="",
            command=self.select_all
        )

        self.select_all_button.pack(
            side="left",
            padx=2
        )


        self.clear_list_button = ttk.Button(
            manage_frame,
            text="",
            command=self.clear_files
        )

        self.clear_list_button.pack(
            side="left",
            padx=2
        )


        # ----------------------------------------------------
        # 文件按钮
        # ----------------------------------------------------

        button_frame = tk.Frame(
            self.content_frame
        )

        button_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )


        self.dashboard_button = ttk.Button(
            button_frame,
            text="",
            command=self.open_dashboard
        )

        self.dashboard_button.pack(
            side="right",
            padx=5
        )


        self.manage_button = ttk.Button(
            button_frame,
            text="",
            command=self.open_manage
        )

        self.manage_button.pack(
            side="right",
            padx=5
        )


        self.start_button = ttk.Button(
            button_frame,
            text="",
            command=self.start_parse
        )

        self.start_button.pack(
            side="right",
            padx=5
        )


        # ----------------------------------------------------
        # 解析状态
        # ----------------------------------------------------

        self.progress_frame = ttk.LabelFrame(
            self.content_frame,
            text=""
        )

        self.progress_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )


        self.state_label = tk.Label(
            self.progress_frame,
            text="",
            anchor="w",
            font=(
                "Microsoft YaHei",
                13,
                "bold"
            )
        )

        self.state_label.pack(
            fill="x",
            padx=15,
            pady=(12, 0)
        )


        self.status_label = tk.Label(
            self.progress_frame,
            text="",
            anchor="w",
            justify="left",
            font=(
                "Microsoft YaHei",
                10
            )
        )

        self.status_label.pack(
            fill="x",
            padx=15,
            pady=(4, 0)
        )


        self.progress = ttk.Progressbar(
            self.progress_frame,
            mode="determinate"
        )

        self.progress.pack(
            fill="x",
            padx=15,
            pady=(10, 4)
        )


        self.counter_label = tk.Label(
            self.progress_frame,
            text="",
            anchor="w",
            font=(
                "Microsoft YaHei",
                9
            )
        )

        self.counter_label.pack(
            fill="x",
            padx=15
        )


        self.elapsed_label = tk.Label(
            self.progress_frame,
            text="",
            anchor="w",
            font=(
                "Microsoft YaHei",
                9
            )
        )

        self.elapsed_label.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )


        # ----------------------------------------------------
        # 日志
        # ----------------------------------------------------

        self.log_frame = ttk.LabelFrame(
            self.content_frame,
            text=""
        )

        self.log_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )


        self.log_text = tk.Text(
            self.log_frame,
            height=8,
            font=(
                "Consolas",
                9
            ),
            state="disabled"
        )

        self.log_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.log_text.bind(
            "<MouseWheel>",
            self._on_text_wheel
        )


    # ========================================================
    # 滚动
    # ========================================================

    def _on_canvas_configure(self, event):
        # content_frame 宽度跟随 canvas 宽度
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )


    def _bind_mousewheel(self):
        # 滚轮滚动整个界面
        self.root.bind_all(
            "<MouseWheel>",
            self._on_wheel
        )


    def _on_wheel(self, event):
        self.canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


    def _on_listbox_wheel(self, event):
        # 文件列表内部滚动，不触发整体滚动
        self.file_listbox.yview_scroll(
            int(-event.delta / 120),
            "units"
        )
        return "break"


    def _on_text_wheel(self, event):
        # 日志内部滚动，不触发整体滚动
        self.log_text.yview_scroll(
            int(-event.delta / 120),
            "units"
        )
        return "break"


    # ========================================================
    # 语言切换
    # ========================================================

    def _on_lang_change(self, event=None):

        name = self.lang_combo.get()

        for code, label in LANGUAGES.items():

            if label == name:

                self.lang = code

                break


        save_lang(self.lang)

        self._apply_language()

        self.log(
            self._t("gui_lang_changed", lang=name)
        )


    def _apply_language(self):
        """
        刷新所有静态文案 + 当前状态下的动态文案。
        """

        self.lang_combo.set(
            LANGUAGES[self.lang]
        )

        self.subtitle_label.config(
            text=self._t("gui_subtitle")
        )

        self.search_label.config(
            text=self._t("gui_search")
        )

        self.clear_search_button.config(
            text=self._t("gui_clear_search")
        )

        self.add_file_button.config(
            text=self._t("gui_add_file")
        )

        self.add_folder_button.config(
            text=self._t("gui_add_folder")
        )

        self.delete_button.config(
            text=self._t("gui_delete_selected")
        )

        self.replace_button.config(
            text=self._t("gui_replace_selected")
        )

        self.select_all_button.config(
            text=self._t("gui_select_all")
        )

        self.clear_list_button.config(
            text=self._t("gui_clear_list")
        )

        self.dashboard_button.config(
            text=self._t("gui_open_dashboard")
        )

        self.manage_button.config(
            text=self._t("gui_manage")
        )

        self.start_button.config(
            text=self._t("gui_start")
        )

        self.progress_frame.config(
            text=self._t("gui_progress_frame")
        )

        self.log_frame.config(
            text=self._t("gui_log_frame")
        )


        # 动态文案
        self._refresh_dynamic_texts()


    def _refresh_dynamic_texts(self):

        self._rebuild_listbox()


        if self.state == "running":

            self.state_label.config(
                text=self._t("gui_state_running")
            )

            self._update_running_status()

            self._update_counter()

        elif self.state == "done":

            self.state_label.config(
                text=self._t("gui_state_done")
            )

            self.status_label.config(
                text=self._t(
                    "gui_counter_done",
                    d=self.done_count,
                    p=self.dup_count,
                    f=self.fail_count
                )
            )

            self.elapsed_label.config(
                text=self._t(
                    "gui_elapsed",
                    t=self._format_elapsed(self.last_elapsed)
                )
            )

        else:

            self.state_label.config(
                text=self._t("gui_state_idle")
            )

            self.status_label.config(
                text=self._t("gui_idle_hint")
            )


    # ========================================================
    # 添加日志（只允许主线程调用）
    # ========================================================

    def log(self, message):

        self.log_text.config(
            state="normal"
        )

        self.log_text.insert(
            tk.END,
            message + "\n"
        )

        self.log_text.see(
            tk.END
        )

        self.log_text.config(
            state="disabled"
        )


    # ========================================================
    # 选择文件
    # ========================================================

    def select_files(self):

        files = filedialog.askopenfilenames(
            title=self._t("gui_dialog_open"),
            filetypes=[
                (
                    self._t("gui_filetype_dem"),
                    "*.dem"
                ),
                (
                    self._t("gui_filetype_all"),
                    "*.*"
                )
            ]
        )


        if not files:
            return


        added = self._add_files(files)


        self.log(
            self._t("gui_log_added", n=added)
        )


    # ========================================================
    # 选择文件夹
    # ========================================================

    def select_folder(self):

        folder = filedialog.askdirectory(
            title=self._t("gui_dialog_folder")
        )


        if not folder:
            return


        files = sorted(
            Path(folder).glob(
                "*.dem"
            )
        )


        if not files:

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_no_dem_in_folder")
            )

            return


        added = self._add_files(files)


        self.log(
            self._t("gui_log_folder_added", n=added)
        )


    # ========================================================
    # 文件管理（增删查改 + 多选）
    # ========================================================

    def _add_files(self, files):
        """
        添加文件到列表（去重），返回新增数量。
        """

        added = 0


        for file in files:

            path = Path(file)

            if path not in self.selected_files:

                self.selected_files.append(
                    path
                )

                added += 1


        if added:

            self._rebuild_listbox()


        return added


    def _rebuild_listbox(self):
        """
        根据当前搜索条件重建文件列表。
        """

        self.file_listbox.delete(
            0,
            tk.END
        )

        self._view_indices = []


        query = self.search_text.strip().lower()


        for index, path in enumerate(
            self.selected_files
        ):

            name = path.name.lower()

            full = str(path).lower()


            if (
                not query
                or query in name
                or query in full
            ):

                self.file_listbox.insert(
                    tk.END,
                    str(path)
                )

                self._view_indices.append(
                    index
                )


        self.file_frame.config(
            text=self._t(
                "gui_files_frame",
                n=len(self.selected_files)
            )
        )


    def _selected_source_indices(self):
        """
        返回当前列表框中选中项对应的源索引。
        """

        indices = []


        for sel in self.file_listbox.curselection():

            if 0 <= sel < len(self._view_indices):

                indices.append(
                    self._view_indices[sel]
                )


        return indices


    def _on_search_key(self, event=None):

        self.search_text = self.search_var.get()

        self._rebuild_listbox()


    def clear_search(self):

        self.search_var.set("")

        self.search_text = ""

        self._rebuild_listbox()


    def select_all(self):

        self.file_listbox.selection_set(
            0,
            tk.END
        )


    def delete_selected(self):

        if self.state == "running":

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_busy")
            )

            return


        indices = self._selected_source_indices()


        if not indices:

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_select_delete")
            )

            return


        for i in sorted(
            indices,
            reverse=True
        ):

            del self.selected_files[i]


        self.log(
            self._t("gui_log_deleted", n=len(indices))
        )

        self._rebuild_listbox()


    def replace_selected(self):

        if self.state == "running":

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_busy")
            )

            return


        indices = self._selected_source_indices()


        if not indices:

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_select_replace")
            )

            return


        file = filedialog.askopenfilename(
            title=self._t("gui_dialog_replace"),
            filetypes=[
                (
                    self._t("gui_filetype_dem"),
                    "*.dem"
                ),
                (
                    self._t("gui_filetype_all"),
                    "*.*"
                )
            ]
        )


        if not file:
            return


        new_path = Path(file)

        self.selected_files[indices[0]] = new_path


        self.log(
            self._t("gui_log_replaced", name=new_path.name)
        )

        self._rebuild_listbox()


    def clear_files(self):

        if self.state == "running":

            messagebox.showinfo(
                self._t("gui_msg_title"),
                self._t("gui_msg_busy")
            )

            return


        self.selected_files.clear()

        self.clear_search()


        self.log(
            self._t("gui_log_cleared")
        )

        self._set_idle()


    # ========================================================
    # 打开 Web 页面（分析页 / 管理页）
    # ========================================================

    def _ensure_server(self):
        """
        确保 Flask 服务器已启动，返回 base URL。
        """

        if self.web_url is not None:
            return self.web_url


        from web.server import start_server


        self.log(
            self._t("gui_log_server_starting")
        )


        self.web_url = start_server(
            open_browser=False
        )


        return self.web_url


    def _open_path(self, path):
        """
        打开 base_url + path，返回完整地址。
        """

        try:

            url = self._ensure_server()

            full_url = url + path


            import webbrowser

            webbrowser.open(
                full_url
            )


            return full_url

        except Exception as e:

            self.log(
                self._t("gui_log_server_fail", e=e)
            )

            return None


    def open_dashboard(self):

        url = self._open_path("")


        if url:

            self.log(
                self._t("gui_log_dashboard", url=url)
            )


    def open_manage(self):

        url = self._open_path("/manage")


        if url:

            self.log(
                self._t("gui_log_manage", url=url)
            )


    # ========================================================
    # 开始解析
    # ========================================================

    def start_parse(self):

        if self.state == "running":
            return


        if not self.selected_files:

            messagebox.showwarning(
                self._t("gui_msg_title"),
                self._t("gui_msg_no_files")
            )

            return


        # 快照文件列表，避免运行中被改动
        files = list(
            self.selected_files
        )


        self.total = len(
            files
        )


        # 进入 running 状态
        self._set_running()


        self.log(
            self._t("gui_log_parse_start", n=self.total)
        )


        # 启动 Worker 线程
        self.worker_thread = threading.Thread(
            target=self._parse_worker,
            args=(files,),
            daemon=True
        )

        self.worker_thread.start()


    # ========================================================
    # Worker 线程（不直接操作 GUI）
    # ========================================================

    def _parse_worker(self, files):

        total = len(files)

        start_time = time.time()


        try:

            for index, demo_path in enumerate(
                files,
                start=1
            ):

                self.queue.put({
                    "type": "file_start",
                    "index": index,
                    "total": total,
                    "name": demo_path.name,
                })


                result = self.task_manager.process_demo(
                    demo_path,
                    on_event=self._queue_event
                )


                self.queue.put({
                    "type": "file_done",
                    "index": index,
                    "total": total,
                    "result": result,
                })


        except Exception as e:

            self.queue.put({
                "type": "fatal",
                "message": str(e)
            })


        finally:

            self.queue.put({
                "type": "finished",
                "elapsed": time.time() - start_time,
            })


    # ========================================================
    # Worker 事件回调（线程安全：只往队列塞消息）
    # ========================================================

    def _queue_event(self, event):

        self.queue.put({
            "type": "stage",
            **event
        })


    # ========================================================
    # 主线程轮询队列
    # ========================================================

    def _poll_queue(self):

        try:

            while True:

                msg = self.queue.get_nowait()

                self._handle_message(msg)

        except queue.Empty:

            pass


        self.root.after(
            50,
            self._poll_queue
        )


    # ========================================================
    # 处理 Worker 消息（主线程）
    # ========================================================

    def _handle_message(self, msg):

        msg_type = msg.get("type")


        # ----------------------------------------------------
        # 文件开始
        # ----------------------------------------------------

        if msg_type == "file_start":

            self.current_index = msg["index"]

            self.total = msg["total"]

            self.current_file = msg["name"]

            self.current_stage = ""

            # Rust Parser 不回报单文件内部进度，
            # 用 indeterminate 动画提示"正在解析"，
            # 避免文件少时进度条一直停在 0。
            self.progress.config(mode="indeterminate")
            self.progress.start(12)

            self._update_running_status()


        # ----------------------------------------------------
        # 阶段事件
        # ----------------------------------------------------

        elif msg_type == "stage":

            stage = msg.get("stage")

            name = msg.get("demo_name", "")

            match_id = msg.get("match_id")


            if stage == "parse":

                self.current_stage = "Rust Parser"

                self.log(
                    self._t("gui_log_file_start", name=name)
                )

            elif stage == "analyze":

                self.current_stage = "Analyzer"

                self.log(
                    self._t("gui_log_parser_done")
                )

            elif stage == "save":

                self.current_stage = self._t("gui_stage_save")

                self.log(
                    self._t("gui_log_analyzer_done")
                )

            elif stage == "ok":

                self.log(
                    self._t("gui_log_saved", id=match_id)
                )

            elif stage == "duplicate":

                self.log(
                    self._t("gui_log_duplicate", id=match_id)
                )

            elif stage == "error":

                self.log(
                    self._t("gui_log_failed", msg=msg.get("message", ""))
                )


            if stage in ("parse", "analyze", "save"):

                self._update_running_status()


        # ----------------------------------------------------
        # 文件完成
        # ----------------------------------------------------

        elif msg_type == "file_done":

            result = msg["result"]

            status = result.get("status")


            if status == "ok":

                self.done_count += 1

            elif status == "duplicate":

                self.dup_count += 1

            else:

                self.fail_count += 1


            self.current_index = msg["index"]

            self.progress.stop()
            self.progress.config(mode="determinate")
            self.progress["value"] = msg["index"]

            self._update_running_status()

            self._update_counter()


        # ----------------------------------------------------
        # 意外错误
        # ----------------------------------------------------

        elif msg_type == "fatal":

            self.log(
                self._t("gui_log_fatal", msg=msg.get("message", ""))
            )


        # ----------------------------------------------------
        # 全部完成
        # ----------------------------------------------------

        elif msg_type == "finished":

            self._enter_done(
                msg.get("elapsed", 0)
            )


    # ========================================================
    # 状态更新
    # ========================================================

    def _update_running_status(self):

        lines = [
            self._t(
                "gui_progress_line",
                i=self.current_index,
                n=self.total
            )
        ]

        if self.current_file:

            lines.append(
                self._t(
                    "gui_current_file",
                    name=self.current_file
                )
            )

        if self.current_stage:

            lines.append(
                self._t(
                    "gui_current_stage",
                    stage=self.current_stage
                )
            )

        self.status_label.config(
            text="\n".join(lines)
        )


    def _update_counter(self):

        # 已处理完的文件数 = 成功 + 重复 + 失败
        completed = (
            self.done_count
            + self.dup_count
            + self.fail_count
        )

        self.counter_label.config(
            text=self._t(
                "gui_counter_running",
                x=completed,
                n=self.total,
                d=self.done_count,
                p=self.dup_count,
                f=self.fail_count
            )
        )


    def _set_running(self):

        self.state = "running"

        self.done_count = 0

        self.dup_count = 0

        self.fail_count = 0

        self.current_index = 0

        self.current_file = ""

        self.current_stage = ""


        self.state_label.config(
            text=self._t("gui_state_running")
        )

        self.status_label.config(
            text=""
        )

        self.counter_label.config(
            text=""
        )

        self.elapsed_label.config(
            text=""
        )

        self.progress.stop()
        self.progress.config(mode="determinate")
        self.progress["maximum"] = self.total

        self.progress["value"] = 0

        self.start_button.config(
            state="disabled"
        )

        self.dashboard_button.config(
            state="disabled"
        )

        self.manage_button.config(
            state="disabled"
        )

        self._update_counter()


    def _set_idle(self):

        self.state = "idle"

        self.state_label.config(
            text=self._t("gui_state_idle")
        )

        self.status_label.config(
            text=self._t("gui_idle_hint")
        )

        self.counter_label.config(
            text=""
        )

        self.elapsed_label.config(
            text=""
        )

        self.progress.stop()
        self.progress.config(mode="determinate")
        self.progress["maximum"] = 1

        self.progress["value"] = 0

        self.start_button.config(
            state="normal"
        )

        self.dashboard_button.config(
            state="normal"
        )

        self.manage_button.config(
            state="normal"
        )


    def _enter_done(self, elapsed):

        self.state = "done"

        self.last_elapsed = elapsed

        self.state_label.config(
            text=self._t("gui_state_done")
        )

        self.status_label.config(
            text=self._t(
                "gui_counter_done",
                d=self.done_count,
                p=self.dup_count,
                f=self.fail_count
            )
        )

        self.elapsed_label.config(
            text=self._t(
                "gui_elapsed",
                t=self._format_elapsed(elapsed)
            )
        )

        self.progress.stop()
        self.progress.config(mode="determinate")
        self.progress["maximum"] = self.total

        self.progress["value"] = self.total

        self.start_button.config(
            state="normal"
        )

        self.dashboard_button.config(
            state="normal"
        )

        self.manage_button.config(
            state="normal"
        )


        # 解析出数据后自动打开分析页面
        if self.done_count > 0:

            self.open_dashboard()


    # ========================================================
    # 时间格式化
    # ========================================================

    @staticmethod
    def _format_elapsed(seconds):

        seconds = max(0, int(seconds))

        minutes, secs = divmod(seconds, 60)

        return f"{minutes}:{secs:02d}"


    # ========================================================
    # 启动
    # ========================================================

    def run(self):

        self.root.after(
            50,
            self._poll_queue
        )

        self.root.mainloop()
