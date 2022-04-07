import os
import requests
import base64
import json

def login():
        login_dict = json.dumps({"username":"dev","password":"secret"})
        body = base64.b64encode(login_dict.encode())
        credentials = requests.post("http://127.0.0.1:1600/token", data=body)
        access_token = str(json.loads(credentials.content))
        return access_token

def test_scale(access_token):
        for file in os.listdir("Examples"):
                with open("Examples/"+file, "rb") as pdf_file:
                        encoded = base64.b64encode(pdf_file.read())
                body=bytes(encoded) 
                reply = requests.post(f"http://127.0.0.1:1600/data/{access_token}",data=body)
                print(json.loads(reply.content.decode("utf-8")).get("QR_content"))

def test_robust_easy(access_token):
        with open("easy_test.pdf", "rb") as pdf_file:
                encoded = base64.b64encode(pdf_file.read())
        body=bytes(encoded) 
        reply = requests.post(f"http://127.0.0.1:1600/data/{access_token}",data=body)
        return(json.loads(reply.content.decode("utf-8")).get("QR_content"))

print(test_scale(login()))
print(test_robust_easy(login()))