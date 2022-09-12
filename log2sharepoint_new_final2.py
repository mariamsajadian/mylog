#!/usr/bin/python3
"""
Writes a CSV copy of the Tomcat logs to the defined Sharepoint directory.
"""

__author__ = "me"
__copyright__ = "Copyright 2021"
__license__ = "Proprietory"
__maintainer__ = "me"
__email__ = "me"


import os
import csv
import fnmatch
import gzip
from pathlib import Path

# from shareplum import Office365
# from shareplum import Site
# from shareplum.site import Version

class new_dict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

PATH = Path.cwd()
logDict = new_dict()
patchLogDict = new_dict()

def main():

    read_input(get_gzips())
    patch_process_data(get_gzips())
    write_logs_csv_patch()
    write_logs_csv()
    removeCommas()
    return


def get_gzips():
    contents = []
    file = open('edg_log_2022-08-16.log', 'r')
    contents += list(file)
    # for file in os.listdir(PATH):
    #     if fnmatch.fnmatch(file, "*.log"):
    #         file = open(file, "r")
    #         contents += list(file)
    #         break

        # elif fnmatch.fnmatch(file, "catalina.*"):
        #     file = open(file)
        #     contents += list(file)
    return contents

def create_dict(date):
    # pregenerates the logdict entries for each date. Could be more efficient.
    nested_dict = {}
    n = 0
    while n <= 7:
        nested_dict.update({n: None})
        n += 1
    if date not in logDict:
        # If necessary a dict entry is made using the date as a key.
        logDict.update({date: nested_dict})
    return


def read_input(log):
    # The heart of the program so to speak, reads the input and checks how each line should be handled.
    for line in log:
        try:
            line = str(line)
            # check if this is a message entry Import starttime: 2020-12-17T01:04:00.098+00:00 | for asset: 55e30b07-b
            if line != "\n" and line.__contains__('ProfileControlElement - SWP Profiling:'):
                #line_array = line.replace("|| |", " | |").split("|")
                line_array = line.split('|')
                date = line_array[1].split('Import starttime:')[1].strip()
                # logDict.update({date:None})
                #create_dict(date)
                # index = 0
                # find specific text
                tIndex = [idx for idx, s in enumerate(line_array) if "IFCXML Importer Step" in s or "HTTP Code Returned" in s][0]
                state_line = line_array[tIndex].strip()
                # print(state_line)
                # state_line = line_array[4].strip()  # step refers to the part of the log that tracks what step of the importer is being handled.
                state_line_parts = state_line.split(':')
                # print(state_line_parts)
                if state_line_parts[0].strip() == "IFCXML Importer Step":
                    handle_step_time(line_array, state_line_parts[1].strip(), date)
                    # The same part of the log that refers to step also shows if there is a http code returned.
                    # It should be noted that the handle_400 variable is misleading since all return codes are handled here.
                elif state_line_parts[0].strip() == "HTTP Code Returned":
                    handle_return(line_array, state_line_parts[1], date)
                else:
                    print("This really REALLY shouldn't happen")  # There is technically not third option available, if due to changes or errors there is this notifies the user about it
        except Exception as e:
            continue
    return

def handle_step_time(line, step_number, date):
    #Step Time
    ms = [idx for idx, s in enumerate(line) if " ms" in s][0]
    logDict[date]['step_' + str(step_number)] = line[ms].split(' ')[1].strip()
    # print(logDict[date]['step_' + str(step_number)])

    fmess = [True for s in line if " for message:" in s]
    if fmess:
        fsIdx = [idx for idx, s in enumerate(line) if "for message:" in s][0]
        logDict[date]['message_uuid'] = line[fsIdx].split('for message:')[1].strip()
    # check for asset title
    foras = [True for s in line if " for asset:" in s]
    if foras:
        faIdx = [idx for idx, s in enumerate(line) if "for asset:" in s][0]
        logDict[date]['asset_uuid'] = line[faIdx].split('for asset:')[1].strip()

    logDict[date]['return_message'] = line[ms-1].strip()
    isIdx = [idx for idx, s in enumerate(line) if "Import starttime:" in s][0]
    logDict[date]['step_' + str(step_number) + '_timestamp'] = line[isIdx].split('Import starttime:')[1].strip()
    return

def handle_return(line, return_code, date):
        logDict[date]['return_code'] = return_code.strip()
        logDict[date]['return_timestamp'] = line[1].split('Import starttime:')[1].strip()
        fmess = [True for s in line if " for message:" in s]
        if fmess:
            fsIdx = [idx for idx, s in enumerate(line) if "for message:" in s][0]
            logDict[date]['message_uuid'] = line[fsIdx].split('for message:')[1].strip()
            logDict[date]['return_message'] = line[5].strip()

        foras = [True for s in line if " for asset:" in s]
        if foras:
            faIdx = [idx for idx, s in enumerate(line) if "for asset:" in s][0]
            logDict[date]['asset_uuid'] = line[faIdx].split('for asset:')[1].strip()
            logDict[date]['return_message'] = line[4].strip()

        return

def removeCommas():
    with open('newlogging', 'rb') as f:
        with open('1test2.log', 'wb') as fi:
            text = f.read()
            while text.find(
                    ',,') != -1:
                text = text.replace(',,', ',', text.count(',,'))

            fi.write(text)
        return

def write_logs_csv():
    with open("newlogging", 'wb') as g:
        csv_writer = csv.writer(g)
        csv_writer.writerow(["importDate","messageUUID","assetUUID","step1Time","step1Timestamp","step2Time","step2Timestamp","step3Time","step3Timestamp","step4Time","step4Timestamp","step5Time","step5Timestamp","returnTimestamp","returnCode","ReturnMessage"])
        for key, value in logDict.items():
            # print(key)
            # print(value)
            csv_writer.writerow(
                                [
                    key,
                    value['message_uuid'] if 'message_uuid' in value else "",
                    value['asset_uuid'] if 'asset_uuid' in value else "",
                    value['step_1'] if 'step_1' in value else "",
                    value['step_1_timestamp'] if 'step_1_timestamp' in value else "",
                    value['step_2'] if 'step_2' in value else "",
                    value['step_2_timestamp'] if 'step_2_timestamp' in value else "",
                    value['step_3'] if 'step_3' in value else "",
                    value['step_3_timestamp'] if 'step_3_timestamp' in value else "",
                    value['step_4'] if 'step_4' in value else "",
                    value['step_4_timestamp'] if 'step_4_timestamp' in value else "",
                    value['step_5'] if 'step_5' in value else "",
                    value['step_5_timestamp'] if 'step_5_timestamp' in value else "",
                    value['return_timestamp'] if 'return_timestamp' in value else "",
                    value['return_code'] if 'return_code' in value else "",
                    value['return_message'] if 'return_message' in value else ""
                ]
            )

        # write_csv.close()

    return

def patch_process_data(data):
    for line in data:
        try:
            line = str(line)
            if line != "\n" and line.__contains__('patch id'):
                line_array = line.split('D.HTTP')
                date = line_array[0].split('INFO')[0].strip().replace(',', '.')
                patchType = line_array[1][line_array[1].find("-") + len("-"):line_array[1].rfind("patch id")].strip()
                patchId = line_array[1][line_array[1].find("patch id:") + len("patch id:"):line_array[1].rfind(" (")].strip()
                lotId = line_array[1].split("ds:")[1].strip()
                size = line_array[1][line_array[1].find("(") + len("("):line_array[1].rfind("bytes")].strip()

                patchLogDict[date]["patchType"] = patchType
                patchLogDict[date]["patchId"] = patchId
                patchLogDict[date]["lotId"] = lotId
                patchLogDict[date]["size"] = size
        except:
            continue
    return

# Patch creator
def write_logs_csv_patch():
    with open("logging_patch", 'wb') as g:
        csv_writer = csv.writer(g)
        csv_writer.writerow(["timestamp","patchType","patchId","lotId","size"])
        for key, value in patchLogDict.items():
            csv_writer.writerow(
                [
                    key,
                    value['patchType'] if 'patchType' in value else "",
                    value['patchId'] if 'patchId' in value else "",
                    value['lotId'] if 'lotId' in value else "",
                    value['size'] if 'size' in value else ""
                ]
            )

    return

# def send_files_sharepoint():
#     authcookie = Office365(
#         "https://taxonicbv.sharepoint.com",
#         username="support@taxonic.com",
#         password="!TaXoNiC2020",
#     ).GetCookies()
#     site = Site(
#         "https://taxonicbv.sharepoint.com/sites/Schiphol/",
#         version=Version.v365,
#         authcookie=authcookie,
#     )
#     folder = site.Folder("Gedeelde documenten/80 Logging/current_logs/")
#     with open("/home/ubuntu/logging", mode="rb") as file:
#         fileContent = file.read()
#     folder.upload_file(fileContent, "asb_log.csv")
#
#     return

main()

