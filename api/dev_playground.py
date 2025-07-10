from utility import test_parse_req_to_ids
import pandas as pd

if __name__ == "__main__":
    df = test_parse_req_to_ids("api/CallRecords.xls")

    pd.set_option('display.max_columns', None)
    
    df["Time"] = df["Time"].str.split().str[0]
          
    row_concat = df[['Time', 'Status', 'Line No', "Ext No", "From TelNo"]].astype(str).agg('_'.join, axis=1)
    name_list = row_concat.tolist()
    print(name_list[:10])