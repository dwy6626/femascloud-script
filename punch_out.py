from lib import PunchSession


if __name__ == '__main__':
    session = PunchSession()
    session.login(auto_modify=True)
    session.punch_out()
    print(session.latest_punch_string())
