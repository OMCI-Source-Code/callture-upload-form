from api.callture import post_login, post_get_calls, post_download_calls
from api.pandas_utility import parse_req_to_df, process_df
from api.google_drive import upload_df_to_drive

def test_single_line_upload():
    lineNo = "All"
    extNo = "All"
    dateRange = "07 Jul 2025 12:00 AM - 10 Jul 2025 12:00 AM"
    
    req = post_login()
    cookies = req.cookies
    req = post_get_calls(cookies, lineNo, extNo, dateRange)
    req = post_download_calls(cookies)
    
    df = parse_req_to_df(req)
    df = process_df(df)
    
    upload_df_to_drive(df)
    
# def test_multiple_line_upload():
#     lineNo = ["", ""]
#     extNo = "All"
#     dateRange = ""
    
#     req = post_login()
#     cookies = req.cookies
#     req = post_get_calls(cookies, lineNo, extNo, dateRange)
#     req = post_download_calls(cookies)
    
#     df = parse_req_to_df(req)
#     df = process_df(df)