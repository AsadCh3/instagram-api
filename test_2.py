import random

import requests

url = 'https://www.instagram.com/api/v1/users/web_profile_info/?username=crictracker'
headers_list = requests.get("https://linkedinloggedout.s3.ap-south-1.amazonaws.com/browser-headers/headers.json").json()[
                'desktop']
proxy = {'http': 'http://geonode_29EgtblBUB:daadd8a2-2815-4c8e-b59e-5f2ff2f6eace@premium-residential.geonode.com:9000',
         'https': 'http://geonode_29EgtblBUB:daadd8a2-2815-4c8e-b59e-5f2ff2f6eace@premium-residential.geonode.com:9000'}
for i in range(0, 11):
    try:
        header = random.choice(headers_list)
        header['user-agent'] = "Mozilla/5.0 (Linux; Android 14; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36 Instagram 313.0.0.26.328 Android (34/14; 378dpi; 1080x2215; Google/google; Pixel 6; oriole; oriole; de_DE; 554218055)"
        response = requests.get(url, headers=header, proxies=proxy)
        print(response.status_code)
        if response.status_code != 200:
            print(response.text)
    except Exception as e:
        print(e)


