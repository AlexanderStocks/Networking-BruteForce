import urllib3

url = "http://www.google.com"

headers = {'User-Agent': "Googlebot"}

pool = urllib3.PoolManager()

request = pool.request('Get', url, headers)
response = pool.urlopen(url=url)

print(response.read())

response.close()

