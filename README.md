# DGIWG GeoPackage Compliance Validator

A Python tool that checks `.gpkg` (OGC GeoPackage) files against the **DGIWG STD-DP-19-005 v1.1** Defence Profile of GeoPackage 1.2, and produces detailed HTML/JSON/CSV compliance reports.

Current version: **v1.58** (pre-release)

## What it does

- Runs all 37 requirements defined in DGIWG STD-DP-19-005 v1.1 (Table 6), covering extensions, CRS rules, WKT2 structure, metadata (DMF/ISO 19115), tile pyramids, and gridded coverage data.
- Two requirements (Req 1, Req 2) require the OGC CITE TeamEngine test suite and are reported as SKIPPED — they cannot be automated. One requirement (Req 6) depends on a project-specific product profile and is also SKIPPED with guidance on how to check it manually.
- Detects the likely authoring tool (QGIS/GDAL vs ArcGIS vs unknown) from structural fingerprints and attaches tool-specific remediation hints to relevant failures.
- Produces a per-file HTML report, a JSON companion file (stable schema for CI pipelines), and a batch rollup HTML/CSV when validating multiple files.
- Runs fully offline (`--offline`) for air-gapped environments — no requirement check depends on internet access to produce a verdict; a few checks additionally cross-reference the EPSG registry and OGC TileMatrixSet definitions online when network access is available.
- Optional libraries (`shapely`, `Pillow`, `pyproj`, `lxml`) deepen specific checks (geometry validity, tile pixel decoding, datum cross-checks, XML schema validation) but are not required — checks fall back to structural-only validation and report `PASS*` when a library is missing.

## Requirements

- Python 3.10+
- Optional, for full-depth checks:
  ```
  pip install shapely Pillow pyproj lxml
  ```

## Installation

Clone or download this repository, then run the package directly — no build step required.

```
git clone <this-repo-url>
cd DGIWG_GeoPackage_Validator
python DGIWG_Validator_v1_58.py
```

## Usage

**Interactive mode** (file picker dialog):
```
python DGIWG_Validator_v1_58.py
```

**Command-line mode:**
```
# Validate a single file
python -m dgiwg_validator myfile.gpkg

# Validate every .gpkg in a folder (add --recursive for subfolders)
python -m dgiwg_validator C:\Data\Project_Alpha

# Air-gapped / offline network — skip all EPSG/OGC internet checks
python -m dgiwg_validator --offline myfile.gpkg

# Write all reports to a specific folder
python -m dgiwg_validator --output-dir out\ C:\Data\Project_Alpha

# Stop at the first non-conformant file (useful in CI, exits 1)
python -m dgiwg_validator --fail-fast myfile.gpkg
```

Run `python -m dgiwg_validator --help` for the full flag list (`--sample-size`, `--timeout`, `--quiet`, `--no-install`, `--dir`, `--file`, `--recursive`, `--version`).

### Output

For each file: `<name>_<TOOL>_DGIWG_Report.html` and a matching `.json` (schema-versioned, containing verdict, per-requirement status/detail, forensic tool detection, and internet-check results). For batch runs: `DGIWG_GPKG_FINAL_REPORT.html` and `.csv` summarizing pass/fail rates across all requirements and files.

Each requirement resolves to one of:

| Status | Meaning |
|---|---|
| `PASS` | Fully automated check passed |
| `PASS*` | Passed, but full verification needs a manual step or an optional library |
| `FAIL` | Non-conformant |
| `SKIPPED` | Not applicable to this file, or not automatable (Req 1, 2, 6) |

## Project layout

```
dgiwg_validator/          Core package
  checks.py                 Req 1-37 implementations + dispatch table
  constants.py               CRS allowlists, DGIWG tables, guidance text
  forensics.py               Source-software detection + deep-dive checks
  net.py                     EPSG/OGC internet checks (offline-aware)
  html_report.py             Per-file HTML report renderer
  rollup.py                   Batch rollup HTML/CSV renderer
  utils.py                    SQLite helpers, file profiling, scoring
  main.py                      CLI argument parsing and batch driver
  config.py                    Runtime flags (--offline, --quiet, etc.)
DGIWG_Validator_v1_58.py   Double-clickable launcher
dgiwg_epsg_cache.json      Offline EPSG registry cache (128 DGIWG CRS codes)
run_local_tests.py         Self-test harness (synthetic GeoPackages, no GDAL needed)
package_release.py         Builds a clean dist/ zip for release
```

## Testing

`run_local_tests.py` generates synthetic GeoPackages with the Python standard library only (no GDAL required), runs the validator against them in `--offline` mode, and asserts the expected status on every affected requirement:

```
python run_local_tests.py
```

A timestamped log (`local_test_log_*.txt`) is written next to the script with full step-by-step detail. Exit code 0 means every assertion passed.

## Building a release

```
python package_release.py
```

Produces `dist/DGIWG_GeoPackage_Validator_v<version>_pre.zip` containing the package, launcher, EPSG cache, and a `VERSION.txt`, with caches, generated reports, and prior-version launchers excluded.

## Known limitations

- Req 1 and Req 2 (OGC Base/Options conformance) require the OGC CITE TeamEngine test suite and are not automated by this tool.
- Req 6 (Conditional Extensions) depends on a project-specific DGIWG product profile that this tool has no access to; it is reported SKIPPED with a manual-check procedure.
- Geometry and tile BLOB checks (Req 24, Req 26) sample a configurable subset of rows per table (`--sample-size`) rather than scanning every row, for performance on large files.
- The verdict `CONFORMANT` requires zero `FAIL` and zero `PASS*` results across all applicable requirements; in practice most real-world files land on `LIKELY CONFORMANT (partial checks)` because some checks are inherently partial (missing optional libraries, or requirements that are only partially automatable).

## License

GPL-2.0-or-later. Copyright (c) 2026 Eui Soo SON.

## Standard reference

DGIWG STD-DP-19-005 v1.1, *Defence Profile of OGC's GeoPackage 1.2*, May 2, 2025. Published by the Defence Geospatial Information Working Group (DGIWG): https://dgiwg.org
