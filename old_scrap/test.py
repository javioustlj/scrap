import requests

user_name = '18605883515'
password = '.Tljgmr001'
auto_login = "1"
# post_type = "ajax"
return_url = "http://www.jisilu.cn/data/sfnew/"

headers = {
    'accept' : 'application/json, text/javascript, */*; q=0.01',
    'connect' : 'keep-alive',
    'referer' : 'https://www.jisilu.cn/login/',
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42'
}

def login():

    url_login = 'https://www.jisilu.cn/account/ajax/login_process/'
    login_params = {
        "user_name" : user_name,
        "password" : password,
        "auto_login" : auto_login,
        'aes' : 1
        # "_post_type" : post_type
    }

    r = requests.post(url_login, data=login_params)
    print(r.status_code)
    print (r.content)
    print (r.raw)

login()
