#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import os
import shutil
import commands
import xlwt
import codecs
import datetime

# Output the display list 
row_items = ['Check Options', 'Results',  "Expect", "Content", "Modification Method"]

def style_color(sign):
    styleOK = xlwt.easyxf('pattern: fore_colour light_blue;'
                          'font: colour %s, bold False;'%sign)
    return styleOK


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostvars=dict(require=True),
            check_item=dict(require=True),
            export_file=dict(require=True)
        ),
        supports_check_mode=False
    )

    result = dict(
        changed=False,
        message='Export excel file success.'
    )

    hostvars = eval(module.params['hostvars'].decode("utf-8"))
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    export_file = module.params['export_file']
    export_file = export_file.split('.')[0] + now + "." + export_file.split('.')[1]
    check_item = eval(module.params['check_item'].decode("utf-8"))
 
    excel_file = xlwt.Workbook(encoding='utf-8')

    all_hosts = hostvars.values()[0]["groups"]["all"]
    # Exclude local
    if "local" in all_hosts: all_hosts.remove("local")
    if 'localhost' in all_hosts: all_hosts.remove("localhost")
    if '127.0.0.1' in all_hosts: all_hosts.remove("127.0.0.1")

    column0 = all_hosts

    sheets = excel_file.add_sheet("Overall Results", cell_overwrite_ok=True)
    sheets.write(0,0,"IP Address")
    sheets.write(0,1,"Overall Results")
    lines = 1

    for j in range(0,len(column0)):
        if len(hostvars[column0[j]]) < 20:
            continue
        line = 1
        tags = 0
        sheet = excel_file.add_sheet(column0[j], cell_overwrite_ok=True)
        for i in range(0,len(row_items)):
            sheet.write(0,i,row_items[i])
        for n in range(0,len(check_item)):
            sheet.write(line,0,str(check_item[n]))
            #module.fail_json(msg=hostvars["172.16.251.131"]["timeChrony_maxslewrate"])
            try:
                if str(hostvars[column0[j]][check_item[n]]["result"]) == "Passed":
                    tag = 'green'
                else:
                    tag = 'red'
                    tags = 1
                sheet.write(line,1,str(hostvars[column0[j]][check_item[n]]["result"]),style_color(tag))

                if str(hostvars[column0[j]][check_item[n]]["result"]) == "Error":
                    sheet.write(line,3,str(hostvars[column0[j]][check_item[n]]["content"]),style_color('red'))
                else:
                    try:
                        sheet.write(line,3,str(hostvars[column0[j]][check_item[n]]["content"]))
                    except:
                        sheet.write(line,3,"No more information")
                sheet.write(line,2,str(hostvars[column0[j]][check_item[n]]["expect"]))
                sheet.write(line,4,str(hostvars[column0[j]][check_item[n]]["tag"]))
            except:
                #module.fail_json(msg=hostvars[column0[j]][check_item[n]])
                if str(hostvars[column0[j]][check_item[n]]["stdout"]) == "Passed":
                    tag = 'green'
                else:
                    tag = 'red'
                    tags = 1
                sheet.write(line,1,str(hostvars[column0[j]][check_item[n]]["stdout"]),style_color(tag))
                try:
                    if hostvars[column0[j]][check_item[n]]["stderr"] != "":
                        sheet.write(line,3,str(hostvars[column0[j]][check_item[n]]["stderr"]),style_color('red'))
                    else:
                        sheet.write(line,3,"No more information")
                except:
                        sheet.write(line,3,"No more information")
                sheet.write(line,2,str(hostvars[column0[j]][check_item[n]]["expect"]))
                sheet.write(line,4,str(hostvars[column0[j]][check_item[n]]["tag"]))
            line += 1

        sheets.write(lines,0,column0[j])
        if tags == 1:
            sheets.write(lines,1,"Failure",style_color('red'))
        else:
            sheets.write(lines,1,"Passed",style_color('green'))
        lines += 1

    excel_file.save(export_file)
    module.exit_json(**result)

from ansible.module_utils.basic import *
from ansible.module_utils.facts import *

if __name__ == '__main__':
    main()
