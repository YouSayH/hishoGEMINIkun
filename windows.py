# ### windows.py (修正後)
# ### ライブラリ、クイズ、ヒントなど、独立したサブウィンドウを定義します。

# import tkinter as tk
# from tkinter import scrolledtext, messagebox, Listbox, Frame, Toplevel, simpledialog
# import database as db
# from ui_components import SearchFrame
# import threading # スレッド処理のためにインポート
# from datetime import datetime # 日付フォーマットのためにインポート


# class LibraryWindow(Toplevel):
#     """ライブラリ閲覧用の新しいウィンドウ"""
#     def __init__(self, master=None, logic=None, app=None):
#         super().__init__(master)
#         self.title("保存済みセッションライブラリ")
#         self.geometry("900x600")
#         self.logic = logic
#         self.app = app
#         self.transient(master)
#         self.grab_set()
#         self.current_search_keyword = None

#         main_frame = Frame(self, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_columnconfigure(1, weight=3)
#         main_frame.grid_columnconfigure(0, weight=1)
#         main_frame.grid_rowconfigure(0, weight=1)

#         # --- 左側パネル (検索 + リスト) ---
#         left_panel = Frame(main_frame)
#         left_panel.grid(row=0, column=0, sticky="nswe", padx=(0, 5))
#         left_panel.grid_rowconfigure(1, weight=1) # リストボックスが伸縮
#         left_panel.grid_columnconfigure(0, weight=1)

#         global_search_frame = tk.LabelFrame(left_panel, text="ライブラリ全体を検索", padx=5, pady=5)
#         global_search_frame.grid(row=0, column=0, sticky="ew")
#         global_search_frame.columnconfigure(0, weight=1)

#         self.global_search_entry = tk.Entry(global_search_frame)
#         self.global_search_entry.grid(row=0, column=0, sticky="ew")
#         self.global_search_entry.bind("<Return>", self.perform_global_search)

#         search_button = tk.Button(global_search_frame, text="検索", command=self.perform_global_search)
#         search_button.grid(row=0, column=1, padx=(5,2))

#         clear_button = tk.Button(global_search_frame, text="クリア", command=self.populate_sessions_list)
#         clear_button.grid(row=0, column=2)

#         list_frame = tk.LabelFrame(left_panel, text="セッションリスト", padx=5, pady=5)
#         list_frame.grid(row=1, column=0, sticky="nswe", pady=(5,0))
#         list_frame.grid_rowconfigure(0, weight=1)
#         list_frame.grid_columnconfigure(0, weight=1)

#         self.session_listbox = Listbox(list_frame, font=("Helvetica", 10))
#         self.session_listbox.grid(row=0, column=0, sticky="nswe")
#         self.session_listbox.bind("<<ListboxSelect>>", self.on_session_select)

#         # --- 右側パネル (詳細表示) ---
#         details_frame = Frame(main_frame)
#         details_frame.grid(row=0, column=1, sticky="nswe")
#         details_frame.grid_rowconfigure(2, weight=1)
#         details_frame.grid_rowconfigure(4, weight=1)
#         details_frame.grid_columnconfigure(0, weight=1)

#         button_frame = Frame(details_frame)
#         button_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))

#         tk.Button(button_frame, text="現在のセッションに読み込む", command=self.load_session_to_main).pack(side=tk.LEFT)
#         tk.Button(button_frame, text="選択したセッションを削除", command=self.delete_selected_session).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="リストを更新", command=self.populate_sessions_list).pack(side=tk.LEFT, padx=5)
#         self.create_quiz_button = tk.Button(button_frame, text="問題を作成", command=self.create_quiz_from_selection, state=tk.DISABLED, font=("Helvetica", 10, "bold"), fg="purple")
#         self.create_quiz_button.pack(side=tk.LEFT, padx=5)

#         transcript_container = tk.LabelFrame(details_frame, text="文字起こし結果", padx=5, pady=5)
#         transcript_container.grid(row=1, column=0, sticky="nsew")
#         transcript_container.grid_rowconfigure(1, weight=1)
#         transcript_container.grid_columnconfigure(0, weight=1)
#         self.transcription_text = scrolledtext.ScrolledText(transcript_container, wrap=tk.WORD, font=("Helvetica", 10), state='disabled', height=10)
#         self.transcription_text.grid(row=1, column=0, sticky="nsew")
#         self.transcription_search = SearchFrame(transcript_container, self.transcription_text)
#         self.transcription_search.grid(row=0, column=0, sticky="ew")

#         summary_container = tk.LabelFrame(details_frame, text="要約結果", padx=5, pady=5)
#         summary_container.grid(row=3, column=0, sticky="nsew", pady=(5,0))
#         summary_container.grid_rowconfigure(1, weight=1)
#         summary_container.grid_columnconfigure(0, weight=1)
#         self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD, font=("Helvetica", 10), state='disabled', height=5)
#         self.summary_text.grid(row=1, column=0, sticky="nsew")
#         self.summary_search = SearchFrame(summary_container, self.summary_text)
#         self.summary_search.grid(row=0, column=0, sticky="ew")

#         self.sessions = []
#         self.populate_sessions_list()

#     def perform_global_search(self, event=None):
#         keyword = self.global_search_entry.get()
#         if not keyword:
#             messagebox.showwarning("キーワードなし", "検索キーワードを入力してください。", parent=self)
#             return

#         self.current_search_keyword = keyword
#         found_sessions = db.search_sessions(keyword)
#         self._update_listbox(found_sessions)
#         self._clear_details()

#     def _update_listbox(self, sessions_data):
#         self.session_listbox.delete(0, tk.END)
#         self.sessions = sessions_data
#         for session in self.sessions:
#             display_text = f"{session['timestamp']} - {session['topic'] or '（テーマなし）'}"
#             self.session_listbox.insert(tk.END, display_text)

#     def _clear_details(self):
#         for widget in [self.transcription_text, self.summary_text]:
#             widget.config(state='normal')
#             widget.delete("1.0", tk.END)
#             widget.config(state='disabled')
#         self.transcription_search._clear_search()
#         self.summary_search._clear_search()
#         self.create_quiz_button.config(state=tk.DISABLED)

#     def populate_sessions_list(self):
#         self.current_search_keyword = None
#         self.global_search_entry.delete(0, tk.END)
#         all_sessions = db.get_all_sessions()
#         self._update_listbox(all_sessions)
#         self._clear_details()

#     def on_session_select(self, event):
#         selected_indices = self.session_listbox.curselection()
#         if not selected_indices: return

#         session_id = self.sessions[selected_indices[0]]['id']
#         session_data = db.get_session_by_id(session_id)

#         if session_data:
#             for widget, content in [(self.transcription_text, session_data['transcription']), (self.summary_text, session_data['summary'])]:
#                 widget.config(state='normal')
#                 widget.delete("1.0", tk.END)
#                 widget.insert(tk.END, content or "")
#                 widget.config(state='disabled')

#             self.create_quiz_button.config(state=tk.NORMAL if session_data['transcription'] else tk.DISABLED)

#             if self.current_search_keyword:
#                 self.transcription_search.execute_search(self.current_search_keyword)
#                 self.summary_search.execute_search(self.current_search_keyword)
#             else:
#                 self.transcription_search._clear_search()
#                 self.summary_search._clear_search()

#     def delete_selected_session(self):
#         selected_indices = self.session_listbox.curselection()
#         if not selected_indices:
#             messagebox.showwarning("選択なし", "削除するセッションを選択してください。", parent=self)
#             return

#         session_id = self.sessions[selected_indices[0]]['id']
#         if messagebox.askyesno("確認", "本当にこのセッションを削除しますか？\nこの操作は元に戻せません。", parent=self):
#             db.delete_session_by_id(session_id)
#             messagebox.showinfo("削除完了", "セッションを削除しました。", parent=self)
#             self.populate_sessions_list()

#     def create_quiz_from_selection(self):
#         if not self.logic:
#             messagebox.showerror("エラー", "システムロジックが利用できません。", parent=self)
#             return
#         transcription = self.transcription_text.get("1.0", tk.END).strip()
#         self.logic.generate_quiz(transcription)

#     def load_session_to_main(self):
#         """選択したセッションをメインウィンドウに読み込む"""
#         if not self.app:
#             messagebox.showerror("エラー", "アプリケーション本体にアクセスできません。", parent=self)
#             return

#         selected_indices = self.session_listbox.curselection()
#         if not selected_indices:
#             messagebox.showwarning("選択なし", "読み込むセッションを選択してください。", parent=self)
#             return

#         if messagebox.askyesno("確認", "現在の文字起こしと要約はクリアされます。\n選択したセッションを読み込みますか？", parent=self):
#             session_id = self.sessions[selected_indices[0]]['id']
#             session_data = db.get_session_by_id(session_id)

#             if session_data:
#                 self.app.load_data_into_session(
#                     session_data['transcription'],
#                     session_data['summary'],
#                     session_data['topic']
#                 )
#                 self.destroy()


# class QuizWindow(Toplevel):
#     def __init__(self, master, quiz_text):
#         super().__init__(master)
#         self.title("AI生成クイズ")
#         self.geometry("700x500")
#         self.transient(master)
#         self.grab_set()

#         main_frame = Frame(self, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_rowconfigure(0, weight=1)
#         main_frame.grid_columnconfigure(0, weight=1)

#         quiz_frame = tk.LabelFrame(main_frame, text="講義内容の理解度チェック", padx=5, pady=5)
#         quiz_frame.grid(row=0, column=0, sticky="nsew")
#         quiz_frame.grid_rowconfigure(0, weight=1)
#         quiz_frame.grid_columnconfigure(0, weight=1)

#         self.quiz_text_widget = scrolledtext.ScrolledText(quiz_frame, wrap=tk.WORD, font=("Helvetica", 10))
#         self.quiz_text_widget.grid(row=0, column=0, sticky="nsew")
#         self.quiz_text_widget.insert(tk.END, quiz_text)
#         self.quiz_text_widget.config(state='disabled')

#         button_frame = Frame(main_frame)
#         button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

#         tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.RIGHT, padx=5)

#     def copy_to_clipboard(self):
#         self.clipboard_clear()
#         self.clipboard_append(self.quiz_text_widget.get("1.0", tk.END))
#         messagebox.showinfo("コピー完了", "クイズの内容をクリップボードにコピーしました。", parent=self)

# class DiscussionPromptWindow(Toplevel):
#     def __init__(self, master, prompt_text):
#         super().__init__(master)
#         self.title("議論を活性化するためのヒント")
#         self.geometry("700x500")
#         self.transient(master)
#         self.grab_set()

#         main_frame = Frame(self, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_rowconfigure(0, weight=1)
#         main_frame.grid_columnconfigure(0, weight=1)

#         prompt_frame = tk.LabelFrame(main_frame, text="行き詰まった会議で使える言葉の例", padx=5, pady=5)
#         prompt_frame.grid(row=0, column=0, sticky="nsew")
#         prompt_frame.grid_rowconfigure(0, weight=1)
#         prompt_frame.grid_columnconfigure(0, weight=1)

#         self.prompt_text_widget = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, font=("Helvetica", 10))
#         self.prompt_text_widget.grid(row=0, column=0, sticky="nsew")
#         self.prompt_text_widget.insert(tk.END, prompt_text)
#         self.prompt_text_widget.config(state='disabled')

#         button_frame = Frame(main_frame)
#         button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

#         tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.RIGHT, padx=5)

#     def copy_to_clipboard(self):
#         self.clipboard_clear()
#         self.clipboard_append(self.prompt_text_widget.get("1.0", tk.END))
#         messagebox.showinfo("コピー完了", "ヒントの内容をクリップボードにコピーしました。", parent=self)

# class ExpandedViewWindow(Toplevel):
#     def __init__(self, master, title, content_text):
#         super().__init__(master)
#         self.title(title)
#         self.geometry("800x600")

#         main_frame = Frame(self, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_rowconfigure(0, weight=1)
#         main_frame.grid_columnconfigure(0, weight=1)

#         text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Helvetica", 12))
#         text_widget.grid(row=0, column=0, sticky="nsew")
#         text_widget.insert(tk.END, content_text)
#         text_widget.config(state='disabled')
#         self.content_text = content_text

#         button_frame = Frame(main_frame)
#         button_frame.grid(row=1, column=0, sticky="e", pady=(10, 0))

#         tk.Button(button_frame, text="クリップボードにコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="閉じる", command=self.destroy).pack(side=tk.LEFT, padx=5)

#     def copy_to_clipboard(self):
#         self.clipboard_clear()
#         self.clipboard_append(self.content_text)
#         messagebox.showinfo("コピー完了", "内容をクリップボードにコピーしました。", parent=self)


# class GoogleDocImportWindow(Toplevel):
#     """Google Driveからドキュメントを検索してインポートするためのウィンドウ"""
#     def __init__(self, master, logic, app):
#         super().__init__(master)
#         self.title("Googleドキュメントをインポート")
#         self.geometry("600x400")
#         self.transient(master)
#         self.grab_set()

#         self.logic = logic
#         self.app = app
#         self.doc_list = [] # (doc_name, doc_id) のタプルを保持

#         # --- UIの構築 ---
#         # メインフレーム：ウィンドウ内のすべての部品を配置する土台
#         main_frame = Frame(self, padx=10, pady=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#         main_frame.grid_rowconfigure(1, weight=1)
#         main_frame.grid_columnconfigure(0, weight=1)

#         # 検索フレーム：検索ボックスやボタンを配置
#         search_frame = Frame(main_frame)
#         search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
#         search_frame.grid_columnconfigure(1, weight=1)

#         tk.Label(search_frame, text="検索:").grid(row=0, column=0, padx=(0, 5))
#         self.search_entry = tk.Entry(search_frame)
#         self.search_entry.grid(row=0, column=1, sticky="ew")
#         self.search_entry.bind("<Return>", self.search_docs)

#         self.search_button = tk.Button(search_frame, text="検索", command=self.search_docs)
#         self.search_button.grid(row=0, column=2, padx=5)

#         self.recent_button = tk.Button(search_frame, text="最新一覧に戻る", command=self.fetch_recent_docs)
#         self.recent_button.grid(row=0, column=3)

#         # リストフレーム：検索結果の一覧を表示
#         list_frame = Frame(main_frame)
#         list_frame.grid(row=1, column=0, sticky="nsew")
#         list_frame.grid_rowconfigure(0, weight=1)
#         list_frame.grid_columnconfigure(0, weight=1)

#         self.listbox = Listbox(list_frame, font=("Helvetica", 10))
#         self.listbox.grid(row=0, column=0, sticky="nsew")

#         scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
#         scrollbar.grid(row=0, column=1, sticky="ns")
#         self.listbox.config(yscrollcommand=scrollbar.set)
#         self.listbox.bind("<Double-1>", self.on_import_click)

#         # ステータスラベル：現在の状態を表示
#         self.status_label = tk.Label(main_frame, text="ドキュメントを取得中...")
#         self.status_label.grid(row=2, column=0, sticky="ew", pady=(5,0))

#         # 下部ボタンフレーム：インポートボタンなどを配置
#         button_frame = Frame(main_frame, pady=5) # エラー回避のためpadyをシンプルな値に変更
#         button_frame.grid(row=3, column=0, sticky="e")

#         # ★★★ ここで self.import_button を確実に定義します ★★★
#         self.import_button = tk.Button(button_frame, text="選択してインポート", command=self.on_import_click, state=tk.DISABLED)
#         self.import_button.pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

#         # --- 初期データ読み込み ---
#         # すべてのUI部品を完全に作成し終えた後で、最後にこのメソッドを呼び出す
#         self.fetch_recent_docs()

#     def _fetch_task(self, query=None):
#         """別スレッドでドキュメントリストを取得するタスク"""
#         try:
#             files = self.logic.fetch_google_docs(query=query)
#             # UIの更新はメインスレッドで行う
#             self.after(0, self.update_listbox, files)
#         except Exception as e:
#             self.after(0, messagebox.showerror, "取得エラー", f"ドキュメントの取得に失敗しました。\n{e}", parent=self)
#             self.after(0, self.destroy)

#     def fetch_recent_docs(self, event=None):
#         """最近使用したドキュメントを取得する処理"""
#         self.search_entry.delete(0, tk.END)
#         self.status_label.config(text="最近使用したドキュメントを取得中...")
#         self.import_button.config(state=tk.DISABLED)
#         self.listbox.delete(0, tk.END)
#         # ネットワーク処理は別スレッドで行い、UIが固まるのを防ぐ
#         threading.Thread(target=self._fetch_task, daemon=True).start()

#     def search_docs(self, event=None):
#         """入力されたキーワードでドキュメントを検索する処理"""
#         query = self.search_entry.get()
#         if not query:
#             messagebox.showwarning("入力エラー", "検索キーワードを入力してください。", parent=self)
#             return
#         self.status_label.config(text=f"「{query}」で検索中...")
#         self.import_button.config(state=tk.DISABLED)
#         self.listbox.delete(0, tk.END)
#         threading.Thread(target=self._fetch_task, args=(query,), daemon=True).start()

#     def update_listbox(self, files):
#         """取得したファイルリストでリストボックスを更新する処理"""
#         self.listbox.delete(0, tk.END)
#         self.doc_list = []
#         if files:
#             for f in files:
#                 mod_time_str = f.get('modifiedTime', '')
#                 try:
#                     # APIから返される日付文字列をPythonのdatetimeオブジェクトに変換し、見やすいようにフォーマット
#                     mod_time = datetime.fromisoformat(mod_time_str.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
#                 except (ValueError, TypeError):
#                     mod_time = "不明な日時"

#                 display_text = f"[{mod_time}] {f.get('name', '名前なし')}"
#                 self.listbox.insert(tk.END, display_text)
#                 self.doc_list.append((f.get('name'), f.get('id')))

#             self.status_label.config(text=f"{len(files)}件のドキュメントが見つかりました。")
#             self.import_button.config(state=tk.NORMAL)
#         else:
#             self.status_label.config(text="対象のドキュメントは見つかりませんでした。")
#             self.import_button.config(state=tk.DISABLED)

#     def on_import_click(self, event=None):
#         """「選択してインポート」ボタンが押されたときの処理"""
#         selected_indices = self.listbox.curselection()
#         if not selected_indices:
#             messagebox.showwarning("選択エラー", "インポートするドキュメントを選択してください。", parent=self)
#             return

#         selected_doc = self.doc_list[selected_indices[0]]
#         doc_id = selected_doc[1]

#         if doc_id:
#             # main.pyのロジックを呼び出してインポートを実行
#             self.app.logic.import_from_google_doc(doc_id=doc_id)
#             self.destroy() # 処理後にウィンドウを閉じる
#         else:
#             messagebox.showerror("インポートエラー", "選択されたドキュメントのIDが見つかりません。", parent=self)



### windows.py (キーワードポップアップ機能 追加版)
### ライブラリ、クイズ、ヒントなど、独立したサブウィンドウを定義します。

import tkinter as tk
from tkinter import scrolledtext, messagebox, Listbox, Frame, Toplevel, simpledialog
import database as db
from ui_components import SearchFrame
import threading # スレッド処理のためにインポート
from datetime import datetime # 日付フォーマットのためにインポート


class LibraryWindow(Toplevel):
    """ライブラリ閲覧用の新しいウィンドウ"""
    def __init__(self, master=None, logic=None, app=None):
        super().__init__(master)
        self.title("保存済みセッションライブラリ")
        self.geometry("900x600")
        self.logic = logic
        self.app = app
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

        tk.Button(button_frame, text="現在のセッションに読み込む", command=self.load_session_to_main).pack(side=tk.LEFT)
        tk.Button(button_frame, text="選択したセッションを削除", command=self.delete_selected_session).pack(side=tk.LEFT, padx=5)
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

    def load_session_to_main(self):
        """選択したセッションをメインウィンドウに読み込む"""
        if not self.app:
            messagebox.showerror("エラー", "アプリケーション本体にアクセスできません。", parent=self)
            return

        selected_indices = self.session_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("選択なし", "読み込むセッションを選択してください。", parent=self)
            return

        if messagebox.askyesno("確認", "現在の文字起こしと要約はクリアされます。\n選択したセッションを読み込みますか？", parent=self):
            session_id = self.sessions[selected_indices[0]]['id']
            session_data = db.get_session_by_id(session_id)

            if session_data:
                self.app.load_data_into_session(
                    session_data['transcription'],
                    session_data['summary'],
                    session_data['topic']
                )
                self.destroy()


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


class GoogleDocImportWindow(Toplevel):
    """Google Driveからドキュメントを検索してインポートするためのウィンドウ"""
    def __init__(self, master, logic, app):
        super().__init__(master)
        self.title("Googleドキュメントをインポート")
        self.geometry("600x400")
        self.transient(master)
        self.grab_set()

        self.logic = logic
        self.app = app
        self.doc_list = [] # (doc_name, doc_id) のタプルを保持

        # --- UIの構築 ---
        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        search_frame = Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(search_frame, text="検索:").grid(row=0, column=0, padx=(0, 5))
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<Return>", self.search_docs)

        self.search_button = tk.Button(search_frame, text="検索", command=self.search_docs)
        self.search_button.grid(row=0, column=2, padx=5)

        self.recent_button = tk.Button(search_frame, text="最新一覧に戻る", command=self.fetch_recent_docs)
        self.recent_button.grid(row=0, column=3)

        list_frame = Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.listbox = Listbox(list_frame, font=("Helvetica", 10))
        self.listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind("<Double-1>", self.on_import_click)

        self.status_label = tk.Label(main_frame, text="ドキュメントを取得中...")
        self.status_label.grid(row=2, column=0, sticky="ew", pady=(5,0))

        button_frame = Frame(main_frame, pady=5)
        button_frame.grid(row=3, column=0, sticky="e")

        self.import_button = tk.Button(button_frame, text="選択してインポート", command=self.on_import_click, state=tk.DISABLED)
        self.import_button.pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

        self.fetch_recent_docs()

    def _fetch_task(self, query=None):
        """別スレッドでドキュメントリストを取得するタスク"""
        try:
            files = self.logic.fetch_google_docs(query=query)
            self.after(0, self.update_listbox, files)
        except Exception as e:
            self.after(0, messagebox.showerror, "取得エラー", f"ドキュメントの取得に失敗しました。\n{e}", parent=self)
            self.after(0, self.destroy)

    def fetch_recent_docs(self, event=None):
        """最近使用したドキュメントを取得する処理"""
        self.search_entry.delete(0, tk.END)
        self.status_label.config(text="最近使用したドキュメントを取得中...")
        self.import_button.config(state=tk.DISABLED)
        self.listbox.delete(0, tk.END)
        threading.Thread(target=self._fetch_task, daemon=True).start()

    def search_docs(self, event=None):
        """入力されたキーワードでドキュメントを検索する処理"""
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("入力エラー", "検索キーワードを入力してください。", parent=self)
            return
        self.status_label.config(text=f"「{query}」で検索中...")
        self.import_button.config(state=tk.DISABLED)
        self.listbox.delete(0, tk.END)
        threading.Thread(target=self._fetch_task, args=(query,), daemon=True).start()

    def update_listbox(self, files):
        """取得したファイルリストでリストボックスを更新する処理"""
        self.listbox.delete(0, tk.END)
        self.doc_list = []
        if files:
            for f in files:
                mod_time_str = f.get('modifiedTime', '')
                try:
                    mod_time = datetime.fromisoformat(mod_time_str.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    mod_time = "不明な日時"

                display_text = f"[{mod_time}] {f.get('name', '名前なし')}"
                self.listbox.insert(tk.END, display_text)
                self.doc_list.append((f.get('name'), f.get('id')))

            self.status_label.config(text=f"{len(files)}件のドキュメントが見つかりました。")
            self.import_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="対象のドキュメントは見つかりませんでした。")
            self.import_button.config(state=tk.DISABLED)

    def on_import_click(self, event=None):
        """「選択してインポート」ボタンが押されたときの処理"""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("選択エラー", "インポートするドキュメントを選択してください。", parent=self)
            return

        selected_doc = self.doc_list[selected_indices[0]]
        doc_id = selected_doc[1]

        if doc_id:
            self.app.logic.import_from_google_doc(doc_id=doc_id)
            self.destroy()
        else:
            messagebox.showerror("インポートエラー", "選択されたドキュメントのIDが見つかりません。", parent=self)

# ★★★ 新機能: キーワードポップアップウィンドウ ★★★
class KeywordPopup(Toplevel):
    """
    キーワードとその概要を一定時間表示するポップアップウィンドウ。
    マウスが乗るとタイマーが停止し、離れると再開する。
    """
    def __init__(self, master, keyword, definition, x_pos, y_pos, duration=10000):
        super().__init__(master)
        self.duration = duration
        self.close_timer = None

        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.config(bg="#FFFFE0", relief="solid", borderwidth=1)

        frame = Frame(self, bg=self.cget('bg'), padx=10, pady=5)
        frame.pack(expand=True, fill=tk.BOTH)

        keyword_label = tk.Label(frame, text=keyword, font=("Helvetica", 10, "bold"), bg=self.cget('bg'))
        keyword_label.pack(anchor="w")

        definition_label = tk.Label(frame, text=definition, wraplength=250, justify=tk.LEFT, font=("Helvetica", 9), bg=self.cget('bg'))
        definition_label.pack(anchor="w", pady=(2, 0))

        self.update_idletasks()
        self.geometry(f"+{x_pos}+{y_pos}")

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        for widget in frame.winfo_children():
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            
        close_button = tk.Button(frame, text="×", command=self.destroy, bg="lightgray", relief=tk.FLAT, font=("Arial", 8), padx=0, pady=0, borderwidth=0, highlightthickness=0)
        close_button.place(relx=1.0, rely=0, anchor="ne")

        self.start_close_timer()

    def start_close_timer(self):
        """ウィンドウを閉じるタイマーを開始または再開する"""
        if self.close_timer:
            self.after_cancel(self.close_timer)
        self.close_timer = self.after(self.duration, self.destroy)

    def on_enter(self, event=None):
        """マウスがウィンドウ内に入ったときにタイマーを停止"""
        if self.close_timer:
            self.after_cancel(self.close_timer)
            self.close_timer = None

    def on_leave(self, event=None):
        """マウスがウィンドウから出たときにタイマーを再開"""
        self.start_close_timer()