import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
import json
import os
import sys
import threading
import time
import winreg
from pathlib import Path
import io
import subprocess

# Windows通知用（オプション：インストール不要）
try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False

# UTF-8 出力のための設定（バッチ実行時のエンコーディング対応）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

IDOLS_FILE = "dere.json"
SETTINGS_FILE = "settings.json"
NOTIFICATION_LOG_FILE = "notification_log.json"
BASE_DIR = Path(__file__).resolve().parent
IDOLS_FILE = str(BASE_DIR / "dere.json")
SETTINGS_FILE = str(BASE_DIR / "settings.json")
NOTIFICATION_LOG_FILE = str(BASE_DIR / "notification_log.json")
SCRIPT_PATH = str(Path(__file__).resolve())

def load_idols():
    """JSONファイルからアイドルデータを読み込む"""
    with open(IDOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    idols = []
    for month_list in data.values():
        idols.extend(month_list)
    return idols

def load_settings():
    """設定ファイルを読み込む"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_settings(selected):
    """設定をファイルに保存"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

def days_until_birthday(birthday_str):
    """誕生日までの日数を計算"""
    today = date.today()
    month, day = map(int, birthday_str.replace("月", " ").replace("日", "").split())
    birthday_this_year = date(today.year, month, day)
    if birthday_this_year < today:
        birthday_this_year = date(today.year + 1, month, day)
    return (birthday_this_year - today).days

def load_notification_log():
    """通知ログを読み込む"""
    if os.path.exists(NOTIFICATION_LOG_FILE):
        try:
            with open(NOTIFICATION_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_notification_log(log):
    """通知ログを保存"""
    with open(NOTIFICATION_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def has_notified_today(idol_name, days):
    """本日、このアイドルに対してこの状態で通知済みか確認"""
    log = load_notification_log()
    today_str = str(date.today())
    
    if today_str not in log:
        return False
    
    key = f"{idol_name}_{days}"
    return key in log[today_str]

def record_notification(idol_name, days):
    """通知をログに記録"""
    log = load_notification_log()
    today_str = str(date.today())
    
    if today_str not in log:
        log[today_str] = []
    
    key = f"{idol_name}_{days}"
    if key not in log[today_str]:
        log[today_str].append(key)
    
    save_notification_log(log)

def show_notification(idol_name, days, age):
    """Windows通知を表示"""
    if days == 0:
        title = "🎉 誕生日です！"
        message = f"{idol_name}さんの誕生日です！\nおめでとうございます！"
    elif days == 1:
        title = "🎂 明日が誕生日"
        message = f"{idol_name}さんの誕生日は明日です！\n準備はいいですか？"
    else:
        title = f"📅 あと {days} 日"
        message = f"{idol_name}さんの誕生日まであと {days} 日です"
    
    print(f"[通知] {title} - {idol_name}")
    
    # PowerShellで Windows 10 Toast Notification を表示（最も安定している）
    try:
        ps_cmd = f"""
$app = 'Birthday Notifier'
$title = '{title}'
$message = '{message}'

# Windows.UI.Notifications を使用
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, System.Xml.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = 'Birthday.Notifier'

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">${{title}}</text>
            <text id="2">${{message}}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
"""
        subprocess.run(['powershell', '-NoProfile', '-Command', ps_cmd], capture_output=True, timeout=5)
    except Exception as e:
        print(f"PowerShell通知失敗: {e}")
        # フォールバック：win10toast を試す
        if HAS_TOAST:
            try:
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10, threaded=True)
            except Exception as e2:
                print(f"Win10Toast失敗（フォールバック）: {e2}")
        else:
            # 最終手段：GUIメッセージボックス
            try:
                messagebox.showinfo(title, message)
            except:
                pass

def notify_birthdays(idols, selected_names):
    """選択されたアイドルの誕生日情報を通知"""
    if not selected_names:
        messagebox.showinfo("通知", "通知対象が設定されていません")
        return
    
    notified_count = 0
    for idol in idols:
        if idol["name"] in selected_names:
            days = days_until_birthday(idol["birthday"])
            age = idol["age"]
            
            # すべての距離で通知を表示
            show_notification(idol["name"], days, age)
            notified_count += 1
    
    if notified_count == 0:
        messagebox.showinfo("通知確認", "通知対象が設定されていません")

def add_to_startup():
    """PCスタートアップに登録"""
    try:
        # Pythonスクリプト実行用のバッチファイルを作成
        bat_path = os.path.join(os.path.dirname(SCRIPT_PATH), "birthday_notifier.bat")
        bat_content = f'''@echo off
REM PC起動時に実行されるバッチファイル
cd /d "%~dp0"
python birthday_notifier.py --silent > nul 2>&1
exit
'''
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        
        # レジストリに登録（Windows通知を表示するため）
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "BirthdayNotifier", 0, winreg.REG_SZ, bat_path)
        winreg.CloseKey(key)
        
        messagebox.showinfo("成功", 
            "✅ スタートアップに登録しました\n\n"
            "• PC起動時に自動的に実行されます\n"
            "• 誕生日が近づくとWindows通知が表示されます\n"
            "• 通知履歴に記録されます")
    except Exception as e:
        messagebox.showerror("エラー", f"登録に失敗しました: {e}")

def background_notifier(interval=600):
    """バックグラウンドで定期的に通知チェック（デフォルト10分ごと）"""
    print(f"バックグラウンド監視開始 - {datetime.now()}")
    idols = load_idols()
    
    while True:
        try:
            selected = load_settings()
            if selected:
                for idol in idols:
                    if idol["name"] in selected:
                        days = days_until_birthday(idol["birthday"])
                        age = idol["age"]
                        
                        # 当日、1日前、7日前に通知
                        if days in [0, 1, 7]:
                            if not has_notified_today(idol["name"], days):
                                show_notification(idol["name"], days, age)
                                record_notification(idol["name"], days)
                                print(f"通知送信: {idol['name']} - あと {days} 日")
            
            # 次のチェックまで待機
            time.sleep(interval)
        except Exception as e:
            print(f"エラー: {e}")
            time.sleep(60)  # エラー時は1分待機

def create_main_window(idols):
    """メイン画面をタブ形式で作成"""
    root = tk.Tk()
    root.title("誕生日通知")
    root.geometry("700x600")
    
    print(f"[DEBUG] メイン画面作成")

    # タブを作成
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)
    
    # ===== タブ1：誕生日カウントダウン =====
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="📅 誕生日カウント")
    
    title = tk.Label(tab1, text="誕生日までのカウントダウン", font=("Arial", 14, "bold"))
    title.pack(pady=10)
    
    # リスト表示用のCanvas
    canvas1 = tk.Canvas(tab1)
    scrollbar1 = tk.Scrollbar(tab1, orient="vertical", command=canvas1.yview)
    scroll_frame1 = tk.Frame(canvas1)
    
    scroll_frame1.bind(
        "<Configure>",
        lambda e: canvas1.configure(scrollregion=canvas1.bbox("all"))
    )
    
    canvas1.create_window((0, 0), window=scroll_frame1, anchor="nw")
    canvas1.configure(yscrollcommand=scrollbar1.set)
    canvas1.pack(side="left", fill="both", expand=True)
    scrollbar1.pack(side="right", fill="y")
    
    # 一覧を表示するための変数
    idol_labels = []
    
    def update_display():
        """誕生日表示を更新"""
        # 前のラベルを削除
        for label in idol_labels:
            label.destroy()
        idol_labels.clear()
        
        selected = load_settings()
        print(f"[DEBUG] 表示更新 - 選択: {selected}")
        
        if selected:
            sorted_idols = []
            for idol in idols:
                if idol["name"] in selected:
                    days = days_until_birthday(idol["birthday"])
                    sorted_idols.append((idol, days))
            
            # 誕生日が近い順にソート
            sorted_idols.sort(key=lambda x: x[1])
            
            for idol, days in sorted_idols:
                color = "lightgreen" if days == 0 else "lightyellow" if days <= 7 else "white"
                
                frame = tk.Frame(scroll_frame1, bg=color, relief="ridge", borderwidth=1)
                frame.pack(fill="x", padx=5, pady=3)
                
                label_text = f"{idol['name']:15} | 誕生日: {idol['birthday']:8} | あと {days:3} 日 | 年齢: {idol['age']}"
                label = tk.Label(frame, text=label_text, font=("Courier", 11), bg=color, justify="left")
                label.pack(padx=5, pady=5)
                idol_labels.append(frame)
        else:
            frame = tk.Frame(scroll_frame1)
            frame.pack(pady=20)
            label = tk.Label(frame, text="選択されたアイドルがありません", font=("Arial", 12))
            label.pack()
            idol_labels.append(frame)
    
    # 初回表示
    update_display()
    
    # ===== タブ2：アイドル選択 =====
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="⚙️ アイドル選択")
    
    title2 = tk.Label(tab2, text="通知対象のアイドルを選択", font=("Arial", 14, "bold"))
    title2.pack(pady=10)
    
    # 検索用エントリー
    search_frame = tk.Frame(tab2)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="検索：").pack(side="left")
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)
    
    # スクロール可能なフレーム
    canvas2 = tk.Canvas(tab2)
    scrollbar2 = tk.Scrollbar(tab2, orient="vertical", command=canvas2.yview)
    scroll_frame2 = tk.Frame(canvas2)
    
    scroll_frame2.bind(
        "<Configure>",
        lambda e: canvas2.configure(scrollregion=canvas2.bbox("all"))
    )
    
    canvas2.create_window((0, 0), window=scroll_frame2, anchor="nw")
    canvas2.configure(yscrollcommand=scrollbar2.set)
    
    canvas2.pack(side="left", fill="both", expand=True, padx=5)
    scrollbar2.pack(side="right", fill="y")
    
    # チェックボックスリスト
    current_settings = load_settings() or []
    selected_set = set(current_settings)
    
    vars_list = []
    checkboxes = []
    
    def create_checkboxes():
        """チェックボックスを作成"""
        for idol in idols:
            is_checked = idol["name"] in selected_set
            var = tk.BooleanVar(value=is_checked)
            
            def on_check_change(idol_name=idol["name"], v=var):
                """チェック状態が変わったら表示を更新"""
                print(f"[DEBUG] {idol_name} のチェック状態が変更: {v.get()}")
                # 表示を更新
                update_display()
            
            chk = tk.Checkbutton(
                scroll_frame2,
                text=f"{idol['name']} ({idol['birthday']}) - 年齢: {idol['age']}",
                variable=var,
                font=("Arial", 10),
                command=on_check_change
            )
            chk.pack(anchor="w", padx=5, pady=2)
            vars_list.append((idol["name"], var))
            checkboxes.append((idol["name"], chk))
    
    create_checkboxes()
    
    # 検索フィルタリング
    def filter_idols(*args):
        search_text = search_var.get().lower()
        for name, chk in checkboxes:
            if search_text == "" or search_text in name.lower():
                chk.pack(anchor="w", padx=5, pady=2)
            else:
                chk.pack_forget()
    
    search_var.trace("w", filter_idols)
    
    # ボタンフレーム
    button_frame = tk.Frame(tab2)
    button_frame.pack(pady=10)
    
    def save_changes():
        """チェック状態を保存"""
        new_selected = [name for name, var in vars_list if var.get()]
        print(f"[DEBUG] 保存対象: {new_selected}")
        
        save_settings(new_selected)
        
        # 保存確認
        saved_data = load_settings()
        print(f"[DEBUG] 保存確認: {saved_data}")
        
        messagebox.showinfo("成功", f"{len(new_selected)} 人を選択しました")
    
    def select_all():
        for _, var in vars_list:
            var.set(True)
        update_display()
    
    def deselect_all():
        for _, var in vars_list:
            var.set(False)
        update_display()
    
    tk.Button(button_frame, text="すべて選択", command=select_all, width=12).pack(side="left", padx=5)
    tk.Button(button_frame, text="すべて解除", command=deselect_all, width=12).pack(side="left", padx=5)
    tk.Button(button_frame, text="💾 保存", command=save_changes, width=12, bg="lightgreen").pack(side="left", padx=5)
    
    # スタートアップボタン
    startup_button = tk.Button(tab2, text="🔌 スタートアップに登録", command=add_to_startup, bg="lightblue")
    startup_button.pack(pady=5)
    
    # ボタンフレーム（メイン）
    main_button_frame = tk.Frame(root)
    main_button_frame.pack(pady=10)
    
    def refresh_all():
        """全体を更新"""
        update_display()
    
    tk.Button(main_button_frame, text="🔄 すべて更新", command=refresh_all, bg="lightyellow", width=20).pack(side="left", padx=5)
    tk.Button(main_button_frame, text="🔔 通知確認", command=lambda: notify_birthdays(idols, load_settings() or []), bg="lightcyan", width=15).pack(side="left", padx=5)
    tk.Button(main_button_frame, text="終了", command=root.quit, width=10).pack(side="left", padx=5)
    
    root.mainloop()

def main():
    # コマンドライン引数で --silent オプション確認
    silent_mode = "--silent" in sys.argv
    
    idols = load_idols()
    selected = load_settings()
    
    print(f"[DEBUG] 読み込み設定: {selected}")

    if not silent_mode:
        # 通常モード：GUIを表示
        if selected is None:  # 初回起動時
            print("[DEBUG] 初回起動 - 設定ウィンドウを表示")
            open_settings()
        
        # メイン画面を作成・表示
        create_main_window(idols)
    else:
        # サイレントモード：バックグラウンドで実行（スタートアップ用）
        print(f"[スタートアップ] {datetime.now()} - サイレントモード開始")
        selected = load_settings()
        print(f"[スタートアップ] 選択されたアイドル: {selected}")
        
        if selected:
            # PC起動時に一度通知をチェック（すべてのアイドルの残り日数を表示）
            for idol in idols:
                if idol["name"] in selected:
                    days = days_until_birthday(idol["birthday"])
                    age = idol["age"]
                    # 全員の残り日数を表示
                    print(f"[スタートアップ] 通知実行: {idol['name']} (あと {days} 日)")
                    show_notification(idol["name"], days, age)
                    time.sleep(2)  # スレッド実行間隔を広げる
            
            # 通知完了を待つ
            time.sleep(5)
            print(f"[スタートアップ] 初回通知完了 - バックグラウンド監視を開始")
            # バックグラウンドで10分ごとにチェック
            background_notifier(600)
        else:
            print(f"[スタートアップ] 選択されたアイドルがないため終了")
            sys.exit(0)

if __name__ == "__main__":
    main()
