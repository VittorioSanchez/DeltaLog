#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
import pandas as pd

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
SPLIT_CHAR = "-"
PATH = "."
NAME = "out"
SEARCH_LIST = []
"""
TODO: accessors for globals
TODO: doc functions
"""

def parse_config(config): # input json
    global TIME_FORMAT, SPLIT_CHAR, SEARCH_LIST, NAME, PATH
    if 'timestampFormat' in config:
        TIME_FORMAT = config['timestampFormat']
    if 'splitCharacter' in config:
        SPLIT_CHAR = config['splitCharacter']
    """
    TODO: Support delta time between same trace
    """
    if 'timeBetween' in config:
        SEARCH_LIST = config['timeBetween']
    if 'outputPath' in config:
        PATH = config['outputPath']
    if 'outputName' in config:
        NAME = config['outputName']
    return

def extract_logs(file):
    start_logs_list = []
    target_logs_list = []
    for search_item in SEARCH_LIST:
        start_logs = []
        target_logs = []

        while True:
            line = file.readline()
            if not line: # EOF
                break
            if search_item[0]['text'] in line:
                start_logs.append(line)
            if search_item[1]['text'] in line:
                target_logs.append(line)

        file.seek(0) #return to beginning of file
        start_logs_list.append(start_logs)
        target_logs_list.append(target_logs)

    return start_logs_list, target_logs_list


def parse_time(logs_list):
    global SPLIT_CHAR, TIME_FORMAT
    time_list = []
    text_list = []

    for log_list in logs_list:
        time_log = []
        text_log = []
        for log in log_list:
            """
            TODO: Improve timestamp detection
            here it's assumed timestamp is at beginning of line.
            """
            timestamp, text = log.split(SPLIT_CHAR, 1)
            time_log.append(datetime.strptime(timestamp, TIME_FORMAT))
            text_log.append(text)
        time_list.append(time_log)
        text_list.append(text_log)

    return time_list, text_list


def calculate_delta_time(start_time_list, start_text_list, targe_timelist, target_text_list):
    link_values_list = []

    for (start_list, start_text, target_list, target_text) in zip(start_time_list, start_text_list, targe_timelist, target_text_list):
        start_len = len(start_list)
        target_len = len(target_list)
        start_index = 0
        target_index = 0

        while start_index < start_len or target_index < target_len:
            if target_index < target_len:
                if start_index < start_len:
                    if start_list[start_index] < target_list[target_index]:
                        link_values_list.append([str(start_list[start_index]),
                                                    start_text[start_index],
                                                    str(target_list[target_index]-start_list[start_index])])
                        start_index += 1
                    else:
                        link_values_list.append([str(target_list[target_index]),
                                                    target_text[target_index],
                                                    None])
                        target_index += 1
                else:
                    link_values_list.append([str(target_list[target_index]),
                                                target_text[target_index],
                                                None])
                    target_index += 1
            else:
                link_values_list.append([str(start_list[start_index]),
                                            start_text[start_index],
                                            None])
                start_index += 1

        link_values_list.append([None,None,None])

    """
    TODO: separate excel output in different function
    """
    df = pd.DataFrame(link_values_list,columns=['Time', 'Log', 'Delta'])

    """"
    TODO: Must verify PATH also
    """
    if os.path.exists(PATH+"/"+NAME+".xlsx"):
        df.to_excel(PATH+"/"+NAME+"_"+datetime.now().strftime("%d-%m-%y_%H_%M_%S")+".xlsx",
                    sheet_name=datetime.now().strftime("%d-%m-%y_%H_%M_%S"))
    else:
        df.to_excel(PATH+"/"+NAME+".xlsx",
                    sheet_name=datetime.now().strftime("%d-%m-%y_%H_%M_%S"))

    return


def main(argv1, argv2):
    logs = open(argv1, 'r')
    config = open(argv2, 'r').read()
    config_json = json.loads(config)
    parse_config(config_json)
    # using lists instead of dictionnaries because they don't allow duplicates
    start, target = extract_logs(logs)
    start_time, start_text = parse_time(start)
    targe_time, target_text = parse_time(target)
    calculate_delta_time(start_time, start_text, targe_time, target_text)

    sys.exit(0)

"""
TODO: Support multiple log files
TODO: tests and examples
"""
# argv1: file log - argv2: json config
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
