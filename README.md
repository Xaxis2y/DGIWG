# DGIWG GeoPackage Compliance Validator

**Version 1.56** · Automated QA/QC for GeoPackage files against the DGIWG GeoPackage Profile (STD-DP-19-005 v1.1 — GeoPackage Profile 1.4, Ed. 1.1)

---

## Overview

A Python tool that automatically validates GeoPackage (`.gpkg`) files against the **DGIWG GeoPackage Profile**, the interoperability standard used by NATO and allied defence organisations. It evaluates a file against the profile's **37 numbered requirements**, grades each one, and produces detailed per-file and roll-up reports.

The validator is **read-only** — it never modifies the GeoPackage being inspected. All checks run locally against the SQLite database inside the file; a few optional cross-checks use offline reference data when available.

## Key Features

- **35 automated requirement checks** (Requirements 3–37). Requirements 1–2 (OGC base conformance) require the OGC CITE TeamEngine harness and are reported as `SKIPPED`.
- **Coordinate Reference Systems** — allowed-CRS lists per DGIWG Tables 9–14, WKT2 structure, datum-name cross-check, bounding-box vs CRS extent.
- **Tiles & gridded coverage** — 256×256 tile sizing, factor-of-2 zoom progression, OGC scale-denominator sequences, and correct use of the `gpkg_2d_gridded_coverage` extension.
- **Metadata** — DGIWG DMF records, ISO 19115 elements, and DGIWG Table 36 scope pairings.
- **Extensions** — mandatory, optional, conditional, and not-allowed extension rules (including WEBP tile detection).
- **Comprehensive reporting** — per-file HTML, machine-readable JSON, a cross-file roll-up HTML, and a CSV summary for spreadsheet analysis.
- **Source-software forensics** — detects QGIS/GDAL vs ArcGIS origin and tailors the probable-cause guidance accordingly.

## Why use it

> Confirms that a GeoPackage deliverable is operationally ready for deployment across ArcGIS, QGIS, and allied military systems — without format-level friction — *before* it is released.

---

## Installation

**Required:** Python 3.9 or newer (core checks use only the standard library).

**Optional (recommended)** — these enable the deepest automated checks. When a library is absent, the affected requirement degrades gracefully to `PASS*` instead of failing:

```bash
pip install pyproj shapely Pillow
```

| Library  | Enables                                                        |
|----------|---------------------------------------------------------------|
| `pyproj` | Req 13 — datum-name cross-check against the EPSG registry      |
| `shapely`| Req 24 — OGC geometry validity sampling                       |
| `Pillow` | Req 26 — decoding tile BLOBs to confirm 256×256 pixels         |

Keep the launcher and the `dgiwg_validator/` package together in the same folder.

## Usage

**Interactive (file picker):**
```bash
python DGIWG_Validator_v1_56.py
```

**Single file or a folder of GeoPackages:**
```bash
python DGIWG_Validator_v1_56.py  path/to/file.gpkg
python DGIWG_Validator_v1_56.py  path/to/gpkg_folder/
```

**As a module:**
```bash
python -m dgiwg_validator  path/to/file.gpkg
```

## Output Reports

| File | Description |
|------|-------------|
| `<name>_DGIWG_Report.html` | Per-file report: every requirement, status, detail, probable cause, and manual-confirmation steps. |
| `<name>_DGIWG_Report.json` | Machine-readable per-file results (`schema_version`, verdict, counts, per-requirement detail). |
| `DGIWG_GPKG_FINAL_REPORT.html` | Roll-up across all files: per-file summary, a file × requirement matrix, and a confidence table. |
| `DGIWG_GPKG_FINAL_REPORT.csv` | Roll-up summary in spreadsheet form. |

## Understanding Results

**Per-requirement status:**

| Status | Meaning |
|--------|---------|
| `PASS` | Fully checked and met. |
| `PASS*` | Partial pass — structural/presence checks passed but content could not be fully verified automatically (or an optional library is missing). Review manually. |
| `FAIL` | Checked and not met; the detail names the offending table, value, or CRS. |
| `SKIPPED` | Not applicable to this file, or needs external context (Req 6 needs the product profile; Req 1–2 need OGC CITE TeamEngine). |

**Overall file verdict:**

| Verdict | Condition |
|---------|-----------|
| `CONFORMANT` | No `FAIL` and no `PASS*`. |
| `LIKELY CONFORMANT (partial checks)` | No `FAIL`, but one or more `PASS*` to confirm manually. |
| `NON-CONFORMANT` | One or more `FAIL`. |

---

## What's New in v1.56

- **Req 7 (Raster CRS Allowed) corrected** — UTM zones (EPSG 32601–32660 / 32701–32760) and per-product **Lambert Conformal Conic** CRS are now accepted for raster tile pyramids, matching DGIWG Tables 11 & 12. These valid CRS were previously reported as `FAIL`.
- Lambert Conformal Conic is detected from the WKT projection method (it has no fixed EPSG code), so per-product LCC definitions pass without a hard-coded code list.
- Req 7 report messages and manual-confirmation guidance updated to list the full allowed CRS set.
- Version advanced to v1.56 across all modules, the launcher, and the JSON report schema.

## Known Limitations

- Requirements 1–2 (OGC base conformance) are not automated — use OGC CITE TeamEngine.
- Requirement 6 (conditional extensions) depends on the applicable DGIWG product profile and is always `SKIPPED`.
- Some checks return `PASS*` when their optional library (`pyproj`, `shapely`, `Pillow`) is not installed.
- Scale-denominator verification is not available for UTM and Lambert Conformal Conic raster CRS (no single global pixel sequence); those return `PASS*` with the CRS confirmed as allowed.

## Documentation

A full user manual is provided: **`DGIWG_GeoPackage_Validator_User_Manual_v1.56.docx`**.

## Author

Created by **MCpl Son E.S.** — Mapping and Charting Establishment / Geomatics Engineering Trials & Evaluation Support Section (GETESS).
Contact: euisoo.son@forces.gc.ca
