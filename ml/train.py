import os
import argparse
import json
import random
import hashlib
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score

import mlflow
import mlflow.sklearn

DEFAULT_LABELS = [
    "概念解释",
    "学习路径建议",
    "示例代码",
    "报错排查",
    "工具安装配置",
    "作业/考试题解读",
    "复习总结/要点",
    "资料推荐",
]


def sha_short(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]


def autosample_dataset(n_per_label: int = 30, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    base = {
        "概念解释": [
            "什么是交叉熵？通俗解释一下",
            "Explain what is overfitting in machine learning",
            "为什么L2正则化能缓解过拟合？",
        ],
        "学习路径建议": [
            "零基础如何学习机器学习？给出学习路径",
            "How to learn deep learning in 3 months?",
            "Python 入门到进阶的建议",
        ],
        "示例代码": [
            "请给出 PyTorch 实现 ResNet18 的示例代码",
            "Show an example of sklearn logistic regression",
            "如何用python实现快速排序？",
        ],
        "报错排查": [
            "训练时报错 CUDA out of memory 怎么办？",
            "How to fix ModuleNotFoundError: numpy?",
            "NullPointerException how to debug",
        ],
        "工具安装配置": [
            "pip 安装 torch 失败，如何解决？",
            "How to install CUDA on Ubuntu 22.04",
            "conda 创建虚拟环境并安装requirements",
        ],
        "作业/考试题解读": [
            "这道微积分题该如何下手？",
            "How to solve this probability question?",
            "数学应用题求解思路",
        ],
        "复习总结/要点": [
            "帮我总结SVM的核心要点",
            "Key takeaways of gradient descent",
            "Transformer 结构复习提纲",
        ],
        "资料推荐": [
            "推荐系统学习资料和最佳实践",
            "Best books to learn statistics",
            "哪里可以找到优质的NLP课程？",
        ],
    }
    rows: List[Tuple[str, str]] = []
    for label, seeds in base.items():
        for _ in range(n_per_label):
            text = random.choice(seeds)
            # 轻度扰动
            if random.random() < 0.3:
                text = text + random.choice([" 请详细一些", " 给个例子", " 有什么坑?", " Why?"])
            rows.append((text, label))
    random.shuffle(rows)
    df = pd.DataFrame(rows, columns=["text", "label"])  # type: ignore
    return df


def load_dataset(path: str | None, autosample: bool) -> Tuple[pd.DataFrame, str]:
    if autosample or not path:
        df = autosample_dataset()
        ds_id = sha_short("autosample-" + str(len(df)))
        return df, ds_id
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".jsonl" or ext == ".json":
        df = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported dataset format: {ext}")
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns")
    df = df.dropna(subset=["text", "label"]).astype({"text": str, "label": str})
    # 简要生成版本ID（基于行数与首尾hash）
    head = df.head(5).to_json(orient="records", force_ascii=False)
    tail = df.tail(5).to_json(orient="records", force_ascii=False)
    ds_id = sha_short(f"{len(df)}-{head}-{tail}")
    return df, ds_id


def train_and_log(df: pd.DataFrame, exp_name: str, run_name: str, max_iter: int = 200):
    X = df["text"].astype(str).tolist()
    y = df["label"].astype(str).tolist()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=30000, ngram_range=(1, 2)) ),
        ("clf", LogisticRegression(max_iter=max_iter, n_jobs=None)),
    ])

    mlflow.set_experiment(exp_name)
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "model": "LogisticRegression",
            "tfidf_max_features": 30000,
            "tfidf_ngram": "1-2",
            "max_iter": max_iter,
        })
        # 代码与数据版本
        git_sha = os.getenv("GITHUB_SHA") or os.popen("git rev-parse --short HEAD").read().strip() or "unknown"
        mlflow.set_tag("git_sha", git_sha)

        labels = sorted(list(set(y)))
        mlflow.log_text("\n".join(labels), artifact_file="labels.txt")

        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="macro")
        mlflow.log_metrics({"accuracy": acc, "f1_macro": f1})

        # 保存模型
        mlflow.sklearn.log_model(pipe, artifact_path="model")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None, help="Path to CSV/JSONL with columns text,label")
    parser.add_argument("--exp", type=str, default="ai-learning-intent")
    parser.add_argument("--run", type=str, default=None)
    parser.add_argument("--autosample", action="store_true")
    parser.add_argument("--max_iter", type=int, default=200)
    args = parser.parse_args()

    df, ds_id = load_dataset(args.data, args.autosample)

    run_name = args.run or (f"intent_{'autosample' if args.autosample else os.path.basename(args.data)}_{ds_id}")

    # 记录数据版本信息
    mlflow.set_tag("dataset_version", ds_id)
    mlflow.set_tag("dataset_rows", str(len(df)))

    train_and_log(df, args.exp, run_name, max_iter=args.max_iter)


if __name__ == "__main__":
    main()
