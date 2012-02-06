from group_spy import settings
from group_spy.utils.misc import get_credentials
from group_spy.crawler.vk import VKCrawler
from group_spy.logger.error import LogError
from time import sleep;
from datetime import datetime, timedelta
import smtplib, gc
from email.mime.text import MIMEText

COMMASPACE = ', '

def send_mail(text):
    msg = MIMEText(text)
    msg['Subject'] = "Group spy needs your assistance"
    msg['From'] = "group_spy"
    msg['To'] = COMMASPACE.join (settings.COMPLAIN_TO)
    gmail_user = 'an@nlomarketing.ru'
    gmail_pwd = 'serotonin'
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(gmail_user, gmail_pwd)
    s.sendmail("group_spy", settings.COMPLAIN_TO, msg.as_string())
    s.quit()    

def complainAndSleep():
    try:
        send_mail("Hello, this is the mighty group spy. I need your assistance with VK credentials, mortal. Please help by visiting this application: http://vkontakte.ru/app2673575.")
    except Exception as e:
        print e
        print "Failed to send an e-mail to admins"
    sleep (settings.CREDENTIALS_POLLING_INTERVAL)
        
def launch(scanner_classes, scan_intervals): 
    current_intervals = [0*s for s in scan_intervals]
    while True:
        credentials = get_credentials()
        if credentials == None:
            complainAndSleep()
            continue
        
        try:
            print "Useful credentials found: " + str(len(credentials))
            crawler = VKCrawler(credentials)
            for index, time_left in enumerate(current_intervals):
                if time_left <= 0:
                    print "Launching " + str(scanner_classes[index])
                    scan_interval = scan_intervals[index]
                    current_intervals[index] = scan_interval
                    time_before = datetime.now()
                    scanner_classes[index]().scan(crawler)
                    gc.collect()                
                    time_after = datetime.now()
                    seconds_passed = (time_after - time_before).total_seconds()
                    for i, v in enumerate(current_intervals):
                        current_intervals[i] = v - seconds_passed
                    print "Scan completed in " + str(timedelta(seconds=seconds_passed))
                    print "Current timing: " + str(current_intervals)
                    print "Next scan scheduled in " + str(timedelta(seconds=max(0, current_intervals[index])))
                    if (current_intervals[index] < 0):
                        send_mail("Hello, this is the mighty group spy. The scan interval is too short. You should consider increasing it or supplying more credentials via http://vkontakte.ru/app2673575.")
            min_time = min(current_intervals)
            if min_time > 0:
                print "sleeping for " + str(timedelta(seconds=min_time))
                sleep(min_time)
                for i, v in enumerate(current_intervals):
                    current_intervals[i] = v - min_time
        except LogError:
            complainAndSleep()
            continue
        