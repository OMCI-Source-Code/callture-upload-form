
from api.google_drive import setup_date_folders, a_upload_df_to_drive

from api.pandas_utility import process_df
import pandas as pd

import time


import asyncio

if __name__ == "__main__":
    print('Starting')
    date_range = "01 Jul 2025 12:00 AM - 10 Jul 2025 12:00 AM"
    day_id_map = setup_date_folders(date_range)
    
    
    start = time.perf_counter()
    
    df = pd.read_excel("tests/data/CallRecords_tenth.xls", skiprows=8)
    df = process_df(df)
    
    asyncio.run(a_upload_df_to_drive(df, day_id_map))
    
    end = time.perf_counter()
    print(f"It took {end - start} to run")