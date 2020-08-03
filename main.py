import requests
from bs4 import BeautifulSoup
# import getpass
# import os
import re


def checkPunchTime(username, passwd) :
    payload = {
        'data[Account][username]': username,
        'data[Account][passwd]': passwd,
    }
    response = requests.post('https://femascloud.com/domain/Accounts/login', data = payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    button = soup.find_all("input")
    script = soup.find_all("script", type="text/javascript")
    print(button)
    print(script)
    # mainData = soup.find(id = 'showMainDataDiv')
    # dragTables = mainData.find_all('td', class_ = 'dragTable')
    # dragTable = dragTables[3]
    # row = dragTable.find_all('tr', class_ = 'ebtr')[0]
    # column = row.find_all('td', class_ = 'ebtd')
    # today = column[0]
    # punchIn = column[2]
    # return 'My punch-in time is: ' + today.get_text() + ' ' + punchIn.get_text()

# passwd = getpass.getpass()
# message = checkPunchTime(YOUR_USER_NAME, passwd)
# os.system("osascript -e 'display notification \"" + message + "\"'")

# checkPunchTime(YOUR_USER_NAME, PASS)

def parseHTML(url="./response.html"):
    with open(url, 'r') as f:
        soup =  BeautifulSoup(f.read(), 'html.parser')
    script = soup.find_all("script", type="text/javascript", string=re.compile("submit"))
    print(script)

parseHTML()