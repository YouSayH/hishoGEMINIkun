# ### system.py (修正済み・全体コード)

# import tkinter as tk
# import threading
# import queue
# import os
# from datetime import datetime, timedelta
# import time
# from datetime import timezone
# import io 
# import re 

# import google.generativeai as genai
# import sounddevice as sd
# from scipy.io.wavfile import write
# import numpy as np
# import moviepy.editor as mp
# from yt_dlp import YoutubeDL
# import database as db

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# from googleapiclient.errors import HttpError

# # --- 1. 初期設定 (環境変数からAPIキーを読み込む) ---
# API_KEY = os.environ.get("GEMINI_API_KEY")

# # 録音設定
# SAMPLE_RATE = 44100
# CHANNELS = 1
# RECORDING_DIR = "recordings"

# # Geminiモデルの基本設定
# generation_config = {"temperature": 0.5}

# # Google API連携設定 (スコープを更新)
# SCOPES = [
#     'https://www.googleapis.com/auth/drive.file', 
#     'https://www.googleapis.com/auth/drive.readonly',
#     'https://www.googleapis.com/auth/calendar.readonly'
# ]
# TOKEN_FILE = 'token.json'
# DEFAULT_CALENDAR_CONFIG_FILE = "calendar_config.txt"


# class AppLogic:
#     def __init__(self, ui_queue):
#         self.ui_queue = ui_queue
#         self.is_recording = False
#         self.audio_queue = queue.Queue()
#         self.transcribed_text_buffer = ""
#         self.last_summary = ""
#         self.stream = None
#         self.credentials = None
        
#         self.interval_sec_var = tk.IntVar(value=20)
#         self.transcription_model_var = tk.StringVar()
#         self.summary_model_var = tk.StringVar()
#         self.lecture_topic_var = tk.StringVar()
#         self.timer_initial_minutes_var = tk.IntVar(value=10)
#         self.drive_folder_name_var = tk.StringVar(value="https://drive.google.com/drive/folders/107Lum5AGu24Awbk3y3-1-QaGR2GEK4mS?usp=drive_link")

#         self.available_models = []
#         self.transcription_model = None
#         self.summary_model = None
        
#         self.transcription_model_var.trace_add("write", self.on_model_change)
#         self.summary_model_var.trace_add("write", self.on_model_change)
        
#         self.timer_running = False
#         self.timer_seconds_left = 0
#         self.timer_job = None

#         os.makedirs(RECORDING_DIR, exist_ok=True)
#         self.load_default_calendar()

#     def load_default_calendar(self):
#         """アプリ起動時に自動でカレンダーリストの取得を開始する"""
#         self.fetch_calendar_list()

#     def set_default_calendar(self):
#         """現在選択中のカレンダーIDを設定ファイルに書き込む"""
#         calendar_id = self.selected_calendar_id_var.get()
#         if not calendar_id:
#             self.ui_queue.put(('show_warning', "カレンダー未選択", "ドロップダウンからカレンダーを選択してください。"))
#             return
#         try:
#             with open(DEFAULT_CALENDAR_CONFIG_FILE, "w", encoding="utf-8") as f:
#                 f.write(calendar_id)
#             self.ui_queue.put(('show_info', "デフォルト設定完了", "選択したカレンダーを既定値として保存しました。"))
#         except Exception as e:
#             self.ui_queue.put(('show_error', "保存エラー", f"デフォルト設定の保存に失敗しました。\n{e}"))

#     def initialize_gemini(self):
#         if not API_KEY:
#             self.ui_queue.put(('update_status', "エラー: 環境変数が設定されていません。"))
#             self.ui_queue.put(('show_error', "APIキーエラー", "環境変数 'GEMINI_API_KEY' が設定されていません。"))
#             self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))
#             return False
        
#         try:
#             genai.configure(api_key=API_KEY)
#             self.ui_queue.put(('update_status', "🔄 利用可能なモデルを取得中..."))
            
#             self.available_models = [
#                 m.name for m in genai.list_models()
#                 if 'generateContent' in m.supported_generation_methods
#             ]
            
#             if not self.available_models:
#                 self.ui_queue.put(('show_error', "モデル取得エラー", "利用可能なモデルが見つかりませんでした。"))
#                 self.ui_queue.put(('update_status', "❌ モデル取得エラー"))
#                 return False

#             self.ui_queue.put(('update_model_menus', self.available_models))

#             if any(m.startswith("models/gemini-2.0-flash-lite") for m in self.available_models):
#                 self.transcription_model_var.set(next(m for m in self.available_models if m.startswith("models/gemini-2.0-flash-lite")))
#             elif self.available_models:
#                 self.transcription_model_var.set(self.available_models[0])
            
#             if any(m.startswith("models/gemini-2.5-pro-exp-03-25") for m in self.available_models):
#                 self.summary_model_var.set(next(m for m in self.available_models if m.startswith("models/gemini-2.5-pro-exp-03-25")))
#             elif self.available_models:
#                 self.summary_model_var.set(self.available_models[0])

#             self.ui_queue.put(('update_status', "✅ モデルの準備ができました"))

#         except Exception as e:
#             self.ui_queue.put(('show_error', "API初期化エラー", f"APIの初期化中にエラーが発生しました。\n{e}"))
#             self.ui_queue.put(('update_status', "❌ API初期化エラー"))
#             return False
#         return True

#     def on_model_change(self, *args):
#         if not self.transcription_model_var.get() or not self.summary_model_var.get():
#             return
#         self.ui_queue.put(('update_status', "🔄 モデルを切り替え中..."))
#         try:
#             trans_model_name = self.transcription_model_var.get()
#             sum_model_name = self.summary_model_var.get()
#             self.transcription_model = genai.GenerativeModel(model_name=trans_model_name)
#             self.summary_model = genai.GenerativeModel(model_name=sum_model_name)
            
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#         except Exception as e:
#             self.ui_queue.put(('show_error', "モデル設定エラー", f"モデルの読み込みに失敗しました。\nエラー: {e}"))
#             self.ui_queue.put(('update_status', "❌ モデル設定エラー"))
#             self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
#             self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))

#     def toggle_transcription(self):
#         if self.stream is None:
#             self.ui_queue.put(('show_error', "エラー", "オーディオストリームが初期化されていません。"))
#             return

#         if self.is_recording:
#             self.stream.stop()
#             self.is_recording = False
#             self.ui_queue.put(('update_status', "⏸️ 一時停止中"))
#             self.ui_queue.put(('set_button_text', 'toggle_button', "文字起こしを再開"))
#         else:
#             self.stream.start()
#             self.is_recording = True
#             self.ui_queue.put(('update_status', "🎙️ 録音中..."))
#             self.ui_queue.put(('set_button_text', 'toggle_button', "文字起こしを停止"))

#     def start_recording(self):
#         if self.is_recording:
#             return
#         def callback(indata, frames, time, status):
#             if status:
#                 print(status)
#             self.audio_queue.put(indata.copy())
#         try:
#             self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback)
#             self.stream.start()
#             self.is_recording = True
#             self.ui_queue.put(('update_status', "🎙️ 録音中..."))
#         except Exception as e:
#             self.ui_queue.put(('show_error', "マイクエラー", f"マイクの起動に失敗しました。\nエラー: {e}"))
#             self.ui_queue.put(('update_status', "❌ マイクエラー"))

#     def periodic_transcribe(self):
#         if self.is_recording and not self.audio_queue.empty():
#             frames_to_process = []
#             while not self.audio_queue.empty():
#                 try:
#                     frames_to_process.append(self.audio_queue.get_nowait())
#                 except queue.Empty:
#                     break
#             if frames_to_process:
#                 current_interval_sec = self.interval_sec_var.get()
#                 self.ui_queue.put(('update_status', f"🔄 {current_interval_sec}秒分の音声を処理中..."))
#                 thread = threading.Thread(target=self.transcribe_task, args=(frames_to_process,))
#                 thread.start()

#     def transcribe_task(self, frames):
#         try:
#             recording_data = np.concatenate(frames, axis=0)
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filepath = os.path.join(RECORDING_DIR, f"rec_temp_{timestamp}.wav")
#             write(filepath, SAMPLE_RATE, recording_data)
#             audio_file = genai.upload_file(path=filepath)
#             lecture_topic = self.lecture_topic_var.get()
#             prompt = f"""これは「{lecture_topic}」についての講義または会議です。専門用語や文脈を考慮して、この音声ファイルを日本語で正確に文字起こししてください。""" if lecture_topic else """この音声ファイルを日本語で正確に文字起こししてください。"""
#             response = self.transcription_model.generate_content([prompt, audio_file], request_options={"timeout": 600})
#             try:
#                 transcript = response.text
#                 self.ui_queue.put(("append_transcription", transcript))
#                 self.transcribed_text_buffer += transcript + "\n"
#                 # ★★★ 新機能: キーワード抽出をトリガー ★★★
#                 self.generate_keyword_insights(transcript)
#             except ValueError:
#                 self.ui_queue.put(("show_warning", "応答ブロック", "AIからの応答が安全機能（著作権保護など）によりブロックされました。\n入力音声の内容を確認してください。"))
#                 self.ui_queue.put(("append_transcription", "（AIからの応答がブロックされました）"))
#             if self.is_recording:
#                 self.ui_queue.put(('update_status', "🎙️ 録音中..."))
#         except Exception as e:
#             self.ui_queue.put(("show_error", "文字起こしエラー", f"{e}"))
#         finally:
#             if 'audio_file' in locals() and audio_file:
#                 try: genai.delete_file(audio_file.name)
#                 except Exception as e: print(f"アップロードしたファイルの削除に失敗: {e}")
#             if 'filepath' in locals() and os.path.exists(filepath):
#                 try: os.remove(filepath)
#                 except Exception as e: print(f"一時ファイルの削除に失敗: {e}")

#     def generate_keyword_insights(self, text):
#         """文字起こしテキストからキーワードを抽出し、概要を生成するタスクを開始する"""
#         if not text.strip():
#             return
#         thread = threading.Thread(target=self._keyword_insights_task, args=(text,))
#         thread.start()

#     def _keyword_insights_task(self, text):
#         """キーワード抽出と概要生成を実行するバックグラウンドタスク"""
#         try:
#             prompt = f"""以下の文章は、ある会議または講義の文字起こしです。
# この中で、参加者が知らない可能性のある重要な専門用語や固有名詞を6つまで特定してください。
# そして、それぞれの用語について、文脈に沿った非常に簡潔な説明（30字程度）を生成してください。

# 出力形式は必ず「用語:説明」の形式で、用語ごとに改行してください。
# 例：
# Gemini: Googleが開発した大規模言語モデル。
# Tkinter: Pythonの標準GUIツールキット。

# もし適切な用語が見つからない場合は、何も出力しないでください。

# 【文字起こし文章】
# ---
# {text}
# ---
# """
#             response = self.transcription_model.generate_content(prompt, generation_config={"temperature": 0.2})
            
#             try:
#                 insights_text = response.text
#                 keyword_data = []
#                 for line in insights_text.strip().split('\n'):
#                     if ':' in line:
#                         parts = line.split(':', 1)
#                         keyword = parts[0].strip()
#                         definition = parts[1].strip()
#                         if keyword and definition:
#                             keyword_data.append({'keyword': keyword, 'definition': definition})
                
#                 if keyword_data:
#                     self.ui_queue.put(('display_keyword_insights', keyword_data))

#             except ValueError:
#                 pass # 安全性設定でブロックされた場合は何もしない
#             except Exception as e:
#                 print(f"キーワードのパース中にエラー: {e}")

#         except Exception as e:
#             print(f"キーワード抽出APIの呼び出し中にエラー: {e}")


#     def process_youtube_url(self, url):
#         thread = threading.Thread(target=self._youtube_task, args=(url,))
#         thread.start()

#     def _youtube_task(self, url):
#         self.ui_queue.put(('update_status', "▶️ YouTube動画情報を取得中..."))
#         final_wav_path = None
#         original_file_path = None
#         try:
#             if not self.lecture_topic_var.get():
#                 try:
#                     with YoutubeDL({'quiet': True}) as ydl:
#                         info = ydl.extract_info(url, download=False)
#                         self.lecture_topic_var.set(info.get('title', ''))
#                 except Exception as e:
#                     print(f"YouTubeのタイトル取得に失敗: {e}")
#             self.ui_queue.put(('update_status', "▶️ 音声データをダウンロード中..."))
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             base_filename = f"yt_temp_{timestamp}"
#             output_template = os.path.join(RECORDING_DIR, f"{base_filename}.%(ext)s")
#             final_wav_path = os.path.join(RECORDING_DIR, f"{base_filename}.wav")
#             ydl_opts = {
#                 'format': 'bestaudio/best', 'outtmpl': output_template,
#                 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}], 'quiet': True,
#             }
#             with YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(url, download=True)
#                 original_file_path = ydl.prepare_filename(info)
#                 final_wav_path = os.path.splitext(original_file_path)[0] + ".wav"
#             if not os.path.exists(final_wav_path):
#                  raise FileNotFoundError("WAVへの変換に失敗しました。ffmpegが正しくインストールされ、パスが通っているか確認してください。")
#             self._process_and_transcribe_file(final_wav_path)
#         except Exception as e:
#             self.ui_queue.put(("show_error", "YouTube処理エラー", f"YouTube動画の処理中にエラーが発生しました。\nURLが正しいか確認してください。\n{e}"))
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#         finally:
#             if final_wav_path and os.path.exists(final_wav_path):
#                 try: os.remove(final_wav_path)
#                 except Exception as e: print(f"一時WAVファイルの削除に失敗: {e}")
#             if original_file_path and os.path.exists(original_file_path):
#                 try: os.remove(original_file_path)
#                 except Exception as e: print(f"一時ファイル（元）の削除に失敗: {e}")

#     def process_media_file(self, filepath):
#         thread = threading.Thread(target=self._process_and_transcribe_file, args=(filepath,))
#         thread.start()

#     def _process_and_transcribe_file(self, filepath):
#         self.ui_queue.put(('update_status', f"ファイルを処理中: {os.path.basename(filepath)}"))
#         audio_path_to_process = None
#         temp_audio_path = None
#         api_audio_file = None
#         try:
#             file_ext = os.path.splitext(filepath)[1].lower()
#             if file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
#                 self.ui_queue.put(('update_status', "動画から音声を抽出中..."))
#                 video = mp.VideoFileClip(filepath)
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 temp_audio_path = os.path.join(RECORDING_DIR, f"temp_audio_from_video_{timestamp}.wav")
#                 video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
#                 audio_path_to_process = temp_audio_path
#             else:
#                 audio_path_to_process = filepath
#             self.ui_queue.put(('update_status', "ファイルをアップロード中..."))
#             api_audio_file = genai.upload_file(path=audio_path_to_process)
#             self.ui_queue.put(('update_status', "AIが文字起こしを実行中..."))
#             prompt = """この音声ファイルを日本語で正確に文字起こししてください。"""
#             response = self.transcription_model.generate_content([prompt, api_audio_file], request_options={"timeout": 1800})
#             try:
#                 transcript = response.text
#                 self.ui_queue.put(("append_transcription", transcript))
#             except ValueError:
#                 self.ui_queue.put(("show_warning", "応答ブロック", "AIからの応答が安全機能によりブロックされました。"))
#                 self.ui_queue.put(("append_transcription", "（ファイルからの文字起こし中にAIからの応答がブロックされました）"))
#         except Exception as e:
#             self.ui_queue.put(("show_error", "ファイル処理エラー", f"ファイルの処理中にエラーが発生しました。\n{e}"))
#         finally:
#             if api_audio_file:
#                 try: genai.delete_file(api_audio_file.name)
#                 except Exception as e: print(f"アップロードしたファイルの削除に失敗: {e}")
#             if temp_audio_path and os.path.exists(temp_audio_path):
#                 try: os.remove(temp_audio_path)
#                 except Exception as e: print(f"一時音声ファイルの削除に失敗: {e}")
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))

#     def on_summarize_click(self):
#         if not self.transcribed_text_buffer.strip():
#             self.ui_queue.put(('show_warning', "テキストなし", "要約対象の新しい文字起こしテキストがありません。"))
#             return
#         self.ui_queue.put(('update_status', "🔄 差分を要約中..."))
#         self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
#         self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
#         text_to_summarize = self.transcribed_text_buffer
#         self.transcribed_text_buffer = ""
#         thread = threading.Thread(target=self.summarize_task, args=(text_to_summarize, self.last_summary, "diff"))
#         thread.start()

#     def on_full_summarize_click(self, full_transcript):
#         if not full_transcript.strip():
#             self.ui_queue.put(('show_warning', "テキストなし", "要約対象の文字起こしテキストがありません。"))
#             return
#         self.ui_queue.put(('update_status', "🔄 全文を要約中..."))
#         self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
#         self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
#         self.transcribed_text_buffer = ""
#         thread = threading.Thread(target=self.summarize_task, args=(full_transcript, "", "full"))
#         thread.start()

#     def summarize_task(self, transcript, last_summary_context, summary_type):
#         try:
#             lecture_topic = self.lecture_topic_var.get()
#             context_prompt = f"これは「{lecture_topic}」に関する会議の議事録です。" if lecture_topic else "これは会議の議事録です。"
            
#             if summary_type == "diff" and last_summary_context:
#                 prompt = f"""あなたは優秀なアシスタントです。{context_prompt}

# 【前回までの会話の要約】
# {last_summary_context}
# ---
# 【今回新たに文字起こしされた会話】
# {transcript}
# ---
# 【指示】
# 前回までの文脈と会議(講義や動画)のテーマを考慮し、「今回新たに文字起こしされた会話」の内容を要約してください。(文字お越しが正確ではない可能性も考慮して要約してください。)"""
#             else:
#                 prompt = f"""あなたは優秀なアシスタントです。{context_prompt}
# 以下の議事録全体を、重要なポイントがわかるように要約してください。(文字お越しが正確ではない可能性も考慮して要約してください。)

# ---
# {transcript}"""

#             response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
#             try:
#                 summary = response.text
#                 timestamp = datetime.now().strftime("%H:%M:%S")
#                 self.ui_queue.put(("update_summary", summary, lecture_topic, summary_type, timestamp))
#                 self.ui_queue.put(("append_summary_marker", timestamp))
#                 self.last_summary += "\n" + summary
#             except ValueError:
#                  self.ui_queue.put(("show_warning", "応答ブロック", "要約の生成中にAIからの応答が安全機能によりブロックされました。"))
#             status = "🎙️ 録音中..." if self.is_recording else "⏸️ 一時停止中"
#             self.ui_queue.put(('update_status', status))
#         except Exception as e:
#             self.ui_queue.put(("show_error", "要約エラー", f"{e}"))
#             if summary_type == "diff":
#                 self.transcribed_text_buffer = transcript + self.transcribed_text_buffer
#         finally:
#             self.ui_queue.put(('set_button_state', 'summarize_button', 'normal'))
#             self.ui_queue.put(('set_button_state', 'full_summarize_button', 'normal'))

#     def generate_quiz(self, full_transcript):
#         if not full_transcript.strip():
#             self.ui_queue.put(('show_warning', "テキストなし", "問題を作成するための文字起こしテキストがありません。"))
#             return
#         self.ui_queue.put(('update_status', "🤖 AIが問題を作成中..."))
#         self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
#         thread = threading.Thread(target=self.quiz_task, args=(full_transcript,))
#         thread.start()
        
#     def quiz_task(self, transcript):
#         try:
#             lecture_topic = self.lecture_topic_var.get()
#             context_prompt = f"「{lecture_topic}」に関する" if lecture_topic else ""
#             prompt = f"""あなたは経験豊富な教師です。
# 以下の{context_prompt}講義または会議の文字起こし内容を読んで、受講者の理解度を確認するための問題を3問作成してください。
# 問題形式は、選択式問題、穴埋め問題、記述式問題などをバランス良く含めてください。
# 問題と合わせて、明確な解答も生成してください。

# 【文字起こし】
# ---
# {transcript}
# ---
# """
#             response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
#             try:
#                 self.ui_queue.put(("display_quiz", response.text))
#             except ValueError:
#                 self.ui_queue.put(("show_warning", "応答ブロック", "クイズの生成中にAIからの応答が安全機能によりブロックされました。"))
#         except Exception as e:
#             self.ui_queue.put(("show_error", "クイズ生成エラー", f"問題の生成中にエラーが発生しました。\n{e}"))
#         finally:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#             self.ui_queue.put(('set_button_state', 'create_quiz_button', 'normal'))

#     def generate_discussion_prompts(self, transcript, summary):
#         if not transcript.strip():
#             self.ui_queue.put(('show_warning', "テキストなし", "ヒントを生成するための会議内容がありません。"))
#             return
#         self.ui_queue.put(('update_status', "🤔 AIが議論のヒントを考え中..."))
#         self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))
#         thread = threading.Thread(target=self.discussion_prompt_task, args=(transcript, summary))
#         thread.start()

#     def discussion_prompt_task(self, transcript, summary):
#         try:
#             lecture_topic = self.lecture_topic_var.get()
#             context_prompt = f"「{lecture_topic}」" if lecture_topic else ""
#             prompt = f"""あなたは、数々の企業の会議を成功に導いてきた、経験豊富なファシリテーターです。
# 現在、ある{context_prompt}会議が手詰まりの状態です。参加者から新しい意見が出なくなり、議論が停滞しています。

# 以下の会議の要約と文字起こしを読んで、この状況を打破し、議論を活性化させるための「言葉がけ」の例を複数提案してください。
# 提案は、以下の３つのカテゴリに分けて、具体的な言葉の例を挙げてください。

# 【カテゴリ】
# 1. **論点を深掘りする質問**: 発言の意図を確認したり、具体例を求めたりして、議論の解像度を上げるための質問。
# 2. **視点を変える質問**: あえて反対の意見を求めたり、時間軸や立場を変えさせたりして、固定観念を崩すための質問。
# 3. **新しいアイデアを促す質問**: 制限を外したり、突拍子もないアイデアを歓迎したりして、発想を広げるための質問。

# 【会議の要約】
# ---
# {summary}
# ---

# 【会議の文字起こし】
# ---
# {transcript}
# ---
# """
#             response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
#             try:
#                 self.ui_queue.put(("display_discussion_prompts", response.text))
#             except ValueError:
#                 self.ui_queue.put(("show_warning", "応答ブロック", "ヒントの生成中にAIからの応答が安全機能によりブロックされました。"))
#         except Exception as e:
#             self.ui_queue.put(("show_error", "ヒント生成エラー", f"ヒントの生成中にエラーが発生しました。\n{e}"))
#         finally:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#             self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'normal'))

#     def update_timer_display(self):
#         mins, secs = divmod(self.timer_seconds_left, 60)
#         time_str = f"{mins:02d}:{secs:02d}"
#         self.ui_queue.put(('update_timer_display', time_str))

#     def start_timer(self):
#         if self.timer_running: return
#         if self.timer_seconds_left <= 0:
#             minutes = self.timer_initial_minutes_var.get()
#             if minutes <= 0:
#                 self.ui_queue.put(('show_warning', "タイマー設定エラー", "時間は1分以上に設定してください。"))
#                 return
#             self.timer_seconds_left = minutes * 60
#         self.timer_running = True
#         self.update_timer_display()
#         self.timer_job = threading.Timer(1.0, self.countdown)
#         self.timer_job.start()
#         self.ui_queue.put(('set_button_state', 'timer_start_button', 'disabled'))
#         self.ui_queue.put(('set_button_state', 'timer_stop_button', 'normal'))
#         self.ui_queue.put(('set_button_state', 'timer_spinbox', 'disabled'))

#     def stop_timer(self):
#         if self.timer_job:
#             self.timer_job.cancel()
#             self.timer_job = None
#         self.timer_running = False
#         self.ui_queue.put(('set_button_state', 'timer_start_button', 'normal'))
#         self.ui_queue.put(('set_button_state', 'timer_stop_button', 'disabled'))
#         self.ui_queue.put(('set_button_state', 'timer_spinbox', 'normal'))

#     def reset_timer(self):
#         self.stop_timer()
#         minutes = self.timer_initial_minutes_var.get()
#         self.timer_seconds_left = minutes * 60
#         self.update_timer_display()

#     def countdown(self):
#         if not self.timer_running: return
#         if self.timer_seconds_left > 0:
#             self.timer_seconds_left -= 1
#             self.update_timer_display()
#             self.timer_job = threading.Timer(1.0, self.countdown)
#             self.timer_job.start()
#         else:
#             self.timer_running = False
#             self.ui_queue.put(('play_bell',))
#             self.ui_queue.put(('show_info', "タイマー終了", "設定時間になりました！"))
#             self.reset_timer()

#     def save_session_to_library(self, transcription, summary):
#         if not transcription:
#             self.ui_queue.put(('show_warning', "保存不可", "保存する文字起こし内容がありません。"))
#             return
#         try:
#             topic = self.lecture_topic_var.get()
#             db.add_session(topic, transcription, summary)
#             self.ui_queue.put(('show_info', "保存完了", "現在のセッションをライブラリに保存しました。"))
#         except Exception as e:
#             self.ui_queue.put(('show_error', "保存エラー", f"データベースへの保存中にエラーが発生しました。\n{e}"))
    
#     def fetch_google_docs(self, query=None, page_size=50):
#         """Google Driveからドキュメントを検索または最近のものを取得する"""
#         creds = self._get_credentials()
#         if not creds:
#             raise Exception("Google認証に失敗しました。")
        
#         service = build('drive', 'v3', credentials=creds)
        
#         q_parts = ["mimeType='application/vnd.google-apps.document'", "trashed=false"]
#         order_by = 'modifiedTime desc'
        
#         if query:
#             q_parts.append(f"name contains '{query}'")

#         search_query = ' and '.join(q_parts)

#         try:
#             results = service.files().list(
#                 q=search_query,
#                 pageSize=page_size,
#                 fields="files(id, name, modifiedTime)",
#                 orderBy=order_by
#             ).execute()
#             return results.get('files', [])
#         except Exception as e:
#             self.ui_queue.put(('show_error', 'Drive APIエラー', f'ドキュメントリストの取得に失敗しました。\n{e}'))
#             return []

#     def import_from_google_doc(self, url=None, doc_id=None):
#         """URLまたはドキュメントIDからドキュメントをインポートする"""
#         if not url and not doc_id:
#             self.ui_queue.put(('show_error', '引数エラー', 'URLまたはドキュメントIDが必要です。'))
#             return
            
#         thread = threading.Thread(target=self._import_from_google_doc_task, args=(url, doc_id))
#         thread.start()

#     def _get_doc_id_from_url(self, url):
#         match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', url)
#         if match: return match.group(1)
#         return None

#     def _import_from_google_doc_task(self, url, doc_id=None):
#         self.ui_queue.put(('update_status', "Googleドキュメントをインポート中..."))
#         creds = self._get_credentials()
#         if not creds:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#             return
#         service = build('drive', 'v3', credentials=creds)

#         try:
#             if not doc_id:
#                 doc_id = self._get_doc_id_from_url(url)
#                 if not doc_id:
#                     self.ui_queue.put(('show_error', 'URLエラー', '有効なGoogleドキュメントのURLではありません。'))
#                     return
                    
#             self.ui_queue.put(('update_status', "ドキュメントをダウンロード中..."))
#             request = service.files().export_media(fileId=doc_id, mimeType='text/plain')
#             fh = io.BytesIO()
#             downloader = MediaIoBaseDownload(fh, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 if status:
#                     self.ui_queue.put(('update_status', f"ダウンロード中: {int(status.progress() * 100)}%"))
#             content = fh.getvalue().decode('utf-8')
#             self.ui_queue.put(('gdoc_import_completed', content))
#         except HttpError as error:
#             if error.resp.status == 404:
#                 self.ui_queue.put(('show_error', 'インポートエラー', 'ドキュメントが見つかりません。URLやアクセス権を確認してください。'))
#             else:
#                  self.ui_queue.put(('show_error', 'インポートエラー', f'Googleドキュメントのインポートに失敗しました。\n{error}'))
#         except Exception as e:
#             self.ui_queue.put(('show_error', 'インポートエラー', f'インポート処理中に予期せぬエラーが発生しました。\n{e}'))
#         finally:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))

#     def import_text_file(self, filepath):
#         try:
#             with open(filepath, 'r', encoding='utf-8') as f: return f.read()
#         except Exception as e:
#             self.ui_queue.put(('show_error', "インポートエラー", f"ファイルの読み込みに失敗しました。\n{e}"))
#             return None

#     def export_text_to_file(self, filepath, content):
#         try:
#             with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
#             self.ui_queue.put(('show_info', "成功", f"エクスポートが完了しました。\n{filepath}"))
#         except Exception as e:
#             self.ui_queue.put(('show_error', "エクスポートエラー", f"ファイルの書き込みに失敗しました。\n{e}"))

#     def _get_credentials(self):
#         """Google APIの認証情報を取得し、self.credentialsに保存して返す"""
#         if self.credentials and self.credentials.valid:
#             return self.credentials
        
#         creds = None
#         if os.path.exists(TOKEN_FILE):
#             creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 try:
#                     creds.refresh(Request())
#                 except Exception as e:
#                     self.ui_queue.put(('show_warning', "Google認証要再設定", f"認証の有効期限が切れました。再度ログインが必要です。\n{e}"))
#                     creds = None
#             if not creds:
#                 if not os.path.exists('credentials.json'):
#                     self.ui_queue.put(('show_error', '認証エラー', 'credentials.json が見つかりません。'))
#                     return None
#                 try:
#                     self.ui_queue.put(('show_info', 'Google認証', 'Googleアカウントでの認証が必要です。ブラウザが開きますので、アクセスを許可してください。'))
#                     self.ui_queue.put(('update_status', "Googleアカウントで認証してください..."))
#                     flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#                     creds = flow.run_local_server(port=0)
#                     self.ui_queue.put(('update_status', "認証に成功しました。"))
#                 except Exception as e:
#                     self.ui_queue.put(('show_error', '認証フローエラー', f'Google認証中にエラーが発生しました。\n{e}'))
#                     return None
            
#             with open(TOKEN_FILE, 'w') as token:
#                 token.write(creds.to_json())
        
#         self.credentials = creds
#         return self.credentials

#     def fetch_calendar_list(self):
#         """ユーザーのカレンダーリストを取得し、UIに送信する"""
#         self.ui_queue.put(('update_status', "カレンダーリストを取得中..."))
#         thread = threading.Thread(target=self._fetch_calendar_list_task)
#         thread.start()

#     def _fetch_calendar_list_task(self):
#         default_id = None
#         try:
#             if os.path.exists(DEFAULT_CALENDAR_CONFIG_FILE):
#                 with open(DEFAULT_CALENDAR_CONFIG_FILE, "r", encoding="utf-8") as f:
#                     default_id = f.read().strip()
#         except Exception as e:
#             print(f"デフォルトカレンダー設定の読み込みに失敗: {e}")

#         try:
#             creds = self._get_credentials()
#             if not creds: return
#             calendar_service = build('calendar', 'v3', credentials=creds)

#             calendars_result = calendar_service.calendarList().list().execute()
#             calendars = calendars_result.get('items', [])

#             calendar_data = [(cal['summary'], cal['id']) for cal in calendars]
            
#             self.ui_queue.put(('update_calendar_menu', (calendar_data, default_id)))
#             self.ui_queue.put(('update_status', "カレンダーリストの取得完了"))

#         except Exception as e:
#             self.ui_queue.put(('show_error', "カレンダー取得エラー", f"カレンダーリストの取得に失敗しました。\n{e}"))
#             self.ui_queue.put(('update_status', "エラー"))

#     def fetch_current_calendar_event(self):
#         """選択されたカレンダーから現在のイベントを取得する"""
#         calendar_id = self.selected_calendar_id_var.get()
#         if not calendar_id:
#             self.ui_queue.put(('show_warning', "カレンダー未選択", "先にカレンダーを選択し、更新ボタンを押してください。"))
#             return
#         self.ui_queue.put(('update_status', "現在の予定を検索中..."))
#         thread = threading.Thread(target=self._fetch_current_event_task, args=(calendar_id,))
#         thread.start()

#     def _fetch_current_event_task(self, calendar_id):
#         try:
#             creds = self._get_credentials()
#             if not creds: return
#             calendar_service = build('calendar', 'v3', credentials=creds)

#             # --- ▼▼▼ 最終修正ロジック ▼▼▼ ---

#             now_dt = datetime.now(timezone.utc)
#             time_min = (now_dt - timedelta(hours=3)).isoformat() # 検索範囲を少し広げる
#             time_max = (now_dt + timedelta(minutes=5)).isoformat()

#             self.ui_queue.put(('update_status', "現在の予定を検索中..."))

#             events_result = calendar_service.events().list(
#                 calendarId=calendar_id, 
#                 timeMin=time_min,
#                 timeMax=time_max,
#                 maxResults=10,
#                 singleEvents=True, 
#                 orderBy='startTime'
#             ).execute()
            
#             events = events_result.get('items', [])
            
#             # 進行中の可能性があるイベント候補をすべてリストアップする
#             candidate_events = []
#             for event in events:
#                 if 'dateTime' not in event['start'] or 'dateTime' not in event['end']:
#                     continue

#                 start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
#                 end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

#                 # 現在時刻がイベントの期間内にあるものを候補として追加
#                 if start_time <= now_dt < end_time:
#                     candidate_events.append(event)
            
#             current_event_name = None
#             if candidate_events:
#                 # 候補が複数ある場合、開始時刻が最も新しいものを選択する
#                 # (sortキーはAPIから返される文字列を直接使う)
#                 candidate_events.sort(key=lambda e: e['start']['dateTime'], reverse=True)
#                 current_event_name = candidate_events[0]['summary']

#             # --- ▲▲▲ 最終修正ロジック ▲▲▲ ---

#             if not current_event_name:
#                 self.ui_queue.put(('show_info', "予定なし", "現在進行中の授業・会議の予定は見つかりませんでした。"))
#                 status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#                 self.ui_queue.put(('update_status', status))
#                 return

#             self.lecture_topic_var.set(current_event_name)
#             self.ui_queue.put(('update_status', f"テーマを設定: {current_event_name}"))

#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             self.ui_queue.put(('show_error', "予定取得エラー", f"予定の取得に失敗しました。\n{e}"))
#             self.ui_queue.put(('update_status', "エラー"))

#         except Exception as e:
#             # エラーが発生した場合もコンソールに出力
#             print(f"\n[!!!] エラーが発生しました: {e}")
#             import traceback
#             traceback.print_exc()
#             self.ui_queue.put(('show_error', "予定取得エラー", f"予定の取得に失敗しました。\n{e}"))
#             self.ui_queue.put(('update_status', "エラー"))

#     def export_to_google_doc(self, title, content):
#         thread = threading.Thread(target=self._export_to_google_doc_task, args=(title, content))
#         thread.start()

#     def _get_folder_id_from_url(self, url):
#         try:
#             folder_id = url.split('/')[-1].split('?')[0]
#             return folder_id
#         except:
#             return None

#     def _resolve_folder_path(self, service, path_string):
#         current_parent_id = 'root'
#         folders_in_path = path_string.replace('\\', '/').split('/')
#         for folder_name in folders_in_path:
#             folder_name_stripped = folder_name.strip()
#             if not folder_name_stripped: continue
#             query = f"'{current_parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
#             response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
#             subfolders = response.get('files', [])
#             found_folder_id = None
#             for subfolder in subfolders:
#                 if subfolder.get('name', '').lower() == folder_name_stripped.lower():
#                     found_folder_id = subfolder.get('id')
#                     break
#             if found_folder_id:
#                 current_parent_id = found_folder_id
#             else:
#                 self.ui_queue.put(('update_status', f"フォルダ「{folder_name_stripped}」を新規作成中..."))
#                 folder_metadata = {'name': folder_name_stripped, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [current_parent_id]}
#                 folder = service.files().create(body=folder_metadata, fields='id').execute()
#                 new_folder_id = folder.get('id')
#                 self.ui_queue.put(('show_info', 'フォルダ作成', f"Google Driveに「{folder_name_stripped}」フォルダを新規作成しました。"))
#                 current_parent_id = new_folder_id
#         return current_parent_id

#     def _export_to_google_doc_task(self, title, content):
#         self.ui_queue.put(('update_status', "Google Driveへエクスポート中..."))
#         creds = self._get_credentials()
#         if not creds:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))
#             return
#         service = build('drive', 'v3', credentials=creds)

#         try:
#             user_input = self.drive_folder_name_var.get().strip()
#             parent_folder_id = None
#             if not user_input:
#                 parent_folder_id = None
#             elif "drive.google.com/drive/folders/" in user_input:
#                 self.ui_queue.put(('update_status', "URLからフォルダIDを抽出中..."))
#                 parent_folder_id = self._get_folder_id_from_url(user_input)
#                 if not parent_folder_id:
#                     self.ui_queue.put(('show_error', 'URLエラー', '有効なGoogle DriveフォルダURLではありません。'))
#                     return
#             else:
#                 self.ui_queue.put(('update_status', "フォルダパスを解決中..."))
#                 parent_folder_id = self._resolve_folder_path(service, user_input)
#             file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
#             if parent_folder_id:
#                 file_metadata['parents'] = [parent_folder_id]
#             media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
#             file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
#             doc_link = file.get('webViewLink')
#             self.ui_queue.put(('show_info', 'エクスポート成功', f'Googleドキュメントを作成しました。\nファイル名: {title}\nリンク: {doc_link}'))
#         except Exception as e:
#             self.ui_queue.put(('show_error', 'エクスポートエラー', f'Googleドキュメントへのエクスポートに失敗しました。\n{e}'))
#         finally:
#             status = "🎙️ 録音中..." if self.is_recording else "準備完了"
#             self.ui_queue.put(('update_status', status))

#     def shutdown(self):
#         if self.timer_job:
#             self.timer_job.cancel()
#         if self.stream and self.is_recording:
#             self.stream.stop()
#             self.stream.close()





### system.py (キーワードモデル分離 修正版)

import tkinter as tk
import threading
import queue
import os
from datetime import datetime, timedelta
import time
from datetime import timezone
import io 
import re 

import google.generativeai as genai
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import moviepy.editor as mp
from yt_dlp import YoutubeDL
import database as db

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# --- 1. 初期設定 (環境変数からAPIキーを読み込む) ---
API_KEY = os.environ.get("GEMINI_API_KEY")

# 録音設定
SAMPLE_RATE = 44100
CHANNELS = 1
RECORDING_DIR = "recordings"

# Geminiモデルの基本設定
generation_config = {"temperature": 0.5}

# Google API連携設定 (スコープを更新)
SCOPES = [
    'https://www.googleapis.com/auth/drive.file', 
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]
TOKEN_FILE = 'token.json'
DEFAULT_CALENDAR_CONFIG_FILE = "calendar_config.txt"


class AppLogic:
    def __init__(self, ui_queue):
        self.ui_queue = ui_queue
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.transcribed_text_buffer = ""
        self.last_summary = ""
        self.stream = None
        self.credentials = None
        
        self.interval_sec_var = tk.IntVar(value=20)
        self.transcription_model_var = tk.StringVar()
        self.summary_model_var = tk.StringVar()
        self.keyword_model_var = tk.StringVar() # ★★★ キーワードモデル用の変数を追加
        self.lecture_topic_var = tk.StringVar()
        self.timer_initial_minutes_var = tk.IntVar(value=10)
        self.drive_folder_name_var = tk.StringVar(value="https://drive.google.com/drive/folders/107Lum5AGu24Awbk3y3-1-QaGR2GEK4mS?usp=drive_link")

        self.available_models = []
        self.transcription_model = None
        self.summary_model = None
        self.keyword_model = None # ★★★ キーワードモデルのインスタンスを保持する変数を追加

        self.transcription_model_var.trace_add("write", self.on_model_change)
        self.summary_model_var.trace_add("write", self.on_model_change)
        self.keyword_model_var.trace_add("write", self.on_model_change) # ★★★ モデル変更を監視
        
        self.timer_running = False
        self.timer_seconds_left = 0
        self.timer_job = None

        os.makedirs(RECORDING_DIR, exist_ok=True)
        self.load_default_calendar()

    def load_default_calendar(self):
        """アプリ起動時に自動でカレンダーリストの取得を開始する"""
        self.fetch_calendar_list()

    def set_default_calendar(self):
        """現在選択中のカレンダーIDを設定ファイルに書き込む"""
        calendar_id = self.selected_calendar_id_var.get()
        if not calendar_id:
            self.ui_queue.put(('show_warning', "カレンダー未選択", "ドロップダウンからカレンダーを選択してください。"))
            return
        try:
            with open(DEFAULT_CALENDAR_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(calendar_id)
            self.ui_queue.put(('show_info', "デフォルト設定完了", "選択したカレンダーを既定値として保存しました。"))
        except Exception as e:
            self.ui_queue.put(('show_error', "保存エラー", f"デフォルト設定の保存に失敗しました。\n{e}"))

    def initialize_gemini(self):
        if not API_KEY:
            self.ui_queue.put(('update_status', "エラー: 環境変数が設定されていません。"))
            self.ui_queue.put(('show_error', "APIキーエラー", "環境変数 'GEMINI_API_KEY' が設定されていません。"))
            self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))
            return False
        
        try:
            genai.configure(api_key=API_KEY)
            self.ui_queue.put(('update_status', "🔄 利用可能なモデルを取得中..."))
            
            self.available_models = [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]
            
            if not self.available_models:
                self.ui_queue.put(('show_error', "モデル取得エラー", "利用可能なモデルが見つかりませんでした。"))
                self.ui_queue.put(('update_status', "❌ モデル取得エラー"))
                return False

            self.ui_queue.put(('update_model_menus', self.available_models))

            if any(m.startswith("models/learnlm-2.0-flash-experimental") for m in self.available_models):
                self.transcription_model_var.set(next(m for m in self.available_models if m.startswith("models/learnlm-2.0-flash-experimental")))
            elif self.available_models:
                self.transcription_model_var.set(self.available_models[0])
            
            if any(m.startswith("models/learnlm-2.0-flash-experimental") for m in self.available_models):
                self.summary_model_var.set(next(m for m in self.available_models if m.startswith("models/learnlm-2.0-flash-experimental")))
            elif self.available_models:
                self.summary_model_var.set(self.available_models[0])

            # ★★★ キーワードモデルのデフォルトを設定 ★★★
            if any(m.startswith("models/learnlm-2.0-flash-experimental") for m in self.available_models):
                self.keyword_model_var.set(next(m for m in self.available_models if m.startswith("models/learnlm-2.0-flash-experimental")))
            elif self.available_models:
                self.keyword_model_var.set(self.available_models[0])

            self.ui_queue.put(('update_status', "✅ モデルの準備ができました"))

        except Exception as e:
            self.ui_queue.put(('show_error', "API初期化エラー", f"APIの初期化中にエラーが発生しました。\n{e}"))
            self.ui_queue.put(('update_status', "❌ API初期化エラー"))
            return False
        return True

    def on_model_change(self, *args):
        # ★★★ キーワードモデルの変数もチェック対象に追加 ★★★
        if not self.transcription_model_var.get() or not self.summary_model_var.get() or not self.keyword_model_var.get():
            return
        self.ui_queue.put(('update_status', "🔄 モデルを切り替え中..."))
        try:
            trans_model_name = self.transcription_model_var.get()
            sum_model_name = self.summary_model_var.get()
            keyword_model_name = self.keyword_model_var.get() # ★★★ キーワードモデル名を取得
            self.transcription_model = genai.GenerativeModel(model_name=trans_model_name)
            self.summary_model = genai.GenerativeModel(model_name=sum_model_name)
            self.keyword_model = genai.GenerativeModel(model_name=keyword_model_name) # ★★★ キーワードモデルを初期化
            
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
        except Exception as e:
            self.ui_queue.put(('show_error', "モデル設定エラー", f"モデルの読み込みに失敗しました。\nエラー: {e}"))
            self.ui_queue.put(('update_status', "❌ モデル設定エラー"))
            self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
            self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))

    def toggle_transcription(self):
        if self.stream is None:
            self.ui_queue.put(('show_error', "エラー", "オーディオストリームが初期化されていません。"))
            return

        if self.is_recording:
            self.stream.stop()
            self.is_recording = False
            self.ui_queue.put(('update_status', "⏸️ 一時停止中"))
            self.ui_queue.put(('set_button_text', 'toggle_button', "文字起こしを再開"))
        else:
            self.stream.start()
            self.is_recording = True
            self.ui_queue.put(('update_status', "🎙️ 録音中..."))
            self.ui_queue.put(('set_button_text', 'toggle_button', "文字起こしを停止"))

    def start_recording(self):
        if self.is_recording:
            return
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_queue.put(indata.copy())
        try:
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback)
            self.stream.start()
            self.is_recording = True
            self.ui_queue.put(('update_status', "🎙️ 録音中..."))
        except Exception as e:
            self.ui_queue.put(('show_error', "マイクエラー", f"マイクの起動に失敗しました。\nエラー: {e}"))
            self.ui_queue.put(('update_status', "❌ マイクエラー"))

    def periodic_transcribe(self):
        if self.is_recording and not self.audio_queue.empty():
            frames_to_process = []
            while not self.audio_queue.empty():
                try:
                    frames_to_process.append(self.audio_queue.get_nowait())
                except queue.Empty:
                    break
            if frames_to_process:
                current_interval_sec = self.interval_sec_var.get()
                self.ui_queue.put(('update_status', f"🔄 {current_interval_sec}秒分の音声を処理中..."))
                thread = threading.Thread(target=self.transcribe_task, args=(frames_to_process,))
                thread.start()

    def transcribe_task(self, frames):
        try:
            recording_data = np.concatenate(frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(RECORDING_DIR, f"rec_temp_{timestamp}.wav")
            write(filepath, SAMPLE_RATE, recording_data)
            audio_file = genai.upload_file(path=filepath)
            lecture_topic = self.lecture_topic_var.get()
            prompt = f"""これは「{lecture_topic}」についての講義または会議です。専門用語や文脈を考慮して、この音声ファイルを日本語で正確に文字起こししてください。""" if lecture_topic else """この音声ファイルを日本語で正確に文字起こししてください。"""
            response = self.transcription_model.generate_content([prompt, audio_file], request_options={"timeout": 600})
            try:
                transcript = response.text
                self.ui_queue.put(("append_transcription", transcript))
                self.transcribed_text_buffer += transcript + "\n"
                self.generate_keyword_insights(transcript)
            except ValueError:
                self.ui_queue.put(("show_warning", "応答ブロック", "AIからの応答が安全機能（著作権保護など）によりブロックされました。\n入力音声の内容を確認してください。"))
                self.ui_queue.put(("append_transcription", "（AIからの応答がブロックされました）"))
            if self.is_recording:
                self.ui_queue.put(('update_status', "🎙️ 録音中..."))
        except Exception as e:
            self.ui_queue.put(("show_error", "文字起こしエラー", f"{e}"))
        finally:
            if 'audio_file' in locals() and audio_file:
                try: genai.delete_file(audio_file.name)
                except Exception as e: print(f"アップロードしたファイルの削除に失敗: {e}")
            if 'filepath' in locals() and os.path.exists(filepath):
                try: os.remove(filepath)
                except Exception as e: print(f"一時ファイルの削除に失敗: {e}")

    def generate_keyword_insights(self, text):
        """文字起こしテキストからキーワードを抽出し、概要を生成するタスクを開始する"""
        if not text.strip():
            return
        thread = threading.Thread(target=self._keyword_insights_task, args=(text,))
        thread.start()

    def _keyword_insights_task(self, text):
        """キーワード抽出と概要生成を実行するバックグラウンドタスク"""
        try:
            prompt = f"""以下の文章は、ある会議または講義の文字起こしです。
この中で、参加者が知らない可能性のある重要な専門用語や固有名詞を6つまで特定してください。
そして、それぞれの用語について、文脈に沿った非常に簡潔な説明（30字程度）を生成してください。

出力形式は必ず「用語:説明」の形式で、用語ごとに改行してください。
例：
Gemini: Googleが開発した大規模言語モデル。
Tkinter: Pythonの標準GUIツールキット。

もし適切な用語が見つからない場合は、何も出力しないでください。

【文字起こし文章】
---
{text}
---
"""
            # ★★★ 使用するモデルをキーワードモデルに変更 ★★★
            response = self.keyword_model.generate_content(prompt, generation_config={"temperature": 0.2})
            
            try:
                insights_text = response.text
                keyword_data = []
                for line in insights_text.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        keyword = parts[0].strip()
                        definition = parts[1].strip()
                        if keyword and definition:
                            keyword_data.append({'keyword': keyword, 'definition': definition})
                
                if keyword_data:
                    self.ui_queue.put(('display_keyword_insights', keyword_data))

            except ValueError:
                pass # 安全性設定でブロックされた場合は何もしない
            except Exception as e:
                print(f"キーワードのパース中にエラー: {e}")

        except Exception as e:
            print(f"キーワード抽出APIの呼び出し中にエラー: {e}")


    def process_youtube_url(self, url):
        thread = threading.Thread(target=self._youtube_task, args=(url,))
        thread.start()

    def _youtube_task(self, url):
        self.ui_queue.put(('update_status', "▶️ YouTube動画情報を取得中..."))
        final_wav_path = None
        original_file_path = None
        try:
            if not self.lecture_topic_var.get():
                try:
                    with YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(url, download=False)
                        self.lecture_topic_var.set(info.get('title', ''))
                except Exception as e:
                    print(f"YouTubeのタイトル取得に失敗: {e}")
            self.ui_queue.put(('update_status', "▶️ 音声データをダウンロード中..."))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"yt_temp_{timestamp}"
            output_template = os.path.join(RECORDING_DIR, f"{base_filename}.%(ext)s")
            final_wav_path = os.path.join(RECORDING_DIR, f"{base_filename}.wav")
            ydl_opts = {
                'format': 'bestaudio/best', 'outtmpl': output_template,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}], 'quiet': True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                original_file_path = ydl.prepare_filename(info)
                final_wav_path = os.path.splitext(original_file_path)[0] + ".wav"
            if not os.path.exists(final_wav_path):
                 raise FileNotFoundError("WAVへの変換に失敗しました。ffmpegが正しくインストールされ、パスが通っているか確認してください。")
            self._process_and_transcribe_file(final_wav_path)
        except Exception as e:
            self.ui_queue.put(("show_error", "YouTube処理エラー", f"YouTube動画の処理中にエラーが発生しました。\nURLが正しいか確認してください。\n{e}"))
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
        finally:
            if final_wav_path and os.path.exists(final_wav_path):
                try: os.remove(final_wav_path)
                except Exception as e: print(f"一時WAVファイルの削除に失敗: {e}")
            if original_file_path and os.path.exists(original_file_path):
                try: os.remove(original_file_path)
                except Exception as e: print(f"一時ファイル（元）の削除に失敗: {e}")

    def process_media_file(self, filepath):
        thread = threading.Thread(target=self._process_and_transcribe_file, args=(filepath,))
        thread.start()

    def _process_and_transcribe_file(self, filepath):
        self.ui_queue.put(('update_status', f"ファイルを処理中: {os.path.basename(filepath)}"))
        audio_path_to_process = None
        temp_audio_path = None
        api_audio_file = None
        try:
            file_ext = os.path.splitext(filepath)[1].lower()
            if file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
                self.ui_queue.put(('update_status', "動画から音声を抽出中..."))
                video = mp.VideoFileClip(filepath)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_audio_path = os.path.join(RECORDING_DIR, f"temp_audio_from_video_{timestamp}.wav")
                video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
                audio_path_to_process = temp_audio_path
            else:
                audio_path_to_process = filepath
            self.ui_queue.put(('update_status', "ファイルをアップロード中..."))
            api_audio_file = genai.upload_file(path=audio_path_to_process)
            self.ui_queue.put(('update_status', "AIが文字起こしを実行中..."))
            prompt = """この音声ファイルを日本語で正確に文字起こししてください。"""
            response = self.transcription_model.generate_content([prompt, api_audio_file], request_options={"timeout": 1800})
            try:
                transcript = response.text
                self.ui_queue.put(("append_transcription", transcript))
            except ValueError:
                self.ui_queue.put(("show_warning", "応答ブロック", "AIからの応答が安全機能によりブロックされました。"))
                self.ui_queue.put(("append_transcription", "（ファイルからの文字起こし中にAIからの応答がブロックされました）"))
        except Exception as e:
            self.ui_queue.put(("show_error", "ファイル処理エラー", f"ファイルの処理中にエラーが発生しました。\n{e}"))
        finally:
            if api_audio_file:
                try: genai.delete_file(api_audio_file.name)
                except Exception as e: print(f"アップロードしたファイルの削除に失敗: {e}")
            if temp_audio_path and os.path.exists(temp_audio_path):
                try: os.remove(temp_audio_path)
                except Exception as e: print(f"一時音声ファイルの削除に失敗: {e}")
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))

    def on_summarize_click(self):
        if not self.transcribed_text_buffer.strip():
            self.ui_queue.put(('show_warning', "テキストなし", "要約対象の新しい文字起こしテキストがありません。"))
            return
        self.ui_queue.put(('update_status', "🔄 差分を要約中..."))
        self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
        self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
        text_to_summarize = self.transcribed_text_buffer
        self.transcribed_text_buffer = ""
        thread = threading.Thread(target=self.summarize_task, args=(text_to_summarize, self.last_summary, "diff"))
        thread.start()

    def on_full_summarize_click(self, full_transcript):
        if not full_transcript.strip():
            self.ui_queue.put(('show_warning', "テキストなし", "要約対象の文字起こしテキストがありません。"))
            return
        self.ui_queue.put(('update_status', "🔄 全文を要約中..."))
        self.ui_queue.put(('set_button_state', 'summarize_button', 'disabled'))
        self.ui_queue.put(('set_button_state', 'full_summarize_button', 'disabled'))
        self.transcribed_text_buffer = ""
        thread = threading.Thread(target=self.summarize_task, args=(full_transcript, "", "full"))
        thread.start()

    def summarize_task(self, transcript, last_summary_context, summary_type):
        try:
            lecture_topic = self.lecture_topic_var.get()
            context_prompt = f"これは「{lecture_topic}」に関する会議の議事録です。" if lecture_topic else "これは会議の議事録です。"
            
            if summary_type == "diff" and last_summary_context:
                prompt = f"""あなたは優秀なアシスタントです。{context_prompt}

【前回までの会話の要約】
{last_summary_context}
---
【今回新たに文字起こしされた会話】
{transcript}
---
【指示】
前回までの文脈と会議(講義や動画)のテーマを考慮し、「今回新たに文字起こしされた会話」の内容を要約してください。(文字お越しが正確ではない可能性も考慮して要約してください。)"""
            else:
                prompt = f"""あなたは優秀なアシスタントです。{context_prompt}
以下の議事録全体を、重要なポイントがわかるように要約してください。(文字お越しが正確ではない可能性も考慮して要約してください。)

---
{transcript}"""

            response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
            try:
                summary = response.text
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.ui_queue.put(("update_summary", summary, lecture_topic, summary_type, timestamp))
                self.ui_queue.put(("append_summary_marker", timestamp))
                self.last_summary += "\n" + summary
            except ValueError:
                 self.ui_queue.put(("show_warning", "応答ブロック", "要約の生成中にAIからの応答が安全機能によりブロックされました。"))
            status = "🎙️ 録音中..." if self.is_recording else "⏸️ 一時停止中"
            self.ui_queue.put(('update_status', status))
        except Exception as e:
            self.ui_queue.put(("show_error", "要約エラー", f"{e}"))
            if summary_type == "diff":
                self.transcribed_text_buffer = transcript + self.transcribed_text_buffer
        finally:
            self.ui_queue.put(('set_button_state', 'summarize_button', 'normal'))
            self.ui_queue.put(('set_button_state', 'full_summarize_button', 'normal'))

    def generate_quiz(self, full_transcript):
        if not full_transcript.strip():
            self.ui_queue.put(('show_warning', "テキストなし", "問題を作成するための文字起こしテキストがありません。"))
            return
        self.ui_queue.put(('update_status', "🤖 AIが問題を作成中..."))
        self.ui_queue.put(('set_button_state', 'create_quiz_button', 'disabled'))
        thread = threading.Thread(target=self.quiz_task, args=(full_transcript,))
        thread.start()
        
    def quiz_task(self, transcript):
        try:
            lecture_topic = self.lecture_topic_var.get()
            context_prompt = f"「{lecture_topic}」に関する" if lecture_topic else ""
            prompt = f"""あなたは経験豊富な教師です。
以下の{context_prompt}講義または会議の文字起こし内容を読んで、受講者の理解度を確認するための問題を3問作成してください。
問題形式は、選択式問題、穴埋め問題、記述式問題などをバランス良く含めてください。
問題と合わせて、明確な解答も生成してください。

【文字起こし】
---
{transcript}
---
"""
            response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
            try:
                self.ui_queue.put(("display_quiz", response.text))
            except ValueError:
                self.ui_queue.put(("show_warning", "応答ブロック", "クイズの生成中にAIからの応答が安全機能によりブロックされました。"))
        except Exception as e:
            self.ui_queue.put(("show_error", "クイズ生成エラー", f"問題の生成中にエラーが発生しました。\n{e}"))
        finally:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
            self.ui_queue.put(('set_button_state', 'create_quiz_button', 'normal'))

    def generate_discussion_prompts(self, transcript, summary):
        if not transcript.strip():
            self.ui_queue.put(('show_warning', "テキストなし", "ヒントを生成するための会議内容がありません。"))
            return
        self.ui_queue.put(('update_status', "🤔 AIが議論のヒントを考え中..."))
        self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'disabled'))
        thread = threading.Thread(target=self.discussion_prompt_task, args=(transcript, summary))
        thread.start()

    def discussion_prompt_task(self, transcript, summary):
        try:
            lecture_topic = self.lecture_topic_var.get()
            context_prompt = f"「{lecture_topic}」" if lecture_topic else ""
            prompt = f"""あなたは、数々の企業の会議を成功に導いてきた、経験豊富なファシリテーターです。
現在、ある{context_prompt}会議が手詰まりの状態です。参加者から新しい意見が出なくなり、議論が停滞しています。

以下の会議の要約と文字起こしを読んで、この状況を打破し、議論を活性化させるための「言葉がけ」の例を複数提案してください。
提案は、以下の３つのカテゴリに分けて、具体的な言葉の例を挙げてください。

【カテゴリ】
1. **論点を深掘りする質問**: 発言の意図を確認したり、具体例を求めたりして、議論の解像度を上げるための質問。
2. **視点を変える質問**: あえて反対の意見を求めたり、時間軸や立場を変えさせたりして、固定観念を崩すための質問。
3. **新しいアイデアを促す質問**: 制限を外したり、突拍子もないアイデアを歓迎したりして、発想を広げるための質問。

【会議の要約】
---
{summary}
---

【会議の文字起こし】
---
{transcript}
---
"""
            response = self.summary_model.generate_content(prompt, request_options={"timeout": 600})
            try:
                self.ui_queue.put(("display_discussion_prompts", response.text))
            except ValueError:
                self.ui_queue.put(("show_warning", "応答ブロック", "ヒントの生成中にAIからの応答が安全機能によりブロックされました。"))
        except Exception as e:
            self.ui_queue.put(("show_error", "ヒント生成エラー", f"ヒントの生成中にエラーが発生しました。\n{e}"))
        finally:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
            self.ui_queue.put(('set_button_state', 'activate_discussion_button', 'normal'))

    def update_timer_display(self):
        mins, secs = divmod(self.timer_seconds_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.ui_queue.put(('update_timer_display', time_str))

    def start_timer(self):
        if self.timer_running: return
        if self.timer_seconds_left <= 0:
            minutes = self.timer_initial_minutes_var.get()
            if minutes <= 0:
                self.ui_queue.put(('show_warning', "タイマー設定エラー", "時間は1分以上に設定してください。"))
                return
            self.timer_seconds_left = minutes * 60
        self.timer_running = True
        self.update_timer_display()
        self.timer_job = threading.Timer(1.0, self.countdown)
        self.timer_job.start()
        self.ui_queue.put(('set_button_state', 'timer_start_button', 'disabled'))
        self.ui_queue.put(('set_button_state', 'timer_stop_button', 'normal'))
        self.ui_queue.put(('set_button_state', 'timer_spinbox', 'disabled'))

    def stop_timer(self):
        if self.timer_job:
            self.timer_job.cancel()
            self.timer_job = None
        self.timer_running = False
        self.ui_queue.put(('set_button_state', 'timer_start_button', 'normal'))
        self.ui_queue.put(('set_button_state', 'timer_stop_button', 'disabled'))
        self.ui_queue.put(('set_button_state', 'timer_spinbox', 'normal'))

    def reset_timer(self):
        self.stop_timer()
        minutes = self.timer_initial_minutes_var.get()
        self.timer_seconds_left = minutes * 60
        self.update_timer_display()

    def countdown(self):
        if not self.timer_running: return
        if self.timer_seconds_left > 0:
            self.timer_seconds_left -= 1
            self.update_timer_display()
            self.timer_job = threading.Timer(1.0, self.countdown)
            self.timer_job.start()
        else:
            self.timer_running = False
            self.ui_queue.put(('play_bell',))
            self.ui_queue.put(('show_info', "タイマー終了", "設定時間になりました！"))
            self.reset_timer()

    def save_session_to_library(self, transcription, summary):
        if not transcription:
            self.ui_queue.put(('show_warning', "保存不可", "保存する文字起こし内容がありません。"))
            return
        try:
            topic = self.lecture_topic_var.get()
            db.add_session(topic, transcription, summary)
            self.ui_queue.put(('show_info', "保存完了", "現在のセッションをライブラリに保存しました。"))
        except Exception as e:
            self.ui_queue.put(('show_error', "保存エラー", f"データベースへの保存中にエラーが発生しました。\n{e}"))
    
    def fetch_google_docs(self, query=None, page_size=50):
        """Google Driveからドキュメントを検索または最近のものを取得する"""
        creds = self._get_credentials()
        if not creds:
            raise Exception("Google認証に失敗しました。")
        
        service = build('drive', 'v3', credentials=creds)
        
        q_parts = ["mimeType='application/vnd.google-apps.document'", "trashed=false"]
        order_by = 'modifiedTime desc'
        
        if query:
            q_parts.append(f"name contains '{query}'")

        search_query = ' and '.join(q_parts)

        try:
            results = service.files().list(
                q=search_query,
                pageSize=page_size,
                fields="files(id, name, modifiedTime)",
                orderBy=order_by
            ).execute()
            return results.get('files', [])
        except Exception as e:
            self.ui_queue.put(('show_error', 'Drive APIエラー', f'ドキュメントリストの取得に失敗しました。\n{e}'))
            return []

    def import_from_google_doc(self, url=None, doc_id=None):
        """URLまたはドキュメントIDからドキュメントをインポートする"""
        if not url and not doc_id:
            self.ui_queue.put(('show_error', '引数エラー', 'URLまたはドキュメントIDが必要です。'))
            return
            
        thread = threading.Thread(target=self._import_from_google_doc_task, args=(url, doc_id))
        thread.start()

    def _get_doc_id_from_url(self, url):
        match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', url)
        if match: return match.group(1)
        return None

    def _import_from_google_doc_task(self, url, doc_id=None):
        self.ui_queue.put(('update_status', "Googleドキュメントをインポート中..."))
        creds = self._get_credentials()
        if not creds:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
            return
        service = build('drive', 'v3', credentials=creds)

        try:
            if not doc_id:
                doc_id = self._get_doc_id_from_url(url)
                if not doc_id:
                    self.ui_queue.put(('show_error', 'URLエラー', '有効なGoogleドキュメントのURLではありません。'))
                    return
                    
            self.ui_queue.put(('update_status', "ドキュメントをダウンロード中..."))
            request = service.files().export_media(fileId=doc_id, mimeType='text/plain')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    self.ui_queue.put(('update_status', f"ダウンロード中: {int(status.progress() * 100)}%"))
            content = fh.getvalue().decode('utf-8')
            self.ui_queue.put(('gdoc_import_completed', content))
        except HttpError as error:
            if error.resp.status == 404:
                self.ui_queue.put(('show_error', 'インポートエラー', 'ドキュメントが見つかりません。URLやアクセス権を確認してください。'))
            else:
                 self.ui_queue.put(('show_error', 'インポートエラー', f'Googleドキュメントのインポートに失敗しました。\n{error}'))
        except Exception as e:
            self.ui_queue.put(('show_error', 'インポートエラー', f'インポート処理中に予期せぬエラーが発生しました。\n{e}'))
        finally:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))

    def import_text_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: return f.read()
        except Exception as e:
            self.ui_queue.put(('show_error', "インポートエラー", f"ファイルの読み込みに失敗しました。\n{e}"))
            return None

    def export_text_to_file(self, filepath, content):
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
            self.ui_queue.put(('show_info', "成功", f"エクスポートが完了しました。\n{filepath}"))
        except Exception as e:
            self.ui_queue.put(('show_error', "エクスポートエラー", f"ファイルの書き込みに失敗しました。\n{e}"))

    def _get_credentials(self):
        """Google APIの認証情報を取得し、self.credentialsに保存して返す"""
        if self.credentials and self.credentials.valid:
            return self.credentials
        
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.ui_queue.put(('show_warning', "Google認証要再設定", f"認証の有効期限が切れました。再度ログインが必要です。\n{e}"))
                    creds = None
            if not creds:
                if not os.path.exists('credentials.json'):
                    self.ui_queue.put(('show_error', '認証エラー', 'credentials.json が見つかりません。'))
                    return None
                try:
                    self.ui_queue.put(('show_info', 'Google認証', 'Googleアカウントでの認証が必要です。ブラウザが開きますので、アクセスを許可してください。'))
                    self.ui_queue.put(('update_status', "Googleアカウントで認証してください..."))
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    self.ui_queue.put(('update_status', "認証に成功しました。"))
                except Exception as e:
                    self.ui_queue.put(('show_error', '認証フローエラー', f'Google認証中にエラーが発生しました。\n{e}'))
                    return None
            
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        return self.credentials

    def fetch_calendar_list(self):
        """ユーザーのカレンダーリストを取得し、UIに送信する"""
        self.ui_queue.put(('update_status', "カレンダーリストを取得中..."))
        thread = threading.Thread(target=self._fetch_calendar_list_task)
        thread.start()

    def _fetch_calendar_list_task(self):
        default_id = None
        try:
            if os.path.exists(DEFAULT_CALENDAR_CONFIG_FILE):
                with open(DEFAULT_CALENDAR_CONFIG_FILE, "r", encoding="utf-8") as f:
                    default_id = f.read().strip()
        except Exception as e:
            print(f"デフォルトカレンダー設定の読み込みに失敗: {e}")

        try:
            creds = self._get_credentials()
            if not creds: return
            calendar_service = build('calendar', 'v3', credentials=creds)

            calendars_result = calendar_service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])

            calendar_data = [(cal['summary'], cal['id']) for cal in calendars]
            
            self.ui_queue.put(('update_calendar_menu', (calendar_data, default_id)))
            self.ui_queue.put(('update_status', "カレンダーリストの取得完了"))

        except Exception as e:
            self.ui_queue.put(('show_error', "カレンダー取得エラー", f"カレンダーリストの取得に失敗しました。\n{e}"))
            self.ui_queue.put(('update_status', "エラー"))

    def fetch_current_calendar_event(self):
        """選択されたカレンダーから現在のイベントを取得する"""
        calendar_id = self.selected_calendar_id_var.get()
        if not calendar_id:
            self.ui_queue.put(('show_warning', "カレンダー未選択", "先にカレンダーを選択し、更新ボタンを押してください。"))
            return
        self.ui_queue.put(('update_status', "現在の予定を検索中..."))
        thread = threading.Thread(target=self._fetch_current_event_task, args=(calendar_id,))
        thread.start()

    def _fetch_current_event_task(self, calendar_id):
        try:
            creds = self._get_credentials()
            if not creds: return
            calendar_service = build('calendar', 'v3', credentials=creds)

            now_dt = datetime.now(timezone.utc)
            time_min = (now_dt - timedelta(hours=3)).isoformat() # 検索範囲を少し広げる
            time_max = (now_dt + timedelta(minutes=5)).isoformat()

            self.ui_queue.put(('update_status', "現在の予定を検索中..."))

            events_result = calendar_service.events().list(
                calendarId=calendar_id, 
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            candidate_events = []
            for event in events:
                if 'dateTime' not in event['start'] or 'dateTime' not in event['end']:
                    continue

                start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

                if start_time <= now_dt < end_time:
                    candidate_events.append(event)
            
            current_event_name = None
            if candidate_events:
                candidate_events.sort(key=lambda e: e['start']['dateTime'], reverse=True)
                current_event_name = candidate_events[0]['summary']

            if not current_event_name:
                self.ui_queue.put(('show_info', "予定なし", "現在進行中の授業・会議の予定は見つかりませんでした。"))
                status = "🎙️ 録音中..." if self.is_recording else "準備完了"
                self.ui_queue.put(('update_status', status))
                return

            self.lecture_topic_var.set(current_event_name)
            self.ui_queue.put(('update_status', f"テーマを設定: {current_event_name}"))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.ui_queue.put(('show_error', "予定取得エラー", f"予定の取得に失敗しました。\n{e}"))
            self.ui_queue.put(('update_status', "エラー"))

        except Exception as e:
            print(f"\n[!!!] エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            self.ui_queue.put(('show_error', "予定取得エラー", f"予定の取得に失敗しました。\n{e}"))
            self.ui_queue.put(('update_status', "エラー"))

    def export_to_google_doc(self, title, content):
        thread = threading.Thread(target=self._export_to_google_doc_task, args=(title, content))
        thread.start()

    def _get_folder_id_from_url(self, url):
        try:
            folder_id = url.split('/')[-1].split('?')[0]
            return folder_id
        except:
            return None

    def _resolve_folder_path(self, service, path_string):
        current_parent_id = 'root'
        folders_in_path = path_string.replace('\\', '/').split('/')
        for folder_name in folders_in_path:
            folder_name_stripped = folder_name.strip()
            if not folder_name_stripped: continue
            query = f"'{current_parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            subfolders = response.get('files', [])
            found_folder_id = None
            for subfolder in subfolders:
                if subfolder.get('name', '').lower() == folder_name_stripped.lower():
                    found_folder_id = subfolder.get('id')
                    break
            if found_folder_id:
                current_parent_id = found_folder_id
            else:
                self.ui_queue.put(('update_status', f"フォルダ「{folder_name_stripped}」を新規作成中..."))
                folder_metadata = {'name': folder_name_stripped, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [current_parent_id]}
                folder = service.files().create(body=folder_metadata, fields='id').execute()
                new_folder_id = folder.get('id')
                self.ui_queue.put(('show_info', 'フォルダ作成', f"Google Driveに「{folder_name_stripped}」フォルダを新規作成しました。"))
                current_parent_id = new_folder_id
        return current_parent_id

    def _export_to_google_doc_task(self, title, content):
        self.ui_queue.put(('update_status', "Google Driveへエクスポート中..."))
        creds = self._get_credentials()
        if not creds:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))
            return
        service = build('drive', 'v3', credentials=creds)

        try:
            user_input = self.drive_folder_name_var.get().strip()
            parent_folder_id = None
            if not user_input:
                parent_folder_id = None
            elif "drive.google.com/drive/folders/" in user_input:
                self.ui_queue.put(('update_status', "URLからフォルダIDを抽出中..."))
                parent_folder_id = self._get_folder_id_from_url(user_input)
                if not parent_folder_id:
                    self.ui_queue.put(('show_error', 'URLエラー', '有効なGoogle DriveフォルダURLではありません。'))
                    return
            else:
                self.ui_queue.put(('update_status', "フォルダパスを解決中..."))
                parent_folder_id = self._resolve_folder_path(service, user_input)
            file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
            doc_link = file.get('webViewLink')
            self.ui_queue.put(('show_info', 'エクスポート成功', f'Googleドキュメントを作成しました。\nファイル名: {title}\nリンク: {doc_link}'))
        except Exception as e:
            self.ui_queue.put(('show_error', 'エクスポートエラー', f'Googleドキュメントへのエクスポートに失敗しました。\n{e}'))
        finally:
            status = "🎙️ 録音中..." if self.is_recording else "準備完了"
            self.ui_queue.put(('update_status', status))

    def shutdown(self):
        if self.timer_job:
            self.timer_job.cancel()
        if self.stream and self.is_recording:
            self.stream.stop()
            self.stream.close()