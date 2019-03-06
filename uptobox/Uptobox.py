import requests
import sys
import re
import json
import os
from requests_toolbelt import MultipartEncoder

class Uptobox(object):
    def __init__(self, username, password):
        self.s = requests.Session()
        self.username = username
        self.password = password
        self.baseurl = "https://uptobox.com"
        if self.login() == False:
            print("Login unsucessful")
            sys.exit(1)
        self.token = self.get_token()

    
    def login(self):
        self.s.post(
            "https://uptobox.com/?op=login&referer=homepage", 
            data = {
                'login': self.username,
                'password': self.password
            }
        )
        page = self.s.get(self.baseurl).text
        if "Logout" in page:
            return True
        return False

    def upload(self, path):
        headers = {
            "Accept": "*/*",
            "Referer": "https://uptobox.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.64",
        }
        basepage = self.s.get(self.baseurl).text
        json_unparsed = re.findall('id=\'content\' class=\'width-content\' data-ui=\'([^\']+)\'', basepage)
        json_parsed = json_unparsed[0].replace('&quot;', '"')
        json_parsed = json.loads(json_parsed)
        field = os.path.basename(path), open(path, 'rb')
        print(field)
        m = MultipartEncoder(fields={
            'files': (field)}
        )
        headers["Content-Type"] = m.content_type
        r = self.s.post(
            "https://" + json_parsed["uploadUrl"][2:].replace("remote", "upload") ,
            data=m,
            headers=headers
        )
        return r.json()["files"][0]["url"]

    def upload_link(self, link):
        basepage = self.s.get(self.baseurl).text
        json_unparsed = re.findall('id=\'content\' class=\'width-content\' data-ui=\'([^\']+)\'', basepage)
        json_parsed = json_unparsed[0].replace('&quot;', '"')
        json_parsed = json.loads(json_parsed)
        payload_dict = {'urls': json.dumps([link]) }
        r = self.s.post(
            "https://" + json_parsed["uploadUrl"][2:] , 
            data=payload_dict
        )
        url = None
        for jsondata in r.text.split("\n"):
            if jsondata != "":
                url = json.loads(jsondata).get("url", None)
        if url == None:
            raise Exception("Unvalid return json")
        return url

    def get_files(self, options={}):
        default = {"token": self.token, "limit": 50, "path": "//"}
        options = {**default, **options}
        return self.s.get("https://uptobox.com/api/user/files", params=options).json()

    def get_token(self):
        basepage = self.s.get("https://uptobox.com/?op=my_account").text
        json_unparsed = re.findall('id=\'content\' class=\'width-content\' data-ui=\'([^\']+)\'', basepage)
        json_parsed = json_unparsed[0].replace('&quot;', '"')
        json_parsed = json.loads(json_parsed)
        return json_parsed["token"]
