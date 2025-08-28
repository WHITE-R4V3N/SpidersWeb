import re
from spiders_web_settings import *

class Hammer(): # Class for enforcing the rules

    def BanHammer(ip_address, reason):
        try:
            print(f'\n[{ORANGE}BANNED{END}] {RED}{ip_address}{END} was banned for {RED}{reason}{END}!\n')
        except:
            print(f'{FAIL} Was unable to ban {RED}{ip_address}{END}. Wait to try again or manually do it.')

class Judgement():
    rulesTable = {}
    activityTable = {}
    activeRules = { 'pa' : 0, 'af' : 0, 't': 0 }

    def ProcessCommands():
        for key in Judgement.rulesTable:
            rules_list = Judgement.rulesTable[key].split('-')
            
            for item in rules_list[1:]:
                item_list = item.split(' ')
                Judgement.activeRules[item_list[0]] = item_list[1]

    def ProcessActivity(activity):
        activityTimes = {}

        for line in activity.split('\n'):
            try:
                date_time = re.search(r'\w+\s+\d+ \d+:\d+:\d+', line).group()
                ip_address = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line).group()

                if ip_address not in activityTimes:
                    activityTimes[ip_address] = []

                activityTimes[ip_address].append(date_time)

            except:
                pass

        
        return activityTimes

    def DeterminePatterns():
        for key in Judgement.activeRules:
            if Judgement.activeRules[key] and key != 't':
                activity = Judgement.ProcessActivity(Judgement.activityTable[key])

                ################ Compare and Find Patterns ################

                timeConstraint = int(Judgement.activeRules['t'])
                maxAttempts = int(Judgement.activeRules[key])

                if key == 'pa':
                    for k_act in activity:
                        attempts = len(activity[k_act])

                        if attempts >= maxAttempts:
                            print(f'attempts: {attempts} | activity: {activity[k_act]}')
                            # Need to see what the data looks like before we can continue

                            # Check the timings of each attempt and see if within attempts (3 attempts) a password was tried in t (seconds)
                            # Turn each datetime into timestamp
                            # ts = datetime.timestamp(item)
                            # then compare 3 attempts times and see if it falls below t [call banHammer if it does], if more pass
                        else:
                            pass

                if key == 'af':
                    for k_act in activity:
                        attempts = len(activity[k_act])

                        if attempts >= maxAttempts:
                            Hammer.BanHammer(k_act, 'Authentication Failure')

