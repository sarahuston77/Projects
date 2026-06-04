# Supply-Chain & Production Planning Optimizer

A **1,000+ line mixed-integer optimization model** built in FICO Xpress / Mosel (`mmxprs`) for a multi-period, multi-product manufacturer ("TomMac"). The model jointly decides purchasing, production, inventory, warehouse expansion, and sales across four products and four planning periods, subject to capacity, storage, and ingredient-composition constraints — improving **modeled profit by 22%** over the baseline plan.

## What it decides
- How much of each tomato variety to purchase per period.
- How much of each finished product to produce per period.
- Whether to invest in additional warehouse capacity / production capacity (binary decisions).
- Inventory carried between periods, subject to storage cost.
- Sales volume per product per period.

## Constraints captured
- Per-product ingredient composition (content × variety matrix).
- Production capacity, expandable via a one-time investment.
- Warehouse capacity, expandable via a one-time investment.
- Period-to-period inventory balance.
- Non-negativity and integrality on all expansion decisions.

## Files
```
Optimization Model for Supply Chain and Production Planning/
├── ConsultationModel.mos    # The Mosel model (1.1k lines)
├── ConsultationData.dat     # Companion data file
└── DataAnalysis.pdf         # Written analysis + sensitivity results
```

The model loads its primary inputs from `TomMac.dat`, `TomMacQuarters.dat`, and `TomMacPlan.dat` (referenced via `initializations from ...` blocks).

## Run

Open `ConsultationModel.mos` in FICO Xpress Workbench and run with the bundled `mmxprs` solver.

```text
File → Open → ConsultationModel.mos → Run
```

## Outcome
Solver-driven plan lifted modeled profit **22%** versus the baseline heuristic, with sensitivity analysis on input cost shocks documented in `DataAnalysis.pdf`.
