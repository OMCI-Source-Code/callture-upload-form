from api.callture import post_login

def test_login():
    req = post_login()
    assert req.status_code == 302

def test_get_calls():
    pass

def test_download_calls():
    pass

def test_download_recordings():
    pass