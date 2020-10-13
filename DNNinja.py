"""
This script will report on the status of Directory Numbers configured in CUCM by looking at the Associated Devices and writing the results to a CSV in the local directory.
Written By Michael Hagans Feb 2020
"""

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault
import getpass
import sys
from lxml import etree as ET
import csv
import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def soapinfo(CUCM_URL,USERNAME,PASSWD, WSDL_URL):
    #Create SOAP Session
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(USERNAME, PASSWD)
    transport = Transport(session=session, timeout=10, cache=SqliteCache())
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(WSDL_URL, settings=settings, transport=transport)
    service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
    return service

def LineGrabber(number, ip, USERNAME, PASSWD):
    CUCM_URL = f'https://{ip}:8443/axl/'
    service = soapinfo(CUCM_URL, USERNAME, PASSWD, WSDL_URL)
    try:
        phone_resp = service.getLine(**{
                'pattern': number,
                'routePartitionName':'ClusterDN-PT'
        })
        if phone_resp['return']['line']['associatedDevices'] is not None:
            print(f'Line {number} is being used!!!\n')
            return number, f'Line {number} is being used!!!'
        else:
            print(f'Line {number} is free; no associated devices.\n') 
            return number, f'Line {number} is free; no associated devices.'
    except Fault as err:
        if 'The specified Line was not found' in str(err):
            print(f'Line {number} is free. This line is not yet configured in CUCM.\n')
            return number, f'Line {number} is free. This line is not configured in CUCM.'
        elif 'Unknown fault occured' in str(err):
            print('\nPlease check your credentials or if you have AXL permissions.')
            return number, 'Please check your credentials or if you have AXL permissions.'
        else:
            raise

if __name__ == "__main__":
    print('\n############## start of script ##########################')
    print('\nWelcome to the DN Ninja.')
    print('\nThis tool will check the status for a range of numbers configured in CUCM.')
    print('The results will be displayed on the screen and be written to a csv file for your viewing pleasure...\n')
    firstNum = input('Tell me the first number in the range: ')
    lastNum = input('Tell me the last number in the range: ')
    ip = input('What is the IP address to the Publisher: ')
    print('\nTime to authenticate')
    USERNAME = input('Enter your username: ')
    PASSWD = getpass.getpass(stream=sys.stderr)
    WSDL_URL = 'AXLAPI.wsdl'
    with open('NumberInventory.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        try:
            for number in range(int(firstNum),int(lastNum)+1):
                Status = LineGrabber(number, ip, USERNAME, PASSWD)
                writer.writerow(Status)
                if 'check your credentials' in Status[1]:
                    break
            print('\nResults have been written to NumberInventory.csv. This file can be found in the same directory you ran this script from.\n')
            print('\n############## end of script ##########################')
        except:
            raise





