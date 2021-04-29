import requests
import random
from datetime import datetime, timedelta
import time
import json


def bill_pay(ts=None, value=1000):

    user_id = str(input("Enter User ID:"))
    seconds = random.randint(4, 80)
    if not ts:
        ts = datetime.now().strftime("%Y%m%d %H%M%S")
    data = {"noun": "bill", "ts": ts, "user_id": user_id, "verb": "pay", "lat_long": "192.11, 14.22", 'time_spent_on_screen': seconds,
            'properties': json.dumps({"bank": "icici", "merchantid": "212", "mode": "netbank", "value": str(value)})}

    r = requests.post("http://127.0.0.1:8000/add-event/", data=data)
    print(r.json())


def fdbk_post():

    user_id = int(input("Enter User ID:"))
    seconds = random.randint(4, 80)
    ts = datetime.now().strftime("%Y%m%d %H%M%S")
    data = {"noun": "fdbk", "ts": ts, "user_id": user_id, "verb": "post", "lat_long": "192.11, 14.22", 'time_spent_on_screen': seconds,
            'properties': json.dumps({"text": "Some error"})}

    r = requests.post("http://127.0.0.1:8000/add-event/", data=data)
    print(r.json())

# bill_pay()
# fdbk_post()


def check_multiple_payment_exceeding_limits():

    t = "20210428 160608"  # A default string
    for i in range(1, 8):
        ts1 = datetime.strptime(t, "%Y%m%d %H%M%S")+timedelta(minutes=i)
        print(ts1)
        ts111 = ts1.now().strftime("%Y%m%d %H%M%S")
        bill_pay(ts111, value=10000*i)
        time.sleep(5)




