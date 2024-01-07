from urllib import request
from bs4 import BeautifulSoup

url = "http://www.qr1234.com/html/34/34011/"

#url = "http://www.qr1234.com/html/34/34011/16093900.html"
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}


#for dd in dds:
#    a = dd.contents[0]
#    title = a.get_text()
#    href = a['href']
#    url = href.split("/")[-1]
#    print(a)

def getUrls(url):
    L = []
    req = request.Request(url, headers=headers)
    response = request.urlopen(req)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    dds = soup.find_all("dd")
    for dd in dds:
        a = dd.contents[0]
        title = a.get_text()
        href = a['href']
        new_url = href.split("/")[-1]
        new_url = url + new_url
        L.append(new_url)
    return L

def getContents(url):
    contents = ''
    req = request.Request(url, headers=headers)
    response = request.urlopen(req)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    h1 = soup.h1
    title = h1.get_text()
    div = soup.find(id="content")
    contents = contents + title + '\n\n'
    print(title)
    #for p in div.contents:
    #    print(p)
    for string in div.strings:
        contents = contents + string + '\n\n'
    return contents


contents = ''
urls = getUrls(url)
for url in urls:
    content = getContents(url)
    contents = contents + content

with open("test.txt", mode='w+', encoding='utf-8') as f:
    f.write(contents)
