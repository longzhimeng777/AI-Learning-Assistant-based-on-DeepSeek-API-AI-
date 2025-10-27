import argparse
import csv
import random
from pathlib import Path

import numpy as np
import pandas as pd

LABEL_MAP = {
    "concept": "概念解释",
    "learning": "学习路径建议",
    "code": "示例代码",
    "debug": "报错排查",
    "setup": "工具安装配置",
    "assignment": "作业/考试题解读",
    "review": "复习总结/要点",
    "resource": "资料推荐",
}

SAMPLE_ROWS = [
    ("什么是交叉熵？", "概念解释", "synthetic", "zh"),
    ("How to install CUDA on Ubuntu?", "工具安装配置", "synthetic", "en"),
]


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows):
    ensure_dir(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "source", "lang"])
        for row in rows:
            writer.writerow(row)


def generate_v1(path: Path):
    rows = []
    for text, label, source, lang in SAMPLE_ROWS:
        rows.append((text, label, source, lang))
    write_csv(path, rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("ml/data/intent_v1.csv"))
    args = parser.parse_args()
    generate_v1(args.output)


if __name__ == "__main__":
    main()
