import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# requests.packages.urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth


class HttpRequest:
    def __init__(self, username='None', password='None', basic='None', headers=None):
        self.username = username
        self.password = password
        if headers is None:
            self.headers = dict()
            self.headers["content-type"] = "application/json"
            self.headers["accept"] = "application/json"
            self.headers["cache-control"] = 'no-cache'
            if basic != 'None:':
                self.headers["Authorization"] = basic
            else:
                self.headers["Authorization"] = 'None'
        else:
            self.headers = headers

    def get_data(self, url, data=None):
        try:
            if 'Authorization' in self.headers and self.headers["Authorization"] != 'None' or 'X-HYBRID-TOKEN' in self.headers:
                r = requests.get(
                    url,
                    headers=self.headers,
                    verify=False,
                    timeout=300
                )
            else:
                headers = {'accept': 'application/json'}
                r = requests.get(
                    url,
                    params=data,
                    headers=headers,
                    auth=HTTPBasicAuth(self.username, self.password),
                    verify=False,
                    timeout=300
                )
            return {"data": str(r.content.decode()), "code": r.status_code}

        except Exception as e:
            return {"data": str(e), "code": 500}

    def post_data(self, url, data):
        try:
            if self.headers["Authorization"] != 'None':
                r = requests.post(
                    url,
                    headers=self.headers,
                    data=data,
                    verify=False,
                    timeout=300
                )
            else:
                r = requests.post(
                    url,
                    headers=self.headers,
                    data=data,
                    auth=HTTPBasicAuth(self.username, self.password),
                    verify=False,
                    timeout=300
                )

            return {"data": str(r.content.decode()), "code": r.status_code}
        except Exception as e:
            return {"data": str(e), "code": 500}

    def put_data(self, url, data):
        try:
            if self.headers["Authorization"] != 'None':
                r = requests.put(
                    url,
                    headers=self.headers,
                    data=data,
                    verify=False,
                    timeout=300
                )
            else:
                r = requests.put(
                    url,
                    headers=self.headers,
                    data=data,
                    auth=HTTPBasicAuth(self.username, self.password),
                    verify=False,
                    timeout=300
                )

            return {"data": r.content, "code": r.status_code}
        except Exception as e:
            return {"data": str(e), "code": 500}

    def post_data_noauth(self, url, data):
        try:
            r = requests.post(
                url,
                headers=self.headers,
                data=data,
                verify=False,
                timeout=300
            )
            return {"data": str(r.content.decode()), "code": r.status_code}
        except Exception as e:
            return {"data": str(e), "code": 500}


def main():
    apiurl = 'http://10.140.212.229:8090'
    data = '''{
        "taskId": "23cf490b-d1c8-4012-9b5e-aa95672faea9"
    }'''
    http_rs = HttpRequest('nouser', 'nopw')
    rs = http_rs.post_data_noauth(apiurl, data)
    print(rs)


if __name__ == '__main__':
    main()
