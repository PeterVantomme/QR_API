import base64
import json
import requests

login_dict = json.dumps({"username":"dev","password":"secret"})
body = base64.b64encode(login_dict.encode())
credentials = requests.post("http://127.0.0.1:1600/token", data=body)
access_token = str(json.loads(credentials.content))
with open("HPD201324TC-20220329-101119-002.pdf", "rb") as pdf_file:
    encoded = base64.b64encode(pdf_file.read())


body=bytes(encoded)
reply=requests.post(f"http://127.0.0.1:1600/data/{access_token}",data=body)

print(reply.content)
filename = json.loads(reply.content.decode("utf-8")).get("filename")
QR_contents = json.loads(reply.content.decode("utf-8")).get("QR_content")
PDF = json.loads(reply.content.decode("utf-8")).get("Pages")
with open(f'datafile.pdf', 'wb') as file:
    file.write(base64.b64decode(PDF))
    print(filename," : ",QR_contents)

reply = requests.get("http://127.0.0.1:1600/home", params=str({"token":access_token}))
print(reply)