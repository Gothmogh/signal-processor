from grequests import async
import random
import time

url = 'http://script.google.com/macros/s/AKfycbzl9EkKflC_MJxhmvQ8ntr2jsQLqFKbj5RnVOtLjjmb1aJg6KM/exec'


for x in range(1000):
    temp =  x * random.random()
    hum = x * random.random()
    async.get(url, params={'temperature': temp, 'humidity': hum})
    time.sleep(.100)
