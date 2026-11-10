import os
import sys
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from PySide2.QtCore import Qt, QThread, Signal, QUrl
from PySide2.QtGui import QPixmap, QIcon, QDesktopServices
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QFileDialog, QProgressBar,
    QSpinBox, QGroupBox, QMessageBox, QCheckBox, QAbstractItemView, QDialog
)

APP_NAME = "ARJSOFT HEIC Converter"
APP_VERSION = "1.0.0"
SUPPORTED = {".heic", ".heif"}


def resource_path(relative_path):
    """Resolve bundled assets in both source and PyInstaller builds."""
    base_path = getattr(sys, "_MEIPASS", str(Path(__file__).resolve().parent))
    return str(Path(base_path) / relative_path)


register_heif_opener()


class ConverterWorker(QThread):
    progress = Signal(int, int, str)
    finished_summary = Signal(int, int, str)

    def __init__(self, files, output_dir, quality, keep_metadata):
        super().__init__()
        self.files = files
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.keep_metadata = keep_metadata

    def run(self):
        success, failed, messages = 0, 0, []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for index, source in enumerate(self.files, 1):
            try:
                source_path = Path(source)
                target = self.output_dir / (source_path.stem + ".jpg")
                if target.exists():
                    target = self.output_dir / (source_path.stem + "_converted.jpg")
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
                result = "OK  " + source_path.name
            except Exception as exc:
                failed += 1
                result = "ERROR  {}: {}".format(Path(source).name, exc)
            messages.append(result)
            self.progress.emit(index, len(self.files), result)
        self.finished_summary.emit(success, failed, "\n".join(messages))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(resource_path("assets/arjsoft-icon.ico")))
        self.resize(840, 640)
        self.files = []
        self.output_dir = str(Path.home() / "Pictures" / "JPEG")
        self.worker = None
        self.persian = False
        self.build_ui()
        self.apply_language()

    def build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(14)
        header = QHBoxLayout()
        self.logo_button = QPushButton()
        self.logo_button.setObjectName("brandLogoButton")
        self.logo_button.setFlat(True)
        self.logo_button.setCursor(Qt.PointingHandCursor)
        self.logo_button.setToolTip("About ARJSOFT")
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
        self.language_button = QPushButton("فارسی")
        self.language_button.clicked.connect(self.toggle_language)
        header.addWidget(self.language_button)
        layout.addLayout(header)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
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

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.file_list, 1)

        settings = QGroupBox()
        settings_layout = QHBoxLayout(settings)
        self.quality_label = QLabel()
        settings_layout.addWidget(self.quality_label)
        self.quality = QSpinBox()
        self.quality.setRange(1, 100)
        self.quality.setValue(95)
        settings_layout.addWidget(self.quality)
        self.metadata = QCheckBox()
        self.metadata.setChecked(True)
        settings_layout.addWidget(self.metadata)
        settings_layout.addStretch()
        layout.addWidget(settings)

        output_row = QHBoxLayout()
        self.output_label = QLabel()
        output_row.addWidget(self.output_label)
        self.output_path = QLabel(self.output_dir)
        self.output_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        output_row.addWidget(self.output_path, 1)
        self.output_button = QPushButton()
        self.output_button.clicked.connect(self.choose_output)
        output_row.addWidget(self.output_button)
        layout.addLayout(output_row)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.convert_button = QPushButton()
        self.convert_button.setObjectName("convert")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        self.about_dialog = None

        self.footer = QLabel("ARJSOFT  •  Version " + APP_VERSION)
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

        self.setCentralWidget(root)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #f5f7fa; color: #243447;
                font-family: 'Segoe UI'; font-size: 10pt; }
            QPushButton#brandLogoButton { background: transparent; border: 0; padding: 2px; }
            QPushButton#brandLogoButton:hover { background: #ffffff; border-radius: 8px; }
            QLabel#subtitle { color: #718096; }
            QLabel#footer { color: #8795a4; font-size: 8pt; padding-top: 4px; }
            QPushButton { background: white; border: 1px solid #d8e0e8;
                border-radius: 8px; padding: 10px 14px; }
            QPushButton:hover { border-color: #edc726; background: #fffaf0; }
            QPushButton#convert { background: #324d62; color: white;
                font-weight: 700; padding: 14px; font-size: 11pt; }
            QPushButton#convert:hover { background: #243f55; }
            QListWidget, QGroupBox { background: white; border: 1px solid #dce3ea;
                border-radius: 8px; padding: 8px; }
            QProgressBar { border: 0; background: #e5eaf0; border-radius: 5px;
                height: 12px; text-align: center; }
            QProgressBar::chunk { background: #6bbda9; border-radius: 5px; }
            QSpinBox { background: white; border: 1px solid #d8e0e8;
                border-radius: 5px; padding: 5px; }
        """)

    def apply_language(self):
        if self.persian:
            self.setLayoutDirection(Qt.RightToLeft)
            values = ("English", "تبدیل سریع و آفلاین تصاویر HEIC و HEIF به JPEG",
                      "افزودن عکس‌ها", "افزودن پوشه", "حذف انتخاب‌شده",
                      "پاک کردن فهرست", "کیفیت JPEG:", "حفظ اطلاعات عکس (EXIF)",
                      "پوشه خروجی:", "انتخاب پوشه", "شروع تبدیل")
            self.logo_button.setToolTip("درباره ARJSOFT")
            self.update_about_dialog_text()
            self.status.setText("تعداد تصاویر: {}".format(len(self.files)))
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            values = ("فارسی", "Fast, offline conversion of HEIC and HEIF photos to JPEG",
                      "Add Photos", "Add Folder", "Remove Selected", "Clear List",
                      "JPEG quality:", "Preserve photo metadata (EXIF)",
                      "Output folder:", "Browse", "Convert to JPEG")
            self.logo_button.setToolTip("About ARJSOFT")
            self.update_about_dialog_text()
            self.status.setText("{} image(s) in queue".format(len(self.files)))
        widgets = (self.language_button, self.subtitle, self.add_files_button,
                   self.add_folder_button, self.remove_button, self.clear_button,
                   self.quality_label, self.metadata, self.output_label,
                   self.output_button, self.convert_button)
        for widget, value in zip(widgets, values):
            widget.setText(value)

    def update_about_dialog_text(self):
        if self.about_dialog is None:
            return
        if self.persian:
            self.about_dialog.setWindowTitle("درباره ARJSOFT")
            self.about_heading.setText("نرم‌افزارهای کاربردی، ساده و قابل‌اعتماد")
            self.about_description.setText(
                "ARJSOFT با هدف طراحی و ارائه نرم‌افزارهای کاربردی و آسان برای استفاده فعالیت می‌کند. "
                "این برنامه یکی از محصولات ARJSOFT است و تبدیل تصاویر شما را به‌صورت آفلاین "
                "و مستقیماً روی رایانه انجام می‌دهد.")
            self.about_website.setText("<a href='https://arjsoft.ir'>مشاهده وب‌سایت رسمی ARJSOFT</a>")
            self.about_close.setText("بستن")
        else:
            self.about_dialog.setWindowTitle("About ARJSOFT")
            self.about_heading.setText("Practical, simple and reliable software")
            self.about_description.setText(
                "ARJSOFT creates practical software that is simple to use and reliable. "
                "This app is part of the ARJSOFT collection and converts your photos offline, "
                "directly on your computer.")
            self.about_website.setText("<a href='https://arjsoft.ir'>Visit the official ARJSOFT website</a>")
            self.about_close.setText("Close")

    def show_about(self):
        if self.about_dialog is None:
            self.about_dialog = QDialog(self)
            self.about_dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            self.about_dialog.setWindowIcon(QIcon(resource_path("assets/arjsoft-icon.ico")))
            self.about_dialog.setFixedWidth(410)
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
            self.about_close.clicked.connect(self.about_dialog.hide)
            dialog_layout.addWidget(self.about_close)
            self.about_dialog.setStyleSheet("""
                QDialog { background: #ffffff; color: #243447; }
                QLabel#aboutHeading { color: #324d62; font-size: 13pt; font-weight: 700; }
                QLabel { font-family: 'Segoe UI'; font-size: 10pt; }
                QPushButton#aboutClose { background: #324d62; color: white;
                    border: 0; border-radius: 8px; padding: 10px; font-weight: 600; }
                QPushButton#aboutClose:hover { background: #243f55; }
            """)
        self.update_about_dialog_text()
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()

    def toggle_language(self):
        self.persian = not self.persian
        self.apply_language()

    def add_paths(self, paths):
        known = set(self.files)
        for path in paths:
            p = str(Path(path))
            if Path(p).suffix.lower() in SUPPORTED and p not in known:
                self.files.append(p)
                self.file_list.addItem(p)
                known.add(p)
        self.apply_language()

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select HEIC/HEIF photos", "", "HEIC/HEIF Images (*.heic *.heif)")
        self.add_paths(paths)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            paths = [str(Path(base) / name) for base, _, names in os.walk(folder)
                     for name in names if Path(name).suffix.lower() in SUPPORTED]
            self.add_paths(paths)

    def remove_selected(self):
        indexes = sorted([self.file_list.row(x) for x in self.file_list.selectedItems()],
                         reverse=True)
        for index in indexes:
            self.file_list.takeItem(index)
            del self.files[index]
        self.apply_language()

    def clear_files(self):
        self.files = []
        self.file_list.clear()
        self.progress.setValue(0)
        self.apply_language()

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder",
                                                   self.output_dir)
        if folder:
            self.output_dir = folder
            self.output_path.setText(folder)

    def start_conversion(self):
        if not self.files:
            QMessageBox.information(self, APP_NAME,
                "Please add HEIC/HEIF images first." if not self.persian
                else "ابتدا تصاویر را اضافه کنید.")
            return
        self.convert_button.setEnabled(False)
        self.progress.setMaximum(len(self.files))
        self.progress.setValue(0)
        self.worker = ConverterWorker(self.files, self.output_dir,
                                      self.quality.value(), self.metadata.isChecked())
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_summary.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, current, total, message):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.status.setText("{}/{}  {}".format(current, total, message))

    def on_finished(self, success, failed, details):
        self.convert_button.setEnabled(True)
        summary = ("Successful: {}    Failed: {}".format(success, failed)
                   if not self.persian else "موفق: {}    ناموفق: {}".format(success, failed))
        QMessageBox.information(self, APP_NAME, summary + "\n\n" + details[:5000])
        self.status.setText(summary)
        if success > 0 and Path(self.output_dir).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_dir))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
