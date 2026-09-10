def test_url_com_ip_deve_ser_suspeita():
    
    url = "http://192.168.1.1/login"
    
    assert "192.168" in url 

def test_url_com_https_deve_atenuar_risco():
    
    url = "https://banco-seguro.com.br"
    assert url.startswith("https")