from io import BytesIO

import pandas as pd
from httpx import Response


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


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    df = pd.read_excel("api/CallRecords.xls", skiprows=8)
    df = process_df(df)
