# 实验记录

本页面用于记录使用 MLflow 追踪的意图分类训练实验信息。

## 实验概览

| Run 名称 | 数据版本 | 模型 | 主要参数 | 指标 | 说明 |
| -------- | -------- | ---- | -------- | ---- | ---- |
| _待运行_ | intent_v1 | LogisticRegression | TF-IDF max_features=30k, ngram=(1,2) | F1: -, Acc: - | 基线实验 |
| _待运行_ | intent_v2 | LogisticRegression | 同上 + 扩展数据 | F1: -, Acc: - | 数据增强后实验 |

## 运行步骤

```bash
# 设置 MLflow Tracking 指向 DagsHub
export MLFLOW_TRACKING_URI="https://dagshub.com/longzhimeng777/AI-Learning-Assistant-based-on-DeepSeek.mlflow"
export MLFLOW_TRACKING_USERNAME="<你的用户名>"
export MLFLOW_TRACKING_PASSWORD="<你的 Token>"

# 运行训练脚本
python ml/train.py --data ml/data/intent_v1.csv --exp ai-learning-intent --run intent_v1_baseline
python ml/train.py --data ml/data/intent_v2.csv --exp ai-learning-intent --run intent_v2_enhanced
```

执行完成后：
- 在 DagsHub 的 MLflow UI 中确认 run 是否存在
- 记录关键指标与模型工件（例如 `model/`, `labels.txt`）
- 将最佳模型版本写入 `ml/registry/current_model.md`

## 结论与下一步（待补）

完成实验后，请补充：
- 哪个 run 作为上线候选，指标多少
- 数据版本、代码版本、参数说明
- 下一步优化方向（例如增加语义向量特征、使用更复杂模型）
