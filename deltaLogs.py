#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
import pandas as pd

timeFormat = "%Y-%m-%d %H:%M:%S.%f"
splitChar = "-"
path = "."
name = "out"
searchList = []

def ParseConfig(config): # input json
    global timeFormat, splitChar, searchList, name, path
    if 'timestampFormat' in config:
        timeFormat = config['timestampFormat']
    if 'splitCharacter' in config:
        splitChar = config['splitCharacter']
    """
    TODO: Support delta time between same trace
    """
    if 'timeBetween' in config:
        searchList = config['timeBetween']
    if 'outputPath' in config:
        path = config['outputPath']
    if 'outputName' in config:
        name = config['outputName']
    return

def extractLogs(file):
    startLogsList = []
    targetLogsList = []
    for searchItem in searchList:
        startLogs = []
        targetLogs = []

        while True:
            line = file.readline()
            if not line: # EOF
                break
            if searchItem[0]['text'] in line:
                startLogs.append(line)
            if searchItem[1]['text'] in line:
                targetLogs.append(line)

        file.seek(0) #return to beginning of file
        startLogsList.append(startLogs)
        targetLogsList.append(targetLogs)

    return startLogsList, targetLogsList


def parseTime(logslist):
    global splitChar, timeFormat
    timeList = []
    textList = []

    for list in logslist:
        timeLog = []
        textLog = []
        for log in list:
            """
            TODO: Improve timestamp detection
            here it's assumed timestamp is at beginning of line.
            """
            timestamp, text = log.split(splitChar, 1)
            timeLog.append(datetime.strptime(timestamp, timeFormat))
            textLog.append(text)
        timeList.append(timeLog)
        textList.append(textLog)

    return timeList, textList


def calculateDeltaTime(startTimeList, startTextList, targetTimeList, targetTextList):
    linkValuesList = []

    for (startList, startText, targetList, targetText) in zip(startTimeList, startTextList, targetTimeList, targetTextList):
        startLen = len(startList)
        targetLen = len(targetList)
        startIndex = 0
        targetIndex = 0

        while startIndex < startLen or targetIndex < targetLen:
            if targetIndex < targetLen:
                if startIndex < startLen:
                    if startList[startIndex] < targetList[targetIndex]:
                        linkValuesList.append([str(startList[startIndex]), startText[startIndex], str(targetList[targetIndex]-startList[startIndex])])
                        startIndex += 1
                    else:
                        linkValuesList.append([str(targetList[targetIndex]), targetText[targetIndex], None])
                        targetIndex += 1
                else:
                    linkValuesList.append([str(targetList[targetIndex]), targetText[targetIndex], None])
                    targetIndex += 1
            else:
                linkValuesList.append([str(startList[startIndex]), startText[startIndex], None])
                startIndex += 1

        linkValuesList.append([None,None,None])

    """
    TODO: separate excel output in different function
    """
    df = pd.DataFrame(linkValuesList,columns=['Time', 'Log', 'Delta'])

    if os.path.exists(path+"/"+name+".xlsx"):
        df.to_excel(path+"/"+name+"_"+datetime.now().strftime("%d-%m-%y_%H_%M_%S")+".xlsx", sheet_name=datetime.now().strftime("%d-%m-%y_%H_%M_%S"))
    else:
        df.to_excel(path+"/"+name+".xlsx", sheet_name=datetime.now().strftime("%d-%m-%y_%H_%M_%S"))

    return


def main(argv1, argv2):
    logs = open(argv1, 'r')
    config = open(argv2, 'r').read()
    configJson = json.loads(config)
    ParseConfig(configJson)
    # using lists instead of dictionnaries because they don't allow duplicates
    start, target = extractLogs(logs)
    startTime, startText = parseTime(start)
    targetTime, targetText = parseTime(target)
    calculateDeltaTime(startTime, startText, targetTime, targetText)

    sys.exit(0)

"""
TODO: Support multiple log files
TODO: tests and examples
"""
# argv1: file log - argv2: json config
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
