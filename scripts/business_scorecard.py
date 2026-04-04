from __future__ import annotations

from business_lib import read_tasks, write_scorecard

if __name__ == "__main__":
    print(write_scorecard(read_tasks()))
