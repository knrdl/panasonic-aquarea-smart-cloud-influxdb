import time
from datetime import date, timedelta, datetime
import traceback
import os

import requests

import aquarea
import influx

LOAD_HISTORIC_DATA = os.getenv("LOAD_HISTORIC_DATA") == "true"

session = requests.Session()

fails = 0
login_required = True

if LOAD_HISTORIC_DATA:
    aquarea.login(session)
    login_required = False

    next_date = date.today()
    while True:
        datestr = next_date.strftime("%Y-%m-%d")
        consumption = aquarea.get_device_consumption(session, datestr)
        if influx.contains_any_consumption_data(consumption):
            influx.write_consumption_data(consumption, datestr)
            next_date -= timedelta(days=1)
        else:
            break

while True:
    try:
        if login_required:
            aquarea.login(session)
            login_required = False

        status = aquarea.get_device_status(session)
        influx.write_current_status(status)

        if datetime.now().minute % 10 == 0:
            today = time.strftime("%Y-%m-%d")
            consumption = aquarea.get_device_consumption(session, today)
            influx.write_consumption_data(consumption, today)
    except:
        traceback.print_exc()
        session = requests.Session()
        login_required = True
        fails += 1

        if fails > 5:
            exit(1)
    finally:
        time.sleep(60)
