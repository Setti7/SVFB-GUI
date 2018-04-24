import requests

login_url = "http://127.0.0.1:8000/accounts/login/?next=/home/"
#
# client = requests.session()
# client.get(login_url)
# csrftoken = client.cookies['csrftoken']
# login_data = {'username': 'b','password':'senha123', 'csrfmiddlewaretoken': csrftoken}
#
# print(client.get(login_url))
# try:
#     response = client.post(login_url, data=login_data)
# except Exception as e:
#     print(e)


import requests
MAX_RETRIES = 20
#url ="http://127.0.0.1:8000/accounts/login"

client = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
#client.mount('https://', adapter)
client.mount('http://', adapter)


client.get(login_url)
csrftoken = client.cookies['csrftoken']
login_data = {'username': 'b','password':'senha123', 'csrfmiddlewaretoken': csrftoken, 'next': '/version-control/'}

print(client.get(login_url))
try:
    response = client.post(login_url, data=login_data)
    print(response.content)
except Exception as e:
    print(e)
