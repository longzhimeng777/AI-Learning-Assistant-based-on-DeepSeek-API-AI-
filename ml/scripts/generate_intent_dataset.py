#!/usr/bin/env python3
"""Generate intent classification datasets (v1/v2) with rules and synthetic augmentation."""

import argparse
import json
import random
from pathlib import Path

import pandas as pd

LABELS = [
    "概念解释",
    "学习路径建议",
    "示例代码",
    "报错排查",
    "工具安装配置",
    "作业/考试题解读",
    "复习总结/要点",
    "资料推荐",
]

BASE_SAMPLES = {
    "概念解释": [
        "什么是交叉熵？",
        "Explain the bias-variance tradeoff in ML",
        "为什么L2正则化能缓解过拟合？",
    ],
    "学习路径建议": [
        "零基础如何学习机器学习？",
        "How to plan a 3-month deep learning study?",
        "Python 入门到进阶的步骤？",
    ],
    "示例代码": [
        "给出 PyTorch ResNet18 的示例代码",
        "Show sklearn logistic regression example",
        "How to implement quicksort in Python?",
    ],
    "报错排查": [
        "训练时报错 CUDA out of memory 怎么办？",
        "How to fix ModuleNotFoundError: numpy?",
        "NullPointerException 调试步骤",
    ],
    "工具安装配置": [
        "pip install torch 失败如何解决？",
        "Install CUDA on Ubuntu 22.04",
        "conda 创建虚拟环境并安装 requirements",
    ],
    "作业/考试题解读": [
        "这道微积分题该如何下手？",
        "How to solve this probability homework?",
        "数学应用题解题思路",
    ],
    "复习总结/要点": [
        "总结 SVM 的核心要点",
        "Key takeaways of gradient descent",
        "Transformer 结构复习提纲",
    ],
    "资料推荐": [
        "推荐机器学习学习资料",
        "Best books to learn statistics",
        "哪里可以找到优质 NLP 课程？",
    ],
}


def augment_text(text: str) -> str:
    suffixes = [
        " 请详细一些",
        " 给个例子",
        " 有哪些常见错误?",
        " 用中文说明",
        " Why?",
    ]
    if random.random() < 0.3:
        return text + random.choice(suffixes)
    return text


def generate_dataset(size_per_label: int, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    for label, samples in BASE_SAMPLES.items():
        for _ in range(size_per_label):
            text = augment_text(random.choice(samples))
            lang = "zh" if "?" in text or any(ord(c) > 127 for c in text) else "en"
            rows.append({
                "text": text,
                "label": label,
                "source": "synthetic",
                "lang": lang,
            })
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=120, help="Number of samples per label")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate_dataset(args.size, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
