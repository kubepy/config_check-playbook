#!/usr/bin/env python

DOCUMENTATION = '''
---
module: configCheck
description: Check or Update configuration file
version_added: 2.2.1
author: Red Hat

requirements:
    - "python >= 2.6"
options:
ptions
    filepath:
        description:
            - The absolute path to the file
        required: True
    value:
        description:
            - The expected results
        required: False
        default: 'NULL'
    configuration:
        description:
            - Check or Update configuration items
        required: True
    rule:
        description:
            - Configuration values equivalent rules (a=1,a 1)
            - Special configuration check existing rules (Regular expressions)
        default: ' '
        choices:
            - ' '
            - '='
            - 'a.*b.*c'
        required: False
'''

EXAMPLES = '''
    - name: shell execution
      local_action:
        module: configCheck
        filepath: '/root/test'
        configuration: 'ansibleserver'
        value: '192.168.0.1'
        rule: '='
'''


import commands
import os

def handler(module, filepath, configuration, value, rule):
    if os.path.exists(filepath):
        if value in ['default', '']:
            command = "grep '^%s[[:space:],=]' %s"% (configuration, filepath)
            #module.fail_json(msg=command)
            ret = commands.getoutput(command)
            if ret == "":
                return "Success"
            else:
                return "Failure"
        elif value == 'NULL':
            if rule != " " and rule != "=":
                command = r"grep '[[:space:],=]%s' %s"% (rule, filepath)
            else:
                command = r"grep '^%s[[:space:],=]' %s"% (configuration, filepath)
            #module.fail_json(msg=command)
            ret = commands.getoutput(command)
            ret = ret.split('\n')
            #module.fail_json(msg=ret)
            if len(ret) > 1:
                return "ERROR"
            elif len(ret) == 1 and ret[0] != "":
                return "Success"
            else:
                return "Failure"
        else:
            command = "grep '^%s[[:space:],=]' %s"% (configuration, filepath)
            #module.fail_json(msg=command)
            ret = commands.getoutput(command)
            ret = ret.split('\n')
            #module.fail_json(msg=ret)
            if len(ret) > 1:
                return "ERROR"
            elif len(ret) == 1 and ret[0] != "":
                command = "if [ -n `grep -q '^%s[[:space:],=]*%s' %s` ];then echo 'True';else echo 'False';fi"% (configuration, value, filepath)
                #module.fail_json(msg=command)
                ret = commands.getoutput(command)
                if ret == "True":
                    return "Success"
                else:
                    return "Failure"
            else:
                return "Failure"
    else:
        return "ERROR"

def main():
    module = AnsibleModule(
        argument_spec=dict(filepath=dict(required=True),
                           value=dict(default="NULL", required=False),
                           configuration=dict(required=True), 
                           rule=dict(default=" ", required=False)),
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json(changed=False)

    value = module.params['value']
    rule = module.params['rule']
    filepath = module.params['filepath']
    configuration = module.params['configuration']
    ret = handler(module, filepath, configuration, value, rule)

    content = ""
    result = ""
    info = ""
    tag = "Check file " + filepath + " setting is [" + configuration + rule + value + "]"
    expect = "File " + filepath + " setting [" + configuration + rule + value + "]"
   
    if ret == "ERROR":
        changed = False
        result = 'Error'
        content = 'File [ %s ] Config [ %s ] check error.' % (filepath, configuration)
        info = "[ ERROR ] : Whether the file exists, Configure more than one."
    elif ret == "Failure":
        changed = False
        result = 'Failure'
        content = 'File [ %s ] Config [ %s ] check failure.' % (filepath, configuration)
        info = 'Check Failure.'
    else:
        changed = False
        result = "Passed"
        content = 'File [ %s ] Config [ %s ] check success.' % (filepath, configuration)
        info = 'Check Success.'
 
    module.exit_json(changed=changed,result=result,content=content,info=info,expect=expect,tag=tag)

from ansible.module_utils.basic import *
main()
