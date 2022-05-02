import json, requests, os

def test():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    login_dict = json.dumps({"username":"dev","password":"Titeca_Admin_1234"})
    credentials = requests.post("http://127.0.0.1/token", data=login_dict, verify=False)
    access_token = str(json.loads(credentials.content))

    for file in os.listdir("Examples_PDFs"):
        try:
            body = open(f"Examples_PDFs/{file}","rb")
        except FileNotFoundError:
            raise FileNotFoundError
        reply=requests.post(f"http://127.0.0.1/data/",files={"file":body}, headers={'Authorization': f'Bearer {access_token}'}, verify=False)
        body.close()
        if reply.status_code in [400,401,404]:
            reply = json.loads(reply.content.decode())
        elif reply.status_code == 200:
            filename = json.loads(reply.content).get("filename")
            QR_contents = json.loads(reply.content).get(filename)
            #memalloc = json.loads(reply.content).get("malloc")
            PDF = requests.get(f"http://127.0.0.1/get_pdf/{filename}",headers={'Authorization': f'Bearer {access_token}'}, verify=False)
            with open(f'datafile.pdf', 'wb') as file:
                file.write(PDF.content)
            reply = ("filename: ",filename,", content: ", QR_contents)
        else:
            reply = reply.status_code," ",reply.content
        print(reply)


test()