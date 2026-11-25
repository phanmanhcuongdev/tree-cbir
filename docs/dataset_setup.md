# Dataset and external artifact setup

The accepted P02 candidate corpus has **507 JPEG RGB images**, each **768 × 1024 px**. The versioned [standardization manifest](../outputs/preprocessing/standardization/standardization_manifest.csv) records relative source/output names, actions and SHA-256 hashes. Image bytes, derived features and restricted reference material use external transfer. `data/processed/` is the immutable original input and `data/standardized/` is the accepted derived corpus. `data/queries/` is local query input.

## Obtain the authorized files

Open the official [500 Ảnh](https://drive.google.com/drive/folders/1GcqBCnZpZZ9-VF6Kf1MTsOCyAioII_4h?usp=drive_link) folder using your authorized team Google account. In Drive select the JPEG files and choose **Download**. Extract the downloaded archives to a temporary folder outside the repository. If Drive denies access, request access from the project owner or ask for the verified `DATA-STD` archive.

The folder listing contains **508 JPEG entries and 507 distinct names**. Both entries named `475.jpg` have the same size. The distinct names and byte sizes match the local originals; for the 37 transformed records, the Drive sizes differ from the standardized files. Use the folder as the **original source**. The Drive listing verified names and sizes; verify the downloaded bytes against the P02 manifest.

1. Use the manifest's `source_path` and `source_sha256` columns to select one exact source per row. Preserve both `475.jpg` downloads in separate temporary folders so neither overwrites the other. Use `Get-FileHash -Algorithm SHA256 <downloaded-file>` on each candidate. Keep one matching copy; if both match they represent the same required input. Leave duplicate or unexpected files outside the input directories.
2. Place the selected JPEGs directly under `data/processed/` with their manifest names. Before preprocessing, run the source guard below from the repository root. Re-download missing or mismatched entries. If no copy matches, contact the owner for the verified `DATA-RAW` or `DATA-STD` archive. Preserve the manifest and existing verified images.
3. Use [the pinned Python environment](../GUIDE.md#python-environment). Run preprocessing in a separate checkout with an empty `data/standardized/`. The standardizer refuses output collisions and writes an experiment manifest in that checkout. Save the tracked acceptance manifest outside the checkout before running, then pass that saved copy to the verifier.

```text
data/
  processed/       507 source JPEGs, named as source_path in the manifest
  standardized/    507 output JPEGs, named as standardized_path in the manifest
```

```powershell
$manifest = 'outputs/preprocessing/standardization/standardization_manifest.csv'
$rows = Import-Csv $manifest
if ($rows.Count -ne 507) { throw 'Expected the 507-row P02 acceptance manifest' }
$actual = @(Get-ChildItem data/processed -File -Recurse -Force |
    Where-Object { $_.Name -ne '.gitkeep' })
if ($actual.Count -ne 507) { throw 'Check for missing, duplicate or extra input files' }
foreach ($row in $rows) {
    $source = Join-Path 'data/processed' $row.source_path
    if (!(Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing input: $source" }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $row.source_sha256) {
        throw "SHA-256 mismatch: $source"
    }
}
Copy-Item -LiteralPath $manifest -Destination ../p02-acceptance-manifest.csv -ErrorAction Stop
./.venv/Scripts/python.exe scripts/standardize_dataset.py
if ($LASTEXITCODE -ne 0) { throw 'Standardization failed' }
./.venv/Scripts/python.exe scripts/verify_dataset.py --manifest ../p02-acceptance-manifest.csv --source data/processed
```

Use a new sibling working folder or a unique filename for the saved acceptance manifest when running multiple replays. If output verification fails, keep the replay separate. Confirm the dependency versions and restore the accepted `DATA-STD` archive if needed. The expected output is **507 JPEG RGB images at 768 × 1024 px**, each matching its recorded SHA-256. For the normal checkout with the tracked manifest, verify the standardized output with `./.venv/Scripts/python.exe scripts/verify_dataset.py`.

## Restoring named archives

Check the archive filename, SHA-256, access tier, member list and destinations in the [artifact manifest](team_preparation/artifact_manifest.csv). The restorer verifies the complete archive and every member before writing, and refuses to replace a differing existing file. You can place downloaded archives anywhere accessible and pass their paths explicitly. Example after placing the files under a private, outside-repository `handoff-artifacts` directory:

```powershell
./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py DATA-STD ../handoff-artifacts/data-std-507.zip
./.venv/Scripts/python.exe scripts/verify_dataset.py
```

With the optional `DATA-RAW` archive, restore the original sources and use the source guard above before regeneration. Once both trees are present, verify them together:

```powershell
./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py DATA-RAW ../handoff-artifacts/data-raw-507.zip
./.venv/Scripts/python.exe scripts/verify_dataset.py --source data/processed
```

For offline bootstrapping, the restore utility uses only the standard library and can run with the base Python before installing dependencies. Use `WHEELS-WIN` and the archive `windows-py314-wheelhouse.zip` to populate the ignored `wheelhouse/`. Then follow the offline install command in the [guide](../GUIDE.md#python-environment). Manifest rows marked `version-control` describe LF-normalized Git bytes. External ZIPs and member hashes describe exact binary bytes.

## Full regression and holdout custody

Independent contract tests use only source-controlled synthetic fixtures. For the legacy curated regression, restore `DATA-STD` and `P03-DEV`. The existing split-disjointness test also reads `P03-SEALED`, which contains the V3 test identities and their checksums. The held-out data custodian or an explicitly authorized runner restores it in an isolated checkout. Do not send the sealed archive with train/validation features, open it for model selection, or attach its content to PRs. There are no verified independent V3 masks or test feature files in these bundles. If access is unavailable, report the affected test as blocked and use the independently runnable tiers.

```powershell
./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py P03-DEV ../handoff-artifacts/p03-development-evidence-r2.zip
# The next command is only for the custodian or authorized regression runners.
./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py P03-SEALED ../handoff-artifacts/p03-v3-frozen-split.zip
```

TASK-A may separately restore `P03-FEATURES` from `p03-v3-train-val-features.zip` to resume existing V3 development without repeating exports. This contains only previously generated train/validation features. Legacy V2 C references are already exposed historical evidence and partly used by V3 for development. They are not the frozen V3 split. See [the V2 preservation notes](../experiments/p03_v2/README.md) and [evaluation split rules](team_preparation/evaluation_protocol.md#split-integrity-and-leakage-prevention).
