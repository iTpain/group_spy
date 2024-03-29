from group_spy import settings
from group_spy.utils.vk import VKCredentialsCollection
from group_spy.crawler.vk import VKCrawler
from group_spy.logger.error import LogError
from group_spy.main_spy.models import ScanStats
from time import sleep;
from datetime import datetime, timedelta
import smtplib, gc
from email.mime.text import MIMEText

COMMASPACE = ', '

def send_mail(text, to):
    msg = MIMEText(text)
    msg['Subject'] = "Group spy needs your assistance"
    msg['From'] = "group_spy"
    msg['To'] = COMMASPACE.join(to)
    gmail_user = 'an@nlomarketing.ru'
    gmail_pwd = 'serotonin'
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(gmail_user, gmail_pwd)
    s.sendmail("group_spy", to, msg.as_string())
    s.quit()    

def complainAndSleep():
    try:
        send_mail("Hello, this is the mighty group spy. I need your assistance with VK credentials, mortal. Please help by visiting this application: http://vkontakte.ru/app2673575.", settings.COMPLAIN_TO)
    except Exception as e:
        print e
        print "Failed to send an e-mail to admins"
    sleep (settings.CREDENTIALS_POLLING_INTERVAL)
        
def launch(scanner_classes, scan_intervals): 
    current_intervals = [0*s for s in scan_intervals]
    while True:
        credentials = VKCredentialsCollection(settings.VK_CREDENTIALS_FILE_PATH)
        if not credentials.get_credentials():
            print "No good credentials found, falling asleep"
            complainAndSleep()
            continue
        
        try:
            print "Useful credentials found: " + str(len(credentials.get_credentials()))
            crawler = VKCrawler(credentials)
            for index, time_left in enumerate(current_intervals):
                if time_left <= 0:
                    print "Launching " + str(scanner_classes[index])
                    scan_interval = scan_intervals[index]
                    current_intervals[index] = scan_interval
                    time_before = datetime.now()
                    if settings.DEBUG:
                        scanner_classes[index]().scan(crawler)
                    else:
                        try:
                            scanner_classes[index]().scan(crawler)
                        except Exception as e:
                            print "Scanner " + str(scanner_classes[index]) + " failure: " + str(e)
                    gc.collect()                
                    time_after = datetime.now()
                    seconds_passed = (time_after - time_before).total_seconds()
                    for i, v in enumerate(current_intervals):
                        current_intervals[i] = v - seconds_passed
                    scan_stat = ScanStats(time_taken=seconds_passed, scanner_class = scanner_classes[index].get_id())
                    scan_stat.save()
                    print "Scan completed in " + str(timedelta(seconds=seconds_passed))
                    print "Current timing: " + str(current_intervals)
                    print "Next scan of this type scheduled in " + str(timedelta(seconds=max(0, current_intervals[index])))
                    if (current_intervals[index] < 0):
                        send_mail("Hello, this is the mighty group spy. The scan interval is too short. You should consider increasing it or supplying more credentials via http://vkontakte.ru/app2673575.", settings.COMPLAIN_TO)
            min_time = min(current_intervals)
            if min_time > 0:
                print "sleeping for " + str(timedelta(seconds=min_time))
                sleep(min_time)
                for i, v in enumerate(current_intervals):
                    current_intervals[i] = v - min_time
        except LogError:
            complainAndSleep()
            continue
        