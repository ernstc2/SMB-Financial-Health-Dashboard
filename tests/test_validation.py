"""
Unit tests for validate_uploaded_df() in src/template.py.

Test coverage:
    VALID-01 — column presence (missing columns, all present)
    VALID-02 — data types (non-numeric columns) and business rules
                (zero headcount, negative cogs, negative cash, single row)
    VALID-03 — actionable error messages (column names and row numbers in text)
"""

import pandas as pd
import pytest

from src.template import generate_template_df, validate_uploaded_df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_df() -> pd.DataFrame:
    """Return a minimal valid 2-row DataFrame based on the template schema."""
    return generate_template_df().copy()


# ---------------------------------------------------------------------------
# VALID-01: Column presence
# ---------------------------------------------------------------------------

def test_missing_columns():
    """DataFrame missing 'revenue' and 'headcount' -> errors naming both."""
    df = _valid_df().drop(columns=["revenue", "headcount"])
    errors = validate_uploaded_df(df)
    assert len(errors) >= 1, "Should return at least one error"
    combined = " ".join(errors)
    assert "revenue" in combined, "Error should name the missing 'revenue' column"
    assert "headcount" in combined, "Error should name the missing 'headcount' column"


def test_all_columns_present():
    """DataFrame with all required columns -> column presence check produces no errors.

    This test only verifies the column-presence step: if we pass a full-schema
    DataFrame with valid types and values, the full validation returns no errors.
    """
    df = _valid_df()
    errors = validate_uploaded_df(df)
    assert errors == [], f"Expected no errors for valid template df, got: {errors}"


# ---------------------------------------------------------------------------
# VALID-02a: Numeric type checks
# ---------------------------------------------------------------------------

def test_non_numeric_revenue():
    """DataFrame where revenue column contains string 'N/A' -> error naming 'revenue'."""
    df = _valid_df()
    df["revenue"] = df["revenue"].astype(object)
    df.loc[0, "revenue"] = "N/A"
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert "revenue" in combined, "Error should name the 'revenue' column"
    assert len(errors) >= 1


def test_non_numeric_multiple():
    """DataFrame where cogs and opex are strings -> errors naming both columns."""
    df = _valid_df()
    df["cogs"] = df["cogs"].astype(str) + " bad"
    df["opex"] = df["opex"].astype(str) + " bad"
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert "cogs" in combined, "Error should name the 'cogs' column"
    assert "opex" in combined, "Error should name the 'opex' column"


# ---------------------------------------------------------------------------
# VALID-02b: Business rule checks
# ---------------------------------------------------------------------------

def test_zero_headcount():
    """DataFrame with headcount=0 in row index 1 -> error mentioning row 3."""
    df = _valid_df()
    df.loc[1, "headcount"] = 0
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert "headcount" in combined, "Error should mention 'headcount'"
    # Row index 1 maps to spreadsheet row 3 (header=row1, data starts row2)
    assert "3" in combined, "Error should report spreadsheet row 3 for index 1"


def test_negative_cogs():
    """DataFrame with cogs=-500 in row index 0 -> error mentioning row 2 and 'cogs'."""
    df = _valid_df()
    df.loc[0, "cogs"] = -500
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert "cogs" in combined, "Error should mention 'cogs'"
    # Row index 0 maps to spreadsheet row 2
    assert "2" in combined, "Error should report spreadsheet row 2 for index 0"


def test_negative_cash():
    """DataFrame with cash_balance=-100 -> error mentioning 'cash_balance'."""
    df = _valid_df()
    df.loc[0, "cash_balance"] = -100
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert "cash_balance" in combined, "Error should mention 'cash_balance'"


def test_single_row():
    """DataFrame with only 1 row -> error about minimum 2 months."""
    df = _valid_df().iloc[:1].copy().reset_index(drop=True)
    errors = validate_uploaded_df(df)
    combined = " ".join(errors)
    assert len(errors) >= 1, "Should return error for single-row file"
    assert "2" in combined or "month" in combined.lower(), (
        "Error should mention minimum row requirement"
    )


# ---------------------------------------------------------------------------
# VALID-03: Valid file and message quality
# ---------------------------------------------------------------------------

def test_valid_file_passes():
    """DataFrame matching generate_template_df() output -> returns empty list."""
    df = _valid_df()
    errors = validate_uploaded_df(df)
    assert errors == [], f"Valid template DataFrame should produce no errors, got: {errors}"


def test_error_messages_actionable():
    """All error strings contain the column name they refer to (no generic messages)."""
    # Test a non-numeric column error
    df_bad_type = _valid_df()
    df_bad_type["cogs"] = "bad"
    errors_type = validate_uploaded_df(df_bad_type)
    assert errors_type, "Should have at least one error"
    assert "cogs" in " ".join(errors_type), "Type error should name the column"

    # Test a business rule error
    df_bad_rule = _valid_df()
    df_bad_rule.loc[0, "headcount"] = 0
    errors_rule = validate_uploaded_df(df_bad_rule)
    assert errors_rule, "Should have at least one error"
    assert "headcount" in " ".join(errors_rule), "Rule error should name the column"

    # Test missing column error
    df_missing = _valid_df().drop(columns=["opex"])
    errors_missing = validate_uploaded_df(df_missing)
    assert errors_missing, "Should have at least one error"
    assert "opex" in " ".join(errors_missing), "Missing column error should name the column"
