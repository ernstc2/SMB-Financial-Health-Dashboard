# Phase 7: Validation - Research

**Researched:** 2026-03-10
**Domain:** CSV/Excel upload validation — column presence, data-type checking, business-rule enforcement, Streamlit error display
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| VALID-01 | System validates that required columns are present (date, revenue, COGS, opex, headcount, cash_balance) | REQUIRED_COLUMNS list already defined in src/template.py; simple set-difference check surfaces missing names |
| VALID-02 | System validates data types (numeric values, valid dates, no impossible values) | pandas dtype inspection + per-column business-rule sweeps identify bad rows; specific cell coordinates surfaced via boolean mask |
| VALID-03 | System displays specific, actionable error messages telling users exactly what to fix | st.error() / st.warning() with column names and row numbers; message templates documented below |
</phase_requirements>

---

## Summary

Phase 6 wired file upload into the dashboard and surfaces parse errors (bad file format, unreadable content) as `ValueError` with a generic sidebar `st.error()`. What it does NOT do is validate the content of a successfully-parsed DataFrame: it does not check whether the six required columns exist, whether numeric columns contain numbers, or whether values obey business rules (positive headcount, non-negative cash balance, etc.).

Phase 7 adds a dedicated validation layer that sits between `read_uploaded_file()` and `calculate_kpis()`. All validation lives in one new function — `validate_uploaded_df()` — inside `src/template.py`. The function returns a list of human-readable error strings; the caller (app.py) decides whether to display them and block processing. Valid files pass through this function returning an empty list, so the happy path is completely silent.

The user-facing display uses Streamlit's native `st.error()` for blocking problems (missing columns, wrong types) and `st.warning()` for non-blocking cautions (e.g., fewer than 3 months of data). Error messages always name the exact column and, for row-level issues, the row number.

**Primary recommendation:** Implement `validate_uploaded_df(df) -> list[str]` in `src/template.py`, call it in the `app.py` upload branch before `calculate_kpis()`, and display errors with `st.error()`.

---

## Standard Stack

No new dependencies required. Everything needed is already installed.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | already in requirements.txt | dtype inspection, boolean masks, `.isnull()`, `.apply()` | The project's data layer; all DataFrames are pandas objects |
| streamlit | already in requirements.txt | `st.error()`, `st.warning()` for user-facing messages | The project's only UI layer; no alternative |

### No New Installs
The validation logic requires only Python builtins and pandas — both already present. `requirements.txt` does not change in Phase 7.

---

## Architecture Patterns

### Where Validation Lives

The function belongs in `src/template.py` alongside `read_uploaded_file()`. Reasons:
- `template.py` already owns the data contract (`REQUIRED_COLUMNS`)
- Keeping validation co-located with the column definition prevents drift
- `app.py` stays thin: it calls validate, checks the result, displays errors or continues

### Recommended Call Flow

```
app.py (upload branch)
  └─ read_uploaded_file(uploaded_file)     # Phase 6: parse bytes → DataFrame
       └─ returns df (raw, no KPI cols)
  └─ validate_uploaded_df(df)             # Phase 7: NEW — returns list[str]
       └─ [] on success → continue
       └─ [errors...] → st.error(), stop
  └─ calculate_kpis(df)                   # existing; only reached on valid data
```

### Pattern 1: Validate-then-Block

```python
# In app.py, inside the `if uploaded_file is not None:` branch
try:
    df_uploaded = read_uploaded_file(uploaded_file)
    errors = validate_uploaded_df(df_uploaded)
    if errors:
        for msg in errors:
            st.sidebar.error(msg)
        df_full = load_data(selected_company, v="v2")   # fall back to sample
    else:
        df_full = calculate_kpis(df_uploaded)
        selected_company = uploaded_file.name.rsplit(".", 1)[0]
except Exception as e:
    st.sidebar.error(f"Could not read file: {e}")
    df_full = load_data(selected_company, v="v2")
```

This preserves the existing `except` fallback for parse errors (Phase 6) while adding a clean validation gate (Phase 7).

### Pattern 2: Validate Function Structure

```python
# src/template.py — new function
def validate_uploaded_df(df: pd.DataFrame) -> list[str]:
    """
    Validate a parsed upload DataFrame against the required schema.

    Returns a list of human-readable error strings.
    An empty list means the file is valid and may proceed to calculate_kpis().
    """
    errors: list[str] = []

    # --- VALID-01: column presence ---
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(
            f"Missing required columns: {', '.join(missing)}. "
            "Download the template to see the required format."
        )
        return errors   # pointless to check types if columns are absent

    # --- VALID-02a: numeric columns ---
    numeric_cols = ["revenue", "cogs", "opex", "headcount", "cash_balance"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(
                f"Column '{col}' must contain numbers only. "
                f"Check for text, currency symbols, or blank cells."
            )

    # --- VALID-02b: business rules (only if types are clean) ---
    if not errors:
        # No negative headcount
        bad_hc = df.index[df["headcount"] <= 0].tolist()
        if bad_hc:
            rows = ", ".join(str(r + 2) for r in bad_hc)   # +2: header row + 0-index
            errors.append(
                f"'headcount' must be greater than 0. "
                f"Fix rows: {rows}."
            )
        # Revenue must be positive
        bad_rev = df.index[df["revenue"] <= 0].tolist()
        if bad_rev:
            rows = ", ".join(str(r + 2) for r in bad_rev)
            errors.append(
                f"'revenue' must be greater than 0. "
                f"Fix rows: {rows}."
            )
        # COGS / opex non-negative
        for col in ["cogs", "opex"]:
            bad = df.index[df[col] < 0].tolist()
            if bad:
                rows = ", ".join(str(r + 2) for r in bad)
                errors.append(
                    f"'{col}' cannot be negative. Fix rows: {rows}."
                )
        # Cash balance non-negative
        bad_cash = df.index[df["cash_balance"] < 0].tolist()
        if bad_cash:
            rows = ", ".join(str(r + 2) for r in bad_cash)
            errors.append(
                f"'cash_balance' cannot be negative. Fix rows: {rows}."
            )
        # Minimum row count (KPI engine needs at least 2 rows for MoM growth)
        if len(df) < 2:
            errors.append(
                "File must contain at least 2 months of data "
                f"(found {len(df)} row)."
            )

    return errors
```

### Anti-Patterns to Avoid

- **Silently clamping bad values:** Never replace negative headcount with 0 or drop bad rows. The user must know their data is wrong; silent correction produces misleading KPIs.
- **Generic messages:** "Invalid data" is not actionable. Every error must name the column and ideally the row.
- **Blocking on warnings:** Fewer than 6 months of data is not an error — it's a UX note. Use `st.warning()` not `st.error()` for soft cautions.
- **Catching all exceptions inside validate:** The function should raise unexpected errors rather than swallowing them; parse errors belong in the `read_uploaded_file()` try/except, not here.
- **Checking types before confirming columns exist:** Always do VALID-01 first and return early. Attempting type-checks on missing columns raises `KeyError`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Numeric type detection | Custom string-scanning loop | `pd.api.types.is_numeric_dtype(df[col])` | Handles int64, float64, and pandas nullable Int64 correctly; survives NaN cells |
| Date parsing | Regex patterns | `pd.to_datetime()` already in `read_uploaded_file()` | Date column is already converted to datetime by Phase 6; Phase 7 only needs to verify it's not all-null |
| Row-number reporting | Custom counter | `df.index[mask].tolist()` then add 2 for display (header + 0-index) | pandas boolean index gives exact row positions |
| Collecting multiple errors | Raise on first error | Accumulate into a `list[str]`, return all | Users need to see every problem at once, not fix-and-resubmit one error at a time |

**Key insight:** `pd.api.types.is_numeric_dtype()` is the correct pandas idiom for column-level type checking. It is part of the stable public API (`pandas.api.types`) and handles all numeric dtypes including nullable integers introduced in pandas 1.0.

---

## Common Pitfalls

### Pitfall 1: Type Check Fails on Mixed-Type Columns Loaded from CSV

**What goes wrong:** A user's CSV has a header like `revenue` but a row contains `"N/A"` or `"$150,000"`. `pd.read_csv()` will infer the column as `object` dtype. `is_numeric_dtype()` returns `False`, which correctly flags the column — but the error message must explain *why* (text values, currency symbols) not just say "not numeric."
**Why it happens:** pandas infers dtype from the whole column; one text cell makes the column `object`.
**How to avoid:** Error message text should say "Check for text, currency symbols (e.g. $), or blank cells."
**Warning signs:** Column dtype is `object` but column name is a numeric field.

### Pitfall 2: Missing Column Check Before Type Check

**What goes wrong:** `validate_uploaded_df` tries `df["revenue"]` when `revenue` is absent → `KeyError` crash instead of clean error message.
**Why it happens:** Validation steps run in the wrong order.
**How to avoid:** VALID-01 (column presence) must run first and return immediately if any columns are missing. No subsequent checks should run until all required columns are confirmed present.
**Warning signs:** Uncaught `KeyError` in production.

### Pitfall 3: Row Numbers Off by One (or Two)

**What goes wrong:** Reporting "row 0" when the user's spreadsheet shows row 2 (row 1 is the header).
**Why it happens:** pandas uses 0-based DataFrame indices; spreadsheet row numbers include the header and are 1-based.
**How to avoid:** Convert `df.index` values to display row numbers with `row_number = index + 2` (add 1 for 0-base, add 1 more for header row).
**Warning signs:** User looks at reported row and finds wrong data.

### Pitfall 4: Error Display Placement

**What goes wrong:** Showing errors in the main page body before the charts render, causing a jarring UX where half the old dashboard is still visible below the errors.
**Why it happens:** `st.error()` in the main area renders at that point in the script; if the fallback branch still computes charts, they appear below.
**How to avoid:** Display errors in `st.sidebar.error()` (consistent with existing Phase 6 error placement), set a boolean flag, and skip `calculate_kpis()` entirely so the dashboard shows sample data rather than crashing.

### Pitfall 5: Validate Before `calculate_kpis`, Not After

**What goes wrong:** Calling `calculate_kpis(df)` on a bad DataFrame causes a `ZeroDivisionError` (headcount = 0 → revenue_per_employee), `NaN` propagation, or misleading KPI values.
**Why it happens:** `calculate_kpis` does `df["revenue"] / df["headcount"]` — zero headcount causes infinity/NaN silently.
**How to avoid:** Call `validate_uploaded_df(df)` and check for errors before any call to `calculate_kpis()`.

---

## Code Examples

### Column Presence Check (VALID-01)

```python
# Source: pandas documented pattern + REQUIRED_COLUMNS from src/template.py
missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    return [
        f"Missing required columns: {', '.join(missing)}. "
        "Download the template to see the required format."
    ]
```

### Numeric Type Check (VALID-02a)

```python
# Source: pandas.api.types documentation
import pandas as pd

numeric_cols = ["revenue", "cogs", "opex", "headcount", "cash_balance"]
for col in numeric_cols:
    if not pd.api.types.is_numeric_dtype(df[col]):
        errors.append(
            f"Column '{col}' must contain numbers only. "
            "Check for text, currency symbols (e.g. $), or blank cells."
        )
```

### Business Rule Check with Row Numbers (VALID-02b)

```python
# Headcount must be > 0
bad_rows = df.index[df["headcount"] <= 0].tolist()
if bad_rows:
    display_rows = ", ".join(str(i + 2) for i in bad_rows)
    errors.append(
        f"'headcount' must be greater than 0. "
        f"Fix spreadsheet rows: {display_rows}."
    )
```

### Streamlit Display in app.py

```python
# In the upload branch of app.py
errors = validate_uploaded_df(df_uploaded)
if errors:
    for msg in errors:
        st.sidebar.error(msg)
    df_full = load_data(selected_company, v="v2")   # fall back gracefully
else:
    df_full = calculate_kpis(df_uploaded)
    selected_company = uploaded_file.name.rsplit(".", 1)[0]
```

---

## Business Rules Reference

The following table is the definitive set of impossible-value checks for VALID-02:

| Column | Rule | Error Message Pattern |
|--------|------|----------------------|
| `headcount` | > 0 (must have at least one employee) | `'headcount' must be greater than 0. Fix rows: {rows}.` |
| `revenue` | > 0 (zero revenue is treated as data error, not a valid business state) | `'revenue' must be greater than 0. Fix rows: {rows}.` |
| `cogs` | >= 0 (cannot have negative cost of goods) | `'cogs' cannot be negative. Fix rows: {rows}.` |
| `opex` | >= 0 (cannot have negative operating expense) | `'opex' cannot be negative. Fix rows: {rows}.` |
| `cash_balance` | >= 0 (negative cash is modelled as $0 cash + outstanding debt, not negative balance in this tool) | `'cash_balance' cannot be negative. Fix rows: {rows}.` |
| Row count | >= 2 rows (need at least 2 months for MoM growth calculation) | `File must contain at least 2 months of data (found {n} row).` |

**Note on `date`:** The date column is already coerced to `datetime` by `read_uploaded_file()`. If that coercion fails, a `ValueError` is raised before `validate_uploaded_df()` is ever called. Phase 7 does not need to re-validate dates.

---

## Integration Points

### What Phase 6 Already Handles (Do Not Duplicate)

| Concern | Where handled | Phase 7 action |
|---------|---------------|----------------|
| Unsupported file extension | `read_uploaded_file()` raises ValueError | None — already caught |
| Unreadable/corrupt file | `read_uploaded_file()` except block | None — already caught |
| Unparseable date column | `read_uploaded_file()` raises ValueError with date-specific message | None — already caught |
| Column name normalisation (strip/lowercase) | `read_uploaded_file()` first step | None — already done; REQUIRED_COLUMNS are lowercase |

### What Phase 7 Must Add

| Concern | Where to add | Mechanism |
|---------|-------------|-----------|
| Missing required columns | `validate_uploaded_df()` in template.py | Set difference against REQUIRED_COLUMNS |
| Non-numeric numeric columns | `validate_uploaded_df()` | `pd.api.types.is_numeric_dtype()` |
| Impossible values (negative, zero headcount, etc.) | `validate_uploaded_df()` | Boolean mask per column |
| Error display | `app.py` upload branch | `st.sidebar.error()` per error string |
| Minimum row count | `validate_uploaded_df()` | `len(df) < 2` check |

---

## Validation Architecture

> `workflow.nyquist_validation` is not set to false in .planning/config.json (the key is absent), so this section is included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected — no pytest.ini, no tests/ directory, no test scripts |
| Config file | None — Wave 0 must create if tests are written |
| Quick run command | `python -m pytest tests/ -x -q` (after Wave 0 setup) |
| Full suite command | `python -m pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VALID-01 | Missing columns → non-empty error list with column names | unit | `pytest tests/test_validation.py::test_missing_columns -x` | Wave 0 |
| VALID-01 | All required columns present → no column errors | unit | `pytest tests/test_validation.py::test_all_columns_present -x` | Wave 0 |
| VALID-02 | Non-numeric revenue → error names the column | unit | `pytest tests/test_validation.py::test_non_numeric_revenue -x` | Wave 0 |
| VALID-02 | Zero headcount → error with row number | unit | `pytest tests/test_validation.py::test_zero_headcount -x` | Wave 0 |
| VALID-02 | Negative cogs → error with row number | unit | `pytest tests/test_validation.py::test_negative_cogs -x` | Wave 0 |
| VALID-02 | Single-row file → error about minimum row count | unit | `pytest tests/test_validation.py::test_single_row -x` | Wave 0 |
| VALID-03 | Error messages contain column name | unit | Covered by above tests via string assertion | Wave 0 |
| VALID-03 | Valid file returns empty list | unit | `pytest tests/test_validation.py::test_valid_file_passes -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m pytest tests/test_validation.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_validation.py` — covers all VALID-0x requirements above
- [ ] `tests/__init__.py` — empty init so pytest discovers the package
- [ ] Framework install: `pip install pytest` — not currently in requirements.txt

*(pytest is the standard Python test framework; adding it as a dev dependency does not affect the running app)*

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|-----------------|--------|
| Raise on first error, show generic message | Accumulate all errors, show specific messages | User fixes everything in one iteration instead of fix-and-resubmit cycles |
| Validate inside read function | Separate validate function, called by app | Testable in isolation; clear single responsibility |

---

## Open Questions

1. **Should `validate_uploaded_df` be imported by app.py directly, or called inside `read_uploaded_file`?**
   - What we know: Separating them keeps `read_uploaded_file` responsible for parsing and `validate_uploaded_df` responsible for correctness. The app can show errors without coupling them.
   - What's unclear: Whether a future Phase (8+) might want to validate silently and return a result rather than display errors.
   - Recommendation: Keep separate. The planner should structure 07-01 so `validate_uploaded_df` is its own exported function, and app.py calls it explicitly. This is more testable and more flexible.

2. **Should warnings (e.g., very few rows) use `st.warning` or `st.info`?**
   - What we know: `st.error` halts processing; `st.warning` does not. The project already uses `st.info` for the "clear file" guidance note.
   - Recommendation: Use `st.warning` for soft issues (< 6 months of data) displayed in the sidebar. `st.error` for hard failures that block `calculate_kpis`. Keep all validation messages in the sidebar to avoid visual fragmentation.

---

## Sources

### Primary (HIGH confidence)

- `src/template.py` — existing `REQUIRED_COLUMNS` constant and `read_uploaded_file()` implementation reviewed in full
- `src/kpi_engine.py` — confirmed which columns it accesses (`headcount`, `revenue`, `net_income`, `cash_balance`) and where division occurs (revenue / headcount, cash_balance / burn_rate)
- `app.py` — upload branch at lines 267-278 is the exact integration point for Phase 7 changes
- `.planning/phases/06-file-input/06-VERIFICATION.md` — confirmed Phase 6 scope boundary: parse errors caught, content validation deferred
- `.planning/STATE.md` decision log — confirmed "column validation deferred to Phase 7 validator"

### Secondary (MEDIUM confidence)

- pandas `api.types` module: `is_numeric_dtype` is documented in the stable pandas public API under `pandas.api.types`; behavior for mixed-type object columns is well-established

### Tertiary (LOW confidence)

- None — all findings verified from first-party source code

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — no new dependencies; everything already in the project
- Architecture: HIGH — integration point in app.py is pinned to specific lines; validate-then-block pattern is standard Streamlit practice
- Pitfalls: HIGH — derived from direct inspection of `read_uploaded_file()` and `calculate_kpis()` code paths; pitfall scenarios confirmed from existing implementation
- Business rules: HIGH — rules derived from KPI engine division operations (headcount > 0 required by `revenue / headcount`) and domain logic (cash_balance used in runway calculation)

**Research date:** 2026-03-10
**Valid until:** 2026-06-10 (stable domain; pandas API and Streamlit display functions are stable)
