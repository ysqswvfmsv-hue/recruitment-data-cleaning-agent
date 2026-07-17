# 招聘数据清洗 Agent

这是一个可公开上传到 GitHub 的作品集版本，用虚拟招聘数据展示招聘 CSV 清洗 Agent 的工程能力。原项目中的真实数据、历史总集、内部 Notebook、账号信息、路径和敏感项目组信息均未复制到本仓库。

## 项目背景

招聘数据通常来自采集工具导出的多份 CSV。原始文件会出现字段命名不统一、链接异常、重复岗位、城市字段不稳定、手工 Notebook 难复现等问题。项目目标是把一次性的人工清洗流程升级为可运行、可测试、可审计的 Agent 工作流。

## 原有问题

- 原始字段包含 `sal`、`er`、`er1`、`er2`、`字段1` 等采集器字段。
- 岗位链接可能带追踪参数、不可见字符或无效域名。
- 同一个岗位会在不同批次重复出现。
- Notebook 流程不利于自动化测试和质量追踪。
- 交付时需要说明删除了多少无效行、合并了多少重复岗位，以及输出质量是否达标。

## 我的解决方案

我将流程整理成公开版 Agent 项目：包含 Skill 说明、Agent 配置、命令行脚本、单元测试、虚拟样例数据、demo 输出和发布前验证报告。公开版保留核心清洗逻辑，但完全使用合成数据。

## Agent 工作流程

1. 读取 `.agents/skills/recruitment-data-cleaning/SKILL.md`。
2. 从 `sample_data/raw/` 读取虚拟原始 CSV。
3. 标准化字段和岗位链接。
4. 删除无效岗位链接。
5. 按岗位 ID 去重，默认保留最新采集记录。
6. 输出清洗后 CSV、质量报告和验证报告。
7. 运行测试，并检查仓库是否仍包含敏感信息。

## 技术栈

- Python 3.10+
- 标准库 `csv` / `argparse` / `json`
- `unittest` 单元测试
- YAML Agent 配置
- Markdown 质量与验证报告

## 测试结果

当前样例输出位于 `demo_outputs/`，发布验证结果位于 `portfolio_validation_report.md`。

本地检查命令：

```bash
python -m unittest discover -s tests
python scripts/validate_portfolio.py --root . --output portfolio_validation_report.md
```

## 运行方法

```bash
python scripts/generate_sample_data.py --output sample_data/raw/sample_recruitment_raw.csv --rows 104
python scripts/clean_recruitment_data.py   --input sample_data/raw/sample_recruitment_raw.csv   --output demo_outputs/cleaned_sample.csv   --quality-report demo_outputs/quality_report.json   --validation-report demo_outputs/validation_report.md   --overwrite
python -m unittest discover -s tests
python scripts/validate_portfolio.py --root . --output portfolio_validation_report.md
```

## 隐私与公开发布说明

本仓库只包含虚拟数据，不包含真实招聘数据、历史总集、内部 Notebook、Cookie、Token、账号信息、私人路径或大型源数据压缩包。
