from io import BytesIO
import pandas as pd

def parse_req_to_ids(req):
    file = BytesIO(req.content)
    df = pd.read_excel(file)
    
    first_col = df.iloc[:, 0]
    
    return first_col