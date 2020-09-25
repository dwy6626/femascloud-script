import schedule
import time
import logging
from lib import AddableTime


logger = logging.getLogger()
FORMAT = '[%(asctime)s] %(message)s'
logging.basicConfig(format=FORMAT)


def punch_in():
    logger.warning("I'm in...")


def punch_out():
    logger.warning("I'm out...")


def clear_job():
    schedule.clear('punch_in')
    schedule.clear('punch_out')
    logger.warning("jobs clear")

def set_job():
    schedule.every().wednesday.at(
        str(AddableTime(9, 29).random_before(25))
    ).do(punch_in).tag('punch_in')
    schedule.every().thursday.at(
        str(AddableTime(9, 29).random_before(25))
    ).do(punch_in).tag('punch_in')
    schedule.every().friday.at(
        str(AddableTime(9, 29).random_before(25))
    ).do(punch_in).tag('punch_in')

    schedule.every().wednesday.at(
        str(AddableTime(18).random_after(13))
    ).do(punch_out).tag('punch_out')
    schedule.every().thursday.at(
        str(AddableTime(18).random_after(13))
    ).do(punch_out).tag('punch_out')
    schedule.every().friday.at(
        str(AddableTime(18).random_after(13))
    ).do(punch_out).tag('punch_out') 
    logger.warning("set jobs")


schedule.every().wednesday.at('09:00').do(set_job)
schedule.every().friday.at('18:30').do(clear_job)


set_job()

while True:
    schedule.run_pending()
    time.sleep(1)
