from pathlib import Path
from datetime import datetime
import threading
import sys
import traceback

class Logger:
    def __init__(self, logfile: str | Path | None = None):
        # default logfile is backend/backend.log (next to this file)
        self.logfile = Path(logfile) if logfile else Path(__file__).resolve().parent / "backend.log"

        self.lock = threading.Lock()
        try:
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            # ensure file exists
            self.logfile.touch(exist_ok=True)
        except Exception:
            # if we can't create the file, continue and still print to stdout
            pass

    def _format(self, level: str, msg: str) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{ts} {level} {msg}"

    def _write(self, level: str, msg: object):
        try:
            text = str(msg)
        except Exception:
            text = "<unrepresentable message>"
        line = self._format(level, text)
        # always print to stdout
        print(line)
        # append to file
        try:
            with self.lock:
                with self.logfile.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
        except Exception:
            # if file write fails, print the error to stderr
            print(self._format("[ERROR]", f"Failed to write log to {self.logfile}: {traceback.format_exc()}"), file=sys.stderr)

    def info(self, msg: object):
        self._write("[INFO]", msg)

    def error(self, msg: object):
        self._write("[ERROR]", msg)

    def mqtt(self, msg: object):
        self._write("[MQTT]", msg)

    def order(self, msg: object):
        self._write("[ORDER]", msg)

    def debug(self, msg: object):
        self._write("[DEBUG]", msg)


# module-level default logger instance
logger = Logger()

# convenience functions
def info(msg: object):
    logger.info(msg)

def error(msg: object):
    logger.error(msg)

def mqtt(msg: object):
    logger.mqtt(msg)

def order(msg: object):
    logger.order(msg)

def debug(msg: object):
    logger.debug(msg)

def set_logfile(path: str | Path):
    """Switch the logfile used by the module-level logger."""
    global logger
    logger 