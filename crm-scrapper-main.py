import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from prometheus_client.core import GaugeMetricFamily, REGISTRY, Gauge, Summary
from prometheus_client import start_http_server
import time
import signal
import sys
import time
import threading

CRM_KEYS_LIST = ['voyagerTopic', 'InfranetJitReader', 'VoyagerJitReader']  # My search is case sensitive, beware, insert just unique values
crm_ops_login = 'http://crmsupport.office.orange.intra/CE/login.php'
CREDENTIALS = {'username': 'crmops', 'password': 'crm_ops'}
CHROMIUM_BROWSER_LOCATION = '/usr/lib64/chromium-browser/chromium-browser'
CHROMIUM_DRIVER_BINARY_LOCATION = '/usr/lib64/chromium-browser/chromedriver'
WAIT_AFTER_LOGIN = 10  # seconds, for that stupid redirect
NUMBER_OF_VALUES = 1  # DON'T CHANGE THIS. Starting from 0 1 -> (0, 1), so two values after the key provided in CRM_KEYS_LIST
# CRM_QUEUE_GAUGES = Gauge('my_inprogress_requests', 'Description of gauge')


# This function finds all key,value pairs based on CRM_KEYS_LIST, also removes the duplicates and returns a unique list
def search_for_key_value(key_name: str, full_element) -> list:
    f_search = re.findall(fr'{key_name}.*\d*', full_element)  # Regex find all <key .* [number]>
    f_search_uniq = list(set(f_search))  # Making a list of unique values
    return f_search_uniq


def get_info_from_crm_dashboard():
    try:
        # Defining chrome options for selenium #############################################################################
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = CHROMIUM_BROWSER_LOCATION
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option(name='detach', value=True)

        # Defining chrome driver options for selenium


        chrome_driver_binary = CHROMIUM_DRIVER_BINARY_LOCATION

        driver = webdriver.Chrome(chrome_driver_binary, options=chrome_options)
        driver.get(crm_ops_login)


        # Starting to scrape data #############################################################################################

        # Filling login credentials ###########################################################################################
        username_form = driver.find_element(By.NAME, value='user')
        username_form.send_keys(CREDENTIALS['username'])

        password_form = driver.find_element(By.NAME, value='password')
        password_form.send_keys(CREDENTIALS['password'])
        password_form.send_keys(Keys.ENTER)

        time.sleep(WAIT_AFTER_LOGIN)  # Waiting for redirect


        get_data = (driver.find_elements(By.TAG_NAME, value='tbody'))  # Getting all tbody tags from http page

        # print(get_data)

        dashboard_data = []
        for element in get_data:
            dashboard_data.append(element.text)  # Appending all http info into a list
        # print(dashboard_data)

        #dashboard_data = ['In process:\nStatus\nNo\nChanges in use: 74\nChanges in Process: 74\n  -Urgent: 294h:20m: 1\n  -High: 533h:14m: 12\n  -Medium: 1228h:3m: 40\n  -Low: 96h:33m: 13\n  -Bulk: 89h:6m: 5\n  -: 3743h:32m: 1\nTOP 5 in Process:\nStatus\nNo\nSuspend Subscriber 25\nOption 8\nUnsuspend Subscriber 8\nNetwork Service 6\nBroadband Options 5\nEvent types:\nStatus\nNo\nOthers (0 types) -\nItems processed last hour: Graph\nStatus\nNo\n%\nProcessed successfully 44908 -3.12%\nPostponed 4925 161.83%\nInitial Condition Incorrect 1006 -18.08%\nNeeds Detailed Checking 25 4.17%\nDatabase Exception 5 25%\nCancelled 2 0%\nPostponed Moved to another Change 1 0%\nItems processed today:\nStatus\nNo\n%\nProcessed successfully 1348514 83.49%\nPostponed 212260 13.14%\nInitial Condition Incorrect 53829 3.33%\nNeeds Detailed Checking 354 0.02%\nDatabase Exception 64 0%\nPostponed Moved to another Change 42 0%\nException Checking Jits 28 0%\nFailed 3 0%\nCancelled 2 0%\nEPOS status: Graph\nStatus\nNo\nWaiting for Confirmation 1\nIn Process 3\nExecuted 324\nProcessed but Needs Checking 4\nNew 43\nInitial condition incorrect 10\nEvents Waiting 4 Jupiter:\nPriority\nNo\nNo matching records found\nCando Flags:\nFlag\nStatus\nAction\nOTGLIVE UP\nUP\nOTGTURBO UP\nUP\nATT_Atlas UP\nUP\nATT_Cronos UP\nUP\nATT_Orfeu UP\nUP\nJUPITER LIVE\nLIVE\nATT_Sisif UP\nUP\nATT_Priam DOWN\nDOWN\nBea Queues:\nQUEUE\nNo\nAcrmChangeEventQueue_Err 42106/0\nOrangeMoney 702/0\nUnknown Queue 46/332\nSOMExec in Queues:\nQueue\nNo\nInnorthExecutor 9\nVoicemailExecutor 18\nSdmExecutor 13\nRedisQueues:\nQueue\nNo\nTkrJitReader 88\nInfranetJitReader 44\nWfmJitReader 16\nVoiceMailMavenirJitReader 15\nNicmJitReader_vhbb 12\nDeviceInventoryJitReader 12\nFomJitReader 6\nTopic Queues:\nQueue\nNo\nInvRemTopic -10000\nvoyagerTopic 0\nORO_DWH_PROCESSING 0\nSimartisKafkaListener 0\nRoamingWelcomeSMSKafkaListener 0\nJup Connectors:\nAction\nSTOP JupConn 1\nSTOP JupConn 2\nSTOP JupConn 3\nSTART JupConn 1\nSTART JupConn 2\nSTART JupConn 3', 'In process:\nStatus\nNo\nChanges in use: 74\nChanges in Process: 74\n  -Urgent: 294h:20m: 1\n  -High: 533h:14m: 12\n  -Medium: 1228h:3m: 40\n  -Low: 96h:33m: 13\n  -Bulk: 89h:6m: 5\n  -: 3743h:32m: 1\nTOP 5 in Process:\nStatus\nNo\nSuspend Subscriber 25\nOption 8\nUnsuspend Subscriber 8\nNetwork Service 6\nBroadband Options 5\nEvent types:\nStatus\nNo\nOthers (0 types) -', 'Changes in use: 74\nChanges in Process: 74\n  -Urgent: 294h:20m: 1\n  -High: 533h:14m: 12\n  -Medium: 1228h:3m: 40\n  -Low: 96h:33m: 13\n  -Bulk: 89h:6m: 5\n  -: 3743h:32m: 1', '', 'Suspend Subscriber 25\nOption 8\nUnsuspend Subscriber 8\nNetwork Service 6\nBroadband Options 5', '', 'Others (0 types) -', '', 'Items processed last hour: Graph\nStatus\nNo\n%\nProcessed successfully 44908 -3.12%\nPostponed 4925 161.83%\nInitial Condition Incorrect 1006 -18.08%\nNeeds Detailed Checking 25 4.17%\nDatabase Exception 5 25%\nCancelled 2 0%\nPostponed Moved to another Change 1 0%\nItems processed today:\nStatus\nNo\n%\nProcessed successfully 1348514 83.49%\nPostponed 212260 13.14%\nInitial Condition Incorrect 53829 3.33%\nNeeds Detailed Checking 354 0.02%\nDatabase Exception 64 0%\nPostponed Moved to another Change 42 0%\nException Checking Jits 28 0%\nFailed 3 0%\nCancelled 2 0%\nEPOS status: Graph\nStatus\nNo\nWaiting for Confirmation 1\nIn Process 3\nExecuted 324\nProcessed but Needs Checking 4\nNew 43\nInitial condition incorrect 10', 'Processed successfully 44908 -3.12%\nPostponed 4925 161.83%\nInitial Condition Incorrect 1006 -18.08%\nNeeds Detailed Checking 25 4.17%\nDatabase Exception 5 25%\nCancelled 2 0%\nPostponed Moved to another Change 1 0%', '', 'Processed successfully 1348514 83.49%\nPostponed 212260 13.14%\nInitial Condition Incorrect 53829 3.33%\nNeeds Detailed Checking 354 0.02%\nDatabase Exception 64 0%\nPostponed Moved to another Change 42 0%\nException Checking Jits 28 0%\nFailed 3 0%\nCancelled 2 0%', '', 'Waiting for Confirmation 1\nIn Process 3\nExecuted 324\nProcessed but Needs Checking 4\nNew 43\nInitial condition incorrect 10', '', 'Events Waiting 4 Jupiter:\nPriority\nNo\nNo matching records found\nCando Flags:\nFlag\nStatus\nAction\nOTGLIVE UP\nUP\nOTGTURBO UP\nUP\nATT_Atlas UP\nUP\nATT_Cronos UP\nUP\nATT_Orfeu UP\nUP\nJUPITER LIVE\nLIVE\nATT_Sisif UP\nUP\nATT_Priam DOWN\nDOWN\nBea Queues:\nQUEUE\nNo\nAcrmChangeEventQueue_Err 42106/0\nOrangeMoney 702/0\nUnknown Queue 46/332\nSOMExec in Queues:\nQueue\nNo\nInnorthExecutor 9\nVoicemailExecutor 18\nSdmExecutor 13', 'No matching records found', '', 'OTGLIVE UP\nUP\nOTGTURBO UP\nUP\nATT_Atlas UP\nUP\nATT_Cronos UP\nUP\nATT_Orfeu UP\nUP\nJUPITER LIVE\nLIVE\nATT_Sisif UP\nUP\nATT_Priam DOWN\nDOWN', '', 'Bea Queues:\nQUEUE\nNo\nAcrmChangeEventQueue_Err 42106/0\nOrangeMoney 702/0\nUnknown Queue 46/332', 'AcrmChangeEventQueue_Err 42106/0\nOrangeMoney 702/0\nUnknown Queue 46/332', '', 'InnorthExecutor 9\nVoicemailExecutor 18\nSdmExecutor 13', '', 'RedisQueues:\nQueue\nNo\nTkrJitReader 88\nInfranetJitReader 44\nWfmJitReader 16\nVoiceMailMavenirJitReader 15\nNicmJitReader_vhbb 12\nDeviceInventoryJitReader 12\nFomJitReader 6', 'TkrJitReader 88\nInfranetJitReader 44\nWfmJitReader 16\nVoiceMailMavenirJitReader 15\nNicmJitReader_vhbb 12\nDeviceInventoryJitReader 12\nFomJitReader 6', '', 'Topic Queues:\nQueue\nNo\nInvRemTopic -10000\nvoyagerTopic 0\nORO_DWH_PROCESSING 0\nSimartisKafkaListener 0\nRoamingWelcomeSMSKafkaListener 0', 'InvRemTopic -10000\nvoyagerTopic 0\nORO_DWH_PROCESSING 0\nSimartisKafkaListener 0\nRoamingWelcomeSMSKafkaListener 0', '', 'Jup Connectors:\nAction\nSTOP JupConn 1\nSTOP JupConn 2\nSTOP JupConn 3\nSTART JupConn 1\nSTART JupConn 2\nSTART JupConn 3', 'STOP JupConn 1\nSTOP JupConn 2\nSTOP JupConn 3\nSTART JupConn 1\nSTART JupConn 2\nSTART JupConn 3', '']

        dashboard_data_joined = '\n'.join(dashboard_data)  # Make the list a very long string
        # print(dashboard_data_joined)

        # Search on all http page, based on CRM_KEYS_LIST #####################################################################
        cdr_found_data_dict = {}
        for crm_key in CRM_KEYS_LIST:
            cdr_found_data_dict_value = search_for_key_value(key_name=f'{crm_key}', full_element=dashboard_data_joined)
            if len(cdr_found_data_dict_value) == NUMBER_OF_VALUES: #NUMBER_OF_VALUES:  # Number of values after the key
                cdr_found_data_dict[crm_key] = cdr_found_data_dict_value

        driver.quit()
        del driver

        print(cdr_found_data_dict)
        cdr_found_data_dict_formatted = {'_'.join(key.split()): int(value[0].split(' ', 1)[1]) for (key, value) in cdr_found_data_dict.items()}
        print(cdr_found_data_dict_formatted)

        #return cdr_found_data_dict
        return cdr_found_data_dict_formatted
    except KeyboardInterrupt:
        driver.close()
        driver.quit()
        driver.stop_client()
        print('\nChromium driver closed.')
        print('Please wait 5 seconds ...')
        time.sleep(5)
        print('KeyboardInterrupt, Bye !')
        sys.exit(1)


class Gauger:
    def __init__(self, crm_keys_list: list, documentation='instant value from CRM CORE dashboard'):
        self.gauge_list = []
        self.data = None
        self.documentation = documentation
        self.gauge_names_list = ['_'.join(x) for x in [x.split() for x in crm_keys_list]]  # Metric must be just a word, not two

    def set_data(self):
        self.data = get_info_from_crm_dashboard()

    def get_data(self):
        return self.data

    def set_gauge_list(self):
        for gauge_name in self.gauge_names_list:
            self.gauge_list.append(Gauge(name=gauge_name, documentation=self.documentation))

    def get_gauge_list(self) -> list:
        return self.gauge_list


if __name__ == '__main__':
    my_gauger = Gauger(CRM_KEYS_LIST)
    my_gauger.set_gauge_list()

    start_http_server(8008)

    while True:
        my_gauger.set_data()
        gauger_data = my_gauger.get_data()
        metric_list = my_gauger.get_gauge_list()

        for metric in metric_list:
            for key, value in gauger_data.items():
                if metric._name == key:
                    metric.set(value)

        time.sleep(2)

