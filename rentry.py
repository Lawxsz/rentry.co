#!/usr/bin/env python3

import http.cookiejar
import sys
import urllib.parse
import urllib.request
from http.cookies import SimpleCookie
from json import loads as json_loads
import argparse

_headers = {"Referer": 'https://rentry.co'}

class UrllibClient:

    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        urllib.request.install_opener(self.opener)

    def get(self, url, headers={}):
        request = urllib.request.Request(url, headers=headers)
        return self._request(request)

    def post(self, url, data=None, headers={}):
        postdata = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(url, postdata, headers)
        return self._request(request)

    def _request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read().decode('utf-8')
        return response

def new(url, edit_code, text):
    client, cookie = UrllibClient(), SimpleCookie()

    cookie.load(vars(client.get('https://rentry.co'))['headers']['Set-Cookie'])
    csrftoken = cookie['csrftoken'].value

    payload = {
        'csrfmiddlewaretoken': csrftoken,
        'url': url,
        'edit_code': edit_code,
        'text': text
    }

    return json_loads(client.post('https://rentry.co/api/new', payload, headers=_headers).data)

def get_rentry_link(text):
    url, edit_code = '', ''

    response = new(url, edit_code, text)
    if response['status'] != '200':
        print('error: {}'.format(response['content']))
        try:
            for i in response['errors'].split('.'):
                i and print(i)
            sys.exit(1)
        except:
            sys.exit(1)
    else:
        pastebin_link = response['url']
        return pastebin_link

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload text file content to Rentry and get the RAW link.')
    parser.add_argument('file', metavar='file', type=str, help='the text file to upload')

    args = parser.parse_args()

    file_path = args.file

    try:
        with open(file_path, 'r') as file:
            file_content = file.read()

        pastebin_link = get_rentry_link(file_content)
        print(pastebin_link)
    except FileNotFoundError:
        print(f"The file '{file_path}' don't exists.")
        sys.exit(1)
