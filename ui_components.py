### ui_components.py
### 検索バーなど、再利用可能なUIコンポーネントを定義します。

import tkinter as tk
from tkinter import Frame

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