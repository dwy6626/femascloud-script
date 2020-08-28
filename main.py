import requests
from bs4 import BeautifulSoup
import keyring
import yaml

import getpass
import os
import re
from datetime import datetime
import subprocess

class PunchSession:
    def __init__(self, setting_path='./settings.yaml'):
        with open(setting_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        self.session = requests.Session()
        self.logged_in = False
        self.payload = {
            'data[Account][username]': self.settings['username'],
            'data[Account][passwd]': self.fetch_password(),
        }
        self.base_uri = 'https://femascloud.com/{}'.format(self.settings['subdomain'])

        self.date_format = '%m-%d'
        self.re = {
            'time': r'\b\d{2}:\d{2}\b',
            'date': r'\b\d{2}-\d{2}\b'
        }
        for k in self.re:
            self.re[k] = re.compile(self.re[k])

    def login(self):
        self.session.post(self.base_uri + '/Accounts/login', data=self.payload) \
                    .raise_for_status()
        self.session.headers.update(
            {'referer': self.base_uri + '/users/main?from=/Accounts/login?ext=html'}
        )
        self.logged_in = True
        
    def fetch_password(self):
        password = keyring.get_password(self.settings['subdomain'], self.settings['username'])
        if password is not None:
            return password

        print("請輸入密碼，密碼將自動儲存")
        password = getpass.getpass()
        keyring.set_password(self.settings['subdomain'], self.settings['username'], password)

        return password

    def get_html(self):
        try:
            response = self.session.get(self.base_uri + '/users/main', data=self.payload)
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            print('connection error:', e)
            return False

    def soup(self, html=None):
        if html is None:
            html = self.get_html()
        return BeautifulSoup(html, 'html.parser')

    def get_time(self):
        soup = self.soup()
        table = soup.find(id='att_status_listing')
        rows = table.find_all('tr')

        rt = {}

        for r in rows:
            date = r.find(text=self.re['date'])
            if not date:
                continue
            punches = r.find_all(text=self.re['time'])
            punches.append('尚未打卡')
            punches.append('尚未打卡')

            weekday = date[5:]
            date = datetime.strptime(date[:5], self.date_format) \
                           .replace(year=datetime.now().year)
            rt[date] = {
                'weekday': weekday,
                'in': punches[0],
                'out': punches[1]
            }

        return rt

    def latest_punch_string(self):
        time_hash = self.get_time()
        latest_date = sorted(time_hash)[::-1].pop()

        return '{}{}\n    上班：{:10}\n    下班：{:10}'.format(
            latest_date.strftime(self.date_format),
            time_hash[latest_date]['weekday'],
            time_hash[latest_date]['in'],
            time_hash[latest_date]['out'],
        )
        

def popup(s):
    subprocess.check_output("osascript -e 'display dialog \"" + s + "\" buttons [\"Check In\", \"Check Out\", \"Cancel\"] giving up after 30'", shell = True)


if __name__ == '__main__':
    session = PunchSession()
    session.login()
    popup(session.latest_punch_string())
