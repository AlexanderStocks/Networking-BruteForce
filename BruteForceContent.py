import urllib3
import urllib
from urllib import parse, error
import queue
import threading

threads = 5
target_url = "http://testphp.vulnweb.com"
wordslist_file = "/tmp/all.txt"  # words list from SVNDigger
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []
        # if no file extension then diretory
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)
        # apply each extensions wanting to test
        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        for brute in attempt_list:
            url = "%s%s" % (target_url, urllib.parse.quote(brute))

            try:
                headers = {"User-Agent": user_agent}

                poolManager = urllib3.PoolManager()

                r = poolManager.request("Get", url, headers=headers)

                response = poolManager.urlopen(r)

                if len(response.read()):
                    print("[%d] => %s" % (response.code, url))
            except urllib.error.URLError as err:
                # ignore "file not found" errors
                if hasattr(err, "code") and err.code != 404:
                    print("!!! %d => %s" % (int(err.code), url))


def build_wordlist(wordslist_file):
    fd = open(wordslist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = queue.SimpleQueue()

    for word in raw_words:
        word = word.strip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from %s" % resume)
        else:
            words.put(word)

    return words


word_queue = build_wordlist(wordslist_file)
extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
    t.start()
