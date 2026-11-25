# Changelog

## Unreleased
- Evaluated four P03.2 trunk segmentation variants and retained the paired-boundary and constrained GrabCut hybrid. Prototype quality targets remain open.
- Closed P02 after human visual review of all standardized crop/resize pairs.
- Standardized the derived dataset with byte-preserving copies for compliant source JPEGs.
- Implemented P02 dataset audit, RGB preprocessing and generic image-processing utilities.
- Initialized P01 repository architecture, feature contracts, local database configuration and validation scaffolding.
- Completed P01 validation: Python 3.14.3 dependencies, Streamlit health, PostgreSQL 17.12 + pgvector 0.8.7, exact vector operations, tests and Ruff.
