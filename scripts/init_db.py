"""Initialize the SQLite store. Run: python scripts/init_db.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from jobagent.config import get_settings  # noqa: E402
from jobagent.store import Store  # noqa: E402


def main() -> None:
    settings = get_settings()
    store = Store(settings.db_path)
    store.init_schema()
    store.close()
    print(f"Initialized store at {settings.db_path}")


if __name__ == "__main__":
    main()
