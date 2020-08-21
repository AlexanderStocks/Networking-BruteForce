import urllib3
import urllib
from urllib import parse, error
import queue
import threading

noThreads = 5
targetAddr = "http://testphp.vulnweb.com"
wordsFile = "/tmp/all.txt"  # words list from SVNDigger
resume = None
UAHeader = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def directoryBruter(words, extensions=None):
    while not words.empty():
        currAttempt = words.get()

        attempts = []
        # if no file extension then directory
        if "." not in currAttempt:
            attempts.append("/%s/" % currAttempt)
        else:
            attempts.append("/%s" % currAttempt)
        # apply each extensions wanting to test
        if extensions:
            for extension in extensions:
                attempts.append("/%s%s" % (currAttempt, extension))

        for attempt in attempts:
            url = "%s%s" % (targetAddr, urllib.parse.quote(attempt))

            try:
                headers = {"User-Agent": UAHeader}

                poolManager = urllib3.PoolManager()

                r = poolManager.request("Get", url, headers=headers)

                response = poolManager.urlopen(r)

                if len(response.read()):
                    print("[%d] => %s" % (response.code, url))
            except urllib.error.URLError as err:
                # ignore "file not found" errors
                if hasattr(err, "code") and err.code != 404:
                    print("!!! %d => %s" % (int(err.code), url))


def buildWords(wordsFile):
    file = open(wordsFile, "rb")
    raw_words = file.readlines()
    file.close()

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


words = buildWords(wordsFile)
extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(noThreads):
    t = threading.Thread(target=directoryBruter, args=(words, extensions,))
    t.start()
