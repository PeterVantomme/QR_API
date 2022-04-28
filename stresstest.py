import json, requests, os

def test():
    login_dict = json.dumps({"username":"dev","password":"Titeca_Admin_1234"})
    credentials = requests.post("http://127.0.0.1/token", data=login_dict)
    access_token = str(json.loads(credentials.content))

    for file in os.listdir("Examples_PDFs"):
        try:
            body = open(f"Examples_PDFs/{file}","rb")
        except FileNotFoundError:
            reply = FileNotFoundError
        reply=requests.post(f"http://127.0.0.1/data/",files={"file":body}, headers={'Authorization': f'Bearer {access_token}'})
        body.close()
        if reply.status_code in [400,401,404]:
            reply = json.loads(reply.content.decode())
        elif reply.status_code == 200:
            filename = json.loads(reply.content).get("filename")
            QR_contents = json.loads(reply.content).get(filename)
            PDF = requests.get(f"http://127.0.0.1/get_pdf/{filename}",headers={'Authorization': f'Bearer {access_token}'})
            with open(f'datafile.pdf', 'wb') as file:
                file.write(PDF.content)
            reply = {filename:QR_contents}
        else:
            reply = reply.status_code," ",reply.content
        print(reply)


test()