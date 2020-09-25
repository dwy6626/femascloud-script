import subprocess


from lib import PunchSession


def popup(s):
    subprocess.check_output("osascript -e 'display dialog \"" + s + "\" buttons [\"Check In\", \"Check Out\", \"Cancel\"] giving up after 30'", shell = True)


if __name__ == '__main__':
    session = PunchSession()
    session.login()
    popup(session.latest_punch_string())
