"""Entry point for the RealSense Lab Video Capture application."""
import sys
import logging
import logging.handlers
from pathlib import Path


def _setup_logging() -> None:
    from app.utils.app_dirs import LOG_DIR
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "app.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Rotating file handler: 5 MB x 3 backups
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
    from app.database.schema import init_db
    from app.ui.main_window import MainWindow

    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as exc:
        logger.critical("Failed to initialize database: %s", exc)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("RealSense Lab Capture")
    app.setOrganizationName("Lab")

    # Stylesheet is bundled inside the frozen app — use __file__ path
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
