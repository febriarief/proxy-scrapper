import aiohttp
import asyncio
import itertools
import os.path
import re
import time

from bs4 import BeautifulSoup
from datetime import date
from modules.commons import *

class ProxyDownloader():
    def __init__(self) -> None:
        self.banner()

        if (os.path.exists('proxy-source.txt') is False):
            Commons.printError('File \'proxy-sources.txt\' not exist')
            return

        self.arrayList = []
        with open("proxy-source.txt") as list:
            self.arrayList = list.readlines()

        totalUrls = len(self.arrayList)
        if (totalUrls == 0):
            Commons.printError('File \'proxy-sources.txt\' is empty')
            return

        Commons.printInfo('Load ' + colors.GREEN + '{0:,}'.format(totalUrls) + colors.END + ' urls')
        print("")

        self.totalProxies = 0

    def banner(self):
        print(colors.RED + "       _ ____              _         _    ")
        print("      (_)  _ \  _____   __/ \   _ __| |_  ")
        print("      | | | | |/ _ \ \ / / _ \ | '__| __| ")
        print(colors.WHITE + "      | | |_| |  __/\ V / ___ \| |  | |_  ")
        print("      |_|____/ \___| \_/_/   \_\_|   \__| ")
        print("-----------------------------------------------" + colors.END)
        print("                Proxy Scrapper")
        print("                    v1.0.0")
        print("-----------------------------------------------")
        print("  Author: iDevArt Crew")
        print("  Email : idevart.crew@gmail.com")
        print("-----------------------------------------------\n")
                                                

    async def download(self): 
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

        async with aiohttp.ClientSession(headers=headers) as session:
            for url in self.arrayList:
                url = '{}'.format(url.rstrip())

                if re.search(r'checkerproxy', url):
                    today = date.today()
                    url = url.format(today)
                
                async with session.get(url) as response:
                    shouldExtractResponse = ['socks-proxy', 'free-proxy-list', 'us-proxy', 'sslproxies', 'free-proxy-list.com', 'proxyrack.com']

                    if re.search(r'geonode', url):
                        try:
                            res = await response.json()
                            data = res['data']
                            body = []

                            for list in data:
                                proxy = "{}:{}".format(list['ip'], list['port'])
                                body.append(proxy)

                            body = str(body)

                        except:
                            Commons.printError(str('Failed to retrieve data from: ' + url))
                            continue

                    elif any(keyword in url for keyword in shouldExtractResponse):
                        responseBody = await response.text()
                        body = str(self.proxyExtractor(responseBody))
                    
                    else:
                        body = await response.text()

                    if response.status != 200:
                        Commons.printError(str('Failed to retrieve data from: ' + url))
                        continue
                    
                    total = self.storeResult(body)

                    Commons.printSuccess(str('Get ' + colors.GREEN + '{0:,}'.format(total) + colors.END + ' proxies from: ' + url))

    def proxyExtractor(self, html):
        bs = BeautifulSoup(html, 'html5lib')
        tables = bs.find_all('table')
        proxies = []

        for table in tables:
            rows = table.find_all('tr')

            for row in rows:
                ip = port = protocol = None
                contents = row.contents

                for data in contents:
                    text = data.text
                    if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text):
                        ip = text
                        continue
                    
                    if re.search('\d{2,5}', text):
                        port = text
                        continue
                
                    if text.lower() in ['http', 'https', 'socks4', 'socks5']:
                        protocol = text
                        continue

                if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', '{}:{}'.format(ip, port)):
                    if protocol is None:
                        proxies.append('{}:{}'.format(ip, port))
                    else:
                        protocol = protocol.lower()
                        proxies.append('{}:{}|{}'.format(ip, port, protocol))

        return proxies
    
    def storeResult(self, data):
        arrayProxies = []
        arrayProxies += re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', data)

        file = open("proxies.txt", "a")
        file.write("\n".join(arrayProxies) + "\n")
        file.close()

        total = len(arrayProxies)
        self.totalProxies += total

        return total

if __name__ == '__main__':
    start_time = time.time()
    
    proxyDownloader = ProxyDownloader()
    
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(proxyDownloader.download())

    totalProxies = proxyDownloader.totalProxies
    duplicateNumber = 0
    validAdded = 0

    print("")
    Commons.printInfo("Server successfully scrape " + colors.GREEN + '{0:,}'.format(totalProxies) + colors.END + " proxies")

    entries = []
    with open('proxies.txt', 'r') as infile:
        sorted_file = sorted(infile.readlines())
        for line, _ in itertools.groupby(sorted_file):
            line = '{}'.format(line.rstrip())
            entries.append(line)

    validAdded = len(entries)
    duplicateNumber = totalProxies - validAdded

    Commons.printInfo("Server remove " + colors.RED + '{0:,}'.format(duplicateNumber) + colors.END + " duplicate proxies")
    
    file = open('proxies.txt', 'w')
    file.write("\n".join(entries) + "\n")
    file.close()
    
    
    Commons.printInfo("Server add " + colors.GREEN + '{0:,}'.format(validAdded) + colors.END + " proxies")
    Commons.printInfo(str("Server finish jobs after: %s seconds\n" % (time.time() - start_time)))
    