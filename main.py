import requests
from bs4 import BeautifulSoup
import getpass
import os
import keyring
import re


class PunchSession:
    def __init__(self, username):
        self.username = username
        self.session = requests.Session()
        self.logged_in = False
        self.payload = {
            'data[Account][username]': self.username,
            'data[Account][passwd]': self.fetch_password(),
        }

    def login(self):
        self.session.post('https://femascloud.com/domain/Accounts/login', data=self.payload) \
                    .raise_for_status()
        self.session.headers.update(
            {'referer': 'https://femascloud.com/domain/users/main?from=/Accounts/login?ext=html'}
        )
        self.logged_in = True
        
    def fetch_password(self):
        password = keyring.get_password(domain, self.username)
        if password is not None:
            return password

        print("請輸入密碼，密碼將自動儲存")
        password = getpass.getpass()
        keyring.set_password(domain, self.username, password)

        return password

    def check_time(self):
        raise NotImplementedError

    def parseHTML(self, url="./response.html"):
        with open(url, 'r') as f:
            soup =  BeautifulSoup(f.read(), 'html.parser')
        script = soup.find_all("script", type="text/javascript", string=re.compile("submit"))


if __name__ == '__main__':
    session = PunchSession(YOUR_USER_NAME)
    session.login()
