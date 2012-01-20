from group_spy import settings
from group_spy.utils.misc import get_credentials
from group_spy.crawler.vk import VKCrawler
from group_spy.logger.error import LogError
from time import sleep;
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

from threading import Thread

COMMASPACE = ', '

def complainAndSleep():
    try:
        msg = MIMEText("Hello, this is the mighty group spy. I need your assistance with VK credentials, mortal. Please help by visiting this application: http://vkontakte.ru/app2673575.")
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
    except Exception as e:
        print e
        print "Failed to send an e-mail to admins"
    sleep (settings.CREDENTIALS_POLLING_INTERVAL)
    
    
def launch(scanner_class, scan_interval): 
    print "launching " + str(scanner_class)
    while True:
        credentials = get_credentials()
        if credentials == None:
            complainAndSleep()
            continue
        
        try:
            print "useful credentials found: " + str(len(credentials))
            time_before = datetime.now()
            crawler = VKCrawler(credentials)
            scanner_class().scan(crawler)
            time_after = datetime.now()
            print "Scan completed in " + str(time_after - time_before)
            sleep(scan_interval)
        except LogError:
            complainAndSleep()
            continue
        
def multilaunch (scanner_classes):
    for sc in scanner_classes:
        thread = Thread(None, launch, None, sc)
        thread.start()
        