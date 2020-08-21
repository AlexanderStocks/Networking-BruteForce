import queue
import threading
import os
import urllib3

noThreads = 8

target = "http://www.google.com"
appLocation = "/Users/Alex/Downloads/joomla-3.1.1"

# list of filters not interested in
ignoreFilters = [".jpg", ".gif", ".png", ".css"]

os.chdir(appLocation)

paths = queue.SimpleQueue()

# go through all files and directories in local web app location
for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in ignoreFilters:
            paths.put(remote_path)


def grabPaths():
    pool = urllib3.PoolManager()
    while not paths.empty():
        path = paths.get()
        url = "%s%s" % (target, path)

        request = pool.request('GET', url)

        try:
            response = pool.urlopen(request)

            content = response.read()

            print("[%d] => %s" % (urllib3.encode_multipart_formdata(response), path))
            response.close()

        except urllib3.exceptions.HTTPError as e:
            print("Failed %s" % e)


for i in range(noThreads):
    print("Spawning thread: %d" % i)
    t = threading.Thread(target=grabPaths())
    t.start()
