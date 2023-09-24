import os
from datetime import datetime
from modules.colors import *

LOG_FILE = 'logs.txt'

class Commons:

    def printInfo(text: str):
        date = datetime.now()
        format = "%d/%m/%y %H:%M:%S"
        datetimeText = date.strftime(format)
        
        # file = open(LOG_FILE, 'a')
        # file.write(str('[' + datetimeText + '] [INFO] ' + text + "\n"))
        # file.close()
        
        print('[' + datetimeText + '] ' + colors.BLUE + '[INFO] ' + colors.END + text)

    def printWarning(text: str):
        date = datetime.now()
        format = "%d/%m/%y %H:%M:%S"
        datetimeText = date.strftime(format)

        # file = open(LOG_FILE, 'a')
        # file.write(str('[' + datetimeText + '] [WARNING] ' + text + "\n"))
        # file.close()

        print('[' + datetimeText + '] ' + colors.YELLOW + '[WARNING] ' + colors.END + text)

    def printError(text: str):
        date = datetime.now()
        format = "%d/%m/%y %H:%M:%S"
        datetimeText = date.strftime(format)

        # file = open(LOG_FILE, 'a')
        # file.write(str('[' + datetimeText + '] [ERROR] ' + text + "\n"))
        # file.close()

        print('[' + datetimeText + '] ' + colors.RED + '[ERROR] ' + colors.END + text)

    def printSuccess(text: str):
        date = datetime.now()
        format = "%d/%m/%y %H:%M:%S"
        datetimeText = date.strftime(format)

        # file = open(LOG_FILE, 'a')
        # file.write(str('[' + datetimeText + '] [SUCCESS] ' + text + "\n"))
        # file.close()

        print('[' + datetimeText + '] ' + colors.GREEN + '[SUCCESS] ' + colors.END + text)
    