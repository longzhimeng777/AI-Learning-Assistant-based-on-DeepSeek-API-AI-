import argparse
import hashlib
import json
import os
import random
from typing import List, Tuple

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

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


def sha_short(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]


def autosample_dataset(n_per_label: int = 30, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)

    base_samples = {
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

    rows: List[Tuple[str, str, str, str]] = []
    suffix_options = [" 请详细一些", " 给个例子", " 有什么坑?", " Why?"]

    for label, seeds in base_samples.items():
        for _ in range(n_per_label):
            text = random.choice(seeds)
            if random.random() < 0.3:
                text = f"{text}{random.choice(suffix_options)}"
            language = "zh" if any(ord(char) > 127 for char in text) else "en"
            rows.append((text, label, "synthetic", language))

    random.shuffle(rows)
    dataframe = pd.DataFrame(rows, columns=["text", "label", "source", "lang"])
    return dataframe


def load_dataset(path: str | None, autosample: bool) -> Tuple[pd.DataFrame, str]:
    if autosample or not path:
        dataframe = autosample_dataset()
        dataset_id = sha_short(f"autosample-{len(dataframe)}")
        return dataframe, dataset_id

    extension = os.path.splitext(path)[1].lower()

    if extension == ".csv":
        dataframe = pd.read_csv(path)
    elif extension in {".jsonl", ".json"}:
        dataframe = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported dataset format: {extension}")

    if "text" not in dataframe.columns or "label" not in dataframe.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns")

    dataframe = dataframe.dropna(subset=["text", "label"]).astype(
        {"text": str, "label": str}
    )

    head_preview = dataframe.head(5).to_json(orient="records", force_ascii=False)
    tail_preview = dataframe.tail(5).to_json(orient="records", force_ascii=False)
    dataset_id = sha_short(f"{len(dataframe)}-{head_preview}-{tail_preview}")

    return dataframe, dataset_id


def train_and_log(
    dataframe: pd.DataFrame, experiment_name: str, run_name: str, max_iter: int = 200
) -> None:
    features = dataframe["text"].astype(str).tolist()
    labels = dataframe["label"].astype(str).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=30_000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=max_iter)),
        ]
    )

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(
            {
                "model": "LogisticRegression",
                "tfidf_max_features": 30_000,
                "tfidf_ngram": "1-2",
                "max_iter": max_iter,
            }
        )

        git_sha = (
            os.getenv("GITHUB_SHA")
            or os.popen("git rev-parse --short HEAD").read().strip()
            or "unknown"
        )
        mlflow.set_tag("git_sha", git_sha)

        unique_labels = sorted(set(labels))
        mlflow.log_text("\n".join(unique_labels), artifact_file="labels.txt")

        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        f1_macro = f1_score(y_test, predictions, average="macro")
        mlflow.log_metrics({"accuracy": accuracy, "f1_macro": f1_macro})

        mlflow.sklearn.log_model(pipeline, artifact_path="model")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to CSV/JSONL with columns text,label",
    )
    parser.add_argument("--exp", type=str, default="ai-learning-intent")
    parser.add_argument("--run", type=str, default=None)
    parser.add_argument("--autosample", action="store_true")
    parser.add_argument("--max_iter", type=int, default=200)
    arguments = parser.parse_args()

    dataframe, dataset_id = load_dataset(arguments.data, arguments.autosample)

    run_name = arguments.run or (
        f"intent_{'autosample' if arguments.autosample else os.path.basename(arguments.data)}_{dataset_id}"
    )

    mlflow.set_tag("dataset_version", dataset_id)
    mlflow.set_tag("dataset_rows", str(len(dataframe)))

    train_and_log(dataframe, arguments.exp, run_name, max_iter=arguments.max_iter)


if __name__ == "__main__":
    main()
