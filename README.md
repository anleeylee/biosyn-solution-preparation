# BioSyn Solution Preparation Batch

> **批量缓冲液 / 试剂配制计算器** — 一次规划多个 buffer / reagent / stock solution 的制备，自动计算质量、体积、纯度校正，生成打印版操作单。
>
> A batch solution preparation calculator: plan multiple buffers, reagents, and stock solutions at once — molar, stock dilution, mass concentration, and percentage modes with purity correction and audit trails.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 核心功能

| 功能 | 说明 |
|------|------|
| **批量配方管理** | 一次性规划多个 solution / buffer / stock，按 Batch 分组 |
| **四种计算模式** | 摩尔溶液 / 从储备液稀释 / 质量浓度 / 百分比（w/v, v/v, w/w） |
| **纯度校正** | 自动按输入纯度计算实际称量量（`corrected = theoretical / purity`） |
| **单位引擎** | g/mg/µg/ng、L/mL/µL、M/mM/µM/nM、g/L/mg/mL/µg/mL |
| **计算审计追踪** | 每个结果显示：输入 → 单位归一化 → 公式 → 代入 → 结果 |
| **自动 QC 检查** | 缺 MW、单位不兼容、纯度 >100%、目标 > 储备浓度等 |
| **打印版操作单** | Preparation Sheet 格式，含组分和用量 |
| **多格式导出** | XLSX（6 个 Sheet）、CSV |
| **完全离线** | 纯数学计算，项目文件可保存为 JSON/YAML |

## 解决的痛点

配缓冲液时，每个组分都要单独算称多少克、加多少毫升。做一批试剂时尤其繁琐。BioSyn Solution Preparation Batch 把所有配方放在一张表里，一次性算出全部称量量。

> 在线溶液配制计算请访问 [BioSyn 溶液配制计算器](https://biosyn-inc.com/tools/solution-preparation) — 本工具是其桌面端批量制备增强版。

## 依赖与安装

### 环境要求

- **Python 3.10+**

### 依赖包

| 包 | 用途 | 是否必需 |
|------|------|----------|
| `openpyxl` | XLSX 多 Sheet 配制单导出 | 必需 |
| `reportlab` | PDF 打印版配制单（计划中） | 可选 |

> 核心计算引擎（摩尔溶液、储备液稀释、质量浓度、百分比、纯度校正、单位换算）**仅依赖 Python 标准库**。

### 安装指令

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/biosyn-solution-preparation.git
cd biosyn-solution-preparation

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python -m src.main examples/sample_recipes.csv --output preparation_sheet.xlsx
```

## 计算模式

| 模式 | 公式 | 适用 |
|------|------|------|
| Molar | `mass = C × V × MW` | 称量固体试剂 |
| From Stock | `C1V1 = C2V2` | 从浓缩储备液稀释 |
| Mass Concentration | `mass = C(g/L) × V(L)` | mg/mL, g/L 等 |
| Percentage | w/v, v/v, w/w | 百分比浓度 |

## 计算审计示例

```
mass = C × V × MW
     = 0.1 mol/L × 0.5 L × 58.44 g/mol
     = 2.922 g
```

## 科学边界

> 本工具只做数学计算，不自动判断：试剂兼容性、化学稳定性、灭菌、pH 调节流程、储存稳定性。这些需用户/SOP 验证。

## Keywords

`solution preparation calculator`, `buffer preparation`, `molar solution calculator`, `stock dilution`, `reagent preparation`, `lab calculation tool`, `purity correction`, `buffer recipe`, `preparation sheet`

## About

By [BioSyn Inc.](https://biosyn-inc.com/) — explore more [solution and buffer preparation tools](https://biosyn-inc.com/tools/solution-preparation).

## License

[MIT](LICENSE)
