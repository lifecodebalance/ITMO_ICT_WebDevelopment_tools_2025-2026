"""Convenience launcher for all experiments in laboratory work 2."""

from __future__ import annotations

import argparse

from lr2.config import DEFAULT_URLS, DEFAULT_WORKERS, SUM_UPPER_BOUND
from lr2.task1.run_benchmark import main as run_task1_main
from lr2.task2.run_benchmark import main as run_task2_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run both laboratory experiments (task 1 and task 2)."
    )
    parser.add_argument("--show-defaults", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.show_defaults:
        print(f"DEFAULT_WORKERS = {DEFAULT_WORKERS}")
        print(f"SUM_UPPER_BOUND = {SUM_UPPER_BOUND}")
        print(f"DEFAULT_URLS = {DEFAULT_URLS}")
        return

    print("Use dedicated commands:")
    print("python -m lr2.task1.run_benchmark")
    print("python -m lr2.task2.run_benchmark")
    print("This launcher is informational only.")


if __name__ == "__main__":
    main()
