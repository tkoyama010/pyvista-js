# Minimum Supported Dependencies

pyvista-js follows [SPEC 0 — Minimum Supported Dependencies](https://scientific-python.org/specs/spec-0000/), a community-wide policy adopted by major Scientific Python projects including NumPy, SciPy, Matplotlib, pandas, scikit-image, NetworkX, xarray, and Zarr.

## Policy Summary

SPEC 0 defines a standardized approach for dropping support of older dependencies:

- **Python versions**: Drop support 36 months (3 years) after initial release
- **Core package dependencies**: Drop support 24 months (2 years) after initial release

This policy balances the need for new features and bug fixes with the stability requirements of downstream users.

## Current Minimum Versions

As of March 2026, pyvista-js supports:

- **Python**: 3.12+ (released October 2023)
- **NumPy**: 2.0+ (released June 2024)

## Version Drop Schedule

The following table shows when support for Python versions will be dropped according to SPEC 0:

| Python Version | Release Date | Support Until | Status |
|----------------|--------------|---------------|--------|
| 3.10 | 2021-10-04 | 2024-10-04 | Dropped |
| 3.11 | 2022-10-24 | 2025-10-24 | Dropped |
| 3.12 | 2023-10-02 | 2026-10-02 | **Supported** |
| 3.13 | 2024-10-07 | 2027-10-07 | **Supported** |
| 3.14 | 2025-10-01 | 2028-10-01 | **Supported** |
| 3.15 | 2026-10-05 (est.) | 2029-10-05 (est.) | **Supported** |

For core dependencies like NumPy, the 24-month window applies:

| NumPy Version | Release Date | Support Until | Status |
|---------------|--------------|---------------|--------|
| 1.20 | 2021-01-30 | 2023-01-30 | Dropped |
| 1.26 | 2023-09-16 | 2025-09-16 | Dropped |
| 2.0 | 2024-06-16 | 2026-06-16 | **Supported** |
| 2.1 | 2024-08-18 | 2026-08-18 | **Supported** |

**Note**: The actual minimum supported version may be more recent than indicated by the "Support Until" date if a newer version provides necessary features or bug fixes.

## Benefits

Adopting SPEC 0 provides several advantages:

1. **Reduced maintenance burden**: Limits the scope of supported dependency combinations
2. **Simplified CI/CD**: Reduces the test matrix complexity
3. **Community alignment**: Aligns with conventions familiar to contributors from other Scientific Python packages
4. **Access to new features**: Enables use of modern Python and library features

## References

- [SPEC 0 — Minimum Supported Dependencies](https://scientific-python.org/specs/spec-0000/)
- [Scientific Python Ecosystem Coordination](https://scientific-python.org/)
