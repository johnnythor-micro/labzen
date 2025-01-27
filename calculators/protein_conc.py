# calculators/protein_conc.py

import pandas as pd
import numpy as np
from io import StringIO
from typing import List, Tuple
import math

STANDARD_CONCENTRATIONS = [
    2.0,   # A1
    1.5,   # A2
    1.0,   # A3
    0.75,  # A4
    0.5,   # A5
    0.25,  # A6
    0.125, # A7
    0.025, # A8
    0.0    # A9
]
"""
These are the fixed concentrations for wells A1 through A9 (in mg/mL).
We assume each has 2 duplicate measurements, thus up to A1..A2 (rep1, rep2),
A2..B2, etc., depending on how the user organizes it.
"""

def parse_standard_duplicates(raw_text: str) -> pd.DataFrame:
    """
    Parse user-pasted absorbance data for 9 standard concentrations,
    each in duplicate.

    :param raw_text: multiline string with 9 rows (A1..A9), each row containing
                     two absorbance values (rep1, rep2).
                     Example (tab or space separated):
                        0.100 0.105
                        0.110 0.115
                        ...
                        0.010 0.015
    :return: DataFrame with columns: [conc_mg_mL, abs_rep1, abs_rep2, abs_mean]
    """
    lines = raw_text.strip().splitlines()
    if len(lines) < 9:
        raise ValueError("You must provide at least 9 lines of data for the 9 standard concentrations (A1–A9).")

    # We'll read all lines as 2 columns of absorbance
    data = []
    for i, line in enumerate(lines[:9]):
        # Use split to handle tabs/spaces
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Line {i+1} doesn't have 2 columns of absorbance.")
        rep1 = float(parts[0])
        rep2 = float(parts[1])
        conc = STANDARD_CONCENTRATIONS[i]
        data.append([conc, rep1, rep2])

    df = pd.DataFrame(data, columns=["conc_mg_mL", "abs_rep1", "abs_rep2"])
    df["abs_mean"] = df[["abs_rep1", "abs_rep2"]].mean(axis=1)
    return df


def compute_standard_regression(standard_df: pd.DataFrame) -> Tuple[float, float]:
    """
    Given a DataFrame with columns: [conc_mg_mL, abs_mean],
    perform a linear regression: Abs = slope * Conc + intercept.

    :return: (slope, intercept)
    """
    x = standard_df["conc_mg_mL"].values
    y = standard_df["abs_mean"].values

    if len(x) < 2:
        raise ValueError("Need at least 2 points for regression.")

    fit = np.polyfit(x, y, 1)  # linear fit
    slope, intercept = fit[0], fit[1]
    return slope, intercept


def compute_sample_concentration(
    abs_val: float,
    slope: float,
    intercept: float,
    dilution_factor: float
) -> float:
    """
    Compute protein concentration (mg/mL) from an absorbance reading,
    using the standard-curve slope/intercept and a known dilution factor.

    :param abs_val: measured absorbance
    :param slope: slope from standard curve
    :param intercept: intercept from standard curve
    :param dilution_factor: user-specified sample dilution factor (>=1)
    :return: final mg/mL
    """
    calc_conc = (abs_val - intercept) / slope
    if calc_conc < 0:
        calc_conc = 0.0
    return calc_conc * dilution_factor


def compute_total_yield(
    concentration_mg_mL: float,
    total_volume_uL: float
) -> float:
    """
    Given final concentration (mg/mL) and total volume in µL,
    compute total mg of protein.
    """
    total_volume_mL = total_volume_uL / 1000.0
    return concentration_mg_mL * total_volume_mL
