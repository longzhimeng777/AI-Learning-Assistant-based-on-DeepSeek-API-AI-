# 数据版本说明

本项目的学习场景意图分类数据集通过公开问答语料与少量合成样本构建，用于训练轻量分类器辅助 AI 学习助手进行意图路由。

## 版本记录

| 版本 | 文件 | 样本数 | 特点 | 变更说明 |
| ---- | ---- | ------ | ---- | -------- |
| v1   | `ml/data/intent_v1.csv` | _待生成_ | 基础版，按类别规则采样 StackOverflow、DuReader、Math23K 题干，并做最小清洗 | 首次提交 |
| v2   | `ml/data/intent_v2.csv` | _待生成_ | 在 v1 基础上扩充长文本、口语化、英文/混合语料，并增加 Hard Negatives | 增强覆盖 |

## 标签集合

标签定义与使用说明位于 `ml/configs/labels.txt`，当前包含：

- 概念解释
- 学习路径建议
- 示例代码
- 报错排查
- 工具安装配置
- 作业/考试题解读
- 复习总结/要点
- 资料推荐

## 数据来源与处理流程

1. StackOverflow (StackSample) 问答标题、正文
2. 百度 DuReader/CMRC 中文问答数据集问题字段
3. Math23K 数学应用题题干
4. 通过 DeepSeek 生成少量补充样本（标记 `source=synthetic`）

`ml/scripts/download_datasets.py` 将负责：

- 下载/抽样公开数据
- 基于关键字规则映射到上述标签
- 输出 CSV 并执行去重、长度截断
- 生成 v1、v2 两个版本

> 注意：脚本默认只生成示例小样本，待你提供 DagsHub Token 后可拉取完整源数据。运行脚本前请阅读文件顶部说明并根据需要调整数据来源。

## 运行方式（待补）

```bash
python ml/scripts/download_datasets.py --output ml/data/intent_v1.csv
python ml/scripts/download_datasets.py --output ml/data/intent_v2.csv --mode enhanced
```

生成后请执行：

```bash
dvc add ml/data/intent_v1.csv ml/data/intent_v2.csv
dvc push
```
