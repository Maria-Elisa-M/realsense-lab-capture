"""Entry point for the RealSense Lab Video Capture application."""
import sys
import logging
import logging.handlers
from pathlib import Path

# Bootstrap logging before any app imports
def _setup_logging() -> None:
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Rotating file handler: 5 MB × 3 backups
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Console handler (INFO and above)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)


_setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    from app.database.schema import init_db
    from app.ui.main_window import MainWindow

    # Initialize database (creates tables and seeds defaults if needed)
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as exc:
        logger.critical("Failed to initialize database: %s", exc)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("RealSense Lab Capture")
    app.setOrganizationName("Lab")

    # Load stylesheet
    qss_path = Path(__file__).parent / "app" / "ui" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        logger.debug("Stylesheet loaded from %s", qss_path)

    window = MainWindow()
    window.show()

    logger.info("Application started.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
