import base64
import json
import zlib
import requests

with open("HPD201324TC-20220329-101119-002.pdf", "rb") as pdf_file:
    encoded = base64.b64encode(pdf_file.read())

body=bytes(encoded)
reply=requests.post("http://127.0.0.1:80/data",body)

filename = json.loads(reply.content.decode("utf-8")).get("filename")
QR_contents = json.loads(reply.content.decode("utf-8")).get("QR_content")
PDF = json.loads(reply.content.decode("utf-8")).get("Pages")
file = open(f'datafile.pdf', 'wb')
file.write(base64.b64decode(PDF))
print(filename," : ",QR_contents)
file.close()
