import requests

login_url = "http://127.0.0.1:8000/accounts/login/"
MAX_RETRIES = 2

client = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
client.mount('http://', adapter)

client.get(login_url)
csrftoken = client.cookies['csrftoken']
login_data = {'username': 'b','password':'senha123', 'csrfmiddlewaretoken': csrftoken}

try:
    response = client.post(login_url, data=login_data)

    if "Logout from b" in str(response.content):

        print("Logged in at {}".format(response.url))
        response2 = client.get('http://127.0.0.1:8000/ranking/')
        print("Logged in at {}".format(response.url))

        csrftoken = client.cookies['csrftoken']
        file_data = {'csrfmiddlewaretoken': csrftoken}
        headers = {"Referer": 'http://127.0.0.1:8000/ranking/'}
        print(file_data)
        print(headers)

        with open('Data\\training_data.npy', 'rb') as f:
            r = requests.post('http://127.0.0.1:8000/ranking/', files={'training_data.npy': f}, data=file_data, headers=headers)
            print("File should be sent")
            print(r.text) # 403 Forbidden -> CSRF verification failed. Request aborted.

    else:
        print("not logged in")

except Exception as e:
    print(e)
