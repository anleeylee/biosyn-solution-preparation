# Changelog

## [1.0.0] - 2024-01-01
### Added
- Batch recipe input (CSV / XLSX) with flexible column mapping
- Molar solution calculation: mass = C × V × MW
- From-stock dilution: C1V1 = C2V2
- Mass concentration modes (g/L, mg/mL, µg/mL)
- Percentage modes: w/v, v/v, w/w
- Purity correction (corrected mass = theoretical / purity_fraction)
- Unit engine: mass, volume, molar, mass concentration units
- Calculation audit trail per component
- QC checks: missing MW, incompatible units, purity >100%, target > stock
- XLSX export (Batch Summary, Component Calculations, Preparation Sheet, Warnings, Methods)
- CSV export
- Offline / local-first operation
