from functools import partial
from pathlib import Path

import click
from PyQt5 import uic
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
)

from shamela2epub import PKG_DIR
from shamela2epub.main import BookDownloader
from shamela2epub.misc.utils import browse_file_directory


class App(QMainWindow):
    download: QPushButton
    statusbar: QLabel
    url_form: QLabel

    def __init__(self) -> None:
        """GUI App constructor."""
        super().__init__()

        uic.loadUi(f"{PKG_DIR}/gui/ui.ui", self)
        # self.setWindowIcon(QIcon(f"{WORK_DIR}/assets/books-duotone-512.png"))
        self.center()
        self.download.clicked.connect(self.run)
        self.statusbar.setText("جاهز")

    def update_statusbar(self, text: str) -> None:
        self.statusbar.setText(text)
        self.statusbar.repaint()

    def on_process_complete(self, filepath: Path) -> None:
        message_box = QMessageBox(
            QMessageBox.Information,
            "اكتمل التحميل",
            "هل تريد فتح الكتاب الآن؟",
            parent=self,
        )
        open_path = QPushButton("فتح")
        message_box.addButton(QPushButton("لا"), QMessageBox.NoRole)
        message_box.addButton(open_path, QMessageBox.ActionRole)
        open_path.clicked.connect(partial(browse_file_directory, filepath))
        message_box.exec_()

    def show_error_message(self, message: str) -> None:
        message_box = QMessageBox(
            QMessageBox.Critical,
            "خطأ",
            message,
            parent=self,
        )
        message_box.addButton(QPushButton("حسنا"), QMessageBox.YesRole)
        message_box.exec_()

    def choose_output_directory(self) -> str:
        """Opens select file Dialog."""
        output_directory = QFileDialog().getExistingDirectory(
            self, "اختر مكان حفظ الكتاب"
        )
        if not output_directory:
            self.show_error_message("لم تختر مكانا لحفظ الكتاب!")
            return ""
        return output_directory

    def run(self) -> None:
        self.download.setDisabled(True)
        if not self.url_form.text():
            self.show_error_message("لم تدخل رابط الكتاب بعد!")
            self.download.setEnabled(True)
            return
        downloader = BookDownloader(self.url_form.text())
        if not downloader.valid:
            self.show_error_message("رابط غير صحيح!")
            self.download.setEnabled(True)
            return
        output = self.choose_output_directory()
        if not output:
            self.download.setEnabled(True)
            return
        self.update_statusbar("تحليل معلومات الرابط")
        downloader.create_info_page()
        self.update_statusbar(
            f"بدء العمل على كتاب {downloader.book_info_page.title} لمؤلفه {downloader.book_info_page.author}"
        )
        downloader.create_first_page()
        self.update_statusbar("إنشاء الصفحة الأولى")
        for page in downloader.download():
            self.update_statusbar(f"إنشاء الصفحة {page}")
        self.update_statusbar("حفظ الكتاب")
        output_book = downloader.save_book(output)
        self.on_process_complete(output_book)
        self.download.setEnabled(True)

    def center(self) -> None:
        """Dynamically center the window in screen."""
        # https://gist.github.com/saleph/163d73e0933044d0e2c4
        # geometry of the main window
        window = self.frameGeometry()
        # center point of screen
        center_point = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        window.moveCenter(center_point)
        # top left of rectangle becomes top left of window centering it
        self.move(window.topLeft())


@click.command()
def gui() -> None:
    """Run Shamela2Epub GUI."""
    import sys

    app = QApplication(sys.argv)
    window = App()
    QFontDatabase.addApplicationFont(f"{PKG_DIR}/assets/NotoNaskhArabic-Regular.ttf")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    gui()
