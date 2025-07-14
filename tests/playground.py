import asyncio

import pandas as pd

from api.google_drive import a_upload_df_to_drive
from api.pandas_utility import process_df

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    df = pd.read_excel("tests/data/CallRecords.xls", skiprows=8)
    df = process_df(df)
    print(df)
    # asyncio.run(a_upload_df_to_drive(df, {}))
