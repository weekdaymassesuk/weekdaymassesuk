#!/home/tgolden/apps/bin/python2.7
import os, sys
import codecs
import csv
import datetime
import httplib
import socket
import string
import subprocess
import time
import threading
import traceback
import Queue
import urlparse

import requests

import smtpmail
import database

_DEBUG = False

TIMEOUT_SECS = 60
socket.setdefaulttimeout(TIMEOUT_SECS)

ENCODING = "cp1252"

def check_curl(url, *options):
    cmd = ["curl", "--connect-timeout", str(TIMEOUT_SECS), "-o", os.devnull, "-w", "%{http_code}"] + list(options) + ['"%s"' % url]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.startswith("2"), stdout

def check_curl_head(url):
    return check_curl(url, "--head")

def check_curl_get(url):
    return check_curl(url)

def check_requests(url):
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
    try:
        r = requests.get(url, timeout=TIMEOUT_SECS, headers={"User-Agent": user_agent})
        return 200 <= r.status_code < 300, "%d: %s" % (r.status_code, httplib.responses.get(r.status_code, "Unknown response"))
    except requests.exceptions.Timeout:
        return False, "Timed Out"
    except Exception, exc:
        return False, exc.message
    return False, "Unknown error"

class Thread(threading.Thread):

    STRATEGIES = [check_requests]

    def __init__(self, request_queue, result_queue, logging_queue, already_found):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.logging_queue = logging_queue
        self.hostnames = {}

    def check_link(self, url, strategy):
        strategy = self.STRATEGIES[strategy]
        url = url.decode(ENCODING)
        if _DEBUG: self.logging_queue.put("Trying %s with %s" % (url, strategy))
        return strategy(url)

    def is_name_ok(self, url):
        hostname = urlparse.urlparse(url).netloc
        if hostname not in self.hostnames:
            try:
                socket.gethostbyname(hostname)
            except socket.error:
                self.hostnames[hostname] = False
            else:
                self.hostnames[hostname] = True
        return self.hostnames[hostname]

    def run(self):
        while True:
            id, url, strategy_to_use = self.request_queue.get()
            if not self.is_name_ok(url):
                self.result_queue.put(((id, url), False, "Invalid DNS name"))
                continue

            success, code = self.check_link(url, strategy=strategy_to_use)
            if success:
                self.result_queue.put(((id, url), success, code))
            else:
                if strategy_to_use < len(self.STRATEGIES) - 1:
                    self.request_queue.put((id, url, strategy_to_use + 1))
                else:
                    self.result_queue.put(((id, url), success, code))

TRANSLATION_MAP = string.maketrans("", "")
def flatten(s):
    return "-".join(s.translate(TRANSLATION_MAP, string.punctuation).split())

def quote(s):
    return "".join(c if ord(c) < 128 else "%%%02x" % ord(c) for c in s.encode("utf8"))

class Writer(object):

    def __init__(self, ofile):
        self.ofile = ofile

    def writerow(self, iterable):
        self.ofile.write(u",".join('"%s"' % unicode(i) for i in iterable) + u"\n")

def main(to_do, *args):
    functions = {
        "areas" : area_websites,
        "churches" : church_websites,
        "test" : test_websites
    }

    request_queue = Queue.Queue()
    result_queue = Queue.Queue()
    logging_queue = Queue.Queue()
    already_found = {}
    N_THREADS = 8
    for n in range(N_THREADS):
        Thread(request_queue, result_queue, logging_queue, already_found).start()

    websites = set()
    for key, url in functions[to_do](*args):
        if key not in websites:
            websites.add(key)
            request_queue.put((key, quote(url), 0))

    ofile = codecs.open("%s.csv" % to_do, "w", encoding=ENCODING)
    writer = Writer(ofile)
    try:
        while websites:
            try:
                log_message = logging_queue.get_nowait()
                print time.asctime(), log_message.encode(sys.stdout.encoding or "iso-8859-1", "ignore")
            except Queue.Empty:
                pass

            try:
                (key, website), success, code = result_queue.get_nowait()
            except Queue.Empty:
                pass
            else:
                logging_queue.put(u"%s => %s | %s" % (website, "SUCCESS" if success else "FAILURE", code))
                if not success:
                    writer.writerow(list(key) + [website, code])
                websites.remove(key)
                left_to_find = len(websites)
                if (left_to_find % 10) == 0:
                    logging_queue.put(u"Waiting for %s" % left_to_find)
                if left_to_find < 5:
                    logging_queue.put(u"Waiting for:")
                    for w in websites:
                        logging_queue.put(u"  %s" % unicode(w))
    finally:
        ofile.close()
    print "All results found"

    files_to_send = ["%s.csv" % to_do]
    try:
        subject = "Link checks: %s" % (" ".join((to_do,) + args))
        smtpmail.send(
            recipients=["checks@weekdaymasses.org.uk", "tim@weekdaymasses.org.uk"],
            subject=subject,
            message_text=subject,
            attachments=files_to_send,
            sender="tim@weekdaymasses.org.uk"
        )
    except socket.error:
        print "Unable to send email"
    print "Check complete"

def test_websites():
    yield ("1", "http://timgolden.me.uk")
    yield ("2", "http://timgolden.me.uk/NOT-THERE")

def area_websites():
    sql = "SELECT * FROM areas"

    for area in database.select(sql):
        key = (u"area", flatten(area.name.encode(ENCODING, "xmlcharrefreplace")).decode(ENCODING))
        websites = set()
        for day in ["weekday", "saturday", "sunday", "holy_day_of_obligation"]:
            website = area['%s_website' % day]
            if website:
                websites.add(website)
        for website in websites:
            yield (key, website)

def church_websites(letter_range=""):
    sql = "SELECT * FROM churches"
    first_letter, _, last_letter = letter_range.lower().partition("-")
    first_letter = first_letter or "a"
    last_letter = last_letter or "z"
    print "first-last:", first_letter, "-", last_letter

    wheres = []
    wheres.append("COALESCE (is_persistent_offender, 'N') <> 'Y'")
    if wheres:
        sql += " WHERE " + " AND ".join(wheres)

    for church in database.select(sql):
        alias_initial = (church.alias or "a").lower()[0]
        if first_letter <= alias_initial <= last_letter:
            website = church.website
            if website:
                key = (u"church", unicode(church.id), church.postcode, flatten(church.name.encode(ENCODING, "xmlcharrefreplace")).decode(ENCODING))
                yield key, u"http://%s" % website

if __name__ == '__main__':
    main(*sys.argv[1:])
