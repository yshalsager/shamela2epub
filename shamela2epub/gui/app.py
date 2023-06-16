from functools import partial
from pathlib import Path
from typing import cast

import click
import qdarktheme
from gevent import Greenlet, joinall, spawn
from PyQt5 import uic
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
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
from shamela2epub.models.book_html_page import BookHTMLPage


class QBookDownloader(BookDownloader):
    def __init__(self, url: str) -> None:
        super().__init__(url, connections=10)
        self.progress: pyqtSignal = pyqtSignal(str)

    def download_page(self, page_number: int) -> BookHTMLPage:
        with self._sem:
            book_html_page = BookHTMLPage(f"{self.url}/{page_number}")
            self.progress.emit(
                f"تحميل الصفحة {page_number} من {self.epub_book.pages_count}"
            )
        return book_html_page

    def download(self) -> None:
        self.progress.emit(f"تحميل الصفحة 1 من {self.epub_book.pages_count}")
        self.create_first_page()
        jobs = [
            spawn(self.download_page, page_number)
            for page_number in range(2, self.epub_book.pages_count + 1)
        ]
        job: Greenlet
        for job in joinall(jobs):
            self.epub_book.add_page(job.value)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    downloaded = pyqtSignal(Path)


class Worker(QRunnable):
    def __init__(self, downloader: QBookDownloader, output: str) -> None:
        super().__init__()
        self.downloader: QBookDownloader = downloader
        self.output: str = output
        self.signals = WorkerSignals()

    def run(self) -> None:
        """Process the book."""
        self.downloader.progress = self.signals.progress
        self.downloader.create_info_page()
        self.signals.progress.emit(
            f"بدء العمل على كتاب {self.downloader.book_info_page.title} لمؤلفه {self.downloader.book_info_page.author}"
        )
        self.downloader.download()
        self.signals.progress.emit("حفظ الكتاب")
        output_book = self.downloader.save_book(self.output)
        self.signals.downloaded.emit(output_book)
        self.signals.finished.emit()


class App(QMainWindow):
    download: QPushButton
    statusbar: QLabel
    url_form: QLabel

    def __init__(self) -> None:
        """GUI App constructor."""
        super().__init__()
        self.thread_pool: QThreadPool = QThreadPool()

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
        return cast(str, output_directory)

    def report_progress(self, progress: str) -> None:
        self.update_statusbar(progress)

    def on_finish(self) -> None:
        self.download.setEnabled(True)
        self.url_form.setEnabled(True)
        self.url_form.setText("")
        self.update_statusbar("اكتمل التحميل!")

    def run(self) -> None:
        self.download.setDisabled(True)
        self.url_form.setDisabled(True)
        if not self.url_form.text():
            self.show_error_message("لم تدخل رابط الكتاب بعد!")
            self.download.setEnabled(True)
            self.url_form.setDisabled(False)
            return
        downloader = QBookDownloader(self.url_form.text())
        if not downloader.valid:
            self.show_error_message("رابط غير صحيح!")
            self.download.setEnabled(True)
            return
        output = self.choose_output_directory()
        if not output:
            self.download.setEnabled(True)
            return
        self.update_statusbar("تحليل معلومات الرابط")
        # Create a qrunner and start it in a thread
        worker = Worker(downloader, output)
        self.thread_pool.start(worker)
        # Connect signals and slots
        worker.signals.progress.connect(self.report_progress)
        worker.signals.downloaded.connect(self.on_process_complete)
        # Final resets
        worker.signals.finished.connect(self.on_finish)

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
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    gui()
