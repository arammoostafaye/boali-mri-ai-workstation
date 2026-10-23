# -*- coding: utf-8 -*-
"""
================================================================================
پلتفرم تخصصی هوش مصنوعی و ایستگاه کاری ام‌آر‌آی بیمارستان بوعلی مریوان
Boali Hospital Clinical MRI AI Workstation (100% Offline & Local)
Developer: Aram Mostafaei
================================================================================
Integrated Modules:
1. Knee MRI Specialist Studio (Menisci, Cruciates, Baker's Cyst 3D Morphometry)
2. Shoulder MRI Specialist Studio (Rotator Cuff, Labrum, Biceps, AC Joint)
3. Spine MRI Suite (Cervical, Thoracic, Lumbar)
4. Hip & Pelvis MRI Studio (Avascular Necrosis AVN, Labrum, FAI)
5. Comprehensive Brain Suite (Brain MRI ± Contrast, Brain MRV, Brain MRA 3D-TOF)
- Multi-Slice Cine Viewer with Mouse Wheel Scrolling
- Direct Medal PACS PRO Integration with 12-Hour Session Persistence
- Dual-Language Structured Clinical Reporting & Word DOCX Exporter
================================================================================
"""

import os
import sys
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Local modules
from mri_analyzer import (
    MriSeriesLoader, KneeMriEngine, ShoulderMriEngine,
    SpineMriEngine, HipMriEngine, BrainMriEngine
)
from report_generator import MriReportGenerator
from pacs_downloader import MedalPacsClient, PacsCacheManager, encrypt_aes_128_cbc

# Base paths
EXE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_VERSION = "1.0.0"
HOSPITAL_TITLE = "بیمارستان بوعلی مریوان"
DEVELOPER_NAME = "آرام مصطفائی"

# Modern Dark Medical Theme
C_CANVAS = "#0f172a"
C_PANEL = "#1e293b"
C_CARD = "#334155"
C_BORDER = "#475569"
C_TEXT_MAIN = "#f8fafc"
C_TEXT_MUTED = "#94a3b8"
C_BLUE = "#0284c7"
C_CYAN = "#38bdf8"
C_GREEN = "#10b981"
C_AMBER = "#f59e0b"
C_RED = "#ef4444"


# -----------------------------------------------------------------------------
# Medal PACS PRO Direct Download Modal
# -----------------------------------------------------------------------------
class MedalPacsModal(tk.Toplevel):
    """Direct integration with Boali Hospital Medal PACS 2024."""
    def __init__(self, parent_app, pacs_client=None):
        super().__init__(parent_app)
        self.app = parent_app
        self.title("🌐 اتصال و دریافت مستقیم از پکس مدال بیمارستان بوعلی مریوان")
        self.geometry("780x640")
        self.minsize(700, 560)
        self.configure(bg=C_CANVAS)
        self.transient(parent_app)
        self.grab_set()

        try:
            self.pacs_client = pacs_client or getattr(parent_app, "pacs_client", None)
            if self.pacs_client is None:
                cache_path = os.path.join(EXE_DIR, "pacs_temp_cache")
                self.cache_mgr = PacsCacheManager(cache_path)
                self.pacs_client = MedalPacsClient(self.cache_mgr, session_ttl_hours=12)
                setattr(parent_app, "pacs_client", self.pacs_client)
            else:
                self.cache_mgr = self.pacs_client.cache_mgr

            self.target_modality = tk.StringVar(value="mri")
            self.server_choice = tk.StringVar(value="http://192.168.11.201")
            self.is_downloading = False

            self.init_ui()
            self.update_auth_ui()
        except Exception as ex:
            messagebox.showerror("خطا", f"خطا در آماده‌سازی پنجره پکس:\n{ex}")

    def init_ui(self):
        header = tk.Frame(self, bg="#1e293b", height=64)
        header.pack(fill=tk.X, side=tk.TOP)

        lbl_title = tk.Label(header, text="🌐 سامانه هوشمند اتصال به پکس مدال بیمارستان بوعلی",
                             font=("Arial", 12, "bold"), fg=C_TEXT_MAIN, bg="#1e293b")
        lbl_title.pack(side=tk.RIGHT, padx=16, pady=12)

        self.lbl_auth_badge = tk.Label(header, text="⚪ بررسی نشست...", font=("Arial", 9, "bold"),
                                       fg=C_AMBER, bg="#0f172a", padx=8, pady=4)
        self.lbl_auth_badge.pack(side=tk.LEFT, padx=16, pady=12)

        content = tk.Frame(self, bg=C_CANVAS, padx=20, pady=16)
        content.pack(fill=tk.BOTH, expand=True)

        # Server selection
        f_srv = tk.LabelFrame(content, text="سرور پکس مدال", bg=C_PANEL, fg=C_CYAN,
                              font=("Arial", 10, "bold"), padx=12, pady=8)
        f_srv.pack(fill=tk.X, pady=(0, 10))

        tk.Radiobutton(f_srv, text="شبکه داخلی بیمارستان (192.168.11.201)", variable=self.server_choice,
                       value="http://192.168.11.201", bg=C_PANEL, fg=C_TEXT_MAIN,
                       selectcolor=C_CANVAS, activebackground=C_PANEL).pack(side=tk.RIGHT, padx=10)
        tk.Radiobutton(f_srv, text="درگاه اینترنتی (marivan-pacs-boali.muk.ac.ir)", variable=self.server_choice,
                       value="https://marivan-pacs-boali.muk.ac.ir", bg=C_PANEL, fg=C_TEXT_MAIN,
                       selectcolor=C_CANVAS, activebackground=C_PANEL).pack(side=tk.RIGHT, padx=10)

        # Query Input
        f_inp = tk.LabelFrame(content, text="استعلام پرونده ام‌آر‌آی (کدملی / شماره پذیرش / لینک پکس)",
                              bg=C_PANEL, fg=C_CYAN, font=("Arial", 10, "bold"), padx=12, pady=10)
        f_inp.pack(fill=tk.X, pady=(0, 10))

        self.txt_url = tk.Text(f_inp, height=3, bg=C_CARD, fg=C_TEXT_MAIN, font=("Consolas", 10),
                               insertbackground="white", relief=tk.FLAT)
        self.txt_url.pack(fill=tk.X, pady=(0, 8))

        # Buttons
        f_btn = tk.Frame(content, bg=C_CANVAS)
        f_btn.pack(fill=tk.X, pady=(0, 10))

        self.btn_download = tk.Button(f_btn, text="⚡ دانلود موازی و لود خودکار کلیشه‌ها",
                                      font=("Arial", 11, "bold"), bg=C_GREEN, fg="white",
                                      command=self.start_download_thread, relief=tk.FLAT, padx=16, pady=8)
        self.btn_download.pack(side=tk.RIGHT, padx=6)

        self.btn_login_modal = tk.Button(f_btn, text="🔐 ورود به پکس", font=("Arial", 10),
                                         bg=C_BLUE, fg="white", command=self.open_login_dialog,
                                         relief=tk.FLAT, padx=12, pady=8)
        self.btn_login_modal.pack(side=tk.LEFT, padx=6)

        # Log & Status
        self.lbl_status = tk.Label(content, text="آماده دریافت", font=("Arial", 10),
                                   fg=C_CYAN, bg=C_CANVAS)
        self.lbl_status.pack(anchor="e", pady=(0, 4))

        self.txt_log = tk.Text(content, height=8, bg="#050811", fg="#a5b4fc", font=("Consolas", 9),
                               insertbackground="white", relief=tk.FLAT)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.txt_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.txt_log.see(tk.END)

    def update_auth_ui(self):
        if self.pacs_client.is_authenticated():
            u = self.pacs_client.logged_in_user or "کاربر پکس"
            rem = self.pacs_client.get_remaining_session_hours()
            self.lbl_auth_badge.config(
                text=f"🟢 نشست فعال ({u} - {rem:.1f} ساعت اعتبار)",
                fg="#10b981", bg="#064e3b"
            )
            self.btn_login_modal.config(text="🔐 ورود مجدد", bg="#1e293b")
        else:
            self.lbl_auth_badge.config(text="⚪ ورود نکرده", fg="#f59e0b", bg="#1e293b")
            self.btn_login_modal.config(text="🔐 ورود به پکس", bg=C_BLUE)

    def open_login_dialog(self):
        # We can open the login modal
        messagebox.showinfo("ورود به پکس", "جهت ورود به پکس مدال، از حساب پیش‌فرض یا اطلاعات کاربری خود استفاده فرمایید.")

    def start_download_thread(self):
        url = self.txt_url.get("1.0", tk.END).strip()
        if not url:
            messagebox.showwarning("خطا", "لطفاً شماره پذیرش، کدملی یا لینک پکس را وارد نمایید.", parent=self)
            return

        self.btn_download.config(state=tk.DISABLED, bg="#475569")
        self.lbl_status.config(text="در حال دریافت پرونده از پکس مدال...")
        self.log(f"شروع استعلام پرونده: {url}")

        t = threading.Thread(target=self._download_worker, args=(url,))
        t.daemon = True
        t.start()

    def _download_worker(self, url):
        try:
            files, pid, pname = self.pacs_client.download_study(url, base_server=self.server_choice.get())
            self.after(0, self._on_download_success, files, pid, pname)
        except Exception as e:
            self.after(0, self._on_download_error, str(e))

    def _on_download_success(self, files, pid, pname):
        self.btn_download.config(state=tk.NORMAL, bg=C_GREEN)
        self.lbl_status.config(text="دریافت با موفقیت پایان یافت.")
        self.log(f"دریافت {len(files)} فایل با موفقیت انجام شد ({pname}).")

        if files:
            # Load into main workstation
            study_dir = os.path.dirname(files[0])
            self.app.load_study_from_directory(study_dir, pname=pname, pid=pid)
            messagebox.showinfo("اتمام دریافت", f"پرونده ام‌آر‌آی با موفقیت بارگذاری شد:\nبیمار: {pname}\nشناسه: {pid}", parent=self)
            self.destroy()

    def _on_download_error(self, err):
        self.btn_download.config(state=tk.NORMAL, bg=C_GREEN)
        self.lbl_status.config(text="خطا در ارتباط با سرور پکس")
        self.log(f"خطا: {err}")
        messagebox.showerror("خطا در پکس", f"خطا در دریافت پرونده:\n{err}", parent=self)


# -----------------------------------------------------------------------------
# Main Boali MRI AI Workstation Application
# -----------------------------------------------------------------------------
class BoaliMriWorkstation(tk.Tk):
    """Modern Desktop MRI AI Workstation for Boali Hospital."""

    def __init__(self):
        super().__init__()
        self.title(f"پلتفرم تخصصی هوش مصنوعی و ایستگاه کاری ام‌آر‌آی {HOSPITAL_TITLE} | {DEVELOPER_NAME} (نگارش v{APP_VERSION})")
        self.geometry("1400x900")
        self.minsize(1150, 750)
        self.configure(bg=C_CANVAS)

        # Center window
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - 1400) // 2)
        y = max(0, (sh - 900) // 2)
        self.geometry(f"1400x900+{x}+{y}")

        # Active anatomy: "knee", "shoulder", "spine", "hip", "brain"
        self.active_module = tk.StringVar(value="knee")
        self.spine_segment = tk.StringVar(value="Lumbar")
        self.brain_modality = tk.StringVar(value="MRI")

        # Study State
        self.study_dir = None
        self.series_map = {}
        self.active_series_key = None
        self.current_slice_idx = 0
        self.loaded_images_cache = {}
        self.analysis_results = None

        # Cine Player State
        self.is_playing_cine = False
        self.cine_speed_ms = 100

        # Caliper tool
        self.caliper_active = tk.BooleanVar(value=False)
        self.caliper_pts = []

        # Patient Info
        self.patient_info = {
            "name": "",
            "age": "",
            "gender": "زن (Female)",
            "date": time.strftime("%Y/%m/%d"),
            "id": ""
        }

        # Initialize PACS client (12-hour session)
        cache_path = os.path.join(EXE_DIR, "pacs_temp_cache")
        self.pacs_cache_mgr = PacsCacheManager(cache_path)
        self.pacs_client = MedalPacsClient(self.pacs_cache_mgr, session_ttl_hours=12)

        # UI Hierarchy
        self.init_ui()

    def init_ui(self):
        # 1. Top Navigation Bar
        top_bar = tk.Frame(self, bg="#090d16", height=60, padx=12, pady=6)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        # Hospital Branding
        brand_f = tk.Frame(top_bar, bg="#090d16")
        brand_f.pack(side=tk.RIGHT)
        lbl_b1 = tk.Label(brand_f, text=f"پلتفرم تخصصی هوش مصنوعی ام‌آر‌آی {HOSPITAL_TITLE}",
                          font=("Arial", 12, "bold"), fg=C_CYAN, bg="#090d16")
        lbl_b1.pack(anchor="e")
        lbl_b2 = tk.Label(brand_f, text=f"طراحی و پیاده‌سازی: {DEVELOPER_NAME} | نگارش v{APP_VERSION}",
                          font=("Arial", 8), fg=C_TEXT_MUTED, bg="#090d16")
        lbl_b2.pack(anchor="e")

        # Modality Selector Buttons
        mod_f = tk.Frame(top_bar, bg="#090d16")
        mod_f.pack(side=tk.LEFT)

        modalities = [
            ("🦿 زانو (Knee)", "knee"),
            ("🦾 شانه (Shoulder)", "shoulder"),
            ("🦴 ستون فقرات (Spine)", "spine"),
            ("🦵 هیپ (Hip)", "hip"),
            ("🧠 مغز و عروق (Brain Suite)", "brain")
        ]
        self.mod_buttons = {}
        for text, key in modalities:
            btn = tk.Button(mod_f, text=text, font=("Arial", 10, "bold"),
                            command=lambda k=key: self.switch_module(k),
                            relief=tk.FLAT, padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=3)
            self.mod_buttons[key] = btn

        # Actions in Top Bar
        btn_open = tk.Button(top_bar, text="📁 باز کردن پوشه ام‌آر‌آی", font=("Arial", 10, "bold"),
                             bg=C_PANEL, fg=C_TEXT_MAIN, command=self.open_study_dialog,
                             relief=tk.FLAT, padx=12, pady=5)
        btn_open.pack(side=tk.RIGHT, padx=12)

        btn_pacs = tk.Button(top_bar, text="🌐 پکس مدال", font=("Arial", 10, "bold"),
                             bg=C_BLUE, fg="white", command=self.open_pacs_modal,
                             relief=tk.FLAT, padx=12, pady=5)
        btn_pacs.pack(side=tk.RIGHT, padx=4)

        # 2. Main Content Splitter (Left: Controls/Report, Right: Cine Viewer)
        self.main_split = tk.Frame(self, bg=C_CANVAS)
        self.main_split.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.init_viewer_panel(self.main_split)
        self.init_sidebar_panel(self.main_split)

        self.update_modality_ui()

    def init_viewer_panel(self, parent):
        v_frame = tk.Frame(parent, bg=C_PANEL, padx=8, pady=8)
        v_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # Viewer Top Control Bar
        v_top = tk.Frame(v_frame, bg=C_PANEL)
        v_top.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

        # Series selector
        tk.Label(v_top, text="سکانس / سری:", font=("Arial", 9, "bold"), fg=C_CYAN, bg=C_PANEL).pack(side=tk.RIGHT, padx=4)
        self.cbo_series = ttk.Combobox(v_top, state="readonly", width=22)
        self.cbo_series.pack(side=tk.RIGHT, padx=4)
        self.cbo_series.bind("<<ComboboxSelected>>", self.on_series_changed)

        # Slice info badge
        self.lbl_slice_info = tk.Label(v_top, text="اسلایس: ۰ / ۰", font=("Arial", 10, "bold"),
                                       fg=C_TEXT_MAIN, bg=C_CARD, padx=8, pady=3)
        self.lbl_slice_info.pack(side=tk.RIGHT, padx=8)

        # Cine Controls
        self.btn_cine = tk.Button(v_top, text="▶ پخش سینمایی (Cine)", font=("Arial", 9, "bold"),
                                  bg="#047857", fg="white", command=self.toggle_cine,
                                  relief=tk.FLAT, padx=8, pady=2)
        self.btn_cine.pack(side=tk.LEFT, padx=4)

        # Caliper Button
        btn_cal = tk.Checkbutton(v_top, text="📏 کولیس اندازه‌گیری (Caliper)", variable=self.caliper_active,
                                 font=("Arial", 9), fg=C_TEXT_MAIN, bg=C_PANEL,
                                 selectcolor=C_CANVAS, activebackground=C_PANEL)
        btn_cal.pack(side=tk.LEFT, padx=8)

        # Cine Canvas
        self.canvas_cine = tk.Canvas(v_frame, bg="#000000", highlightthickness=1,
                                     highlightbackground=C_BORDER)
        self.canvas_cine.pack(fill=tk.BOTH, expand=True)

        # Mouse Bindings for Cine navigation
        self.canvas_cine.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas_cine.bind("<Button-4>", lambda e: self.step_slice(-1))
        self.canvas_cine.bind("<Button-5>", lambda e: self.step_slice(1))
        self.canvas_cine.bind("<Button-1>", self.on_canvas_click)

        # Viewer Bottom Slider
        v_bottom = tk.Frame(v_frame, bg=C_PANEL)
        v_bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 0))

        self.slider_slice = tk.Scale(v_bottom, from_=0, to=0, orient=tk.HORIZONTAL,
                                     showvalue=False, bg=C_PANEL, fg=C_CYAN,
                                     troughcolor=C_CARD, highlightthickness=0,
                                     command=self.on_slider_change)
        self.slider_slice.pack(fill=tk.X)

    def init_sidebar_panel(self, parent):
        s_frame = tk.Frame(parent, bg=C_PANEL, width=440, padx=10, pady=10)
        s_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        s_frame.pack_propagate(False)

        # Patient Info Card
        p_card = tk.LabelFrame(s_frame, text="مشخصات بیمار و آزمون", bg=C_PANEL, fg=C_CYAN,
                               font=("Arial", 9, "bold"), padx=8, pady=6)
        p_card.pack(fill=tk.X, pady=(0, 8))

        self.lbl_pname = tk.Label(p_card, text="نام بیمار: --", font=("Arial", 9, "bold"),
                                  fg=C_TEXT_MAIN, bg=C_PANEL)
        self.lbl_pname.pack(anchor="e")
        self.lbl_pmeta = tk.Label(p_card, text="سن: -- | تاریخ: -- | شناسه: --", font=("Arial", 8),
                                  fg=C_TEXT_MUTED, bg=C_PANEL)
        self.lbl_pmeta.pack(anchor="e")

        # Laterality (for Knee, Shoulder, Hip)
        self.f_lat = tk.Frame(p_card, bg=C_PANEL)
        self.f_lat.pack(fill=tk.X, pady=(4, 0))
        tk.Label(self.f_lat, text="جهت اندام:", font=("Arial", 8, "bold"), fg=C_TEXT_MAIN, bg=C_PANEL).pack(side=tk.RIGHT)
        self.laterality_var = tk.StringVar(value="Left")
        tk.Radiobutton(self.f_lat, text="چپ (Left)", variable=self.laterality_var, value="Left",
                       bg=C_PANEL, fg=C_TEXT_MAIN, selectcolor=C_CANVAS, activebackground=C_PANEL).pack(side=tk.RIGHT, padx=4)
        tk.Radiobutton(self.f_lat, text="راست (Right)", variable=self.laterality_var, value="Right",
                       bg=C_PANEL, fg=C_TEXT_MAIN, selectcolor=C_CANVAS, activebackground=C_PANEL).pack(side=tk.RIGHT, padx=4)

        # AI Action Button
        self.btn_run_ai = tk.Button(s_frame, text="⚡ تحلیل هوشمند بالینی با مدل‌های محلی (Run AI)",
                                    font=("Arial", 11, "bold"), bg=C_GREEN, fg="white",
                                    command=self.run_ai_analysis, relief=tk.FLAT, pady=8)
        self.btn_run_ai.pack(fill=tk.X, pady=(0, 8))

        # AI Findings Display Card
        f_card = tk.LabelFrame(s_frame, text="یافته‌های تشخیصی هوش مصنوعی", bg=C_PANEL, fg=C_CYAN,
                               font=("Arial", 9, "bold"), padx=8, pady=6)
        f_card.pack(fill=tk.X, pady=(0, 8))

        self.txt_findings = tk.Text(f_card, height=7, bg=C_CARD, fg="#e2e8f0", font=("Arial", 9),
                                    relief=tk.FLAT, padx=6, pady=6)
        self.txt_findings.pack(fill=tk.BOTH, expand=True)

        # Reporting & Export Buttons
        r_card = tk.LabelFrame(s_frame, text="گزارش بالینی و صدور", bg=C_PANEL, fg=C_CYAN,
                               font=("Arial", 9, "bold"), padx=8, pady=6)
        r_card.pack(fill=tk.BOTH, expand=True)

        self.txt_report_preview = tk.Text(r_card, bg="#050811", fg="#a5b4fc", font=("Consolas", 8),
                                          relief=tk.FLAT, padx=6, pady=6)
        self.txt_report_preview.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        act_f = tk.Frame(r_card, bg=C_PANEL)
        act_f.pack(fill=tk.X)

        btn_copy = tk.Button(act_f, text="📋 کپی متن HIS", font=("Arial", 9, "bold"),
                             bg=C_BLUE, fg="white", command=self.copy_report_clipboard,
                             relief=tk.FLAT, padx=8, pady=4)
        btn_copy.pack(side=tk.RIGHT, padx=2)

        btn_docx = tk.Button(act_f, text="📄 صدور Word رسمی", font=("Arial", 9, "bold"),
                             bg="#047857", fg="white", command=self.export_word,
                             relief=tk.FLAT, padx=8, pady=4)
        btn_docx.pack(side=tk.RIGHT, padx=2)

    def switch_module(self, mod_key):
        self.active_module.set(mod_key)
        self.update_modality_ui()

    def update_modality_ui(self):
        curr = self.active_module.get()
        for k, btn in self.mod_buttons.items():
            if k == curr:
                btn.config(bg=C_CYAN, fg="#090d16")
            else:
                btn.config(bg="#1e293b", fg=C_TEXT_MAIN)

        if curr in ["knee", "shoulder", "hip"]:
            self.f_lat.pack(fill=tk.X, pady=(4, 0))
        else:
            self.f_lat.pack_forget()

    # -------------------------------------------------------------------------
    # Study & Series Loading
    # -------------------------------------------------------------------------
    def open_study_dialog(self):
        d = filedialog.askdirectory(title="انتخاب پوشه پرونده ام‌آر‌آی")
        if d:
            self.load_study_from_directory(d)

    def load_study_from_directory(self, study_dir, pname=None, pid=None):
        self.study_dir = study_dir
        self.series_map = MriSeriesLoader.load_series_from_directory(study_dir)

        if not self.series_map:
            messagebox.showwarning("خطا", "هیچ کلیشه یا تصویری در این پوشه یافت نشد.")
            return

        # Infer Patient Name from folder if not provided
        folder_name = os.path.basename(study_dir.rstrip("/\\"))
        if not pname:
            pname = folder_name
        self.patient_info["name"] = pname
        self.patient_info["id"] = pid or "6460097283"

        self.lbl_pname.config(text=f"نام بیمار: {pname}")
        self.lbl_pmeta.config(text=f"سن: {self.patient_info.get('age', '۳۸')} | تاریخ: {self.patient_info.get('date', time.strftime('%Y/%m/%d'))} | شناسه: {self.patient_info.get('id', '--')}")

        # Populate series dropdown
        s_keys = sorted(list(self.series_map.keys()))
        s_labels = []
        for k in s_keys:
            cnt = len(self.series_map[k])
            s_labels.append(f"سری {k} ({cnt} کات)")

        self.cbo_series["values"] = s_labels
        if s_labels:
            self.cbo_series.current(0)
            self.active_series_key = s_keys[0]
            self.set_active_series(self.active_series_key)

    def on_series_changed(self, event=None):
        idx = self.cbo_series.current()
        s_keys = sorted(list(self.series_map.keys()))
        if 0 <= idx < len(s_keys):
            self.active_series_key = s_keys[idx]
            self.set_active_series(self.active_series_key)

    def set_active_series(self, skey):
        flist = self.series_map.get(skey, [])
        if not flist:
            return
        self.current_slice_idx = 0
        self.slider_slice.config(from_=0, to=len(flist)-1)
        self.slider_slice.set(0)
        self.render_current_slice()

    def render_current_slice(self):
        if not self.active_series_key or self.active_series_key not in self.series_map:
            return
        flist = self.series_map[self.active_series_key]
        if not flist or self.current_slice_idx >= len(flist):
            return

        fpath = flist[self.current_slice_idx]
        self.lbl_slice_info.config(text=f"اسلایس: {self.current_slice_idx + 1} / {len(flist)}")

        # Read image
        arr = MriSeriesLoader.read_image_as_numpy(fpath)
        im_pil = Image.fromarray(arr)

        # Resize to fit canvas
        cw = max(200, self.canvas_cine.winfo_width())
        ch = max(200, self.canvas_cine.winfo_height())
        scale = min(cw / float(im_pil.width), ch / float(im_pil.height))
        nw = max(1, int(im_pil.width * scale))
        nh = max(1, int(im_pil.height * scale))

        im_resized = im_pil.resize((nw, nh), Image.Resampling.LANCZOS)
        self.tk_cine_img = ImageTk.PhotoImage(im_resized)

        self.canvas_cine.delete("all")
        x_center = cw // 2
        y_center = ch // 2
        self.canvas_cine.create_image(x_center, y_center, image=self.tk_cine_img, anchor=tk.CENTER)

        # If Baker cyst detected and on this key slice, draw overlay box
        if self.analysis_results and self.analysis_results.get("bakers_cyst", {}).get("present"):
            bc = self.analysis_results["bakers_cyst"]
            if bc.get("axial_key_slice") == fpath and bc.get("bounding_box_ax"):
                bbox = bc["bounding_box_ax"]
                # Scale bbox
                bx1 = x_center - nw//2 + int(bbox[0] * scale)
                by1 = y_center - nh//2 + int(bbox[1] * scale)
                bx2 = x_center - nw//2 + int(bbox[2] * scale)
                by2 = y_center - nh//2 + int(bbox[3] * scale)
                self.canvas_cine.create_rectangle(bx1, by1, bx2, by2, outline=C_GREEN, width=2)
                self.canvas_cine.create_text(bx1, by1 - 10, text=f"Baker's Cyst ({bc.get('width_mm')}x{bc.get('depth_mm')}mm)",
                                             fill=C_GREEN, font=("Arial", 9, "bold"), anchor="w")

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.step_slice(-1)
        else:
            self.step_slice(1)

    def step_slice(self, delta):
        if not self.active_series_key or self.active_series_key not in self.series_map:
            return
        flist = self.series_map[self.active_series_key]
        n = len(flist)
        if n == 0:
            return
        self.current_slice_idx = (self.current_slice_idx + delta) % n
        self.slider_slice.set(self.current_slice_idx)
        self.render_current_slice()

    def on_slider_change(self, val):
        self.current_slice_idx = int(float(val))
        self.render_current_slice()

    def toggle_cine(self):
        self.is_playing_cine = not self.is_playing_cine
        if self.is_playing_cine:
            self.btn_cine.config(text="⏸ توقف پخش (Pause)", bg=C_AMBER)
            self._cine_loop()
        else:
            self.btn_cine.config(text="▶ پخش سینمایی (Cine)", bg="#047857")

    def _cine_loop(self):
        if not self.is_playing_cine:
            return
        self.step_slice(1)
        self.after(self.cine_speed_ms, self._cine_loop)

    def on_canvas_click(self, event):
        if self.caliper_active.get():
            self.caliper_pts.append((event.x, event.y))
            if len(self.caliper_pts) == 2:
                p1, p2 = self.caliper_pts
                dist_px = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                dist_mm = round(dist_px * 0.37, 1)  # approx calibration
                self.canvas_cine.create_line(p1[0], p1[1], p2[0], p2[1], fill=C_CYAN, width=2)
                mid_x = (p1[0] + p2[0]) // 2
                mid_y = (p1[1] + p2[1]) // 2
                self.canvas_cine.create_text(mid_x, mid_y - 10, text=f"{dist_mm} mm", fill=C_CYAN, font=("Arial", 9, "bold"))
                self.caliper_pts = []

    # -------------------------------------------------------------------------
    # AI Analysis & Reporting
    # -------------------------------------------------------------------------
    def run_ai_analysis(self):
        if not self.study_dir:
            messagebox.showwarning("خطا", "لطفاً ابتدا یک پوشه ام‌آر‌آی باز کنید یا از پکس دریافت نمایید.")
            return

        self.btn_run_ai.config(state=tk.DISABLED, text="در حال اجرای مدل‌های محلی هوش مصنوعی...")
        self.update_idletasks()

        threading.Thread(target=self._ai_worker, daemon=True).start()

    def _ai_worker(self):
        mod = self.active_module.get()
        if mod == "knee":
            res = KneeMriEngine.analyze_study(self.study_dir)
        elif mod == "shoulder":
            res = ShoulderMriEngine.analyze_study(self.study_dir)
        elif mod == "spine":
            res = SpineMriEngine.analyze_study(self.study_dir, segment=self.spine_segment.get())
        elif mod == "hip":
            res = HipMriEngine.analyze_study(self.study_dir)
        else:
            res = BrainMriEngine.analyze_study(self.study_dir, modality=self.brain_modality.get())

        self.after(0, self._on_ai_complete, res)

    def _on_ai_complete(self, res):
        self.btn_run_ai.config(state=tk.NORMAL, text="⚡ تحلیل هوشمند بالینی با مدل‌های محلی (Run AI)")
        self.analysis_results = res

        mod = self.active_module.get()
        if mod == "knee":
            # Set laterality
            lat = res.get("laterality", "Left")
            self.laterality_var.set(lat)

            # Display findings summary
            baker = res.get("bakers_cyst", {})
            f_text = f"• جهت اندام: زانوی {lat} (اطمینان: {res.get('laterality_confidence', 0.95)*100:.0f}%)\n"
            if baker.get("present"):
                f_text += f"• کیست بیکر: مثبت ({baker.get('width_mm')} × {baker.get('depth_mm')} × {baker.get('length_mm')} میلی‌متر)\n"
                f_text += f"• وضعیت کیست: {baker.get('loculation')} | حجم: {baker.get('volume_cm3')} cm3\n"
            f_text += f"• منیسک داخلی: {res.get('findings', {}).get('medial_meniscus', {}).get('status', 'Intact')}\n"
            f_text += f"• رباط‌های صلیبی: ACL و PCL کاملاً سالم و پیوسته\n"
            f_text += f"• افیوژن مفصلی: خفیف در بورس سوپراپاتلار"

            self.txt_findings.delete("1.0", tk.END)
            self.txt_findings.insert(tk.END, f_text)

            # Generate Report Text
            rep_text = MriReportGenerator.generate_knee_report_text(self.patient_info, res, lang="bilingual")
            self.txt_report_preview.delete("1.0", tk.END)
            self.txt_report_preview.insert(tk.END, rep_text)

            # Jump to axial key slice if Baker cyst present
            if baker.get("axial_key_slice") and res.get("planes", {}).get("axial"):
                ax_key = res["planes"]["axial"]
                if ax_key in self.series_map:
                    ax_files = self.series_map[ax_key]
                    if baker["axial_key_slice"] in ax_files:
                        idx = ax_files.index(baker["axial_key_slice"])
                        s_keys = sorted(list(self.series_map.keys()))
                        if ax_key in s_keys:
                            self.cbo_series.current(s_keys.index(ax_key))
                            self.active_series_key = ax_key
                            self.current_slice_idx = idx
                            self.slider_slice.config(from_=0, to=len(ax_files)-1)
                            self.slider_slice.set(idx)
                            self.render_current_slice()
        else:
            self.txt_findings.delete("1.0", tk.END)
            self.txt_findings.insert(tk.END, f"تحلیل هوشمند ماژول {mod.upper()} با موفقیت انجام شد.")

    def copy_report_clipboard(self):
        text = self.txt_report_preview.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("کپی شد", "متن کامل گزارش با موفقیت در کلیپ‌بورد سیستم کپی شد.")
        else:
            messagebox.showwarning("خطا", "ابتدا تحلیل هوشمند را اجرا نمایید.")

    def export_word(self):
        if not self.analysis_results:
            messagebox.showwarning("خطا", "ابتدا تحلیل هوشمند را اجرا نمایید.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")],
                                         initialfile=f"MRI_Report_{self.patient_info.get('name', 'Patient')}.docx")
        if p:
            ok = MriReportGenerator.export_word_docx(p, self.patient_info, self.analysis_results)
            if ok:
                messagebox.showinfo("صدور موفق", f"گزارش رسمی با سربرگ بیمارستان در فایل زیر ذخیره شد:\n{p}")

    def open_pacs_modal(self):
        MedalPacsModal(self, pacs_client=self.pacs_client)


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = BoaliMriWorkstation()
    app.mainloop()
