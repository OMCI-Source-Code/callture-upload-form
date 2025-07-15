
from api.google_drive import setup_date_folders, upload_df_to_drive

from api.pandas_utility import process_df
import pandas as pd

import time


import asyncio

if __name__ == "__main__":
    print('Starting')
    date_range = "01 Jul 2025 12:00 AM - 10 Jul 2025 12:00 AM"
    day_id_map = setup_date_folders(date_range)
    
    df = pd.read_excel("tests/data/CallRecords.xls", skiprows=8)
    df = process_df(df)
    
    # # Async Sem - 20 limit - It took 1654.6957413090004 seconds to run
    # a_sem_start = time.perf_counter()
    # asyncio.run(a_upload_df_to_drive(df, day_id_map, True))
    # a_sem_end = time.perf_counter()
    # print(f"Async Sem - It took {a_sem_end - a_sem_start} seconds to run")
    
    
    # Batched async
    # a_sem_start = time.perf_counter()
    # asyncio.run(upload_df_to_drive(df, day_id_map, True))
    # a_sem_end = time.perf_counter()
    # print(f"Async Sem - It took {a_sem_end - a_sem_start} seconds to run")
    
    # Errors because Google doesn't support async fully
    # a_nosem_start = time.perf_counter()
    # asyncio.run(a_upload_df_to_drive(df, day_id_map, True))
    # try:
    #     a_nosem_end = time.perf_counter()
    # except Exception as e:
    #     print("error")
    #     print(f"Async NoSem - It took {a_nosem_end - a_nosem_start} seconds to run")
    
    
    # Sync - It took 2059.8085700089996 seconds to run
    s_start = time.perf_counter()
    upload_df_to_drive(df, day_id_map)
    s_end = time.perf_counter()
    print(f"Sync - It took {s_end - s_start} seconds to run")