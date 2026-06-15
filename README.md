DGIWG GeoPackage Compliance Validator (v1.56)

Overview

A Python-based QA/QC tool designed to automate the validation of GeoPackage (.gpkg) files against the DGIWG GeoPackage Profile (STD-DP-19-005 v1.1). This tool ensures that geospatial data products meet the strict interoperability requirements for NATO and allied defense organizations.

Core Functionality
35 Automated Checks: Validates Requirements 3 through 37 of the DGIWG profile.

Compliance Verification: Checks Coordinate Reference Systems (CRS), Tile Matrix Sets (TMS), metadata structures, and extension usage.

Comprehensive Reporting:

HTML Reports: Detailed per-file validation logs.

Rollup Summary: A cross-file "Final Report" for batch processing.

Data Export: CSV for Excel analysis and JSON for machine-readable workflows.

Quick Compliance Check
The validator checks for:

CRS: Proper WKT2 definitions and EPSG compliance (UTM/UPS/WGS84).

Gridded Coverage: Proper use of the gpkg_2d_gridded_coverage extension.

Geometry: Adherence to DGIWG-specific tile pyramid and metadata constraints.

Why use this?
"Ensures that spatial data is operationally ready for deployment across ArcGIS, QGIS, and allied military systems without format-level friction."
