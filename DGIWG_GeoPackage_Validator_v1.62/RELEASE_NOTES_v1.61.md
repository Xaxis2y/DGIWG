# DGIWG GeoPackage Compliance Validator — Release Notes v1.61

**Release date:** 2026-09-02
**Standard:** DGIWG STD-DP-19-005 v1.1 (GeoPackage Profile 1.4, Edition 1.1)
**License:** GPL-2.0-or-later — © 2026 Eui Soo SON

---

## Summary

v1.60's own release notes documented, as a known and deliberate limitation, that
the `CONFORMANT` verdict was structurally unreachable: ten requirements
(5, 9, 10, 12, 14, 20, 23, 28, 29, 33) returned `PASS*` on every file regardless
of outcome, and `score_results()` required zero `PASS*` anywhere to award
`CONFORMANT`. A hand-built, deliberately clean synthetic GeoPackage scored
13 PASS / 0 FAIL / 9 PASS* and reported `LIKELY CONFORMANT (partial checks)` —
never the top verdict, no matter how clean the file.

v1.61 fixes this by generalising a distinction the tool already used in one
place (`_manual_checks()`'s `unverifiable` flag, since v1.59) to every `PASS*`
result: each one now carries a **reason** — `Sampled`, `Evidence missing`, or
`Advisory` — and the verdict is scored from that reason, not from the mere
presence of a `PASS*`.

---

## 1. Every PASS* now carries a reason (`constants.PASSSTAR_*`)

Three reason codes, defined in `constants.py` alongside a metadata dict
(`PASSSTAR_REASON_META`) giving each one a label, description, colour, and a
remedy string used in both the console summary and the HTML report:

| Reason | Blocks CONFORMANT? | Meaning |
|---|---|---|
| `SAMPLED` | Yes | Only part of the data was examined (a tile or geometry sample smaller than the full table). A violation outside the sample would not have been seen. |
| `EVIDENCE_MISSING` | Yes | An optional library was absent, the run was `--offline`, or a row/column the check needed did not exist — the automated check could not gather enough evidence. |
| `ADVISORY` | No | The automated check is complete and found no violation. The note is informational, or asks for a quick manual confirmation of something the tool cannot judge automatically. |

`checks.check_req()` normalises every `_rN()` check's return value into a
`(status, detail, reason)` 3-tuple; a `PASS*` with no explicit reason defaults
to `ADVISORY` so nothing can silently become an unexplained coverage gap.
`utils.coverage_gaps(results)` returns the `(req_num, reason)` pairs whose
reason blocks the verdict; `utils.advisory_reqs(results)` returns the
requirement numbers whose `PASS*` does not.

## 2. A new three-tier verdict (`utils.score_results()`)

```
NON-CONFORMANT                 — one or more FAIL
CONFORMANT — REDUCED COVERAGE  — no FAIL, but coverage_gaps() is non-empty
CONFORMANT (automated scope)   — no FAIL, no coverage gaps (advisory PASS* only, or none)
```

This replaces the old two-tier `CONFORMANT` / `LIKELY CONFORMANT (partial
checks)` split. The difference in practice: before, *any* `PASS*` — including
a fully-verified informational note — blocked the top verdict; now only a
`PASS*` that is genuinely missing evidence does.

The console per-file summary and the JSON export both surface which
requirements are holding a file at `REDUCED COVERAGE` and what would close
each gap:

```
Verdict : CONFORMANT — REDUCED COVERAGE
PASS    : 16
FAIL    : 0
PASS*   : 4
SKIPPED : 17

Coverage: incomplete on Req 13
          Install the optional library / supply the missing data, then re-run, or verify this requirement by hand.
```

The JSON report gains a `"coverage"` block (`{"gaps": [{"req": n, "reason": r}, ...], "advisory": [n, ...]}`)
and each requirement entry gains a `"reason"` field, so scripted consumers of
the JSON output can apply the same distinction. The HTML report shows a small
coloured reason chip next to every `PASS*` status badge, plus a
"Coverage Gaps" banner (when any exist) and a separate "Advisory notes" banner
— replacing the single ambiguous `PASS*` badge with an explicit, actionable
signal.

## 3. Per-requirement changes

The ten legacy unconditional-`PASS*` sites now return a real `PASS` on
exhaustive, clean-data checks (they were never actually incomplete — the
status was just hardcoded):

- **Req 9, 10** (2D/3D vector CRS), **Req 12** (gridded 3D CRS), **Req 28**
  (multi-zoom pixel-size monotonicity), **Req 29** (single-zoom tile
  dimension consistency), **Req 33** (gridded extension core) — every row the
  check examines is checked against its allowlist/rule in the same pass;
  a clean result is exhaustive, so it is now `PASS`.
- **Req 14** (compound CRS usage) — the "no vector geometry columns, no
  compound CRS declared" and "no geometry rows" cases now return `SKIPPED`
  (the requirement genuinely does not apply) instead of `PASS*`; the "compound
  CRS declared but no geometry columns to check against" case returns
  `PASS*`/`EVIDENCE_MISSING`; a clean, checked result returns `PASS`.

Six further sites that were already conditional (not the unconditional-PASS*
bug) are now correctly reason-tagged instead of unconditionally blocking:

- **Req 4** (optional extensions), **Req 20** (metadata row completeness),
  **Req 23** (product partial metadata), **Req 31/32** (tile/feature layer
  metadata, when the layers are fully linked but no matching metadata
  document exists to inspect) — `ADVISORY`: the automated check is complete;
  the note is informational.
- **Req 5** (WEBP tile scan), **Req 26** (Pillow tile BLOB decode) — `SAMPLED`
  only when the scan genuinely covered fewer BLOBs than exist; a small table
  scanned in full now returns `PASS`.
- **Req 7, 8, 13, 18, 21, 24** — `EVIDENCE_MISSING` where the check fell back
  to a lighter method (no `gpkg_tile_matrix`, no lxml/lightweight header
  parser instead of Pillow, `--offline`/no-pyproj datum lookup, no Shapely).
  Req 13 additionally distinguishes: when `pyproj` **is** available and the
  full structural/datum cross-check ran, a remaining informational note
  (e.g. a datum-name alias, a confirmed-compliant axis order) is `ADVISORY`,
  not `EVIDENCE_MISSING` — the check completed; only when `pyproj` is
  unavailable does the reduced evidence apply.

## 4. Two further defects found while proving the fix works

Verifying that a clean file can actually reach `CONFORMANT (automated scope)`
— not just that the scoring logic is internally consistent — surfaced two
more defects, fixed in this release:

- **Req 5 ignored `--sample-size`.** The WEBP tile-format scan had a
  hardcoded `LIMIT 10`, so any tile table with more than 10 stored tiles was
  permanently tagged `SAMPLED` — no `--sample-size` value could ever close
  the gap. It now honours `_config.SAMPLE_SIZE`, the same as Req 24 and 26.
- **Req 13's axis-order check matched the wrong CRS type, and its AXIS
  pattern couldn't parse real-world WKT2.** `"GEOGCRS[" in wkt_upper` also
  matches inside `"BASEGEOGCRS["` — the WKT2 keyword for a *projected* CRS's
  underlying base geographic CRS — so every projected CRS (e.g. EPSG:3857)
  was wrongly run through the geographic-CRS axis-order check. Separately,
  the regex used to extract `AXIS[name, direction]` pairs
  (`AXIS\["([^"]*)"[^]]*,\s*([A-Z]+)\]`) required the direction word to be
  immediately followed by the block's closing bracket — which only matches
  WKT1-style `AXIS["Lat",NORTH]` entries. Real WKT2, as PROJ and GDAL
  actually emit it, writes `AXIS["geodetic latitude (Lat)",north,ORDER[1],
  ANGLEUNIT[...]]` — sub-elements between the direction and the closing
  bracket that the old pattern could never match, so this check silently
  failed to parse axes on almost every modern file. Both are fixed: the CRS
  type is now decided from the start of the WKT (the outermost keyword),
  and the AXIS pattern only requires the direction word to immediately
  follow the axis name.

## 5. Verification performed

- **Reachability, proven not asserted.** A clean synthetic tile-pyramid
  GeoPackage (`good_tiles.gpkg`, from `run_local_tests.py`) with a
  standards-correct WKT2 CRS definition, full optional libraries
  (shapely/Pillow/pyproj/lxml) installed, and `--sample-size` covering every
  stored tile reaches `CONFORMANT (automated scope)` with 0 coverage gaps —
  confirmed by direct inspection of `score_results()`/`coverage_gaps()`
  output, not just a passing test assertion.
- **Positive control.** `bad_mixed.gpkg` (16+ deliberate violations) still
  reports `NON-CONFORMANT`. Each of the ten legacy-converted requirements
  (9, 10, 12, 14, 28, 29, 33 — the ones whose clean-data status changed from
  `PASS*` to `PASS`/`SKIPPED`) was additionally tested in isolation against a
  hand-built violation and confirmed to still return `FAIL` — the status
  change only affects the clean-data path, not violation detection.
- **Regression suite.** `run_local_tests.py`'s expectation tables were
  updated for every requirement whose clean-data status changed, and the full
  suite (batch run, fail-fast exit code, version-stamp consistency, manual-
  check tuple shape, HTML banners, release-asset manifest, v1.60's Z/M and
  `--offline` regression tests) was re-run end to end against the actual
  packaged CLI, not just unit-level.
- **Static checks.** `pyflakes` and `compileall` across every changed module;
  no new warnings introduced by this release's changes.

---

*v1.60's fixes — Req 24 Z/M derived from the WKB type code rather than the
envelope-indicator bits of the header flags byte, Req 33 no longer raising an
opaque exception when `gpkg_extensions` is absent, the remaining ungated
`--offline` network helpers, and the smaller Req 24/26 and pick-files
corrections — are all present in v1.61.*
