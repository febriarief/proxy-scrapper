import os.path
import signal
import time
import requests
import json

from concurrent.futures import ThreadPoolExecutor, wait
from modules.commons import *
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class ProxyChecker():
    def __init__(self) -> None:
        self.banner()

        if (os.path.exists('proxies.txt') is False):
            Commons.printError('File \'proxies.txt\' not exist')
            return

        self.arrayList = []
        with open("proxies.txt") as list:
            self.arrayList = list.readlines()

        totalProxies = len(self.arrayList)
        if (totalProxies == 0):
            Commons.printError('File \'proxies.txt\' is empty')
            return

        Commons.printInfo('Load ' + colors.GREEN + '{0:,}'.format(totalProxies) + colors.END + ' proxies')
        print("")

        self.totalProxies = totalProxies

    def banner(self):
        print(colors.RED + "       _ ____              _         _    ")
        print("      (_)  _ \  _____   __/ \   _ __| |_  ")
        print("      | | | | |/ _ \ \ / / _ \ | '__| __| ")
        print(colors.WHITE + "      | | |_| |  __/\ V / ___ \| |  | |_  ")
        print("      |_|____/ \___| \_/_/   \_\_|   \__| ")
        print("-----------------------------------------------" + colors.END)
        print("                Proxy Checker")
        print("                    v1.0.0")
        print("-----------------------------------------------")
        print("  Author: iDevArt Crew")
        print("  Email : idevart.crew@gmail.com")
        print("-----------------------------------------------\n")

    def getRandomUserAgent(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        return user_agent_rotator.get_random_user_agent()           

    def check(self): 
        def process(proxy):
            for protocol in ['http', 'socks4', 'socks5']:
                try:
                    headers = { 'User-Agent': self.getRandomUserAgent() }
                    response = requests.get("https://icanhazip.com/", headers=headers, proxies={"https": "{}://{}".format(protocol, proxy)}, timeout=10)
                    if response.status_code == 200:
                        proxyJudge = self.proxyJudge(proxy, protocol)
                        ip, port = proxy.split(':')

                        try:
                            if proxyJudge.status_code == 200:
                                result = proxyJudge.json()
                                if result['status'] == 'ok':
                                    if result[ip]['proxy'] == 'yes':
                                        input = "{}|{}".format(proxy, protocol)
                                        self.pickGoodResult(input, 'blacklist')
                                        Commons.printSuccess("Proxy {}|{} LIVE and marked as BLACKLIST IP".format(proxy, protocol))
                                    else:
                                        input = "{}|{}".format(proxy, protocol)
                                        self.pickGoodResult(input, 'clean')
                                        Commons.printSuccess("Proxy {}|{} LIVE and marked as GOOD IP".format(proxy, protocol))
                                else:
                                    file = open('logs.txt', 'a')
                                    file.write(str(result) + "\n")
                                    file.close()

                                    input = "{}|{}".format(proxy, protocol)
                                    self.pickGoodResult(input, 'unknown')
                                    Commons.printSuccess("Proxy {}|{} LIVE and marked as UNKNOWN due to server cannot get details info".format(proxy, protocol))
                            else:
                                file = open('logs.txt', 'a')
                                file.write(str(proxyJudge) + "\n")
                                file.close()

                                input = "{}|{}".format(proxy, protocol)
                                self.pickGoodResult(input, 'unknown')
                                Commons.printSuccess("Proxy {}|{} LIVE and marked as UNKNOWN due to server cannot get details info".format(proxy, protocol))

                        except Exception as e:
                            file = open('logs.txt', 'a')
                            file.write(str(e) + "\n")
                            file.close()

                            input = "{}|{}".format(proxy, protocol)
                            self.pickGoodResult(input, 'unknown')
                            Commons.printSuccess("Proxy {}|{} LIVE and marked as UNKNOWN due to exception of server".format(proxy, protocol))

                        break

                    else:
                        self.throwToTrash(proxy)
                        Commons.printError("Proxy {}|{} not working anymore".format(proxy, protocol))
                        continue
                except Exception:
                    self.throwToTrash(proxy)
                    Commons.printError("Proxy {}|{} not working anymore".format(proxy, protocol))
            
            time.sleep(1)

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(process, '{}'.format(proxy.rstrip())) for proxy in self.arrayList]
            done, not_done = wait(futures, timeout=0)

            try:
                while not_done:
                    freshly_done, not_done = wait(not_done, timeout=5)
                    done |= freshly_done
            except KeyboardInterrupt:
                print("")
                Commons.printWarning('Keyboard interrupted! Shutting down server')
                print("")

                executor.shutdown(wait=False)
                self.killProcess()
            except Exception: 
                print("ERROR")

    def proxyJudge(self, proxy, protocol):
        ip, port = proxy.split(':')
        headers  = { 'User-Agent': self.getRandomUserAgent() }
        response = requests.get("https://proxycheck.io/apiproxy/{}?vpn=1&asn=1&tag=proxycheck.io".format(ip), headers=headers, proxies={"https": "{}://{}".format(protocol, proxy)}, timeout=10)
        return response

    def killProcess(self):
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)
    
    def pickGoodResult(self, text: str, type):
        filename = 'unknown-proxy.txt'

        if type == 'clean':
            filename = 'clean-proxy.txt'
        elif type == 'blacklist':
            filename = 'blacklist-proxy.txt'

        file = open(filename, 'a')
        file.write(text + "\n")
        file.close()

    def throwToTrash(self, text: str):
        file = open('bad-proxy.txt', 'a')
        file.write(text + "\n")
        file.close()

if __name__ == '__main__':
    start_time = time.time()

    MAX_THREADS = 1000
    
    proxyChecker = ProxyChecker()
    proxyChecker.check()

    print("")
    Commons.printInfo(str("Server finish jobs after: %s seconds\n" % (time.time() - start_time)))
    