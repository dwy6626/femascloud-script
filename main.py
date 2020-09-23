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
        self.login_payload = {
            'data[Account][username]': self.settings['username'],
            'data[Account][passwd]': self.fetch_password(),
        }

        self.payload_user_id = None
        self.punch_payload = {
            'data[ClockRecord][shift_id]': 27,
            'data[ClockRecord][period]': 1,
        }

        self.base_uri = 'https://femascloud.com/{}'.format(self.settings['subdomain'])
        self.punch_url = '{}/{}'.format(self.base_uri, 'users/clock_listing')
        self.date_format = '%m-%d'

        self.re_raw = {
            'time': r'^\d{2}:\d{2}$',
            'date': r'^\d{2}-\d{2}\b',
            'schedule': r'\d{4}-\d{4}',
            'scheduled_time': r'\b\d{4}\b'
        }
        self.re = {k: re.compile(v) for k, v in self.re_raw.items()}

    def login(self):
        res = self.session.post(self.base_uri + '/Accounts/login', data=self.login_payload) \
                    .raise_for_status()
        self.payload_user_id = self.soup(res).find(id = 'EboardBrowserUserId')['value']
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
            response = self.session.get(self.base_uri + '/users/main')
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            print('connection error:', e)
            return False

    def soup(self, html=None):
        if html is None:
            html = self.get_html()
        return BeautifulSoup(html, 'html.parser')

    def get_schedule(self):
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

            schedule = r.find(text=self.re['schedule'])
            if schedule is None:
                scheduled_in = scheduled_out = None
            else:
                scheduled_in, scheduled_out = self.re['scheduled_time'].findall(schedule)[:2]

            rt[date] = {
                'weekday': weekday,
                'scheduled_in': scheduled_in,
                'scheduled_out': scheduled_out,
                'in': punches[0],
                'out': punches[1],
            }

        return rt

    def latest_punch_string(self):
        schedule_hash = self.get_schedule()
        latest_date = sorted(schedule_hash).pop()

        return '{}{}\n    上班：{:10}\n    下班：{:10}'.format(
            latest_date.strftime(self.date_format),
            schedule_hash[latest_date]['weekday'],
            schedule_hash[latest_date]['in'],
            schedule_hash[latest_date]['out'],
        )

    def get_punch_payload(self, punch_type='in'):
        payload = self.punch_payload.copy()
        payload['data[ClockRecord][user_id]'] = self.payload_user_id
        payload['data[AttRecord][user_id]'] = self.payload_user_id
        payload['data[ClockRecord][clock_type]'] = 'S' if punch_type == 'in' else 'E'
        return payload

    def punch_in(self):
        self.session.post(self.punch_url, data=self.get_punch_payload(punch_type='in')) \
                    .raise_for_status()

    def punch_out(self):
        self.session.post(self.punch_url, data=self.get_punch_payload(punch_type='out')) \
                    .raise_for_status()


def popup(s):
    subprocess.check_output("osascript -e 'display dialog \"" + s + "\" buttons [\"Check In\", \"Check Out\", \"Cancel\"] giving up after 30'", shell = True)


if __name__ == '__main__':
    session = PunchSession()
    session.login()
    session.punch_in()
    print(session.get_schedule())
    # popup(session.latest_punch_string())
