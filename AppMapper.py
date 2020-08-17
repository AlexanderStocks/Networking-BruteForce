import queue
import threading
import os
import urllib3

threads = 8

target = "http://www.google.com"
directory = "/Users/Alex/Downloads/joomla-3.1.1"

# list of filters not interested in
filters = [".jpg", ".gif", ".png", ".css"]

os.chdir(directory)

web_paths = queue.SimpleQueue()

# go through all files and directories in local web app directory
for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    pool = urllib3.PoolManager()
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s%s" % (target, path)

        request = pool.request('GET', url)

        try:
            response = pool.urlopen(request)

            content = response.read()

            print("[%d] => %s" % (urllib3.encode_multipart_formdata(response), path))
            response.close()

        except urllib3.exceptions.HTTPError as e:
            print("Failed %s" % e)


for i in range(threads):
    print("Spawning thread: %d" % i)
    t = threading.Thread(target=test_remote())
    t.start()
