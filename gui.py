### gui.py (GUI部分)
### アプリケーションのウィンドウ、ボタン、テキストエリアなどの見た目と操作を担当します。

import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, filedialog, Toplevel, Listbox, Frame, simpledialog
import queue
import system
import database as db

class SearchFrame(Frame):
    """テキスト検索用のUIフレーム"""
    def __init__(self, master, target_text_widget):
        super().__init__(master)
        self.text_widget = target_text_widget
        self.matches = []
        self.current_match_index = -1
        
        # ハイライト用のタグを設定
        if self.text_widget:
            self.text_widget.tag_configure("search_highlight", background="yellow", foreground="black")

        self.search_label = tk.Label(self, text="検索:")
        self.search_label.pack(side=tk.LEFT, padx=(5, 2))

        self.search_entry = tk.Entry(self, font=("Helvetica", 9))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self._find_all)
        self.search_entry.bind("<KeyRelease>", self._on_key_release)

        self.prev_button = tk.Button(self, text="◀ 前", command=self._previous_match, state=tk.DISABLED, relief=tk.FLAT)
        self.prev_button.pack(side=tk.LEFT, padx=(2,0))
        
        self.next_button = tk.Button(self, text="次 ▶", command=self._next_match, state=tk.DISABLED, relief=tk.FLAT)
        self.next_button.pack(side=tk.LEFT)

        self.result_label = tk.Label(self, text="", width=10)
        self.result_label.pack(side=tk.LEFT, padx=(2, 5))
        
        if self.text_widget:
            self.text_widget.bind("<<Modified>>", self._on_text_modified, add='+')
        self.is_modified_by_search = False

    def execute_search(self, keyword):
        """外部から検索をトリガーするためのメソッド"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, keyword)
        self._find_all()

    def _on_key_release(self, event):
        """入力がなくなったら検索をクリアする"""
        if not self.search_entry.get():
            self._clear_search()
            
    def _on_text_modified(self, event=None):
        """テキストウィジェットの変更を検知"""
        if not self.is_modified_by_search:
            self._clear_search()
        if self.text_widget:
            self.text_widget.edit_modified(False)

    def _find_all(self, event=None):
        """テキストウィジェット内の全一致箇所を検索する"""
        if not self.text_widget: return
        self._clear_search()
        keyword = self.search_entry.get()
        if not keyword:
            return

        start_index = "1.0"
        while True:
            pos = self.text_widget.search(keyword, start_index, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(keyword)}c"
            self.matches.append((pos, end_pos))
            start_index = end_pos
        
        if self.matches:
            self.current_match_index = 0
            self._highlight_current_match()
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
        self._update_result_label()

    def _next_match(self):
        """次の一致箇所に移動する"""
        if not self.matches: return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._highlight_current_match()
        self._update_result_label()

    def _previous_match(self):
        """前の一致箇所に移動する"""
        if not self.matches: return
        self.current_match_index = (self.current_match_index - 1 + len(self.matches)) % len(self.matches)
        self._highlight_current_match()
        self._update_result_label()

    def _highlight_current_match(self):
        """現在の一致箇所をハイライトして表示"""
        if not self.text_widget: return
        self.is_modified_by_search = True
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        if self.current_match_index >= 0:
            start, end = self.matches[self.current_match_index]
            self.text_widget.tag_add("search_highlight", start, end)
            self.text_widget.see(start)
        self.is_modified_by_search = False

    def _update_result_label(self):
        """結果ラベルを更新 (例: "1/5")"""
        if not self.matches:
            self.result_label.config(text="")
        else:
            self.result_label.config(text=f"{self.current_match_index + 1}/{len(self.matches)}")

    def _clear_search(self):
        """検索結果とハイライトをクリアする"""
        if not self.text_widget: return
        self.is_modified_by_search = True
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.is_modified_by_search = False

        self.matches = []
        self.current_match_index = -1
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.result_label.config(text="")


class LibraryWindow(Toplevel):
    """ライブラリ閲覧用の新しいウィンドウ"""
    def __init__(self, master=None, logic=None):
        super().__init__(master)
        self.title("保存済みセッションライブラリ")
        self.geometry("900x600")
        self.logic = logic
        self.transient(master)
        self.grab_set()
        self.current_search_keyword = None

        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- 左側パネル (検索 + リスト) ---
        left_panel = Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nswe", padx=(0, 5))
        left_panel.grid_rowconfigure(1, weight=1) # リストボックスが伸縮
        left_panel.grid_columnconfigure(0, weight=1)

        global_search_frame = tk.LabelFrame(left_panel, text="ライブラリ全体を検索", padx=5, pady=5)
        global_search_frame.grid(row=0, column=0, sticky="ew")
        global_search_frame.columnconfigure(0, weight=1)
        
        self.global_search_entry = tk.Entry(global_search_frame)
        self.global_search_entry.grid(row=0, column=0, sticky="ew")
        self.global_search_entry.bind("<Return>", self.perform_global_search)
        
        search_button = tk.Button(global_search_frame, text="検索", command=self.perform_global_search)
        search_button.grid(row=0, column=1, padx=(5,2))
        
        clear_button = tk.Button(global_search_frame, text="クリア", command=self.populate_sessions_list)
        clear_button.grid(row=0, column=2)

        list_frame = tk.LabelFrame(left_panel, text="セッションリスト", padx=5, pady=5)
        list_frame.grid(row=1, column=0, sticky="nswe", pady=(5,0))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.session_listbox = Listbox(list_frame, font=("Helvetica", 10))
        self.session_listbox.grid(row=0, column=0, sticky="nswe")
        self.session_listbox.bind("<<ListboxSelect>>", self.on_session_select)

        # --- 右側パネル (詳細表示) ---
        details_frame = Frame(main_frame)
        details_frame.grid(row=0, column=1, sticky="nswe")
        details_frame.grid_rowconfigure(2, weight=1)
        details_frame.grid_rowconfigure(4, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)

        button_frame = Frame(details_frame)
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        
        tk.Button(button_frame, text="選択したセッションを削除", command=self.delete_selected_session).pack(side=tk.LEFT)
        tk.Button(button_frame, text="リストを更新", command=self.populate_sessions_list).pack(side=tk.LEFT, padx=5)
        self.create_quiz_button = tk.Button(button_frame, text="問題を作成", command=self.create_quiz_from_selection, state=tk.DISABLED, font=("Helvetica", 10, "bold"), fg="purple")
        self.create_quiz_button.pack(side=tk.LEFT, padx=5)

        transcript_container = tk.LabelFrame(details_frame, text="文字起こし結果", padx=5, pady=5)
        transcript_container.grid(row=1, column=0, sticky="nsew")
        transcript_container.grid_rowconfigure(1, weight=1)
        transcript_container.grid_columnconfigure(0, weight=1)
        self.transcription_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10), state='disabled', height=10)
        self.transcription_text.grid(row=1, column=0, sticky="nsew")
        self.transcription_search = SearchFrame(transcript_container, self.transcription_text)
        self.transcription_search.grid(row=0, column=0, sticky="ew")

        summary_container = tk.LabelFrame(details_frame, text="要約結果", padx=5, pady=5)
        summary_container.grid(row=3, column=0, sticky="nsew", pady=(5,0))
        summary_container.grid_rowconfigure(1, weight=1)
        summary_container.grid_columnconfigure(0, weight=1)
        self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10), state='disabled', height=5)
        self.summary_text.grid(row=1, column=0, sticky="nsew")
        self.summary_search = SearchFrame(summary_container, self.summary_text)
        self.summary_search.grid(row=0, column=0, sticky="ew")

        self.sessions = []
        self.populate_sessions_list()

    def perform_global_search(self, event=None):
        keyword = self.global_search_entry.get()
        if not keyword:
            messagebox.showwarning("キーワードなし", "検索キーワードを入力してください。", parent=self)
            return
        
        self.current_search_keyword = keyword
        found_sessions = db.search_sessions(keyword)
        self._update_listbox(found_sessions)
        self._clear_details()

    def _update_listbox(self, sessions_data):
        self.session_listbox.delete(0, tk.END)
        self.sessions = sessions_data
        for session in self.sessions:
            display_text = f"{session['timestamp']} - {session['topic'] or '（テーマなし）'}"
            self.session_listbox.insert(tk.END, display_text)

    def _clear_details(self):
        for widget in [self.transcription_text, self.summary_text]:
            widget.config(state='normal')
            widget.delete("1.0", tk.END)
            widget.config(state='disabled')
        self.transcription_search._clear_search()
        self.summary_search._clear_search()
        self.create_quiz_button.config(state=tk.DISABLED)

    def populate_sessions_list(self):
        self.current_search_keyword = None
        self.global_search_entry.delete(0, tk.END)
        all_sessions = db.get_all_sessions()
        self._update_listbox(all_sessions)
        self._clear_details()

    def on_session_select(self, event):
        selected_indices = self.session_listbox.curselection()
        if not selected_indices: return

        session_id = self.sessions[selected_indices[0]]['id']
        session_data = db.get_session_by_id(session_id)

        if session_data:
            for widget, content in [(self.transcription_text, session_data['transcription']), (self.summary_text, session_data['summary'])]:
                widget.config(state='normal')
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, content or "")
                widget.config(state='disabled')
            
            self.create_quiz_button.config(state=tk.NORMAL if session_data['transcription'] else tk.DISABLED)
            
            if self.current_search_keyword:
                self.transcription_search.execute_search(self.current_search_keyword)
                self.summary_search.execute_search(self.current_search_keyword)
            else:
                self.transcription_search._clear_search()
                self.summary_search._clear_search()

    def delete_selected_session(self):
        selected_indices = self.session_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("選択なし", "削除するセッションを選択してください。", parent=self)
            return

        session_id = self.sessions[selected_indices[0]]['id']
        if messagebox.askyesno("確認", "本当にこのセッションを削除しますか？\nこの操作は元に戻せません。", parent=self):
            db.delete_session_by_id(session_id)
            messagebox.showinfo("削除完了", "セッションを削除しました。", parent=self)
            self.populate_sessions_list()

    def create_quiz_from_selection(self):
        if not self.logic:
            messagebox.showerror("エラー", "システムロジックが利用できません。", parent=self)
            return
        transcription = self.transcription_text.get("1.0", tk.END).strip()
        self.logic.generate_quiz(transcription)


class QuizWindow(Toplevel):
    def __init__(self, master, quiz_text):
        super().__init__(master)
        self.title("AI生成クイズ")
        self.geometry("700x500")
        self.transient(master)
        self.grab_set()

        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        quiz_frame = tk.LabelFrame(main_frame, text="講義内容の理解度チェック", padx=5, pady=5)
        quiz_frame.grid(row=0, column=0, sticky="nsew")
        quiz_frame.grid_rowconfigure(0, weight=1)
        quiz_frame.grid_columnconfigure(0, weight=1)

        self.quiz_text_widget = scrolledtext.ScrolledText(quiz_frame, wrap=tk.WORD, font=("Helvetica", 10))
        self.quiz_text_widget.grid(row=0, column=0, sticky="nsew")
        self.quiz_text_widget.insert(tk.END, quiz_text)
        self.quiz_text_widget.config(state='disabled')

        button_frame = Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.quiz_text_widget.get("1.0", tk.END))
        messagebox.showinfo("コピー完了", "クイズの内容をクリップボードにコピーしました。", parent=self)

class DiscussionPromptWindow(Toplevel):
    def __init__(self, master, prompt_text):
        super().__init__(master)
        self.title("議論を活性化するためのヒント")
        self.geometry("700x500")
        self.transient(master)
        self.grab_set()

        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        prompt_frame = tk.LabelFrame(main_frame, text="行き詰まった会議で使える言葉の例", padx=5, pady=5)
        prompt_frame.grid(row=0, column=0, sticky="nsew")
        prompt_frame.grid_rowconfigure(0, weight=1)
        prompt_frame.grid_columnconfigure(0, weight=1)

        self.prompt_text_widget = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, font=("Helvetica", 10))
        self.prompt_text_widget.grid(row=0, column=0, sticky="nsew")
        self.prompt_text_widget.insert(tk.END, prompt_text)
        self.prompt_text_widget.config(state='disabled')

        button_frame = Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.prompt_text_widget.get("1.0", tk.END))
        messagebox.showinfo("コピー完了", "ヒントの内容をクリップボードにコピーしました。", parent=self)

class ExpandedViewWindow(Toplevel):
    def __init__(self, master, title, content_text):
        super().__init__(master)
        self.title(title)
        self.geometry("800x600")

        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Helvetica", 12))
        text_widget.grid(row=0, column=0, sticky="nsew")
        text_widget.insert(tk.END, content_text)
        text_widget.config(state='disabled')
        self.content_text = content_text

        button_frame = Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="e", pady=(10, 0))

        tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.content_text)
        messagebox.showinfo("コピー完了", "内容をクリップボードにコピーしました。", parent=self)

class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini リアルタイム文字起こし＆要約アプリ")
        self.root.geometry("1000x850")
        
        self.ui_queue = queue.Queue()
        self.logic = system.AppLogic(self.ui_queue)
        self.summary_colors = ["#0000FF", "#008000", "#8A2BE2", "#FF4500", "#DC143C"]
        self.summary_color_index = 0

        db.init_db()
        self.create_widgets()
        
        self.logic.initialize_gemini()
        self.logic.start_recording()
        self.process_ui_queue()
        
        initial_interval_ms = self.logic.interval_sec_var.get() * 1000
        self.root.after(initial_interval_ms, self.periodic_transcribe_trigger)

    def create_widgets(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        # ★ 変更点: YouTubeからのインポート機能を追加
        file_menu.add_command(label="YouTube動画から文字起こし...", command=self.import_from_youtube)
        file_menu.add_command(label="音声/動画ファイルから文字起こし...", command=self.import_media_file)
        file_menu.add_command(label="テキストファイルをインポート (.txt)", command=self.import_text_file)
        file_menu.add_separator()
        file_menu.add_command(label="文字起こし結果をエクスポート (.txt)", command=self.export_transcription)
        file_menu.add_command(label="要約結果をエクスポート (.txt)", command=self.export_summary)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.on_closing)

        library_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ライブラリ", menu=library_menu)
        library_menu.add_command(label="現在のセッションをライブラリに保存", command=self.save_session_to_library)
        library_menu.add_command(label="ライブラリを開く", command=self.open_library)

        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(5, weight=2) # 文字起こしコンテナ
        main_frame.grid_rowconfigure(6, weight=1) # 要約コンテナ
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = tk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.status_label = tk.Label(top_frame, text="初期化中...", font=("Helvetica", 12))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_button = tk.Button(top_frame, text="文字起こしを停止", command=self.logic.toggle_transcription, font=("Helvetica", 10))
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        self.activate_discussion_button = tk.Button(top_frame, text="議論を活性化", command=self.on_activate_discussion_click, font=("Helvetica", 12, "bold"), fg="darkgreen")
        self.activate_discussion_button.pack(side=tk.RIGHT, padx=5)
        self.create_quiz_button = tk.Button(top_frame, text="問題を作成", command=self.on_create_quiz_click, font=("Helvetica", 12, "bold"), fg="purple")
        self.create_quiz_button.pack(side=tk.RIGHT, padx=(5, 0))
        self.full_summarize_button = tk.Button(top_frame, text="全文を要約", command=self.on_full_summarize_click, font=("Helvetica", 12))
        self.full_summarize_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.summarize_button = tk.Button(top_frame, text="差分を要約", command=self.on_summarize_click, font=("Helvetica", 12))
        self.summarize_button.pack(side=tk.RIGHT, padx=5)
        
        timer_frame = tk.LabelFrame(main_frame, text="タイマー", padx=5, pady=5)
        timer_frame.grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
        tk.Label(timer_frame, text="設定時間(分):").pack(side=tk.LEFT, padx=(5,0))
        self.timer_spinbox = tk.Spinbox(
            timer_frame, from_=1, to=180, width=5, 
            textvariable=self.logic.timer_initial_minutes_var
        )
        self.timer_spinbox.pack(side=tk.LEFT, padx=5)
        self.timer_display_label = tk.Label(timer_frame, text="00:00", font=("Helvetica", 20, "bold"), fg="darkblue")
        self.timer_display_label.pack(side=tk.LEFT, padx=(20, 20))
        self.timer_start_button = tk.Button(timer_frame, text="開始", command=self.logic.start_timer)
        self.timer_start_button.pack(side=tk.LEFT, padx=2)
        self.timer_stop_button = tk.Button(timer_frame, text="停止", command=self.logic.stop_timer, state=tk.DISABLED)
        self.timer_stop_button.pack(side=tk.LEFT, padx=2)
        self.timer_reset_button = tk.Button(timer_frame, text="リセット", command=self.logic.reset_timer)
        self.timer_reset_button.pack(side=tk.LEFT, padx=2)
        self.logic.reset_timer()

        settings_frame = tk.Frame(main_frame)
        settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        interval_label = tk.Label(settings_frame, text="文字起こし間隔(秒):", font=("Helvetica", 10))
        interval_label.pack(side=tk.LEFT, padx=(5, 5))
        self.interval_spinbox = tk.Spinbox(
            settings_frame, from_=5, to=120, width=5,
            textvariable=self.logic.interval_sec_var, font=("Helvetica", 10)
        )
        self.interval_spinbox.pack(side=tk.LEFT)

        model_settings_frame = tk.LabelFrame(main_frame, text="モデル設定", padx=5, pady=5)
        model_settings_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        model_settings_frame.grid_columnconfigure(1, weight=1)
        trans_model_label = tk.Label(model_settings_frame, text="文字起こしモデル:", font=("Helvetica", 10))
        trans_model_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.trans_model_menu = tk.OptionMenu(model_settings_frame, self.logic.transcription_model_var, "")
        self.trans_model_menu.config(font=("Helvetica", 9), anchor='w')
        self.trans_model_menu.grid(row=0, column=1, sticky="ew", padx=5)
        sum_model_label = tk.Label(model_settings_frame, text="要約モデル:", font=("Helvetica", 10))
        sum_model_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.sum_model_menu = tk.OptionMenu(model_settings_frame, self.logic.summary_model_var, "")
        self.sum_model_menu.config(font=("Helvetica", 9), anchor='w')
        self.sum_model_menu.grid(row=1, column=1, sticky="ew", padx=5)

        lecture_frame = tk.Frame(main_frame)
        lecture_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        lecture_label = tk.Label(lecture_frame, text="講義テーマ/会議名:", font=("Helvetica", 10))
        lecture_label.pack(side=tk.LEFT, padx=(5, 5))
        self.lecture_topic_entry = tk.Entry(lecture_frame, font=("Helvetica", 10), textvariable=self.logic.lecture_topic_var)
        self.lecture_topic_entry.pack(fill=tk.X, expand=True)

        transcript_container = tk.LabelFrame(main_frame, text="文字起こし結果", padx=5, pady=5)
        transcript_container.grid(row=5, column=0, sticky="nsew", pady=(5,0))
        transcript_container.grid_rowconfigure(1, weight=1)
        transcript_container.grid_columnconfigure(0, weight=1)
        
        self.transcript_search = SearchFrame(transcript_container, None) 
        self.transcript_search.grid(row=0, column=0, sticky="ew")
        
        self.transcript_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10))
        self.transcript_text.grid(row=1, column=0, sticky="nsew")
        self.transcript_search.text_widget = self.transcript_text 

        expand_transcript_button = tk.Button(transcript_container, text="拡大", command=self.open_expanded_transcription, relief=tk.FLAT)
        expand_transcript_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")

        summary_container = tk.LabelFrame(main_frame, text="要約結果", padx=5, pady=5)
        summary_container.grid(row=6, column=0, sticky="nsew", pady=(5, 0))
        summary_container.grid_rowconfigure(1, weight=1)
        summary_container.grid_columnconfigure(0, weight=1)
        
        self.summary_search = SearchFrame(summary_container, None)
        self.summary_search.grid(row=0, column=0, sticky="ew")

        self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10))
        self.summary_text.grid(row=1, column=0, sticky="nsew")
        self.summary_search.text_widget = self.summary_text

        expand_summary_button = tk.Button(summary_container, text="拡大", command=self.open_expanded_summary, relief=tk.FLAT)
        expand_summary_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")
        
    def periodic_transcribe_trigger(self):
        self.logic.periodic_transcribe()
        current_interval_ms = self.logic.interval_sec_var.get() * 1000
        self.root.after(current_interval_ms, self.periodic_transcribe_trigger)

    def open_expanded_transcription(self):
        content = self.transcript_text.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("テキストなし", "拡大表示する文字起こし内容がありません。")
            return
        ExpandedViewWindow(self.root, "文字起こし - 拡大表示", content)

    def open_expanded_summary(self):
        content = self.summary_text.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("テキストなし", "拡大表示する要約内容がありません。")
            return
        ExpandedViewWindow(self.root, "要約 - 拡大表示", content)

    def on_summarize_click(self):
        self.logic.on_summarize_click()

    def on_full_summarize_click(self):
        full_transcript = self.transcript_text.get("1.0", tk.END)
        self.logic.on_full_summarize_click(full_transcript)
        
    def on_create_quiz_click(self):
        full_transcript = self.transcript_text.get("1.0", tk.END)
        self.logic.generate_quiz(full_transcript)
        
    def on_activate_discussion_click(self):
        transcript = self.transcript_text.get("1.0", tk.END)
        summary = self.summary_text.get("1.0", tk.END)
        self.logic.generate_discussion_prompts(transcript, summary)

    def save_session_to_library(self):
        transcription = self.transcript_text.get("1.0", tk.END).strip()
        summary = self.summary_text.get("1.0", tk.END).strip()
        self.logic.save_session_to_library(transcription, summary)

    def import_text_file(self):
        filepath = filedialog.askopenfilename(
            title="テキストファイルをインポート",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if not filepath:
            return
        
        content = self.logic.import_text_file(filepath)
        if content is not None:
             if messagebox.askyesno("確認", "現在の文字起こし結果をクリアしてインポートしますか？"):
                self.transcript_text.delete("1.0", tk.END)
                self.summary_text.delete("1.0", tk.END)
                self.transcript_text.insert("1.0", content)
                messagebox.showinfo("成功", "ファイルのインポートが完了しました。")
    
    # ★ 新機能: YouTubeからのインポート処理の起点
    def import_from_youtube(self):
        url = simpledialog.askstring("YouTube URL", "文字起こしするYouTube動画のURLを入力してください:", parent=self.root)
        if not url:
            return
            
        if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、YouTube動画から文字起こしを実行しますか？"):
            self.transcript_text.delete("1.0", tk.END)
            self.summary_text.delete("1.0", tk.END)
            self.logic.process_youtube_url(url)

    def import_media_file(self):
        filepath = filedialog.askopenfilename(
            title="音声/動画ファイルを選択",
            filetypes=[("メディアファイル", "*.mp3 *.wav *.mp4"), 
                       ("音声ファイル", "*.mp3 *.wav"),
                       ("動画ファイル", "*.mp4"),
                       ("すべてのファイル", "*.*")]
        )
        if not filepath:
            return
            
        if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、ファイルから文字起こしを実行しますか？"):
            self.transcript_text.delete("1.0", tk.END)
            self.summary_text.delete("1.0", tk.END)
            self.logic.process_media_file(filepath)

    def export_text_widget(self, widget, title, default_name):
        content = widget.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
            return
        
        filepath = filedialog.asksaveasfilename(
            title=title,
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filepath:
            self.logic.export_text_to_file(filepath, content)

    def export_transcription(self):
        self.export_text_widget(self.transcript_text, "文字起こし結果をエクスポート", "transcription.txt")

    def export_summary(self):
        self.export_text_widget(self.summary_text, "要約結果をエクスポート", "summary.txt")

    def open_library(self):
        LibraryWindow(self.root, self.logic)

    def process_ui_queue(self):
        try:
            message = self.ui_queue.get_nowait()
            msg_type, *payload = message
            
            if msg_type == "update_status":
                self.status_label.config(text=payload[0])
            
            elif msg_type == "show_error":
                messagebox.showerror(payload[0], payload[1])
            
            elif msg_type == "show_info":
                messagebox.showinfo(payload[0], payload[1])
            
            elif msg_type == "show_warning":
                messagebox.showwarning(payload[0], payload[1])

            elif msg_type == "set_button_state":
                widget_name, state = payload
                widgets = {
                    "toggle_button": self.toggle_button,
                    "summarize_button": self.summarize_button,
                    "full_summarize_button": self.full_summarize_button,
                    "timer_start_button": self.timer_start_button,
                    "timer_stop_button": self.timer_stop_button,
                    "timer_spinbox": self.timer_spinbox,
                    "create_quiz_button": self.create_quiz_button,
                    "activate_discussion_button": self.activate_discussion_button,
                }
                if widget_name in widgets:
                    widgets[widget_name].config(state=state)

            elif msg_type == "set_button_text":
                widget_name, text = payload
                if widget_name == "toggle_button":
                    self.toggle_button.config(text=text)

            elif msg_type == "update_model_menus":
                models = payload[0]
                trans_menu = self.trans_model_menu["menu"]
                trans_menu.delete(0, "end")
                sum_menu = self.sum_model_menu["menu"]
                sum_menu.delete(0, "end")
                for model_name in sorted(models):
                    trans_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.transcription_model_var.set(v))
                    sum_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.summary_model_var.set(v))

            elif msg_type == "append_transcription":
                transcript = payload[0]
                self.transcript_text.insert(tk.END, transcript + "\n\n")
                self.transcript_text.see(tk.END)
            
            elif msg_type == "append_summary_marker":
                timestamp = payload[0]
                self.transcript_text.insert(tk.END, f"\n--- ▲ ここまでの内容を要約しました ({timestamp}) ▲ ---\n\n")
                self.transcript_text.see(tk.END)

            elif msg_type == "update_summary":
                summary, topic, summary_type, timestamp = payload
                summary_title = "差分要約" if summary_type == "diff" else "全文要約"
                topic_header = f" (テーマ: {topic})" if topic else ""
                header = f"--- {timestamp} の{summary_title}{topic_header} ---\n"
                
                current_color = self.summary_colors[self.summary_color_index]
                tag_name = f"summary_tag_{timestamp.replace(':', '')}"
                self.summary_text.tag_configure(tag_name, foreground=current_color)
                
                if summary_type == "full":
                    self.summary_text.delete("1.0", tk.END)

                self.summary_text.insert(tk.END, header + summary + "\n\n", (tag_name,))
                self.summary_color_index = (self.summary_color_index + 1) % len(self.summary_colors)
                self.summary_text.see(tk.END)

            elif msg_type == "update_timer_display":
                self.timer_display_label.config(text=payload[0])

            elif msg_type == "play_bell":
                self.root.bell()
            
            elif msg_type == "display_quiz":
                quiz_text = payload[0]
                QuizWindow(self.root, quiz_text)

            elif msg_type == "display_discussion_prompts":
                prompt_text = payload[0]
                DiscussionPromptWindow(self.root, prompt_text)


        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_ui_queue)

    def on_closing(self):
        self.logic.shutdown()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriberApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()