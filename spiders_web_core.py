#! /usr/bin/env python3

import sys, string, os, re
import paramiko
import base64
import ast
import json
import time
import subprocess
from threading import Thread
from ipaddress import ip_address
from string import ascii_uppercase, ascii_lowercase, digits
from cryptography.fernet import Fernet

from spiders_web_hammer import *
from spiders_web_settings import *

class Cmd_prompt:
    original_prompt = prompt = f"{MAIN}Spiders-Web >{END} "
    SPACE = '#>SPACE$<#'

class PromptHelp:
    commands = {

        'help' : {
            'details' : f'''
            \r  Really ?
            \r  Displays basic help information or detailed help.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  help
            \r  \t\tor
            \r  help <command>
            ''',
            'min_args' : 0,
            'max_args' : 1
        },

        'create' : {
            'details' : f'''
            \r  Create a custom session with commands.
            \r  Allowing you to create sessions for ssh, ftp, wget, etc.
            \r  ALL SUPPORTED SESSIONS ARE LISTED BELOW. SEE SUPPORTS
            
            \r                    Supports
            \r      ------------------------------------
            \r      |   SSH         FTP         WGET   |
            \r      |   Python Scripts          NetCat |
            \r      ------------------------------------

            \r  Command Usage
            \r  --------------------------------------------------
            \r  create ssh <ip> <username> <password>
            ''',
            'min_args' : 2,
            'max_args' : 4
        },

        'save' : {
            'details' : f'''
            \r  Creates a encrypted file with the information used to create
            \r  each session. Allowing you to quickly recreate previous sessions.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  save <filename.extension> <encryption password>
            ''',
            'min_args' : 4,
            'max_args' : 4
        },

        'load' : {
            'details' : f'''
            \r  Loads an encrypted file with information previously used.
            \r  Allowing you to quickly recreate previous sessions.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  load <filename.extension> <encryption password>
            ''',
            'min_args' : 4,
            'max_args' : 4
        },

        'exit' : {
            'details' : f'''
            \r  Closes the program and terminates any running sessions.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  exit
            \r  \t\t or
            \r  close
            ''',
            'min_args' : 0,
            'max_args' : 0
        },

        'delete' : {
            'details' : f'''
            \r  Deletes a session that was created.
            \r  Takes only one arguement that is the session ID you wish to close.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  delete <session ID>
            ''',
            'min_args' : 1,
            'max_args' : 1
        },

        'sessions' : {
            'details' : f'''
            \r  Displays all currently active sessions.
            \r  Displays session information: ID, User, IP Address, etc.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  sessions
            ''',
            'min_args' : 0,
            'max_args' : 1
        },

        'connect' : {
            'details' : f'''
            \r  Connects to the thread that holds the session.
            \r  Allows you to interact with the session.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  connect <session ID>
            ''',
            'min_args' : 0,
            'max_args' : 1
        },

        'monitor' : {
            'details' : f'''
            \r  Connects to the thread that holds the session.
            \r  Will monitor and send alerts for suspicious activity.

            \r  You can use Ctrl + C to stop monitoring a session.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  monitor <session id> (monitor specific session device)
            \r      or
            \r  monitor all (will monitor all sessions and devices)
            ''',
            'min_args' : 0,
            'max_args' : 1
        },

        'rules' : {
            'details' : f'''
            \r  Allows user to set up rules for monitor mode.
            \r  Rules can be added, removed, modified, etc.

            \r  Command Usage
            \r  --------------------------------------------------
            \r  rules <add, remove, modify> <rule name> <rule type> <specifics>
            \r
            \r  example:
            \r  rules add BanPass ban -pa 3 (After 3 password attempts, ban device ip)
            \r  rules remove BanPass (removes the rule from the rules table)
            \r  rules modify BanPass <complete new command> (changes the command)
            \r  rules save <filename.extention> (Saves rules to file)
            \r  rules load <filename.extension> (Loads the rules from a file)
            \r
            \r  To view all rules on the table use:
            \r  rules table
            ''',
            'min_args' : 0,
            'max_args' : 1
        },

    }

    def print_small_help():
        print(
            f'''
            \r  Command             Decsription
            \r  --------------------------------------------------
            \r  help        [+]     Print this message.
            \r  create      [+]     Create custom sessions.
            \r  save                Saves all session data.
            \r  load                Loads saved session data.
            \r  delete      [+]     Deletes a session.
            \r  sessions            Lists all sessions.
            \r  connect     [+]     Connects to the session.
            \r  monitor     [+]     Monitors connected server.
            \r  rules       [+]     Create rules for monitor mode.
            \r  exit                Closes the application.

            \r Commands with [+] may take additional arguements.
            \r For details use: help <COMMAND>
            '''
        )

    def print_details_help(cmd):
        print(PromptHelp.commands[cmd]['details']) if cmd in PromptHelp.commands.keys() else print(f'{FAIL} No details for command "{cmd}".')

class SSH:
    def CreateSSH(command_list):
        host = command_list[2]
        username = command_list[3]
        password = command_list[4]

        print(f"\n[{LRED}CONNECTING{END}] Trying the information provided:")
        print(f" Connection:\t\tSSH")
        print(f" Host:\t\t\t{host}")
        print(f" Username:\t\t{username}")
        print(f" Password:\t\t{password}\n")

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=username, password=password)
            #client.close()

            print(f"{SUCCESS} Connection to {command_list[1]} successful.")
            print(f"  Type {GREEN}pause{END} to suspend session while in one.\n")
        except:
            print(f"{FAIL} IP, Password, or Username is wrong.\n  Connection was not established.")

        return client
    
    def ExecuteCMDSSH(client, ip):
        print(f"\n{SUCCESS} Connection established.\n")
        while True:
            cmd = input(f"{GREEN}{ip}/SSH>{END} ")

            if cmd != "pause":
                _stdin, _stdout, _stderr = client.exec_command(cmd)
                print(_stdout.read().decode())
            else:
                print()
                break

    def CloseConnectionSSH(client):
        client.close()

class Base64Conversion:
    def EncodeString(command_list):
        raw_string = f"{command_list[2]}{command_list[3]}{command_list[4]}".encode("ascii")
        base64_string = base64.b64encode(raw_string).decode("ascii")

        raw_classifier = f"{command_list[1]}".encode("ascii")
        base64_classifier = base64.b64encode(raw_classifier).decode("ascii")

        encoded_string = f"{base64_classifier}-{base64_string}"

        return encoded_string

class EncDecFile():
    def FileEncryption(data, filename): # Add data_filename, and key_filename
        key = Fernet.generate_key()

        with open('enc_key.key', 'wb') as file:
            file.write(key)

        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(data).encode())
        with open(filename, 'wb') as file:
            file.write(encrypted)

    def FileDecryption(connections_dict, filename): # Add data_filename, and key_filename

        print(f"{filename}")
        with open('enc_key.key', 'rb') as file:
            key = file.read()

        fernet = Fernet(key)
        with open(filename, 'rb') as file:
            data = json.loads(fernet.decrypt(file.read()))

        for key in data:
            command_list = ["create", data[key][0], data[key][1], data[key][2], data[key][3]]
            ssh_client = SSH.CreateSSH(command_list)

            thread_ID = Base64Conversion.EncodeString(command_list)

            conns_update = {thread_ID: [ssh_client, command_list[1], command_list[2], command_list[3], command_list[4]]}
            connections_dict.update(conns_update)

class MonitorSessions():
    def ConnectionData(data):
        print(f'\t\t\t\t{GREEN}SESSION DATA{END}')
        print(f'    ip ({data[2]})   |   username ({data[3]})   |   password({data[4]})')

        return data[0]

    def GetActivity(client):
        print(f'\n\t\t\t{GREEN}Possible Active Connections{END}')
        cmd = 'netstat --tcp --numeric | grep 22'
        _stdin, _stdout, _stderr = client.exec_command(cmd)
        print(_stdout.read().decode())

        print(f'\t\t\t\t {GREEN}SERVER FEED{END}')
        cmd = 'grep "authentication failure" /var/log/auth.log'
        _stdin, _stdout, _stderr = client.exec_command(cmd)
        Judgement.activityTable['af'] = _stdout.read().decode()
        print(f'{Judgement.activityTable["af"]}')

        cmd = 'grep "Failed password" /var/log/auth.log'
        _stdin, _stdout, _stderr = client.exec_command(cmd)
        Judgement.activityTable['pa'] = _stdout.read().decode()
        print(f'{Judgement.activityTable["pa"]}')

        Judgement.DeterminePatterns()

        time.sleep(30)

class MonitorRules():

    def ViewRules():
        print(f'\n[{ORANGE}Grabbing Rules{END}] Grabbing the rules table for viewing')
        # For each key in rulesTable print key and rules string
        print(f'\n\t\t   [{GREEN}RULES TABLE{END}]\n')

        print('\t' + '-'*45)
        for key in Judgement.rulesTable:
            print(f'\t|{key.center(10)} | {Judgement.rulesTable[key].center(30)}|')
        print('\t' + '-'*45 + '\n')

    def AddRule(cmd_list):
        try:
            Judgement.rulesTable[cmd_list[1]] = ' '.join(cmd_list[2:])
            Judgement.ProcessCommands()
            print(f'\n{SUCCESS} Rule was added successfully.\n')
        except:
            print(f'\n{FAIL} Rule was not created. Please try again.\n')

    def RemoveRule(cmd_list):
        try:
            del Judgement.rulesTable[cmd_list[1]]
            # Remove it from the activeRules as well
            print(f'\n{SUCCESS} Rule was removed successfully.\n')
        except:
            print(f'\n[{FAIL}] Rule was not found in the rules table. Please try again.\n')
        # del rulesTable[rule_name]

    def ModifyRule(cmd_list):
        try:
            updateRule = ' '.join(cmd_list[2:])
            Judgement.rulesTable[cmd_list[1]] = updateRule
            Judgement.ProcessCommands()
            print(f'\n{SUCCESS} {cmd_list[1]} rule has been modified.\n')
        except:
            print(f'\n{FAIL} Could not change rule. Please try again.\n')

    def SaveRules(cmd_list):
        try:
            with open(cmd_list[1], "w") as fp:
                json.dump(Judgement.rulesTable, fp)
        
            print(f'\n{SUCCESS} Saved the rules table to {cmd_list[1]}\n')
        except:
            print(f'\n{FAIL} Rules were not saved correctly. Please try again.\n')

    def LoadRules(cmd_list):
        try:
            with open(cmd_list[1], 'r') as fp:
                Judgement.rulesTable = json.load(fp)
                Judgement.ProcessCommands()
                print(f'\n{SUCCESS} Rules were loaded from the file.\n')
        except:
            print(f'\n{FAIL} Rules were not loaded correctly. Please try again.\n')

        # Something is wrong with the variable rulesTable in this function. The variable comes from the hammer.py
