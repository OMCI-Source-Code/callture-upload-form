import pandas as pd
from api.google_drive import a_upload_df_to_drive
from api.pandas_utility import process_df

if __name__ == "__main__":
    df = pd.read_excel("tests/data/CallRecords.xls", skiprows=8)
    df = process_df(df)
    a_upload_df_to_drive(df, {})
