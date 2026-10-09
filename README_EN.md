# BioSyn Solution Preparation Batch

> **Batch solution preparation calculator** — plan multiple buffers, reagents, and stock solutions at once with molar, stock dilution, mass concentration, and percentage modes.

## Overview

Preparing a batch of buffers? Each component needs its own mass or volume calculation. **BioSyn Solution Preparation Batch** takes a recipe table and computes every component amount at once — with purity correction, unit normalization, and a full audit trail for each calculation.

> For online solution calculators, visit [BioSyn solution preparation tools](https://biosyn-inc.com/tools/solution-preparation) — this is the batch desktop companion.

## Quick Start

```bash
git clone https://github.com/your-org/biosyn-solution-preparation.git
cd biosyn-solution-preparation
pip install -r requirements.txt

python -m src.main examples/sample_recipes.csv --output preparation_sheet.xlsx
```

## Calculation Modes

| Mode | Formula |
|------|---------|
| Molar | mass = C × V × MW |
| From Stock | C1V1 = C2V2 |
| Mass Conc. | mass = C(g/L) × V(L) |
| % w/v | mass(g) = % / 100 × V(mL) |
| % v/v | vol(mL) = % / 100 × V(mL) |

## Audit Trail

Every result shows: Input → Unit Normalization → Formula → Substitution → Result.

## Disclaimer

Mathematical planning only. Does not assess reagent compatibility, chemical stability, pH adjustment, or storage. Verify against lab SOP.

## Keywords

`solution preparation calculator`, `buffer preparation`, `molar solution calculator`, `stock dilution`, `reagent preparation`, `lab calculation`, `purity correction`, `preparation sheet`

## About

Built by [BioSyn Inc.](https://biosyn-inc.com/)

## License

[MIT](LICENSE)
