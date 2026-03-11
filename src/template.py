"""
Template generation and file reading utilities for SMB Financial Health Dashboard.

Provides:
- REQUIRED_COLUMNS: list of columns the upload pipeline expects
- generate_template_df(): returns a DataFrame with 3 example rows
- read_uploaded_file(): parses a Streamlit UploadedFile (CSV or Excel) into a
  DataFrame whose columns match what generate_company_data() produces
- get_template_csv_bytes(): returns the template as bytes for st.download_button
"""

import io

import pandas as pd

# ---------------------------------------------------------------------------
# Data contract
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: list[str] = [
    "date",
    "revenue",
    "cogs",
    "opex",
    "headcount",
    "cash_balance",
]

# ---------------------------------------------------------------------------
# Example rows — realistic SMB SaaS figures
# ---------------------------------------------------------------------------

_EXAMPLE_ROWS: list[dict] = [
    {
        "date": "2024-01-01",
        "revenue": 150_000,
        "cogs": 40_000,
        "opex": 55_000,
        "headcount": 15,
        "cash_balance": 2_000_000,
    },
    {
        "date": "2024-02-01",
        "revenue": 160_000,
        "cogs": 43_000,
        "opex": 57_000,
        "headcount": 15,
        "cash_balance": 2_060_000,
    },
    {
        "date": "2024-03-01",
        "revenue": 172_000,
        "cogs": 46_000,
        "opex": 60_000,
        "headcount": 16,
        "cash_balance": 2_115_000,
    },
]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def generate_template_df() -> pd.DataFrame:
    """Return a DataFrame with 3 example rows matching the required column schema.

    Intended for st.download_button — this produces the same data as the static
    CSV but programmatically so callers can rely on it regardless of disk state.
    """
    df = pd.DataFrame(_EXAMPLE_ROWS)
    df["date"] = pd.to_datetime(df["date"])
    return df[REQUIRED_COLUMNS]


def get_template_csv_bytes() -> bytes:
    """Return the CSV template as UTF-8 bytes suitable for st.download_button."""
    df = generate_template_df()
    # Format date as YYYY-MM-DD before serialising
    df = df.copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.to_csv(index=False).encode("utf-8")


def validate_uploaded_df(df: pd.DataFrame) -> list[str]:
    """Validate a parsed upload DataFrame against the required schema.

    Checks are ordered so that cheaper, blocking errors (missing columns) are
    reported first and later checks are only run when they are meaningful.

    Parameters
    ----------
    df:
        A DataFrame returned by ``read_uploaded_file()``.

    Returns
    -------
    list[str]
        Human-readable error strings, one per violation.  An empty list means
        the DataFrame is valid and may proceed to ``calculate_kpis()``.
    """
    errors: list[str] = []

    # --- VALID-01: column presence ---
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(
            f"Missing required columns: {', '.join(missing)}. "
            "Download the template to see the required format."
        )
        return errors  # pointless to check types if columns are absent

    # --- VALID-02a: numeric columns ---
    numeric_cols = ["revenue", "cogs", "opex", "headcount", "cash_balance"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(
                f"Column '{col}' must contain numbers only. "
                "Check for text, currency symbols (e.g. $), or blank cells."
            )
        elif df[col].isna().any():
            bad_rows = df.index[df[col].isna()].tolist()
            rows = ", ".join(str(r + 2) for r in bad_rows)
            errors.append(
                f"Column '{col}' has blank or unreadable values in rows: {rows}. "
                "Fill in all cells with numbers."
            )

    # --- VALID-02b: business rules (only if types are clean) ---
    if not errors:
        # Headcount must be > 0
        bad_hc = df.index[df["headcount"] <= 0].tolist()
        if bad_hc:
            rows = ", ".join(str(r + 2) for r in bad_hc)
            errors.append(
                f"'headcount' must be greater than 0. "
                f"Fix rows: {rows}."
            )
        # Revenue must be > 0
        bad_rev = df.index[df["revenue"] <= 0].tolist()
        if bad_rev:
            rows = ", ".join(str(r + 2) for r in bad_rev)
            errors.append(
                f"'revenue' must be greater than 0. "
                f"Fix rows: {rows}."
            )
        # COGS and opex must be non-negative
        for col in ["cogs", "opex"]:
            bad = df.index[df[col] < 0].tolist()
            if bad:
                rows = ", ".join(str(r + 2) for r in bad)
                errors.append(
                    f"'{col}' cannot be negative. Fix rows: {rows}."
                )
        # Cash balance must be non-negative
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


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Parse a Streamlit UploadedFile (CSV or Excel) into a pipeline-compatible DataFrame.

    The returned DataFrame includes all columns that ``generate_company_data()``
    produces so the existing KPI engine and charting code can consume it without
    modification:

        date, month_label, month_index, revenue, cogs, gross_profit,
        opex, net_income, headcount, cash_balance

    Parameters
    ----------
    uploaded_file:
        A ``streamlit.runtime.uploaded_file_manager.UploadedFile`` object.

    Returns
    -------
    pd.DataFrame
        Sorted by date ascending, with derived columns computed.

    Raises
    ------
    ValueError
        If the file cannot be parsed (unsupported extension or malformed content).
    """
    name: str = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            raise ValueError(
                f"Unsupported file type '{uploaded_file.name}'. "
                "Please upload a .csv or .xlsx file."
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Could not parse '{uploaded_file.name}': {exc}"
        ) from exc

    # Normalise column names (strip whitespace, lowercase)
    df.columns = [c.strip().lower() for c in df.columns]

    # Parse and sort by date (skip if date column is missing —
    # validate_uploaded_df() will report the missing column)
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
        except Exception as exc:
            raise ValueError(
                f"Could not parse 'date' column: {exc}. "
                "Use ISO format YYYY-MM-DD (e.g. 2024-01-01)."
            ) from exc

        df = df.sort_values("date").reset_index(drop=True)

    # Compute derived columns only if source columns are present.
    # Missing columns are caught by validate_uploaded_df() with actionable messages
    # rather than crashing here with an unhelpful KeyError.
    has_financials = all(c in df.columns for c in ["revenue", "cogs", "opex"])
    if has_financials:
        df["gross_profit"] = df["revenue"] - df["cogs"]
        df["net_income"] = df["revenue"] - df["cogs"] - df["opex"]

    if "date" in df.columns:
        df["month_label"] = df["date"].dt.strftime("%b %Y")
        df["month_index"] = range(1, len(df) + 1)

    # Return with column order matching generate_company_data()
    ordered_cols = [
        "date",
        "month_label",
        "month_index",
        "revenue",
        "cogs",
        "gross_profit",
        "opex",
        "net_income",
        "headcount",
        "cash_balance",
    ]
    # Only include columns that actually exist
    present_cols = [c for c in ordered_cols if c in df.columns]
    extra_cols = [c for c in df.columns if c not in ordered_cols]
    return df[present_cols + extra_cols]
