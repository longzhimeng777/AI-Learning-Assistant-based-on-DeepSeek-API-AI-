# 数据与实验溯源

- 训练数据：
  - `ml/data/intent_v1.csv`：StackOverflow / DuReader / Math23K 抽样 + 合成补充
  - `ml/data/intent_v2.csv`：计划作为增强版，包含更复杂样本
- 数据版本管理：使用 DVC 追踪，远端存储配置为 DagsHub（待执行 `dvc remote add`）。
- 实验追踪：使用 MLflow（DagsHub Tracking URI）。
- 模型工件：训练脚本会将模型、标签文件上传至 MLflow Artifacts。

记录流程：
1. 使用 `ml/scripts/download_datasets.py` 生成指定版本数据
2. `dvc add` 并 `dvc push`
3. 运行 `ml/train.py` 产生基线与增强实验
4. 将指标与工件信息填写进 `ml/README_experiments.md`，并更新 `ml/registry/current_model.md`
