import os
import sys
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from PySide2.QtCore import Qt, QThread, Signal, QUrl, QSettings
from PySide2.QtGui import (
    QPixmap, QIcon, QDesktopServices, QPainter, QColor, QBrush, QKeySequence
)
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QProgressBar, QSpinBox, QSlider, QFrame, QMessageBox, QCheckBox,
    QAbstractItemView, QDialog, QLineEdit, QShortcut
)

APP_NAME = "ARJSOFT HEIC Converter"
APP_VERSION = "1.0.0"
SUPPORTED = {".heic", ".heif"}

TEXT = {
    "en": {
        "lang_button": "فارسی",
        "subtitle": "Fast, offline conversion of HEIC and HEIF photos to JPEG",
        "add_files": "Add Photos",
        "add_folder": "Add Folder",
        "remove": "Remove Selected",
        "clear": "Clear List",
        "quality": "JPEG quality:",
        "quality_hint": "Higher quality means a larger file",
        "metadata": "Preserve photo metadata (EXIF)",
        "open_when_done": "Open the output folder when finished",
        "output": "Output folder:",
        "browse": "Browse…",
        "open_folder": "Open Folder",
        "convert": "Convert to JPEG",
        "cancel": "Cancel Conversion",
        "empty": "Drag and drop HEIC / HEIF photos or folders here\n"
                 "or use the “Add Photos” button",
        "queue": "{n} image(s) in queue",
        "added": "{n} image(s) added",
        "added_skip": "{n} image(s) added ({s} duplicate or unsupported file(s) skipped)",
        "nothing_added": "No new HEIC/HEIF images were found",
        "converting": "Converting {c} of {t}: {name}",
        "done_ok": "All {n} image(s) were converted successfully",
        "done_fail": "Finished: {ok} succeeded, {fail} failed",
        "cancelled": "Conversion cancelled ({ok} of {t} image(s) were converted)",
        "warn_title": "Some images could not be converted",
        "quit_confirm": "A conversion is in progress. Do you want to cancel it and exit?",
        "footer": "ARJSOFT  •  Version {v}",
        "dlg_files": "Select HEIC/HEIF photos",
        "dlg_filter": "HEIC/HEIF Images (*.heic *.heif)",
        "dlg_folder": "Select a folder containing HEIC/HEIF photos",
        "dlg_output": "Choose output folder",
        "output_failed": "Could not create the output folder: {e}",
        "about_tt": "About ARJSOFT",
        "about_title": "About ARJSOFT",
        "about_heading": "Practical, simple and reliable software",
        "about_desc": "ARJSOFT creates practical software that is simple to use and reliable. "
                      "This app is part of the ARJSOFT collection and converts your photos "
                      "offline, directly on your computer.",
        "about_link": "Visit the official ARJSOFT website",
        "close": "Close",
        "yes": "Yes",
        "no": "No",
    },
    "fa": {
        "lang_button": "English",
        "subtitle": "تبدیل سریع و آفلاین تصاویر HEIC و HEIF به JPEG",
        "add_files": "افزودن عکس‌ها",
        "add_folder": "افزودن پوشه",
        "remove": "حذف انتخاب‌شده",
        "clear": "پاک کردن فهرست",
        "quality": "کیفیت JPEG:",
        "quality_hint": "کیفیت بالاتر یعنی حجم فایل بیشتر",
        "metadata": "حفظ اطلاعات عکس (EXIF)",
        "open_when_done": "پس از پایان، پوشه خروجی باز شود",
        "output": "پوشه خروجی:",
        "browse": "انتخاب پوشه…",
        "open_folder": "باز کردن پوشه",
        "convert": "شروع تبدیل",
        "cancel": "لغو تبدیل",
        "empty": "عکس‌ها یا پوشه‌های HEIC / HEIF را اینجا بکشید و رها کنید\n"
                 "یا از دکمه «افزودن عکس‌ها» استفاده کنید",
        "queue": "تعداد تصاویر: {n}",
        "added": "{n} تصویر اضافه شد",
        "added_skip": "{n} تصویر اضافه شد ({s} فایل تکراری یا نامعتبر نادیده گرفته شد)",
        "nothing_added": "تصویر HEIC/HEIF جدیدی پیدا نشد",
        "converting": "در حال تبدیل {c} از {t}: {name}",
        "done_ok": "تبدیل همه {n} تصویر با موفقیت انجام شد",
        "done_fail": "پایان: {ok} موفق، {fail} ناموفق",
        "cancelled": "تبدیل لغو شد ({ok} از {t} تصویر تبدیل شد)",
        "warn_title": "تبدیل برخی تصاویر انجام نشد",
        "quit_confirm": "تبدیل در حال انجام است. می‌خواهید آن را لغو کنید و خارج شوید؟",
        "footer": "ARJSOFT  •  نسخه {v}",
        "dlg_files": "انتخاب تصاویر HEIC/HEIF",
        "dlg_filter": "تصاویر HEIC/HEIF (*.heic *.heif)",
        "dlg_folder": "انتخاب پوشه‌ای که شامل تصاویر HEIC/HEIF است",
        "dlg_output": "انتخاب پوشه خروجی",
        "output_failed": "ساخت پوشه خروجی ممکن نشد: {e}",
        "about_tt": "درباره ARJSOFT",
        "about_title": "درباره ARJSOFT",
        "about_heading": "نرم‌افزارهای کاربردی، ساده و قابل‌اعتماد",
        "about_desc": "ARJSOFT با هدف طراحی و ارائه نرم‌افزارهای کاربردی و آسان برای استفاده "
                      "فعالیت می‌کند. این برنامه یکی از محصولات ARJSOFT است و تبدیل تصاویر "
                      "شما را به‌صورت آفلاین و مستقیماً روی رایانه انجام می‌دهد.",
        "about_link": "مشاهده وب‌سایت رسمی ARJSOFT",
        "close": "بستن",
        "yes": "بله",
        "no": "خیر",
    },
}

STATUS_COLORS = {"info": "#718096", "ok": "#2f855a", "warn": "#b7791f", "error": "#c53030"}


def resource_path(relative_path):
    """Resolve bundled assets in both source and PyInstaller builds."""
    base_path = getattr(sys, "_MEIPASS", str(Path(__file__).resolve().parent))
    return str(Path(base_path) / relative_path)


def unique_target(output_dir, stem):
    """Return a .jpg path that never overwrites an existing file."""
    target = output_dir / (stem + ".jpg")
    counter = 1
    while target.exists():
        suffix = "_converted" if counter == 1 else "_converted{}".format(counter)
        target = output_dir / (stem + suffix + ".jpg")
        counter += 1
    return target


def collect_supported(paths):
    """Expand files and folders (recursively) into supported image paths."""
    found = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for base, _, names in os.walk(str(path)):
                for name in sorted(names):
                    if Path(name).suffix.lower() in SUPPORTED:
                        found.append(str(Path(base) / name))
        elif path.suffix.lower() in SUPPORTED:
            found.append(str(path))
    return found


register_heif_opener()


class ConverterWorker(QThread):
    # index (0-based), total, ok, detail
    file_done = Signal(int, int, bool, str)
    # success, failed, cancelled, details of failures
    finished_summary = Signal(int, int, bool, str)

    def __init__(self, files, output_dir, quality, keep_metadata):
        super().__init__()
        self.files = list(files)
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.keep_metadata = keep_metadata

    def run(self):
        total = len(self.files)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.finished_summary.emit(0, total, False, "OUTPUT: {}".format(exc))
            return
        success, failed, errors, cancelled = 0, 0, [], False
        for index, source in enumerate(self.files):
            if self.isInterruptionRequested():
                cancelled = True
                break
            source_path = Path(source)
            try:
                target = unique_target(self.output_dir, source_path.stem)
                with Image.open(str(source_path)) as opened:
                    exif = opened.info.get("exif")
                    icc = opened.info.get("icc_profile")
                    image = ImageOps.exif_transpose(opened)
                    if image.mode in ("RGBA", "LA"):
                        rgba = image.convert("RGBA")
                        background = Image.new("RGB", rgba.size, "white")
                        background.paste(rgba, mask=rgba.getchannel("A"))
                        image = background
                    elif image.mode != "RGB":
                        image = image.convert("RGB")
                    options = {"format": "JPEG", "quality": self.quality, "optimize": True}
                    if self.keep_metadata:
                        if exif:
                            options["exif"] = exif
                        if icc:
                            options["icc_profile"] = icc
                    image.save(str(target), **options)
                success += 1
                self.file_done.emit(index, total, True, target.name)
            except Exception as exc:
                failed += 1
                errors.append("{}: {}".format(source_path.name, exc))
                self.file_done.emit(index, total, False, str(exc))
        self.finished_summary.emit(success, failed, cancelled, "\n".join(errors))


class FileList(QListWidget):
    """List that shows a hint while it is empty."""

    def __init__(self):
        super().__init__()
        self.placeholder = ""

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0 and self.placeholder:
            painter = QPainter(self.viewport())
            painter.setPen(QColor("#8795a4"))
            painter.drawText(self.viewport().rect().adjusted(24, 24, -24, -24),
                             Qt.AlignCenter | Qt.TextWordWrap, self.placeholder)
            painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("ARJSOFT", "HEIC Converter")
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(resource_path("assets/arjsoft-icon.ico")))
        self.resize(860, 680)
        self.setMinimumSize(700, 600)
        self.setAcceptDrops(True)
        self.output_dir = str(self.settings.value(
            "output_dir", str(Path.home() / "Pictures" / "JPEG")))
        self.worker = None
        self.persian = self.settings.value("persian", 0) in (1, "1", True, "true")
        self.status_state = ("queue", "info", {"n": 0})
        self.about_dialog = None
        self.build_ui()
        self.apply_language()
        self.update_controls()

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self.logo_button = QPushButton()
        self.logo_button.setObjectName("brandLogoButton")
        self.logo_button.setFlat(True)
        self.logo_button.setCursor(Qt.PointingHandCursor)
        logo_pixmap = QPixmap(resource_path("assets/arjsoft-logo.png"))
        if not logo_pixmap.isNull():
            self.logo_button.setIcon(QIcon(logo_pixmap))
            self.logo_button.setIconSize(logo_pixmap.size().scaled(230, 66, Qt.KeepAspectRatio))
            self.logo_button.setFixedSize(240, 74)
        else:
            self.logo_button.setText("ARJSOFT")
        self.logo_button.clicked.connect(self.show_about)
        header.addWidget(self.logo_button)
        header.addStretch()
        self.language_button = QPushButton()
        self.language_button.setCursor(Qt.PointingHandCursor)
        self.language_button.clicked.connect(self.toggle_language)
        header.addWidget(self.language_button, 0, Qt.AlignTop)
        layout.addLayout(header)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        actions = QHBoxLayout()
        self.add_files_button = QPushButton()
        self.add_files_button.clicked.connect(self.add_files)
        self.add_folder_button = QPushButton()
        self.add_folder_button.clicked.connect(self.add_folder)
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button = QPushButton()
        self.clear_button.clicked.connect(self.clear_files)
        for button in (self.add_files_button, self.add_folder_button,
                       self.remove_button, self.clear_button):
            actions.addWidget(button)
        layout.addLayout(actions)

        self.file_list = FileList()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setAlternatingRowColors(False)
        self.file_list.itemSelectionChanged.connect(self.update_controls)
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.file_list)
        self.delete_shortcut.setContext(Qt.WidgetShortcut)
        self.delete_shortcut.activated.connect(self.remove_selected)
        layout.addWidget(self.file_list, 1)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        quality_row = QHBoxLayout()
        self.quality_label = QLabel()
        quality_row.addWidget(self.quality_label)
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setLayoutDirection(Qt.LeftToRight)
        quality_row.addWidget(self.quality_slider, 1)
        self.quality = QSpinBox()
        self.quality.setRange(1, 100)
        self.quality.setButtonSymbols(QSpinBox.NoButtons)
        self.quality.setAlignment(Qt.AlignCenter)
        self.quality.setLayoutDirection(Qt.LeftToRight)
        self.quality.setFixedWidth(60)
        quality_row.addWidget(self.quality)
        initial_quality = int(self.settings.value("quality", 95))
        self.quality.setValue(initial_quality)
        self.quality_slider.setValue(initial_quality)
        self.quality_slider.valueChanged.connect(self.quality.setValue)
        self.quality.valueChanged.connect(self.quality_slider.setValue)
        card_layout.addLayout(quality_row)
        self.quality_hint = QLabel()
        self.quality_hint.setObjectName("hint")
        card_layout.addWidget(self.quality_hint)

        self.metadata = QCheckBox()
        self.metadata.setChecked(self.settings.value("metadata", 1) in (1, "1", True, "true"))
        card_layout.addWidget(self.metadata)
        self.open_when_done = QCheckBox()
        self.open_when_done.setChecked(
            self.settings.value("open_when_done", 1) in (1, "1", True, "true"))
        card_layout.addWidget(self.open_when_done)
        layout.addWidget(card)

        output_row = QHBoxLayout()
        self.output_label = QLabel()
        output_row.addWidget(self.output_label)
        self.output_path = QLineEdit(self.output_dir)
        self.output_path.setReadOnly(True)
        self.output_path.setLayoutDirection(Qt.LeftToRight)
        self.output_path.setCursorPosition(0)
        output_row.addWidget(self.output_path, 1)
        self.output_button = QPushButton()
        self.output_button.clicked.connect(self.choose_output)
        output_row.addWidget(self.output_button)
        layout.addLayout(output_row)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("%v / %m")
        layout.addWidget(self.progress)

        status_row = QHBoxLayout()
        self.status = QLabel()
        self.status.setWordWrap(True)
        status_row.addWidget(self.status, 1)
        self.open_folder_button = QPushButton()
        self.open_folder_button.clicked.connect(self.open_output_folder)
        status_row.addWidget(self.open_folder_button)
        layout.addLayout(status_row)

        self.convert_button = QPushButton()
        self.convert_button.setObjectName("convert")
        self.convert_button.setProperty("busy", False)
        self.convert_button.setCursor(Qt.PointingHandCursor)
        self.convert_button.clicked.connect(self.on_convert_clicked)
        layout.addWidget(self.convert_button)

        self.footer = QLabel()
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

        self.setCentralWidget(root)
        self.setStyleSheet("""
            QWidget { color: #243447; font-family: 'Segoe UI', 'Tahoma'; font-size: 10pt; }
            QMainWindow, QWidget#root { background: #f5f7fa; }
            QLabel, QCheckBox { background: transparent; }
            QPushButton#brandLogoButton { background: transparent; border: 0; padding: 2px; }
            QPushButton#brandLogoButton:hover { background: #ffffff; border-radius: 8px; }
            QLabel#subtitle { color: #718096; }
            QLabel#hint { color: #8795a4; font-size: 9pt; }
            QLabel#footer { color: #8795a4; font-size: 8pt; padding-top: 4px; }
            QPushButton { background: white; border: 1px solid #d8e0e8;
                border-radius: 8px; padding: 9px 14px; }
            QPushButton:hover { border-color: #edc726; background: #fffaf0; }
            QPushButton:focus { border-color: #324d62; }
            QPushButton:pressed { background: #fdf3d0; }
            QPushButton:disabled { color: #a0aec0; background: #eef1f5; border-color: #e3e8ee; }
            QPushButton#convert { background: #324d62; color: white; border: 0;
                font-weight: 700; padding: 14px; font-size: 11pt; }
            QPushButton#convert:hover { background: #243f55; }
            QPushButton#convert:disabled { background: #a9b8c4; color: #eef1f5; }
            QPushButton#convert[busy="true"] { background: #b4533c; }
            QPushButton#convert[busy="true"]:hover { background: #9a432e; }
            QFrame#card { background: white; border: 1px solid #dce3ea; border-radius: 8px; }
            QFrame#card QLabel, QFrame#card QCheckBox { background: transparent; }
            QListWidget { background: white; border: 1px solid #dce3ea;
                border-radius: 8px; padding: 4px; outline: 0; }
            QListWidget::item { padding: 6px 8px; border-radius: 6px; }
            QListWidget::item:hover { background: #f1f5f9; }
            QListWidget::item:selected { background: #dff1ec; color: #243447; }
            QProgressBar { border: 0; background: #e5eaf0; border-radius: 8px;
                min-height: 16px; max-height: 16px; text-align: center; font-size: 8pt; }
            QProgressBar::chunk { background: #6bbda9; border-radius: 8px; }
            QSpinBox, QLineEdit { background: white; border: 1px solid #d8e0e8;
                border-radius: 6px; padding: 6px; }
            QLineEdit:read-only { background: #eef1f5; color: #4a5a6a; }
            QSlider::groove:horizontal { height: 6px; background: #e5eaf0; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #6bbda9; border-radius: 3px; }
            QSlider::handle:horizontal { background: #324d62; width: 16px;
                margin: -6px 0; border-radius: 8px; }
        """)

    # ------------------------------------------------------------ language
    def t(self, key, **kwargs):
        text = TEXT["fa" if self.persian else "en"][key]
        return text.format(**kwargs) if kwargs else text

    def apply_language(self):
        self.setLayoutDirection(Qt.RightToLeft if self.persian else Qt.LeftToRight)
        self.language_button.setText(self.t("lang_button"))
        self.subtitle.setText(self.t("subtitle"))
        self.add_files_button.setText(self.t("add_files"))
        self.add_folder_button.setText(self.t("add_folder"))
        self.remove_button.setText(self.t("remove"))
        self.clear_button.setText(self.t("clear"))
        self.quality_label.setText(self.t("quality"))
        self.quality_hint.setText(self.t("quality_hint"))
        self.metadata.setText(self.t("metadata"))
        self.open_when_done.setText(self.t("open_when_done"))
        self.output_label.setText(self.t("output"))
        self.output_button.setText(self.t("browse"))
        self.open_folder_button.setText(self.t("open_folder"))
        self.logo_button.setToolTip(self.t("about_tt"))
        self.footer.setText(self.t("footer", v=APP_VERSION))
        self.file_list.placeholder = self.t("empty")
        self.file_list.viewport().update()
        self.refresh_convert_button()
        self.render_status()
        self.update_about_dialog_text()

    def toggle_language(self):
        self.persian = not self.persian
        self.settings.setValue("persian", int(self.persian))
        self.apply_language()

    # -------------------------------------------------------------- status
    def set_status(self, key, kind="info", **kwargs):
        self.status_state = (key, kind, kwargs)
        self.render_status()

    def render_status(self):
        key, kind, kwargs = self.status_state
        self.status.setText(self.t(key, **kwargs))
        self.status.setStyleSheet("color: {};".format(STATUS_COLORS[kind]))

    def refresh_convert_button(self):
        busy = self.is_busy()
        self.convert_button.setText(self.t("cancel" if busy else "convert"))
        self.convert_button.setProperty("busy", busy)
        self.convert_button.style().unpolish(self.convert_button)
        self.convert_button.style().polish(self.convert_button)

    def is_busy(self):
        return self.worker is not None and self.worker.isRunning()

    def update_controls(self):
        busy = self.is_busy()
        has_files = self.file_list.count() > 0
        self.add_files_button.setEnabled(not busy)
        self.add_folder_button.setEnabled(not busy)
        self.remove_button.setEnabled(not busy and bool(self.file_list.selectedItems()))
        self.clear_button.setEnabled(not busy and has_files)
        self.output_button.setEnabled(not busy)
        self.quality.setEnabled(not busy)
        self.quality_slider.setEnabled(not busy)
        self.metadata.setEnabled(not busy)
        self.convert_button.setEnabled(busy or has_files)
        self.open_folder_button.setEnabled(Path(self.output_dir).is_dir())

    # --------------------------------------------------------------- about
    def update_about_dialog_text(self):
        if self.about_dialog is None:
            return
        self.about_dialog.setLayoutDirection(Qt.RightToLeft if self.persian else Qt.LeftToRight)
        self.about_dialog.setWindowTitle(self.t("about_title"))
        self.about_heading.setText(self.t("about_heading"))
        self.about_description.setText(self.t("about_desc"))
        self.about_website.setText("<a href='https://arjsoft.ir'>{}</a>".format(self.t("about_link")))
        self.about_close.setText(self.t("close"))

    def show_about(self):
        if self.about_dialog is None:
            self.about_dialog = QDialog(self)
            self.about_dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            self.about_dialog.setWindowIcon(QIcon(resource_path("assets/arjsoft-icon.ico")))
            self.about_dialog.setFixedWidth(430)
            dialog_layout = QVBoxLayout(self.about_dialog)
            dialog_layout.setContentsMargins(28, 24, 28, 22)
            dialog_layout.setSpacing(14)

            mark = QLabel()
            mark.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(resource_path("assets/arjsoft-logo.png"))
            if not pixmap.isNull():
                mark.setPixmap(pixmap.scaledToHeight(76, Qt.SmoothTransformation))
            dialog_layout.addWidget(mark)

            self.about_heading = QLabel()
            self.about_heading.setObjectName("aboutHeading")
            self.about_heading.setAlignment(Qt.AlignCenter)
            self.about_heading.setWordWrap(True)
            dialog_layout.addWidget(self.about_heading)

            self.about_description = QLabel()
            self.about_description.setWordWrap(True)
            self.about_description.setAlignment(Qt.AlignCenter)
            dialog_layout.addWidget(self.about_description)

            self.about_website = QLabel()
            self.about_website.setTextFormat(Qt.RichText)
            self.about_website.setOpenExternalLinks(True)
            self.about_website.setAlignment(Qt.AlignCenter)
            dialog_layout.addWidget(self.about_website)

            self.about_close = QPushButton()
            self.about_close.setObjectName("aboutClose")
            self.about_close.setDefault(True)
            self.about_close.clicked.connect(self.about_dialog.hide)
            dialog_layout.addWidget(self.about_close)
            self.about_dialog.setStyleSheet("""
                QDialog { background: #ffffff; color: #243447; }
                QLabel#aboutHeading { color: #324d62; font-size: 13pt; font-weight: 700; }
                QLabel { font-family: 'Segoe UI', 'Tahoma'; font-size: 10pt; }
                QPushButton#aboutClose { background: #324d62; color: white;
                    border: 0; border-radius: 8px; padding: 10px; font-weight: 600; }
                QPushButton#aboutClose:hover { background: #243f55; }
            """)
        self.update_about_dialog_text()
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()

    # --------------------------------------------------------- file queue
    def queued_paths(self):
        return [self.file_list.item(i).data(Qt.UserRole) for i in range(self.file_list.count())]

    def add_paths(self, paths):
        candidates = collect_supported(paths)
        known = set(self.queued_paths())
        added = 0
        for path in candidates:
            if path in known:
                continue
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.file_list.addItem(item)
            known.add(path)
            added += 1
        skipped = len(candidates) - added
        if added and skipped:
            self.set_status("added_skip", "info", n=added, s=skipped)
        elif added:
            self.set_status("added", "info", n=added)
        else:
            self.set_status("nothing_added", "warn")
        self.progress.setValue(0)
        self.update_controls()

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, self.t("dlg_files"), "", self.t("dlg_filter"))
        if paths:
            self.add_paths(paths)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t("dlg_folder"))
        if folder:
            self.add_paths([folder])

    def remove_selected(self):
        if self.is_busy():
            return
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.set_status("queue", "info", n=self.file_list.count())
        self.update_controls()

    def clear_files(self):
        self.file_list.clear()
        self.progress.setValue(0)
        self.set_status("queue", "info", n=0)
        self.update_controls()

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, self.t("dlg_output"), self.output_dir)
        if folder:
            self.output_dir = folder
            self.output_path.setText(folder)
            self.output_path.setCursorPosition(0)
            self.settings.setValue("output_dir", folder)
            self.update_controls()

    def open_output_folder(self):
        folder = Path(self.output_dir)
        if folder.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    # --------------------------------------------------------- drag & drop
    def dragEnterEvent(self, event):
        if not self.is_busy() and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if self.is_busy():
            return
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.add_paths(paths)
            event.acceptProposedAction()

    # ----------------------------------------------------------- conversion
    def on_convert_clicked(self):
        if self.is_busy():
            self.worker.requestInterruption()
            self.convert_button.setEnabled(False)
            return
        files = self.queued_paths()
        if not files:
            return
        self.settings.setValue("quality", self.quality.value())
        self.settings.setValue("metadata", int(self.metadata.isChecked()))
        self.settings.setValue("open_when_done", int(self.open_when_done.isChecked()))
        # Reset result marks from a previous run.
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setText(Path(item.data(Qt.UserRole)).name)
            item.setForeground(QBrush())
            item.setToolTip(item.data(Qt.UserRole))
        self.progress.setMaximum(len(files))
        self.progress.setValue(0)
        self.worker = ConverterWorker(files, self.output_dir,
                                      self.quality.value(), self.metadata.isChecked())
        self.worker.file_done.connect(self.on_file_done)
        self.worker.finished_summary.connect(self.on_finished)
        self.worker.start()
        self.set_status("converting", "info", c=1, t=len(files),
                        name=Path(files[0]).name)
        self.refresh_convert_button()
        self.update_controls()

    def on_file_done(self, index, total, ok, detail):
        item = self.file_list.item(index)
        name = Path(item.data(Qt.UserRole)).name
        if ok:
            item.setText("✓  " + name)
            item.setForeground(QBrush(QColor("#2f855a")))
            item.setToolTip(item.data(Qt.UserRole) + "\n→ " + detail)
        else:
            item.setText("✗  " + name)
            item.setForeground(QBrush(QColor("#c53030")))
            item.setToolTip(item.data(Qt.UserRole) + "\n" + detail)
        self.file_list.scrollToItem(item)
        self.progress.setMaximum(total)
        self.progress.setValue(index + 1)
        if index + 1 < total:
            next_name = Path(self.file_list.item(index + 1).data(Qt.UserRole)).name
            self.set_status("converting", "info", c=index + 2, t=total, name=next_name)

    def on_finished(self, success, failed, cancelled, details):
        self.worker.wait()
        total = self.file_list.count()
        self.refresh_convert_button()
        self.update_controls()
        if details.startswith("OUTPUT: "):
            self.set_status("output_failed", "error", e=details[len("OUTPUT: "):])
            return
        if cancelled:
            self.set_status("cancelled", "warn", ok=success, t=total)
        elif failed:
            self.set_status("done_fail", "warn", ok=success, fail=failed)
        else:
            self.set_status("done_ok", "ok", n=success)
        if failed:
            box = QMessageBox(QMessageBox.Warning, APP_NAME, self.t("done_fail", ok=success, fail=failed),
                              QMessageBox.Ok, self)
            box.setWindowTitle(self.t("warn_title"))
            box.setDetailedText(details[:5000])
            box.exec_()
        if success > 0 and not cancelled and self.open_when_done.isChecked():
            self.open_output_folder()

    # ---------------------------------------------------------------- exit
    def closeEvent(self, event):
        if self.is_busy():
            box = QMessageBox(QMessageBox.Question, APP_NAME, self.t("quit_confirm"),
                              QMessageBox.NoButton, self)
            yes = box.addButton(self.t("yes"), QMessageBox.YesRole)
            box.addButton(self.t("no"), QMessageBox.NoRole)
            box.exec_()
            if box.clickedButton() is not yes:
                event.ignore()
                return
            self.worker.requestInterruption()
            self.worker.wait(10000)
        self.settings.setValue("quality", self.quality.value())
        self.settings.setValue("metadata", int(self.metadata.isChecked()))
        self.settings.setValue("open_when_done", int(self.open_when_done.isChecked()))
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
