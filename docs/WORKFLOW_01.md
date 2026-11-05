# 功能01：点线命名

## Intended execution contract

1. Confirm QGIS is reachable and a project is open.
2. Inspect required layers and fields; stop on missing/ambiguous inputs.
3. Create a recoverable backup before any write.
4. Invoke the existing ODN_Tools_Pro access-point naming and cable naming operations in the confirmed order.
5. Verify generated names, empty values, duplicates, and processed feature counts.
6. Return SUCCESS / FAILED / CANCELLED with a diagnostic report.

## Current implementation

Only the bridge and safe preflight are present. Naming is deliberately disabled until the current working ODN_Tools_Pro package is inspected. Historical function names are not treated as a supported API.

## Decisions still required

- Exact order of access-point naming and cable naming.
- Whether both operations run every time, or whether either can be independently selected.
- Whether the current naming dialogs have fixed options that must be applied, and what those values are.
- Backup scope: QGIS project only, edited data sources too, or a complete project data package.
