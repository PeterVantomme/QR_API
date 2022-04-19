import base64
import json
import unittest
import requests

class helper():

    def wrong_password_username(self) -> str:
        login_dict = json.dumps({"username":"devt","password":"secrett"})
        body = base64.b64encode(login_dict.encode())

        credentials = requests.post("http://127.0.0.1:1600/token", data=body)
        access_token = str(json.loads(credentials.content))
        return access_token

    def wrong_password(self) -> str:
        login_dict = json.dumps({"username":"dev","password":"secrett"})
        body = base64.b64encode(login_dict.encode())

        credentials = requests.post("http://127.0.0.1:1600/token", data=body)
        access_token = str(json.loads(credentials.content))
        return access_token

    def wrong_username(self) -> str:
        login_dict = json.dumps({"username":"devt","password":"secret"})
        body = base64.b64encode(login_dict.encode())

        credentials = requests.post("http://127.0.0.1:1600/token", data=body)
        access_token = str(json.loads(credentials.content))
        return access_token

    def correct_credentials(self) -> str:
        login_dict = json.dumps({"username":"dev","password":"secret"})
        body = base64.b64encode(login_dict.encode())

        credentials = requests.post("http://127.0.0.1:1600/token", data=body)
        access_token = str(json.loads(credentials.content))
        return access_token

    def run_post(self, access_token, body):
        reply=requests.post(f"http://127.0.0.1:1600/data/{access_token}",data=body)
        if reply.status_code in [400,401,404]:
            return json.loads(reply.content.decode())
        elif reply.status_code == 200:
            filename = json.loads(reply.content.decode("utf-8")).get("filename")
            QR_contents = json.loads(reply.content.decode("utf-8")).get("QR_content")
            PDF = json.loads(reply.content.decode("utf-8")).get("Pages")
            with open(f'datafile.pdf', 'wb') as file:
                file.write(base64.b64decode(PDF))
            return {filename:QR_contents}
        else:
            return reply.status_code," ",reply.content

    def run_correct_post_request(self,access_token):
        with open("test_document.pdf", "rb") as pdf_file:
            encoded = base64.b64encode(pdf_file.read())
        body=bytes(encoded)
        return(self.run_post(access_token, body))
    
    def run_wrong_auth_post_request(self,access_token):
        with open("test_document.pdf", "rb") as pdf_file:
            encoded = base64.b64encode(pdf_file.read())
        body=bytes(encoded)
        access_token = access_token+"12"
        return(self.run_post(access_token, body))

    def run_wrong_body_post_request(self,access_token):
        return(self.run_post(access_token, "12345678"))
        
class test_token(unittest.TestCase):
    def test_wrong_password_username(self):
        self.assertEqual(helper().wrong_password_username(), "{'detail': '400 - Incorrect username or password'}")

    def test_wrong_password(self):
        self.assertEqual(helper().wrong_password(), "{'detail': '400 - Incorrect username or password'}")

    def test_correct_credentials(self):
        self.assertNotIn("detail", helper().correct_credentials())

class test_post(unittest.TestCase):
    def test_wrong_credentials_post_request(self):
        self.assertEqual(helper().run_correct_post_request(helper().wrong_password_username()), {'detail': '401 - Could not validate credentials - Invalid token'})

    def test_wrong_auth_post_request(self):
        self.assertEqual(helper().run_wrong_auth_post_request(helper().correct_credentials()), {'detail': '401 - Could not validate credentials - Invalid token'})

    def test_wrong_body_post_request(self):
        self.assertEqual(helper().run_wrong_body_post_request(helper().correct_credentials()), {'detail': "400 - Can't read PDF document"})
    
    def test_correct_post_request(self):
        self.assertNotIn("detail", helper().run_correct_post_request(helper().correct_credentials()))

if __name__ == '__main__':
    unittest.main()