# # ### main.py (エラー修正・Googleドキュメント検索機能 追加版)

# # import tkinter as tk
# # from tkinter import scrolledtext, messagebox, Menu, filedialog, simpledialog
# # import queue
# # import system
# # import database as db
# # from ui_components import SearchFrame
# # ### 変更箇所１ ###
# # from windows import LibraryWindow, QuizWindow, DiscussionPromptWindow, ExpandedViewWindow, GoogleDocImportWindow
# # from datetime import datetime

# # class TranscriberApp:
# #     def __init__(self, root):
# #         self.root = root
# #         self.root.title("Gemini リアルタイム文字起こし＆要約アプリ")
# #         self.root.geometry("1000x900")
        
# #         self.ui_queue = queue.Queue()
# #         self.logic = system.AppLogic(self.ui_queue)
        
# #         # カレンダー連携用の変数をlogic内に追加
# #         self.logic.selected_calendar_id_var = tk.StringVar()
        
# #         self.summary_colors = ["#0000FF", "#008000", "#8A2BE2", "#FF4500", "#DC143C"]
# #         self.summary_color_index = 0

# #         db.init_db()
# #         self.create_widgets()
        
# #         self.logic.initialize_gemini()
# #         self.logic.start_recording()
# #         self.process_ui_queue()
        
# #         initial_interval_ms = self.logic.interval_sec_var.get() * 1000
# #         self.root.after(initial_interval_ms, self.periodic_transcribe_trigger)

# #     def create_widgets(self):
# #         menubar = Menu(self.root)
# #         self.root.config(menu=menubar)

# #         file_menu = Menu(menubar, tearoff=0)
# #         menubar.add_cascade(label="ファイル", menu=file_menu)
# #         file_menu.add_command(label="Googleドキュメントからインポート...", command=self.import_from_gdoc)
# #         file_menu.add_command(label="YouTube動画から文字起こし...", command=self.import_from_youtube)
# #         file_menu.add_command(label="音声/動画ファイルから文字起こし...", command=self.import_media_file)
# #         file_menu.add_command(label="テキストファイルをインポート (.txt)", command=self.import_text_file)
# #         file_menu.add_separator()
# #         file_menu.add_command(label="文字起こし結果をエクスポート (.txt)", command=self.export_transcription)
# #         file_menu.add_command(label="要約結果をエクスポート (.txt)", command=self.export_summary)
# #         file_menu.add_separator()
# #         file_menu.add_command(label="文字起こしをGoogleドキュメントへエクスポート", command=self.export_transcription_to_gdoc)
# #         file_menu.add_command(label="要約をGoogleドキュメントへエクスポート", command=self.export_summary_to_gdoc)
# #         file_menu.add_command(label="文字起こしと要約をGoogleドキュメントへエクスポート", command=self.export_all_to_gdoc)
# #         file_menu.add_separator()
# #         file_menu.add_command(label="終了", command=self.on_closing)

# #         library_menu = Menu(menubar, tearoff=0)
# #         menubar.add_cascade(label="ライブラリ", menu=library_menu)
# #         library_menu.add_command(label="現在のセッションをライブラリに保存", command=self.save_session_to_library)
# #         library_menu.add_command(label="ライブラリを開く", command=self.open_library)
        
# #         main_frame = tk.Frame(self.root, padx=10, pady=10)
# #         main_frame.pack(fill=tk.BOTH, expand=True)
# #         main_frame.grid_rowconfigure(7, weight=2)
# #         main_frame.grid_rowconfigure(8, weight=1)
# #         main_frame.grid_columnconfigure(0, weight=1)

# #         top_frame = tk.Frame(main_frame)
# #         top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
# #         self.status_label = tk.Label(top_frame, text="初期化中...", font=("Helvetica", 12))
# #         self.status_label.pack(side=tk.LEFT, padx=5)
        
# #         self.toggle_button = tk.Button(top_frame, text="文字起こしを停止", command=self.logic.toggle_transcription, font=("Helvetica", 10))
# #         self.toggle_button.pack(side=tk.LEFT, padx=5)

# #         self.save_to_library_button = tk.Button(top_frame, text="ライブラリに保存", command=self.save_session_to_library, font=("Helvetica", 10))
# #         self.save_to_library_button.pack(side=tk.LEFT, padx=5)

# #         self.activate_discussion_button = tk.Button(top_frame, text="議論を活性化", command=self.on_activate_discussion_click, font=("Helvetica", 12, "bold"), fg="darkgreen")
# #         self.activate_discussion_button.pack(side=tk.RIGHT, padx=5)
# #         self.create_quiz_button = tk.Button(top_frame, text="問題を作成", command=self.on_create_quiz_click, font=("Helvetica", 12, "bold"), fg="purple")
# #         self.create_quiz_button.pack(side=tk.RIGHT, padx=(5, 0))
# #         self.full_summarize_button = tk.Button(top_frame, text="全文を要約", command=self.on_full_summarize_click, font=("Helvetica", 12))
# #         self.full_summarize_button.pack(side=tk.RIGHT, padx=(0, 5))
# #         self.summarize_button = tk.Button(top_frame, text="差分を要約", command=self.on_summarize_click, font=("Helvetica", 12))
# #         self.summarize_button.pack(side=tk.RIGHT, padx=5)
        
# #         timer_frame = tk.LabelFrame(main_frame, text="タイマー", padx=5, pady=5)
# #         timer_frame.grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
# #         tk.Label(timer_frame, text="設定時間(分):").pack(side=tk.LEFT, padx=(5,0))
# #         self.timer_spinbox = tk.Spinbox(
# #             timer_frame, from_=1, to=180, width=5, 
# #             textvariable=self.logic.timer_initial_minutes_var
# #         )
# #         self.timer_spinbox.pack(side=tk.LEFT, padx=5)
# #         self.timer_display_label = tk.Label(timer_frame, text="00:00", font=("Helvetica", 20, "bold"), fg="darkblue")
# #         self.timer_display_label.pack(side=tk.LEFT, padx=(20, 20))
# #         self.timer_start_button = tk.Button(timer_frame, text="開始", command=self.logic.start_timer)
# #         self.timer_start_button.pack(side=tk.LEFT, padx=2)
# #         self.timer_stop_button = tk.Button(timer_frame, text="停止", command=self.logic.stop_timer, state=tk.DISABLED)
# #         self.timer_stop_button.pack(side=tk.LEFT, padx=2)
# #         self.timer_reset_button = tk.Button(timer_frame, text="リセット", command=self.logic.reset_timer)
# #         self.timer_reset_button.pack(side=tk.LEFT, padx=2)
# #         self.logic.reset_timer()

# #         settings_frame = tk.Frame(main_frame)
# #         settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
# #         interval_label = tk.Label(settings_frame, text="文字起こし間隔(秒):", font=("Helvetica", 10))
# #         interval_label.pack(side=tk.LEFT, padx=(5, 5))
# #         self.interval_spinbox = tk.Spinbox(
# #             settings_frame, from_=5, to=120, width=5,
# #             textvariable=self.logic.interval_sec_var, font=("Helvetica", 10)
# #         )
# #         self.interval_spinbox.pack(side=tk.LEFT)

# #         model_settings_frame = tk.LabelFrame(main_frame, text="モデル設定", padx=5, pady=5)
# #         model_settings_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
# #         model_settings_frame.grid_columnconfigure(1, weight=1)
# #         trans_model_label = tk.Label(model_settings_frame, text="文字起こしモデル:", font=("Helvetica", 10))
# #         trans_model_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
# #         self.trans_model_menu = tk.OptionMenu(model_settings_frame, self.logic.transcription_model_var, "")
# #         self.trans_model_menu.config(font=("Helvetica", 9), anchor='w')
# #         self.trans_model_menu.grid(row=0, column=1, sticky="ew", padx=5)
# #         sum_model_label = tk.Label(model_settings_frame, text="要約モデル:", font=("Helvetica", 10))
# #         sum_model_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
# #         self.sum_model_menu = tk.OptionMenu(model_settings_frame, self.logic.summary_model_var, "")
# #         self.sum_model_menu.config(font=("Helvetica", 9), anchor='w')
# #         self.sum_model_menu.grid(row=1, column=1, sticky="ew", padx=5)
        
# #         # --- カレンダー連携フレーム ---
# #         calendar_frame = tk.LabelFrame(main_frame, text="カレンダー連携", padx=5, pady=5)
# #         calendar_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
# #         calendar_frame.grid_columnconfigure(1, weight=1)

# #         self.refresh_calendars_button = tk.Button(calendar_frame, text="カレンダー更新", command=self.logic.fetch_calendar_list)
# #         self.refresh_calendars_button.grid(row=0, column=0, padx=5)
        
# #         self.calendar_menu = tk.OptionMenu(calendar_frame, self.logic.selected_calendar_id_var, "")
# #         self.calendar_menu.config(font=("Helvetica", 9), anchor='w')
# #         self.calendar_menu.grid(row=0, column=1, sticky="ew")

# #         self.fetch_current_event_button = tk.Button(calendar_frame, text="現在の授業を取得", command=self.logic.fetch_current_calendar_event)
# #         self.fetch_current_event_button.grid(row=0, column=2, padx=5)
        
# #         self.set_default_cal_button = tk.Button(calendar_frame, text="✔ デフォルトに設定", command=self.logic.set_default_calendar)
# #         self.set_default_cal_button.grid(row=0, column=3, padx=5)

# #         lecture_frame = tk.Frame(main_frame)
# #         lecture_frame.grid(row=5, column=0, sticky="ew", pady=(0, 5))
# #         lecture_label = tk.Label(lecture_frame, text="講義テーマ/会議名:", font=("Helvetica", 10))
# #         lecture_label.pack(side=tk.LEFT, padx=(5, 5))
# #         self.lecture_topic_entry = tk.Entry(lecture_frame, font=("Helvetica", 10), textvariable=self.logic.lecture_topic_var)
# #         self.lecture_topic_entry.pack(fill=tk.X, expand=True)

# #         drive_folder_frame = tk.Frame(main_frame)
# #         drive_folder_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10))
# #         drive_folder_label = tk.Label(drive_folder_frame, text="DriveフォルダURL / パス:", font=("Helvetica", 10))
# #         drive_folder_label.pack(side=tk.LEFT, padx=(5,5))
# #         self.drive_folder_entry = tk.Entry(drive_folder_frame, font=("Helvetica", 10), textvariable=self.logic.drive_folder_name_var)
# #         self.drive_folder_entry.pack(fill=tk.X, expand=True)

# #         transcript_container = tk.LabelFrame(main_frame, text="文字起こし結果", padx=5, pady=5)
# #         transcript_container.grid(row=7, column=0, sticky="nsew", pady=(5,0))
# #         transcript_container.grid_rowconfigure(1, weight=1)
# #         transcript_container.grid_columnconfigure(0, weight=1)
        
# #         self.transcript_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10))
# #         self.transcript_search = SearchFrame(transcript_container, self.transcript_text) 
# #         self.transcript_search.grid(row=0, column=0, sticky="ew")
        
# #         self.transcript_text.grid(row=1, column=0, sticky="nsew")

# #         expand_transcript_button = tk.Button(transcript_container, text="拡大", command=self.open_expanded_transcription, relief=tk.FLAT)
# #         expand_transcript_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")

# #         summary_container = tk.LabelFrame(main_frame, text="要約結果", padx=5, pady=5)
# #         summary_container.grid(row=8, column=0, sticky="nsew", pady=(5, 0))
# #         summary_container.grid_rowconfigure(1, weight=1)
# #         summary_container.grid_columnconfigure(0, weight=1)
        
# #         self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10))
# #         self.summary_search = SearchFrame(summary_container, self.summary_text)
# #         self.summary_search.grid(row=0, column=0, sticky="ew")
        
# #         self.summary_text.grid(row=1, column=0, sticky="nsew")

# #         expand_summary_button = tk.Button(summary_container, text="拡大", command=self.open_expanded_summary, relief=tk.FLAT)
# #         expand_summary_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")
        
# #     def periodic_transcribe_trigger(self):
# #         self.logic.periodic_transcribe()
# #         current_interval_ms = self.logic.interval_sec_var.get() * 1000
# #         self.root.after(current_interval_ms, self.periodic_transcribe_trigger)

# #     def open_expanded_transcription(self):
# #         content = self.transcript_text.get("1.0", tk.END)
# #         if not content.strip():
# #             messagebox.showwarning("テキストなし", "拡大表示する文字起こし内容がありません。")
# #             return
# #         ExpandedViewWindow(self.root, "文字起こし - 拡大表示", content)

# #     def open_expanded_summary(self):
# #         content = self.summary_text.get("1.0", tk.END)
# #         if not content.strip():
# #             messagebox.showwarning("テキストなし", "拡大表示する要約内容がありません。")
# #             return
# #         ExpandedViewWindow(self.root, "要約 - 拡大表示", content)

# #     def on_summarize_click(self):
# #         self.logic.on_summarize_click()

# #     def on_full_summarize_click(self):
# #         full_transcript = self.transcript_text.get("1.0", tk.END)
# #         self.logic.on_full_summarize_click(full_transcript)
        
# #     def on_create_quiz_click(self):
# #         full_transcript = self.transcript_text.get("1.0", tk.END)
# #         self.logic.generate_quiz(full_transcript)
        
# #     def on_activate_discussion_click(self):
# #         transcript = self.transcript_text.get("1.0", tk.END)
# #         summary = self.summary_text.get("1.0", tk.END)
# #         self.logic.generate_discussion_prompts(transcript, summary)

# #     def save_session_to_library(self):
# #         transcription = self.transcript_text.get("1.0", tk.END).strip()
# #         summary = self.summary_text.get("1.0", tk.END).strip()
# #         self.logic.save_session_to_library(transcription, summary)

# #     ### 変更箇所２ ###
# #     def import_from_gdoc(self):
# #         """Googleドキュメント検索用の専用ウィンドウを開く"""
# #         try:
# #             # 新しいウィンドウクラスを、logicとappインスタンスを渡して呼び出す
# #             GoogleDocImportWindow(self.root, self.logic, self)
# #         except Exception as e:
# #             messagebox.showerror("エラー", f"インポートウィンドウを開けませんでした。\n{e}")
    
# #     def import_text_file(self, filepath):
# #         filepath = filedialog.askopenfilename(
# #             title="テキストファイルをインポート",
# #             filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
# #         )
# #         if not filepath:
# #             return
        
# #         content = self.logic.import_text_file(filepath)
# #         if content is not None:
# #              if messagebox.askyesno("確認", "現在の文字起こし結果をクリアしてインポートしますか？"):
# #                 self.transcript_text.delete("1.0", tk.END)
# #                 self.summary_text.delete("1.0", tk.END)
# #                 self.transcript_text.insert("1.0", content)
# #                 messagebox.showinfo("成功", "ファイルのインポートが完了しました。")
    
# #     def import_from_youtube(self):
# #         url = simpledialog.askstring("YouTube URL", "文字起こしするYouTube動画のURLを入力してください:", parent=self.root)
# #         if not url:
# #             return
            
# #         if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、YouTube動画から文字起こしを実行しますか？"):
# #             self.transcript_text.delete("1.0", tk.END)
# #             self.summary_text.delete("1.0", tk.END)
# #             self.logic.process_youtube_url(url)

# #     def import_media_file(self):
# #         filepath = filedialog.askopenfilename(
# #             title="音声/動画ファイルを選択",
# #             filetypes=[("メディアファイル", "*.mp3 *.wav *.mp4"), 
# #                        ("音声ファイル", "*.mp3 *.wav"),
# #                        ("動画ファイル", "*.mp4"),
# #                        ("すべてのファイル", "*.*")]
# #         )
# #         if not filepath:
# #             return
            
# #         if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、ファイルから文字起こしを実行しますか？"):
# #             self.transcript_text.delete("1.0", tk.END)
# #             self.summary_text.delete("1.0", tk.END)
# #             self.logic.process_media_file(filepath)

# #     def export_text_widget(self, widget, title, default_name):
# #         content = widget.get("1.0", tk.END).strip()
# #         if not content:
# #             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
# #             return
        
# #         filepath = filedialog.asksaveasfilename(
# #             title=title,
# #             initialfile=default_name,
# #             defaultextension=".txt",
# #             filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
# #         )
# #         if filepath:
# #             self.logic.export_text_to_file(filepath, content)

# #     def export_transcription(self):
# #         self.export_text_widget(self.transcript_text, "文字起こし結果をエクスポート", "transcription.txt")

# #     def export_summary(self):
# #         self.export_text_widget(self.summary_text, "要約結果をエクスポート", "summary.txt")

# #     def export_transcription_to_gdoc(self):
# #         content = self.transcript_text.get("1.0", tk.END).strip()
# #         if not content:
# #             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
# #             return
# #         topic = self.logic.lecture_topic_var.get() or "無題の文字起こし"
# #         title = f"{topic} - {datetime.now().strftime('%Y-%m-%d')}"
# #         self.logic.export_to_google_doc(title, content)

# #     def export_summary_to_gdoc(self):
# #         content = self.summary_text.get("1.0", tk.END).strip()
# #         if not content:
# #             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
# #             return
# #         topic = self.logic.lecture_topic_var.get() or "無題の要約"
# #         title = f"[要約] {topic} - {datetime.now().strftime('%Y-%m-%d')}"
# #         self.logic.export_to_google_doc(title, content)

# #     def export_all_to_gdoc(self):
# #         transcription = self.transcript_text.get("1.0", tk.END).strip()
# #         summary = self.summary_text.get("1.0", tk.END).strip()

# #         if not transcription and not summary:
# #             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
# #             return
            
# #         content_plain = f"■■■ 文字起こし結果 ■■■\n\n{transcription}\n\n\n"
# #         content_plain += f"■■■ 要約結果 ■■■\n\n{summary}"

# #         topic = self.logic.lecture_topic_var.get() or "無題のセッション"
# #         title = f"{topic} (文字起こしと要約) - {datetime.now().strftime('%Y-%m-%d')}"

# #         self.logic.export_to_google_doc(title, content_plain)

# #     def open_library(self):
# #         LibraryWindow(self.root, self.logic, self)

# #     def load_data_into_session(self, transcription, summary, topic):
# #         self.transcript_text.delete("1.0", tk.END)
# #         self.summary_text.delete("1.0", tk.END)

# #         self.transcript_text.insert("1.0", transcription or "")
# #         self.summary_text.insert("1.0", summary or "")

# #         self.logic.lecture_topic_var.set(topic or "")
        
# #         self.logic.transcribed_text_buffer = ""
# #         self.logic.last_summary = ""
        
# #         self.ui_queue.put(('show_info', "読み込み完了", "セッションの読み込みが完了しました。"))

# #     def process_ui_queue(self):
# #         try:
# #             message = self.ui_queue.get_nowait()
# #             msg_type, *payload = message
            
# #             if msg_type == "update_status":
# #                 self.status_label.config(text=payload[0])
            
# #             elif msg_type == "show_error":
# #                 messagebox.showerror(payload[0], payload[1])
            
# #             elif msg_type == "show_info":
# #                 messagebox.showinfo(payload[0], payload[1])
            
# #             elif msg_type == "show_warning":
# #                 messagebox.showwarning(payload[0], payload[1])

# #             elif msg_type == "set_button_state":
# #                 widget_name, state = payload
# #                 widgets = {
# #                     "toggle_button": self.toggle_button,
# #                     "summarize_button": self.summarize_button,
# #                     "full_summarize_button": self.full_summarize_button,
# #                     "timer_start_button": self.timer_start_button,
# #                     "timer_stop_button": self.timer_stop_button,
# #                     "timer_spinbox": self.timer_spinbox,
# #                     "create_quiz_button": self.create_quiz_button,
# #                     "activate_discussion_button": self.activate_discussion_button,
# #                 }
# #                 if widget_name in widgets:
# #                     widgets[widget_name].config(state=state)

# #             elif msg_type == "set_button_text":
# #                 widget_name, text = payload
# #                 if widget_name == "toggle_button":
# #                     self.toggle_button.config(text=text)

# #             elif msg_type == "update_model_menus":
# #                 models = payload[0]
# #                 trans_menu = self.trans_model_menu["menu"]
# #                 trans_menu.delete(0, "end")
# #                 sum_menu = self.sum_model_menu["menu"]
# #                 sum_menu.delete(0, "end")
# #                 for model_name in sorted(models):
# #                     trans_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.transcription_model_var.set(v))
# #                     sum_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.summary_model_var.set(v))

# #             elif msg_type == "append_transcription":
# #                 transcript = payload[0]
# #                 self.transcript_text.insert(tk.END, transcript + "\n\n")
# #                 self.transcript_text.see(tk.END)
            
# #             elif msg_type == "append_summary_marker":
# #                 timestamp = payload[0]
# #                 self.transcript_text.insert(tk.END, f"\n--- ▲ ここまでの内容を要約しました ({timestamp}) ▲ ---\n\n")
# #                 self.transcript_text.see(tk.END)

# #             elif msg_type == "update_summary":
# #                 summary, topic, summary_type, timestamp = payload
# #                 summary_title = "差分要約" if summary_type == "diff" else "全文要約"
# #                 topic_header = f" (テーマ: {topic})" if topic else ""
# #                 header = f"--- {timestamp} の{summary_title}{topic_header} ---\n"
                
# #                 current_color = self.summary_colors[self.summary_color_index]
# #                 tag_name = f"summary_tag_{timestamp.replace(':', '')}"
# #                 self.summary_text.tag_configure(tag_name, foreground=current_color)
                
# #                 if summary_type == "full":
# #                     self.summary_text.delete("1.0", tk.END)

# #                 self.summary_text.insert(tk.END, header + summary + "\n\n", (tag_name,))
# #                 self.summary_color_index = (self.summary_color_index + 1) % len(self.summary_colors)
# #                 self.summary_text.see(tk.END)

# #             elif msg_type == "update_timer_display":
# #                 self.timer_display_label.config(text=payload[0])

# #             elif msg_type == "play_bell":
# #                 self.root.bell()
            
# #             elif msg_type == "display_quiz":
# #                 quiz_text = payload[0]
# #                 QuizWindow(self.root, quiz_text)

# #             elif msg_type == "display_discussion_prompts":
# #                 prompt_text = payload[0]
# #                 DiscussionPromptWindow(self.root, prompt_text)
            
# #             elif msg_type == "gdoc_import_completed":
# #                 content = payload[0]
# #                 if messagebox.askyesno("インポート確認", "現在の文字起こしと要約をクリアして、ドキュメントをインポートしますか？"):
# #                     self.transcript_text.delete("1.0", tk.END)
# #                     self.summary_text.delete("1.0", tk.END)
# #                     self.transcript_text.insert("1.0", content)
# #                     self.logic.transcribed_text_buffer = ""
# #                     self.logic.last_summary = ""
# #                     messagebox.showinfo("成功", "Googleドキュメントのインポートが完了しました。")
            
# #             # ★★★ エラーを修正したカレンダーメニュー更新処理 ★★★
# #             elif msg_type == "update_calendar_menu":
# #                 # payload[0]に(calendar_data, default_id)のタプルが入っている
# #                 calendar_data, default_id = payload[0]
# #                 menu = self.calendar_menu["menu"]
# #                 menu.delete(0, "end")

# #                 found_default = False
# #                 if calendar_data:
# #                     for summary, cal_id in calendar_data:
# #                         menu.add_command(label=summary, command=lambda v=cal_id: self.logic.selected_calendar_id_var.set(v))
# #                         if default_id and cal_id == default_id:
# #                             self.logic.selected_calendar_id_var.set(cal_id)
# #                             found_default = True
                    
# #                     if not found_default and calendar_data:
# #                         self.logic.selected_calendar_id_var.set(calendar_data[0][1])
# #                 else:
# #                     self.logic.selected_calendar_id_var.set("")


# #         except queue.Empty:
# #             pass
# #         finally:
# #             self.root.after(100, self.process_ui_queue)

# #     def on_closing(self):
# #         self.logic.shutdown()
# #         self.root.destroy()

# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = TranscriberApp(root)
# #     root.protocol("WM_DELETE_WINDOW", app.on_closing)
# #     root.mainloop()




# ### main.py (エラー修正・Googleドキュメント検索機能・キーワードポップアップ機能 追加版)

# import tkinter as tk
# from tkinter import scrolledtext, messagebox, Menu, filedialog, simpledialog
# import queue
# import system
# import database as db
# from ui_components import SearchFrame
# ### 変更箇所１ ###
# from windows import LibraryWindow, QuizWindow, DiscussionPromptWindow, ExpandedViewWindow, GoogleDocImportWindow, KeywordPopup
# from datetime import datetime

# class TranscriberApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Gemini リアルタイム文字起こし＆要約アプリ")
#         self.root.geometry("1000x900")
        
#         self.ui_queue = queue.Queue()
#         self.logic = system.AppLogic(self.ui_queue)
        
#         self.logic.selected_calendar_id_var = tk.StringVar()
        
#         self.summary_colors = ["#0000FF", "#008000", "#8A2BE2", "#FF4500", "#DC143C"]
#         self.summary_color_index = 0

#         db.init_db()
#         self.create_widgets()
        
#         # ★★★ 新機能: ポップアップ管理用のリスト ★★★
#         self.keyword_popups = []

#         self.logic.initialize_gemini()
#         self.logic.start_recording()
#         self.process_ui_queue()
        
#         initial_interval_ms = self.logic.interval_sec_var.get() * 1000
#         self.root.after(initial_interval_ms, self.periodic_transcribe_trigger)

#     def create_widgets(self):
#         menubar = Menu(self.root)
#         self.root.config(menu=menubar)

#         file_menu = Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="ファイル", menu=file_menu)
#         file_menu.add_command(label="Googleドキュメントからインポート...", command=self.import_from_gdoc)
#         file_menu.add_command(label="YouTube動画から文字起こし...", command=self.import_from_youtube)
#         file_menu.add_command(label="音声/動画ファイルから文字起こし...", command=self.import_media_file)
#         file_menu.add_command(label="テキストファイルをインポート (.txt)", command=self.import_text_file)
#         file_menu.add_separator()
#         file_menu.add_command(label="文字起こし結果をエクスポート (.txt)", command=self.export_transcription)
#         file_menu.add_command(label="要約結果をエクスポート (.txt)", command=self.export_summary)
#         file_menu.add_separator()
#         file_menu.add_command(label="文字起こしをGoogleドキュメントへエクスポート", command=self.export_transcription_to_gdoc)
#         file_menu.add_command(label="要約をGoogleドキュメントへエクスポート", command=self.export_summary_to_gdoc)
#         file_menu.add_command(label="文字起こしと要約をGoogleドキュメントへエクスポート", command=self.export_all_to_gdoc)
#         file_menu.add_separator()
#         file_menu.add_command(label="終了", command=self.on_closing)

#         library_menu = Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="ライブラリ", menu=library_menu)
#         library_menu.add_command(label="現在のセッションをライブラリに保存", command=self.save_session_to_library)
#         library_menu.add_command(label="ライブラリを開く", command=self.open_library)
        
#         main_frame = tk.Frame(self.root, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_rowconfigure(7, weight=2)
#         main_frame.grid_rowconfigure(8, weight=1)
#         main_frame.grid_columnconfigure(0, weight=1)

#         top_frame = tk.Frame(main_frame)
#         top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
#         self.status_label = tk.Label(top_frame, text="初期化中...", font=("Helvetica", 12))
#         self.status_label.pack(side=tk.LEFT, padx=5)
        
#         self.toggle_button = tk.Button(top_frame, text="文字起こしを停止", command=self.logic.toggle_transcription, font=("Helvetica", 10))
#         self.toggle_button.pack(side=tk.LEFT, padx=5)

#         self.save_to_library_button = tk.Button(top_frame, text="ライブラリに保存", command=self.save_session_to_library, font=("Helvetica", 10))
#         self.save_to_library_button.pack(side=tk.LEFT, padx=5)

#         self.activate_discussion_button = tk.Button(top_frame, text="議論を活性化", command=self.on_activate_discussion_click, font=("Helvetica", 12, "bold"), fg="darkgreen")
#         self.activate_discussion_button.pack(side=tk.RIGHT, padx=5)
#         self.create_quiz_button = tk.Button(top_frame, text="問題を作成", command=self.on_create_quiz_click, font=("Helvetica", 12, "bold"), fg="purple")
#         self.create_quiz_button.pack(side=tk.RIGHT, padx=(5, 0))
#         self.full_summarize_button = tk.Button(top_frame, text="全文を要約", command=self.on_full_summarize_click, font=("Helvetica", 12))
#         self.full_summarize_button.pack(side=tk.RIGHT, padx=(0, 5))
#         self.summarize_button = tk.Button(top_frame, text="差分を要約", command=self.on_summarize_click, font=("Helvetica", 12))
#         self.summarize_button.pack(side=tk.RIGHT, padx=5)
        
#         timer_frame = tk.LabelFrame(main_frame, text="タイマー", padx=5, pady=5)
#         timer_frame.grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
#         tk.Label(timer_frame, text="設定時間(分):").pack(side=tk.LEFT, padx=(5,0))
#         self.timer_spinbox = tk.Spinbox(
#             timer_frame, from_=1, to=180, width=5, 
#             textvariable=self.logic.timer_initial_minutes_var
#         )
#         self.timer_spinbox.pack(side=tk.LEFT, padx=5)
#         self.timer_display_label = tk.Label(timer_frame, text="00:00", font=("Helvetica", 20, "bold"), fg="darkblue")
#         self.timer_display_label.pack(side=tk.LEFT, padx=(20, 20))
#         self.timer_start_button = tk.Button(timer_frame, text="開始", command=self.logic.start_timer)
#         self.timer_start_button.pack(side=tk.LEFT, padx=2)
#         self.timer_stop_button = tk.Button(timer_frame, text="停止", command=self.logic.stop_timer, state=tk.DISABLED)
#         self.timer_stop_button.pack(side=tk.LEFT, padx=2)
#         self.timer_reset_button = tk.Button(timer_frame, text="リセット", command=self.logic.reset_timer)
#         self.timer_reset_button.pack(side=tk.LEFT, padx=2)
#         self.logic.reset_timer()

#         settings_frame = tk.Frame(main_frame)
#         settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
#         interval_label = tk.Label(settings_frame, text="文字起こし間隔(秒):", font=("Helvetica", 10))
#         interval_label.pack(side=tk.LEFT, padx=(5, 5))
#         self.interval_spinbox = tk.Spinbox(
#             settings_frame, from_=5, to=120, width=5,
#             textvariable=self.logic.interval_sec_var, font=("Helvetica", 10)
#         )
#         self.interval_spinbox.pack(side=tk.LEFT)

#         model_settings_frame = tk.LabelFrame(main_frame, text="モデル設定", padx=5, pady=5)
#         model_settings_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
#         model_settings_frame.grid_columnconfigure(1, weight=1)
#         trans_model_label = tk.Label(model_settings_frame, text="文字起こしモデル:", font=("Helvetica", 10))
#         trans_model_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
#         self.trans_model_menu = tk.OptionMenu(model_settings_frame, self.logic.transcription_model_var, "")
#         self.trans_model_menu.config(font=("Helvetica", 9), anchor='w')
#         self.trans_model_menu.grid(row=0, column=1, sticky="ew", padx=5)
#         sum_model_label = tk.Label(model_settings_frame, text="要約モデル:", font=("Helvetica", 10))
#         sum_model_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
#         self.sum_model_menu = tk.OptionMenu(model_settings_frame, self.logic.summary_model_var, "")
#         self.sum_model_menu.config(font=("Helvetica", 9), anchor='w')
#         self.sum_model_menu.grid(row=1, column=1, sticky="ew", padx=5)
        
#         calendar_frame = tk.LabelFrame(main_frame, text="カレンダー連携", padx=5, pady=5)
#         calendar_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
#         calendar_frame.grid_columnconfigure(1, weight=1)

#         self.refresh_calendars_button = tk.Button(calendar_frame, text="カレンダー更新", command=self.logic.fetch_calendar_list)
#         self.refresh_calendars_button.grid(row=0, column=0, padx=5)
        
#         self.calendar_menu = tk.OptionMenu(calendar_frame, self.logic.selected_calendar_id_var, "")
#         self.calendar_menu.config(font=("Helvetica", 9), anchor='w')
#         self.calendar_menu.grid(row=0, column=1, sticky="ew")

#         self.fetch_current_event_button = tk.Button(calendar_frame, text="現在の授業を取得", command=self.logic.fetch_current_calendar_event)
#         self.fetch_current_event_button.grid(row=0, column=2, padx=5)
        
#         self.set_default_cal_button = tk.Button(calendar_frame, text="✔ デフォルトに設定", command=self.logic.set_default_calendar)
#         self.set_default_cal_button.grid(row=0, column=3, padx=5)

#         lecture_frame = tk.Frame(main_frame)
#         lecture_frame.grid(row=5, column=0, sticky="ew", pady=(0, 5))
#         lecture_label = tk.Label(lecture_frame, text="講義テーマ/会議名:", font=("Helvetica", 10))
#         lecture_label.pack(side=tk.LEFT, padx=(5, 5))
#         self.lecture_topic_entry = tk.Entry(lecture_frame, font=("Helvetica", 10), textvariable=self.logic.lecture_topic_var)
#         self.lecture_topic_entry.pack(fill=tk.X, expand=True)

#         drive_folder_frame = tk.Frame(main_frame)
#         drive_folder_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10))
#         drive_folder_label = tk.Label(drive_folder_frame, text="DriveフォルダURL / パス:", font=("Helvetica", 10))
#         drive_folder_label.pack(side=tk.LEFT, padx=(5,5))
#         self.drive_folder_entry = tk.Entry(drive_folder_frame, font=("Helvetica", 10), textvariable=self.logic.drive_folder_name_var)
#         self.drive_folder_entry.pack(fill=tk.X, expand=True)

#         transcript_container = tk.LabelFrame(main_frame, text="文字起こし結果", padx=5, pady=5)
#         transcript_container.grid(row=7, column=0, sticky="nsew", pady=(5,0))
#         transcript_container.grid_rowconfigure(1, weight=1)
#         transcript_container.grid_columnconfigure(0, weight=1)
        
#         self.transcript_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10))
#         self.transcript_search = SearchFrame(transcript_container, self.transcript_text) 
#         self.transcript_search.grid(row=0, column=0, sticky="ew")
        
#         self.transcript_text.grid(row=1, column=0, sticky="nsew")

#         expand_transcript_button = tk.Button(transcript_container, text="拡大", command=self.open_expanded_transcription, relief=tk.FLAT)
#         expand_transcript_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")

#         summary_container = tk.LabelFrame(main_frame, text="要約結果", padx=5, pady=5)
#         summary_container.grid(row=8, column=0, sticky="nsew", pady=(5, 0))
#         summary_container.grid_rowconfigure(1, weight=1)
#         summary_container.grid_columnconfigure(0, weight=1)
        
#         self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10))
#         self.summary_search = SearchFrame(summary_container, self.summary_text)
#         self.summary_search.grid(row=0, column=0, sticky="ew")
        
#         self.summary_text.grid(row=1, column=0, sticky="nsew")

#         expand_summary_button = tk.Button(summary_container, text="拡大", command=self.open_expanded_summary, relief=tk.FLAT)
#         expand_summary_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")
        
#     def periodic_transcribe_trigger(self):
#         self.logic.periodic_transcribe()
#         current_interval_ms = self.logic.interval_sec_var.get() * 1000
#         self.root.after(current_interval_ms, self.periodic_transcribe_trigger)

#     def open_expanded_transcription(self):
#         content = self.transcript_text.get("1.0", tk.END)
#         if not content.strip():
#             messagebox.showwarning("テキストなし", "拡大表示する文字起こし内容がありません。")
#             return
#         ExpandedViewWindow(self.root, "文字起こし - 拡大表示", content)

#     def open_expanded_summary(self):
#         content = self.summary_text.get("1.0", tk.END)
#         if not content.strip():
#             messagebox.showwarning("テキストなし", "拡大表示する要約内容がありません。")
#             return
#         ExpandedViewWindow(self.root, "要約 - 拡大表示", content)

#     def on_summarize_click(self):
#         self.logic.on_summarize_click()

#     def on_full_summarize_click(self):
#         full_transcript = self.transcript_text.get("1.0", tk.END)
#         self.logic.on_full_summarize_click(full_transcript)
        
#     def on_create_quiz_click(self):
#         full_transcript = self.transcript_text.get("1.0", tk.END)
#         self.logic.generate_quiz(full_transcript)
        
#     def on_activate_discussion_click(self):
#         transcript = self.transcript_text.get("1.0", tk.END)
#         summary = self.summary_text.get("1.0", tk.END)
#         self.logic.generate_discussion_prompts(transcript, summary)

#     def save_session_to_library(self):
#         transcription = self.transcript_text.get("1.0", tk.END).strip()
#         summary = self.summary_text.get("1.0", tk.END).strip()
#         self.logic.save_session_to_library(transcription, summary)

#     def import_from_gdoc(self):
#         """Googleドキュメント検索用の専用ウィンドウを開く"""
#         try:
#             GoogleDocImportWindow(self.root, self.logic, self)
#         except Exception as e:
#             messagebox.showerror("エラー", f"インポートウィンドウを開けませんでした。\n{e}")
    
#     def import_text_file(self, filepath):
#         filepath = filedialog.askopenfilename(
#             title="テキストファイルをインポート",
#             filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
#         )
#         if not filepath:
#             return
        
#         content = self.logic.import_text_file(filepath)
#         if content is not None:
#              if messagebox.askyesno("確認", "現在の文字起こし結果をクリアしてインポートしますか？"):
#                 self.transcript_text.delete("1.0", tk.END)
#                 self.summary_text.delete("1.0", tk.END)
#                 self.transcript_text.insert("1.0", content)
#                 messagebox.showinfo("成功", "ファイルのインポートが完了しました。")
    
#     def import_from_youtube(self):
#         url = simpledialog.askstring("YouTube URL", "文字起こしするYouTube動画のURLを入力してください:", parent=self.root)
#         if not url:
#             return
            
#         if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、YouTube動画から文字起こしを実行しますか？"):
#             self.transcript_text.delete("1.0", tk.END)
#             self.summary_text.delete("1.0", tk.END)
#             self.logic.process_youtube_url(url)

#     def import_media_file(self):
#         filepath = filedialog.askopenfilename(
#             title="音声/動画ファイルを選択",
#             filetypes=[("メディアファイル", "*.mp3 *.wav *.mp4"), 
#                        ("音声ファイル", "*.mp3 *.wav"),
#                        ("動画ファイル", "*.mp4"),
#                        ("すべてのファイル", "*.*")]
#         )
#         if not filepath:
#             return
            
#         if messagebox.askyesno("確認", "現在の文字起こしと要約をクリアして、ファイルから文字起こしを実行しますか？"):
#             self.transcript_text.delete("1.0", tk.END)
#             self.summary_text.delete("1.0", tk.END)
#             self.logic.process_media_file(filepath)

#     def export_text_widget(self, widget, title, default_name):
#         content = widget.get("1.0", tk.END).strip()
#         if not content:
#             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
#             return
        
#         filepath = filedialog.asksaveasfilename(
#             title=title,
#             initialfile=default_name,
#             defaultextension=".txt",
#             filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
#         )
#         if filepath:
#             self.logic.export_text_to_file(filepath, content)

#     def export_transcription(self):
#         self.export_text_widget(self.transcript_text, "文字起こし結果をエクスポート", "transcription.txt")

#     def export_summary(self):
#         self.export_text_widget(self.summary_text, "要約結果をエクスポート", "summary.txt")

#     def export_transcription_to_gdoc(self):
#         content = self.transcript_text.get("1.0", tk.END).strip()
#         if not content:
#             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
#             return
#         topic = self.logic.lecture_topic_var.get() or "無題の文字起こし"
#         title = f"{topic} - {datetime.now().strftime('%Y-%m-%d')}"
#         self.logic.export_to_google_doc(title, content)

#     def export_summary_to_gdoc(self):
#         content = self.summary_text.get("1.0", tk.END).strip()
#         if not content:
#             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
#             return
#         topic = self.logic.lecture_topic_var.get() or "無題の要約"
#         title = f"[要約] {topic} - {datetime.now().strftime('%Y-%m-%d')}"
#         self.logic.export_to_google_doc(title, content)

#     def export_all_to_gdoc(self):
#         transcription = self.transcript_text.get("1.0", tk.END).strip()
#         summary = self.summary_text.get("1.0", tk.END).strip()

#         if not transcription and not summary:
#             messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
#             return
            
#         content_plain = f"■■■ 文字起こし結果 ■■■\n\n{transcription}\n\n\n"
#         content_plain += f"■■■ 要約結果 ■■■\n\n{summary}"

#         topic = self.logic.lecture_topic_var.get() or "無題のセッション"
#         title = f"{topic} (文字起こしと要約) - {datetime.now().strftime('%Y-%m-%d')}"

#         self.logic.export_to_google_doc(title, content_plain)

#     def open_library(self):
#         LibraryWindow(self.root, self.logic, self)

#     def load_data_into_session(self, transcription, summary, topic):
#         self.transcript_text.delete("1.0", tk.END)
#         self.summary_text.delete("1.0", tk.END)

#         self.transcript_text.insert("1.0", transcription or "")
#         self.summary_text.insert("1.0", summary or "")

#         self.logic.lecture_topic_var.set(topic or "")
        
#         self.logic.transcribed_text_buffer = ""
#         self.logic.last_summary = ""
        
#         self.ui_queue.put(('show_info', "読み込み完了", "セッションの読み込みが完了しました。"))

#     def process_ui_queue(self):
#         try:
#             message = self.ui_queue.get_nowait()
#             msg_type, *payload = message
            
#             if msg_type == "update_status":
#                 self.status_label.config(text=payload[0])
            
#             elif msg_type == "show_error":
#                 messagebox.showerror(payload[0], payload[1])
            
#             elif msg_type == "show_info":
#                 messagebox.showinfo(payload[0], payload[1])
            
#             elif msg_type == "show_warning":
#                 messagebox.showwarning(payload[0], payload[1])

#             elif msg_type == "set_button_state":
#                 widget_name, state = payload
#                 widgets = {
#                     "toggle_button": self.toggle_button,
#                     "summarize_button": self.summarize_button,
#                     "full_summarize_button": self.full_summarize_button,
#                     "timer_start_button": self.timer_start_button,
#                     "timer_stop_button": self.timer_stop_button,
#                     "timer_spinbox": self.timer_spinbox,
#                     "create_quiz_button": self.create_quiz_button,
#                     "activate_discussion_button": self.activate_discussion_button,
#                 }
#                 if widget_name in widgets:
#                     widgets[widget_name].config(state=state)

#             elif msg_type == "set_button_text":
#                 widget_name, text = payload
#                 if widget_name == "toggle_button":
#                     self.toggle_button.config(text=text)

#             elif msg_type == "update_model_menus":
#                 models = payload[0]
#                 trans_menu = self.trans_model_menu["menu"]
#                 trans_menu.delete(0, "end")
#                 sum_menu = self.sum_model_menu["menu"]
#                 sum_menu.delete(0, "end")
#                 for model_name in sorted(models):
#                     trans_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.transcription_model_var.set(v))
#                     sum_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.summary_model_var.set(v))

#             elif msg_type == "append_transcription":
#                 transcript = payload[0]
#                 self.transcript_text.insert(tk.END, transcript + "\n\n")
#                 self.transcript_text.see(tk.END)
            
#             elif msg_type == "append_summary_marker":
#                 timestamp = payload[0]
#                 self.transcript_text.insert(tk.END, f"\n--- ▲ ここまでの内容を要約しました ({timestamp}) ▲ ---\n\n")
#                 self.transcript_text.see(tk.END)

#             elif msg_type == "update_summary":
#                 summary, topic, summary_type, timestamp = payload
#                 summary_title = "差分要約" if summary_type == "diff" else "全文要約"
#                 topic_header = f" (テーマ: {topic})" if topic else ""
#                 header = f"--- {timestamp} の{summary_title}{topic_header} ---\n"
                
#                 current_color = self.summary_colors[self.summary_color_index]
#                 tag_name = f"summary_tag_{timestamp.replace(':', '')}"
#                 self.summary_text.tag_configure(tag_name, foreground=current_color)
                
#                 if summary_type == "full":
#                     self.summary_text.delete("1.0", tk.END)

#                 self.summary_text.insert(tk.END, header + summary + "\n\n", (tag_name,))
#                 self.summary_color_index = (self.summary_color_index + 1) % len(self.summary_colors)
#                 self.summary_text.see(tk.END)

#             elif msg_type == "update_timer_display":
#                 self.timer_display_label.config(text=payload[0])

#             elif msg_type == "play_bell":
#                 self.root.bell()
            
#             elif msg_type == "display_quiz":
#                 quiz_text = payload[0]
#                 QuizWindow(self.root, quiz_text)

#             elif msg_type == "display_discussion_prompts":
#                 prompt_text = payload[0]
#                 DiscussionPromptWindow(self.root, prompt_text)
            
#             elif msg_type == "gdoc_import_completed":
#                 content = payload[0]
#                 if messagebox.askyesno("インポート確認", "現在の文字起こしと要約をクリアして、ドキュメントをインポートしますか？"):
#                     self.transcript_text.delete("1.0", tk.END)
#                     self.summary_text.delete("1.0", tk.END)
#                     self.transcript_text.insert("1.0", content)
#                     self.logic.transcribed_text_buffer = ""
#                     self.logic.last_summary = ""
#                     messagebox.showinfo("成功", "Googleドキュメントのインポートが完了しました。")

#             # ★★★ 新機能: キーワードポップアップ表示処理 ★★★
#             elif msg_type == "display_keyword_insights":
#                 for popup in self.keyword_popups:
#                     try:
#                         popup.destroy()
#                     except tk.TclError:
#                         pass
#                 self.keyword_popups.clear()

#                 keyword_data_list = payload[0]
                
#                 screen_width = self.root.winfo_screenwidth()
#                 screen_height = self.root.winfo_screenheight()
                
#                 x_offset = screen_width - 320 
#                 y_offset = screen_height - 150 

#                 for data in keyword_data_list:
#                     popup = KeywordPopup(
#                         self.root, 
#                         data['keyword'], 
#                         data['definition'],
#                         x_pos=x_offset,
#                         y_pos=y_offset
#                     )
#                     self.keyword_popups.append(popup)
                    
#                     y_offset -= (popup.winfo_height() + 10)

#             elif msg_type == "update_calendar_menu":
#                 calendar_data, default_id = payload[0]
#                 menu = self.calendar_menu["menu"]
#                 menu.delete(0, "end")

#                 found_default = False
#                 if calendar_data:
#                     for summary, cal_id in calendar_data:
#                         menu.add_command(label=summary, command=lambda v=cal_id: self.logic.selected_calendar_id_var.set(v))
#                         if default_id and cal_id == default_id:
#                             self.logic.selected_calendar_id_var.set(cal_id)
#                             found_default = True
                    
#                     if not found_default and calendar_data:
#                         self.logic.selected_calendar_id_var.set(calendar_data[0][1])
#                 else:
#                     self.logic.selected_calendar_id_var.set("")


#         except queue.Empty:
#             pass
#         finally:
#             self.root.after(100, self.process_ui_queue)

#     def on_closing(self):
#         self.logic.shutdown()
#         self.root.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TranscriberApp(root)
#     root.protocol("WM_DELETE_WINDOW", app.on_closing)
#     root.mainloop()




### main.py (キーワードモデル分離 修正版)

import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, filedialog, simpledialog
import queue
import system
import database as db
from ui_components import SearchFrame
from windows import LibraryWindow, QuizWindow, DiscussionPromptWindow, ExpandedViewWindow, GoogleDocImportWindow, KeywordPopup
from datetime import datetime

class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini リアルタイム文字起こし＆要約アプリ")
        self.root.geometry("1000x900")
        
        self.ui_queue = queue.Queue()
        self.logic = system.AppLogic(self.ui_queue)
        
        self.logic.selected_calendar_id_var = tk.StringVar()
        
        self.summary_colors = ["#0000FF", "#008000", "#8A2BE2", "#FF4500", "#DC143C"]
        self.summary_color_index = 0

        db.init_db()
        self.create_widgets()
        
        self.keyword_popups = []

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
        file_menu.add_command(label="Googleドキュメントからインポート...", command=self.import_from_gdoc)
        file_menu.add_command(label="YouTube動画から文字起こし...", command=self.import_from_youtube)
        file_menu.add_command(label="音声/動画ファイルから文字起こし...", command=self.import_media_file)
        file_menu.add_command(label="テキストファイルをインポート (.txt)", command=self.import_text_file)
        file_menu.add_separator()
        file_menu.add_command(label="文字起こし結果をエクスポート (.txt)", command=self.export_transcription)
        file_menu.add_command(label="要約結果をエクスポート (.txt)", command=self.export_summary)
        file_menu.add_separator()
        file_menu.add_command(label="文字起こしをGoogleドキュメントへエクスポート", command=self.export_transcription_to_gdoc)
        file_menu.add_command(label="要約をGoogleドキュメントへエクスポート", command=self.export_summary_to_gdoc)
        file_menu.add_command(label="文字起こしと要約をGoogleドキュメントへエクスポート", command=self.export_all_to_gdoc)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.on_closing)

        library_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ライブラリ", menu=library_menu)
        library_menu.add_command(label="現在のセッションをライブラリに保存", command=self.save_session_to_library)
        library_menu.add_command(label="ライブラリを開く", command=self.open_library)
        
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(7, weight=2)
        main_frame.grid_rowconfigure(8, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = tk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.status_label = tk.Label(top_frame, text="初期化中...", font=("Helvetica", 12))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_button = tk.Button(top_frame, text="文字起こしを停止", command=self.logic.toggle_transcription, font=("Helvetica", 10))
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        self.save_to_library_button = tk.Button(top_frame, text="ライブラリに保存", command=self.save_session_to_library, font=("Helvetica", 10))
        self.save_to_library_button.pack(side=tk.LEFT, padx=5)

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
        
        # ★★★ キーワードモデル用のUIを追加 ★★★
        keyword_model_label = tk.Label(model_settings_frame, text="キーワードモデル:", font=("Helvetica", 10))
        keyword_model_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.keyword_model_menu = tk.OptionMenu(model_settings_frame, self.logic.keyword_model_var, "")
        self.keyword_model_menu.config(font=("Helvetica", 9), anchor='w')
        self.keyword_model_menu.grid(row=2, column=1, sticky="ew", padx=5)

        calendar_frame = tk.LabelFrame(main_frame, text="カレンダー連携", padx=5, pady=5)
        calendar_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        calendar_frame.grid_columnconfigure(1, weight=1)

        self.refresh_calendars_button = tk.Button(calendar_frame, text="カレンダー更新", command=self.logic.fetch_calendar_list)
        self.refresh_calendars_button.grid(row=0, column=0, padx=5)
        
        self.calendar_menu = tk.OptionMenu(calendar_frame, self.logic.selected_calendar_id_var, "")
        self.calendar_menu.config(font=("Helvetica", 9), anchor='w')
        self.calendar_menu.grid(row=0, column=1, sticky="ew")

        self.fetch_current_event_button = tk.Button(calendar_frame, text="現在の授業を取得", command=self.logic.fetch_current_calendar_event)
        self.fetch_current_event_button.grid(row=0, column=2, padx=5)
        
        self.set_default_cal_button = tk.Button(calendar_frame, text="✔ デフォルトに設定", command=self.logic.set_default_calendar)
        self.set_default_cal_button.grid(row=0, column=3, padx=5)

        lecture_frame = tk.Frame(main_frame)
        lecture_frame.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        lecture_label = tk.Label(lecture_frame, text="講義テーマ/会議名:", font=("Helvetica", 10))
        lecture_label.pack(side=tk.LEFT, padx=(5, 5))
        self.lecture_topic_entry = tk.Entry(lecture_frame, font=("Helvetica", 10), textvariable=self.logic.lecture_topic_var)
        self.lecture_topic_entry.pack(fill=tk.X, expand=True)

        drive_folder_frame = tk.Frame(main_frame)
        drive_folder_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        drive_folder_label = tk.Label(drive_folder_frame, text="DriveフォルダURL / パス:", font=("Helvetica", 10))
        drive_folder_label.pack(side=tk.LEFT, padx=(5,5))
        self.drive_folder_entry = tk.Entry(drive_folder_frame, font=("Helvetica", 10), textvariable=self.logic.drive_folder_name_var)
        self.drive_folder_entry.pack(fill=tk.X, expand=True)

        transcript_container = tk.LabelFrame(main_frame, text="文字起こし結果", padx=5, pady=5)
        transcript_container.grid(row=7, column=0, sticky="nsew", pady=(5,0))
        transcript_container.grid_rowconfigure(1, weight=1)
        transcript_container.grid_columnconfigure(0, weight=1)
        
        self.transcript_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10))
        self.transcript_search = SearchFrame(transcript_container, self.transcript_text) 
        self.transcript_search.grid(row=0, column=0, sticky="ew")
        
        self.transcript_text.grid(row=1, column=0, sticky="nsew")

        expand_transcript_button = tk.Button(transcript_container, text="拡大", command=self.open_expanded_transcription, relief=tk.FLAT)
        expand_transcript_button.place(relx=1.0, rely=0, x=-5, y=-2, anchor="ne")

        summary_container = tk.LabelFrame(main_frame, text="要約結果", padx=5, pady=5)
        summary_container.grid(row=8, column=0, sticky="nsew", pady=(5, 0))
        summary_container.grid_rowconfigure(1, weight=1)
        summary_container.grid_columnconfigure(0, weight=1)
        
        self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10))
        self.summary_search = SearchFrame(summary_container, self.summary_text)
        self.summary_search.grid(row=0, column=0, sticky="ew")
        
        self.summary_text.grid(row=1, column=0, sticky="nsew")

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

    def import_from_gdoc(self):
        """Googleドキュメント検索用の専用ウィンドウを開く"""
        try:
            GoogleDocImportWindow(self.root, self.logic, self)
        except Exception as e:
            messagebox.showerror("エラー", f"インポートウィンドウを開けませんでした。\n{e}")
    
    def import_text_file(self, filepath):
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

    def export_transcription_to_gdoc(self):
        content = self.transcript_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
            return
        topic = self.logic.lecture_topic_var.get() or "無題の文字起こし"
        title = f"{topic} - {datetime.now().strftime('%Y-%m-%d')}"
        self.logic.export_to_google_doc(title, content)

    def export_summary_to_gdoc(self):
        content = self.summary_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
            return
        topic = self.logic.lecture_topic_var.get() or "無題の要約"
        title = f"[要約] {topic} - {datetime.now().strftime('%Y-%m-%d')}"
        self.logic.export_to_google_doc(title, content)

    def export_all_to_gdoc(self):
        transcription = self.transcript_text.get("1.0", tk.END).strip()
        summary = self.summary_text.get("1.0", tk.END).strip()

        if not transcription and not summary:
            messagebox.showwarning("エクスポート不可", "エクスポートする内容がありません。")
            return
            
        content_plain = f"■■■ 文字起こし結果 ■■■\n\n{transcription}\n\n\n"
        content_plain += f"■■■ 要約結果 ■■■\n\n{summary}"

        topic = self.logic.lecture_topic_var.get() or "無題のセッション"
        title = f"{topic} (文字起こしと要約) - {datetime.now().strftime('%Y-%m-%d')}"

        self.logic.export_to_google_doc(title, content_plain)

    def open_library(self):
        LibraryWindow(self.root, self.logic, self)

    def load_data_into_session(self, transcription, summary, topic):
        self.transcript_text.delete("1.0", tk.END)
        self.summary_text.delete("1.0", tk.END)

        self.transcript_text.insert("1.0", transcription or "")
        self.summary_text.insert("1.0", summary or "")

        self.logic.lecture_topic_var.set(topic or "")
        
        self.logic.transcribed_text_buffer = ""
        self.logic.last_summary = ""
        
        self.ui_queue.put(('show_info', "読み込み完了", "セッションの読み込みが完了しました。"))

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
                # ★★★ キーワードモデルメニューを更新する処理を追加 ★★★
                keyword_menu = self.keyword_model_menu["menu"]
                keyword_menu.delete(0, "end")
                for model_name in sorted(models):
                    trans_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.transcription_model_var.set(v))
                    sum_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.summary_model_var.set(v))
                    # ★★★ キーワードモデルメニューにコマンドを追加 ★★★
                    keyword_menu.add_command(label=model_name, command=lambda v=model_name: self.logic.keyword_model_var.set(v))

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
            
            elif msg_type == "gdoc_import_completed":
                content = payload[0]
                if messagebox.askyesno("インポート確認", "現在の文字起こしと要約をクリアして、ドキュメントをインポートしますか？"):
                    self.transcript_text.delete("1.0", tk.END)
                    self.summary_text.delete("1.0", tk.END)
                    self.transcript_text.insert("1.0", content)
                    self.logic.transcribed_text_buffer = ""
                    self.logic.last_summary = ""
                    messagebox.showinfo("成功", "Googleドキュメントのインポートが完了しました。")

            elif msg_type == "display_keyword_insights":
                for popup in self.keyword_popups:
                    try:
                        popup.destroy()
                    except tk.TclError:
                        pass
                self.keyword_popups.clear()

                keyword_data_list = payload[0]
                
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                x_offset = screen_width - 320 
                y_offset = screen_height - 150 

                for data in keyword_data_list:
                    popup = KeywordPopup(
                        self.root, 
                        data['keyword'], 
                        data['definition'],
                        x_pos=x_offset,
                        y_pos=y_offset
                    )
                    self.keyword_popups.append(popup)
                    
                    y_offset -= (popup.winfo_height() + 10)

            elif msg_type == "update_calendar_menu":
                calendar_data, default_id = payload[0]
                menu = self.calendar_menu["menu"]
                menu.delete(0, "end")

                found_default = False
                if calendar_data:
                    for summary, cal_id in calendar_data:
                        menu.add_command(label=summary, command=lambda v=cal_id: self.logic.selected_calendar_id_var.set(v))
                        if default_id and cal_id == default_id:
                            self.logic.selected_calendar_id_var.set(cal_id)
                            found_default = True
                    
                    if not found_default and calendar_data:
                        self.logic.selected_calendar_id_var.set(calendar_data[0][1])
                else:
                    self.logic.selected_calendar_id_var.set("")


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