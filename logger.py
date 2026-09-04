import os
import sys
from datetime import datetime, timezone

class Logger:
    @staticmethod
    def _get_timestamp() -> str:
        # Match TS toISOString() format, e.g. "2026-08-04T10:39:49.123Z"
        # We can format it with datetime.now(timezone.utc)
        now = datetime.now(timezone.utc)
        # Use strftime to get precise milliseconds formatting
        return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def info(message: str, *args) -> None:
        if os.environ.get("SILENT") == "true":
            return
        extra = f" {' '.join(map(str, args))}" if args else ""
        print(f"\033[36m[{Logger._get_timestamp()}] [INFO]\033[0m {message}{extra}")
        sys.stdout.flush()

    @staticmethod
    def success(message: str, *args) -> None:
        if os.environ.get("SILENT") == "true":
            return
        extra = f" {' '.join(map(str, args))}" if args else ""
        print(f"\033[32m[{Logger._get_timestamp()}] [SUCCESS]\033[0m {message}{extra}")
        sys.stdout.flush()

    @staticmethod
    def warning(message: str, *args) -> None:
        if os.environ.get("SILENT") == "true":
            return
        extra = f" {' '.join(map(str, args))}" if args else ""
        print(f"\033[33m[{Logger._get_timestamp()}] [WARNING]\033[0m {message}{extra}", file=sys.stderr)
        sys.stderr.flush()

    @staticmethod
    def error(message: str, error = None) -> None:
        if os.environ.get("SILENT") == "true":
            return
        err_msg = f" {error}" if error is not None else ""
        print(f"\033[31m[{Logger._get_timestamp()}] [ERROR]\033[0m {message}{err_msg}", file=sys.stderr)
        sys.stderr.flush()

    @staticmethod
    def debug(message: str, *args) -> None:
        if os.environ.get("SILENT") == "true":
            return
        if os.environ.get("DEBUG") == "true":
            extra = f" {' '.join(map(str, args))}" if args else ""
            print(f"\033[90m[{Logger._get_timestamp()}] [DEBUG]\033[0m {message}{extra}")
            sys.stdout.flush()
