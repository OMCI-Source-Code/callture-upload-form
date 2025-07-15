"""
pandas_utility.py

This module provides utilities for anything pandas related

Classes:
    PersonRow

Functions:
    parse_req_to_df
    process_df

Author: Terry Luan
Date: 2025-07-14
"""

from io import BytesIO
from typing import NamedTuple

import pandas as pd
from httpx import Response


class PersonRow(NamedTuple):
    Index: int
    CDRID: int
    Status: str
    Date: str
    Time: str
    Line_No: str
    Ext_No: str
    Line_Description: str
    Calling_Area: str
    From_TelNo: str
    Called_Area: str
    To_TelNo: str
    Duration: str
    Year: int
    Month: int
    Day: int


def parse_req_to_df(req: Response):
    file = BytesIO(req.content)
    df = pd.read_excel(file, skiprows=8)

    return df


def process_df(df: pd.DataFrame):
    # Add a Day/Month/Years column
    df[["Date", "Time"]] = df["Time"].str.split(pat=None, n=1, expand=True)
    dates = df["Date"].str.split("/", expand=True)
    df["Year"], df["Month"], df["Day"] = (
        dates[2],
        dates[0].str.zfill(2),
        dates[1].str.zfill(2),
    )
    df["Date"] = df["Year"] + "/" + df["Month"] + "/" + df["Day"]
    df.columns = [col.replace(" ", "_") for col in df.columns]
    return df
