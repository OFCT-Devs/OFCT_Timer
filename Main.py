import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

folderPath = os.getenv('APPDATA') + "\\HexChat\\"
serverConfigFile = open(folderPath + "servlist.conf", "r")
serverConfigFileText = serverConfigFile.read()
serverDomainPosition = serverConfigFileText.find("S=irc.ppy.sh")
logFileDestination = "a"
previousLogTextLen = 0
logTextToCheck = "a"
defaultTitle = "OFCT"
matchRefs = []

if serverDomainPosition == -1:
    serverDomainPosition = serverConfigFileText.find("S=cho.ppy.sh")

if serverDomainPosition == -1:
    print("HexChat에서 osu!irc 설정을 찾을 수 없습니다.")
    exit()

servername = serverConfigFileText[0:serverDomainPosition]
servername = servername[servername.rfind("N=") + 2:]
servername = servername[:servername.find("P=") - 1]

defaultTitle = input("타이머 기본 텍스트를 입력해 주세요 : ")
mpNumber = input("mp 번호를 입력해 주세요 : ")

logFileDestination = folderPath + "logs\\" + servername + "\\#mp_" + mpNumber + ".log"
# logFileDestination = folderPath + "logs\\" + servername + "\\test.log"
# logFileDestination = folderPath+"logs\\"+servername+"\\#osu.log"

try:
    logFile = open(logFileDestination, "r", encoding="UTF8")
    previousLogTextLen = len(logFile.read())
except FileNotFoundError:
    print("방 번호가 잘못되었거나, HexChat에서 방에 접속하지 않았습니다. 다시 확인해주세요.")
    time.sleep(5)
    exit()


def textCheck(loopCheck):
    global previousLogTextLen
    global logFile
    global logTextToCheck
    global matchRefs

    logFile = open(logFileDestination, "r", encoding="UTF8")
    logTextToCheck = logFile.read()[previousLogTextLen:]
    logFile.close()

    if not loopCheck:
        previousLogTextLen = previousLogTextLen + len(logTextToCheck)

    print(logTextToCheck)
    global reset

    if "\t!mp addref " in logTextToCheck:
        refereeNick = logTextToCheck[logTextToCheck.find("!mp addref ") + 11:]
        if not logTextToCheck.find("\n", logTextToCheck.find("\t!mp addref ")) == -1:
            refereeNick = logTextToCheck[logTextToCheck.find("!mp addref ") + 11:logTextToCheck.find("\n",
                                                                                                     logTextToCheck.find(
                                                                                                         "\t!mp addref "))]
        refereeNick.replace("\n", "")
        matchRefs.append(refereeNick)
        print(matchRefs)
        print("Added " + refereeNick + " to referees")

    for i in range(len(matchRefs)):
        if "<" + matchRefs[i] + ">\t!mp timer 90 r" in logTextToCheck:
            if loopCheck:
                return True
            resetText()
            roster()

        if "<" + matchRefs[i] + ">\t!mp timer 90 pr" in logTextToCheck:
            if loopCheck:
                return True
            resetText()
            pick(True)

        if "<" + matchRefs[i] + ">\t!mp timer 90 pb" in logTextToCheck:
            if loopCheck:
                return True
            resetText()
            pick(False)

        if "<" + matchRefs[i] + ">\t!mp timer 120 br" in logTextToCheck:
            if loopCheck:
                return True
            resetText()
            ban(True)

        if "<" + matchRefs[i] + ">\t!mp timer 120 bb" in logTextToCheck:
            if loopCheck:
                return True
            resetText()
            ban(False)

        else:
            if "<" + matchRefs[i] + ">\t!mp timer " in logTextToCheck:
                try:
                    customText = logTextToCheck[logTextToCheck.find("<" + matchRefs[i] + ">\t!mp timer "):]
                    customText = customText.split("\n")[0]
                    customText = customText.split(" ", 3)
                    customTime = int(customText[2])
                    customText = customText[3]

                    if customText.startswith("`"):
                        if loopCheck:
                            return True
                        resetText()
                        customText = customText[1:]
                        titleWrite(customText)
                        timer(customTime)
                except ValueError:
                    print("입력값에 오류가 있습니다.")

        if "<" + matchRefs[i] + ">\t!mp aborttimer" in logTextToCheck:
            if loopCheck:
                return True
            resetText()

        if "<" + matchRefs[i] + ">\t`reset" in logTextToCheck:
            if loopCheck:
                return True
            resetText()


def roster():
    titleWrite("로스터")
    redWrite("")
    blueWrite("")
    timer(90)


def pick(team):
    titleWrite("픽")

    if team:
        redWrite("Red")
    if not team:
        blueWrite("Blue")
    timer(90)


def ban(team):
    titleWrite("밴")

    if team:
        redWrite("Red")
    if not team:
        blueWrite("Blue")
    timer(120)


def timer(setTime):
    for i in range(setTime + 1):
        timeWrite(str(setTime - i))
        if textCheck(True):
            print("timer canceled")
            textCheck(False)
            return
        time.sleep(1)

    titleWrite("타이머 종료")
    redWrite("")
    blueWrite("")

    for i in range(20):
        time.sleep(0.5)
        if textCheck(True):
            textCheck(False)
            return

    resetText()


def titleWrite(text):
    titleFile = open("./timerTitle.txt", "w", encoding="UTF8")
    titleFile.write(text)
    titleFile.close()


def timeWrite(text):
    timeFile = open("./time.txt", "w", encoding="UTF8")
    timeFile.write(text)
    timeFile.close()


def redWrite(text):
    redFile = open("./redTitle.txt", "w", encoding="UTF8")
    redFile.write(text)
    redFile.close()


def blueWrite(text):
    blueFile = open("./blueTitle.txt", "w", encoding="UTF8")
    blueFile.write(text)
    blueFile.close()


def resetText():
    titleWrite(defaultTitle)
    blueWrite("")
    redWrite("")
    timeWrite("")


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        textCheck(False)


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folderPath + "logs\\" + servername + "\\", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    # observer.join()
