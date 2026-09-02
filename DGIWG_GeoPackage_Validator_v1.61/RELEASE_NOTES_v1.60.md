# DGIWG GeoPackage Compliance Validator — Release Notes v1.60

**Release date:** 2026-09-02
**Standard:** DGIWG STD-DP-19-005 v1.1 (GeoPackage Profile 1.4, Edition 1.1)
**License:** GPL-2.0-or-later — © 2026 Eui Soo SON

---

## Summary

v1.60 is a correctness release on top of v1.59. Nothing was added; six defects
were removed. One of them (§1) changes a verdict that v1.47 through v1.59 could
produce on perfectly conformant files, so **re-run any GeoPackage that failed
Req 24 on "Z/M consistency" under an earlier build** — that finding was very
likely spurious.

---

## 1. Req 24 — Z/M consistency false failures (critical)

`_decode_gpkg_geom_header()` read Z and M dimension presence from bits 1 and 2
of the GeoPackage geometry header flags byte:

```python
"has_z": bool(flags & 0x02),
"has_m": bool(flags & 0x04),
```

There are no Z or M flags in that byte. Per OGC 12-128r15 §2.1.3 the flags byte
is laid out as:

| bits | mask | meaning |
|------|------|---------|
| 0 | `0x01` | header byte order |
| 1–3 | `0x0E` | **envelope indicator** (0 = none, 1 = XY, 2 = XYZ, 3 = XYM, 4 = XYZM) |
| 4 | `0x10` | empty-geometry flag |
| 5 | `0x20` | ExtendedGeoPackageBinary marker |

So `0x02` and `0x04` were reading envelope bits. What that meant in practice:

| geometry as stored | old `has_z` | old `has_m` | correct |
|---|---|---|---|
| 2D, XY envelope (GDAL/QGIS default for lines & polygons) | **True** | False | False / False |
| 2D, no envelope | False | False | False / False |
| 3D, no envelope | **False** | False | **True** / False |
| 3D, XYZ envelope | **False** | **True** | **True** / False |

Any 2D feature table written by GDAL or QGIS with envelopes — which is the
normal case — was therefore reported as
`declared z=0 (prohibited) but header Z-flag=1`, a hard FAIL on Req 24. In the
other direction a genuine 3D geometry stored without an envelope was reported
as carrying no Z, so a real violation was missed.

**Fix.** Z/M is now derived from the WKB geometry type code, which is where the
standard actually records it — ISO/OGC 06-103r4 thousands offset (`1xxx` = Z,
`2xxx` = M, `3xxx` = ZM), plus PostGIS EWKB high-bit flags (`0x80000000` = Z,
`0x40000000` = M) for producers that wrote EWKB instead of ISO WKB. The new
helper is `utils._wkb_zm_flags()`.

Two related header defects were fixed at the same time:

* A BLOB whose first two bytes are not the `GP` magic marker is now reported as
  a decode error instead of being parsed as if it were a GeoPackage geometry.
* A flags byte declaring a reserved envelope indicator (5–7) is now reported
  rather than silently decoded at the no-envelope offset, which produced
  garbage WKB.
* Where the WKB type code cannot be read at all, the geometry is reported as
  **not verifiable** (a skip note) rather than assumed 2D. `z`/`m` = 2
  ("optional") continues to be exempt from the check.

## 2. Req 33 — opaque failure when `gpkg_extensions` is absent

`gpkg_extensions` is optional in the OGC core specification. `_r33()` queried it
without a `table_exists()` guard, so a gridded GeoPackage that did not carry the
table raised `no such table: gpkg_extensions`, which `check_req()` converted
into a generic `Exception during check: …` FAIL with no actionable text.

This is the same defect class v1.58 fixed for Req 3, 4 and 5 (Bug B); Req 33 was
missed at the time. It now reports the missing registration in plain terms.

## 3. Offline mode — remaining ungated network helpers

`net._http_get()` and `net._http_head()` built their own `urllib` requests and
so bypassed the `--offline` gate in `_net_get()` — exactly the defect v1.58
fixed in `_net_check_uri()`. Neither is called on any current code path, but on
an air-gapped / 국방망 network a helper that *can* reach the internet is a defect
whether or not it is reached today. Both are now gated and return
`OFFLINE MODE — internet checks disabled` without touching the network.

## 4. Smaller corrections

| Area | Problem | Fix |
|---|---|---|
| Req 24, ATS 5.4 / 5.5 | `has_tile_tables` recognised only the `2d-gridded-coverage` spelling, though Req 11/12/25/26 also accept `2d_gridded_coverage` and `gpkg_2d_gridded_coverage`. A gridded file using either variant skipped the checks for a missing `gpkg_tile_matrix_set` / `gpkg_tile_matrix`, which were then reported as "not required". | All four spellings accepted, case-insensitively. |
| Req 26 | `--sample-size` was ignored on the no-Pillow header-parser path, which always used 3 BLOBs per zoom level — contradicting the flag's own `--help` text. | The flag is honoured; 3 remains the default when it is not given. |
| Req 26 | The per-zoom success line interpolated `actual_w`/`actual_h`, loop variables left over from the last decoded tile, so it could quote a size belonging to a different tile. | Size tracked explicitly per zoom level. |
| Forensics, Req 18 | The ArcGIS internal-path detector matched against `[r"c:\\", r"c:/", ".gdb\\", "geodatabase\\"]`. Those are raw strings, so three entries contained **two** literal backslashes and could never match a real Windows path, which is written with one. The check had never fired since it was added. | Single-backslash patterns, not hardcoded to drive C:. |
| `rollup.py` | The module ended with `if __name__ == '__main__': main()`, but `main` is not defined there — running the file directly raised `NameError`. | Guard removed; `rollup.py` is a library module. |
| `utils.pick_files_dialog()` | The tkinter-unavailable message told the user to run `DGIWG_Report_Generator.py`, a filename not present in the distribution — the same stale-name problem v1.59 fixed in the `--help` epilog. | Names the real entry points. |
| Dead code | `_xsd_build_err` and `_ph_sql` assigned but never used; `import csv as _csv_mod` repeated inside `_write_rollup()`, shadowing the identical module-level import. | Removed. |

## 5. Known limitation carried into v1.60 (unchanged, deliberately)

**A top verdict of `CONFORMANT` is still not reachable.** `score_results()`
awards `CONFORMANT` only when `FAIL == 0` **and** `PASS* == 0`, but these
requirements return `PASS*` unconditionally even when nothing is wrong:

> Req 5, 9, 10, 12, 14, 20, 23, 28, 29, 33

A fully clean file therefore settles at `LIKELY CONFORMANT (partial checks)`.
v1.59 changed Req 4 from an unconditional `PASS*` to `PASS` for exactly this
reason, but the remaining ten were not touched then and are not touched now:
changing them alters the meaning of every report the tool has ever produced, and
which of them are genuinely "not fully automatable" is a judgement for the
standard owner rather than a bug fix. **Read `LIKELY CONFORMANT` with zero FAIL
as the best result currently achievable.**

Also unchanged from v1.59: Req 1, 2 and 6 are never executed (they need OGC CITE
TeamEngine and the applicable product profile), which the scope banner in every
report states.

## 6. Verification

`run_local_tests.py` was extended for this release and passes end to end with
`shapely`, `Pillow`, `pyproj` and `lxml` present:

* the v1.59 assertions, re-pointed at 1.60;
* a direct regression test of `_decode_gpkg_geom_header()` over five
  envelope/dimension combinations, which fails on the v1.59 decoder;
* an end-to-end test that a 2D feature table written **with XY envelopes** —
  the case that produced the false failure — no longer reports a Req 24 Z/M
  mismatch;
* a test that a gridded GeoPackage with no `gpkg_extensions` table gets a
  readable Req 33 FAIL rather than a generic exception;
* a test that `_http_get` / `_http_head` refuse to run under `--offline`.

## 7. Upgrading

Drop-in replacement — no schema, CLI or output-format changes beyond the wording
noted above.

```
python DGIWG_Validator_v1_60.py "C:\Data\my_file.gpkg"
python -m dgiwg_validator --offline --recursive "C:\Data"
```

Files whose only Req 24 failure was Z/M consistency should be re-validated.
