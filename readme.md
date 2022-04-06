# This API scans QR-codes from pdf-documents with multiple pages where the first page is a QR-code.
To find out how to use it, it's best to look at it's implementations in test.py. There you can see how it is supposed to work.

# Steps for usage
> - Clone git repo
> - Use the predefined dockerfile to launch api
> - Get a token by logging in with an authorised account
> - Use that token in the url to call upon the /data link
> - Add b64encoded pdf to the body of the post-request for /data/{token}
> - You should be receiving a dictionary with the QR-contents and the file should be in the content of the reply as well
> - In order to use the returned PDF, you must first decode the reply which is base 64 encoded

# Notes
> - The Config file can be used to change certain parameters of the API. Don't forget to change the dockerfile too when necessary.
> - In the Models/Site folder, there are models which contain userdata, hashed passwords and other details.
> - The files starting with "$" and the Data folder are cleanup up after each request in order to preserve space.
> - The Models/WeChat folder contains important models that are used by the QR-scanner.