from io import BytesIO
import pandas as pd

def parse_req_to_ids(req):
    file = BytesIO(req.content)
    df = pd.read_excel(file, skiprows=8)
    print(df.head(10))
    
    return df