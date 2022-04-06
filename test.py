import base64
import json
import requests

def wrong_password_username() -> str:
    login_dict = json.dumps({"username":"devt","password":"secrett"})
    body = base64.b64encode(login_dict.encode())

    credentials = requests.post("http://127.0.0.1:1600/token", data=body)
    access_token = str(json.loads(credentials.content))
    return access_token

def wrong_password() -> str:
    login_dict = json.dumps({"username":"dev","password":"secrett"})
    body = base64.b64encode(login_dict.encode())

    credentials = requests.post("http://127.0.0.1:1600/token", data=body)
    access_token = str(json.loads(credentials.content))
    return access_token

def wrong_username() -> str:
    login_dict = json.dumps({"username":"devt","password":"secret"})
    body = base64.b64encode(login_dict.encode())

    credentials = requests.post("http://127.0.0.1:1600/token", data=body)
    access_token = str(json.loads(credentials.content))
    return access_token

def correct_credentials() -> str:
    login_dict = json.dumps({"username":"dev","password":"secret"})
    body = base64.b64encode(login_dict.encode())

    credentials = requests.post("http://127.0.0.1:1600/token", data=body)
    access_token = str(json.loads(credentials.content))
    print(access_token)
    return access_token

#print(wrong_password())
#print(wrong_password_username())
#print(wrong_username())
#print(correct_credentials())

def run_post_request(access_token):
    with open("HPD201324TC-20220329-101119-002.pdf", "rb") as pdf_file:
        encoded = base64.b64encode(pdf_file.read())
    body=bytes(encoded)
    reply=requests.post(f"http://127.0.0.1:1600/data/{access_token}",data=body)
    filename = json.loads(reply.content.decode("utf-8")).get("filename")
    QR_contents = json.loads(reply.content.decode("utf-8")).get("QR_content")
    PDF = json.loads(reply.content.decode("utf-8")).get("Pages")
    with open(f'datafile.pdf', 'wb') as file:
        file.write(base64.b64decode(PDF))
    return {filename:QR_contents}

def run_correct_pr():
    return run_post_request(correct_credentials())

def run_wrong_pr():
    return run_post_request(wrong_password_username())

run_wrong_pr()
#TODO: in main.py exceptions toevoegen zodat de errors duidelijk zijn voor end-user