
import glob 
import os
import codecs
import logging
import zipfile

import requests 
import urllib
from urllib import parse

import re

import hashlib
import hmac
import base64

import datetime

import openpyxl 

import json

from sshtunnel import SSHTunnelForwarder

import psycopg2

#
# env  info
#

home_dir = "D:\\nipa_cf_script"

api_host = "https://api.ucloudbiz.olleh.com"
path = "/gserver/v1/client/api"; 

# admin gcloud key
apiKey = "-I56y9-Chy83Vq6UORvBaRAsIur5A7b58xTId4mMv2HjESyqEpNP4gipclAqPfQOnM2xiS_oFBWigq62ayo09A";    
secretKey = "nqyX-NvSfs4AFMcQevDMp5kv19IMHZ02sbgWPqLbudov6OJw7pSljucflp_O4CZ5UuHj5dx0LLg5BvL-6bOqzA";



# log

logging.basicConfig(filename='%s\\check_gcloud.log'%(home_dir),
		    level=logging.INFO,
		    format='%(asctime)s %(name)-12s %(message)s',
                    datefmt='%m-%d %H:%M')

logger = logging.getLogger("")


#
# functions
#

def check_vms(key_list):
  logger = logging.getLogger("check_vms")
  try:

    vm_count_list = [];
    total_vms = 0;
    checked_company = 0;


    for key in key_list  :
        print('name : %s' % (key['name']))
        print('company : %s' % (key['company']))
        print('api_key : %s' % (key['api_key']))
        print('secret_key : %s' % (key['secret_key']))

        if key['api_key'] is None or key['secret_key'] is None :
            logger.info("%s has no key to access" %(key['name']));
            continue;


        logger.info(" %s of %s - start request  " %(key['name'],key['company']))
        resp_text, resp_status = request_vm(key['api_key'],key['secret_key']);
        logger.info(" %s of %s - end request  " %(key['name'],key['company']))

        if resp_status is not 200 :
            logger.info("%s has invalid response" %(key['name']));
            continue;
        
        checked_company += 1;

        print(resp_text);
        # json parsing
        data = json.loads(resp_text);
       

        if len(data['listvirtualmachinesresponse'])==0 or data['listvirtualmachinesresponse']['count']=='0':
            print("no vm");
        else :
            total_vms += data['listvirtualmachinesresponse']['count'];
            vm_count = { 'name' :  key['name'],
                    'company' : key['company'],
                    'count' : data['listvirtualmachinesresponse']['count']
                    };
            vm_count_list.append(vm_count);
            
        writeResultFile(checked_company,total_vms,vm_count_list);        

  except Exception as ex:
      logger.info("Check VMs 실패: %s " % ex) 

def request_vm(api_key,secret_key) :
  logger = logging.getLogger("request_vm_list")
  try:

# url param 

    params = { 'command' : 'listVirtualMachines',
               'response' : 'json' 
              }

    logger.info("api_key: \"%s\"" % api_key);
    logger.info("security_key: \"%s\"" % secret_key);

    query = composeQueryString(params,api_key,secret_key);

# url
    url = api_host + path + "?"+ query;

    logger.info("request :\n%s" % url);

    resp = requests.get(url)

    logger.info("response status: %d" % resp.status_code);
#    logger.info("response headers:\n%s" % resp.headers);
    logger.info("response body:\n%s" % resp.text);

    return resp.text, resp.status_code;

  except Exception as ex:
      logger.info("VM list 획득 실패: %s " % ex) 

def request_vm_list() :
  logger = logging.getLogger("request_vm_list")
  try:

# url param 

    params = { 'command' : 'listVirtualMachines',
               'response' : 'json' 
              }

    query = composeQueryString(params,apiKey,secretKey);

# url
    url = api_host + path + "?"+ query;

    logger.info("request :\n%s" % url);

    resp = requests.get(url)

    logger.info("response status: %d" % resp.status_code);
    logger.info("response headers:\n%s" % resp.headers);
    logger.info("response body:\n%s" % resp.text);

#    writeFile(resp.text);


# json parsing
    data = json.loads(resp.text);
    print(data['listvirtualmachinesresponse']['count']);




  except Exception as ex:
      logger.info("VM list 획득 실패: %s " % ex) 


def request_account_list() :
  logger = logging.getLogger("request_account_list")
  try:

# url param 

    params = { 'command' : 'listAccounts',
               'listall' : 'false',
               'response' : 'json', 
            #   'response' : 'xml',
              }

    query = composeQueryString(params,apiKey,secretKey);

# url
    url = api_host + path + "?"+ query;

    logger.info("request :\n%s" % url);

    resp = requests.get(url)

    logger.info("response status: %d" % resp.status_code);
    logger.info("response headers:\n%s" % resp.headers);
    logger.info("response body:\n%s" % resp.text);

    writeFile(resp.text);

  except Exception as ex:
      logger.info("account list 획득 실패: %s " % ex) 


def check_paasta_bbs() :
  logger = logging.getLogger("check_paasta_bbs")
  try:
    print("ssh tunnel");

    server = SSHTunnelForwarder(
        ('203.245.1.66', 22),
        ssh_username="ubuntu",
        ssh_pkey="nipa_master_rsa_key",
        remote_bind_address=('10.10.3.21', 5524),
        local_bind_address=('0.0.0.0', 5524)
    );

    server.start();

    print(server.local_bind_port);

    #jcloud database via ssh tunneling
    jcloud_database = "host='127.0.0.1' port='5524' dbname='portaldb' user='portaladmin' password='admin'"

    conn = psycopg2.connect(jcloud_database);
  
    
    # 커서를 연다
    cursor = conn.cursor()
 
    # SELECT명령을 실행해서 결과를 얻는다
    cursor.execute("select no,title,user_id,created from question where status != 'answered';") 

    print(cursor.rowcount);


    writeAppend("-------------------------------\n");
    if cursor.rowcount is 0 :
        writeAppend("no paasta question\n");
    else :
        writeAppend("unanswered paasta questions : %d \n"%(cursor.rowcount));
    writeAppend("\n");

    for no,title,user_id,created in cursor.fetchall():
        writeAppend("%s %s question : \"%s\" at %s \n"%(no,user_id,title,created));
    

    conn.close();

    server.stop();

      
  except Exception as ex:
      logger.info("paasta bbs 획득 실패: %s " % ex) 

# APIs

def writeResultFile(checked_company,total_vms,vm_count_list) :        
  logger = logging.getLogger("writeResultFile")
  try:
    # 파일이름 + 날짜 

    postfix = datetime.datetime.today().strftime('%Y%m%d')

    filename = home_dir + "\\gcloud_vm_paasta_question_"+postfix+".txt";

    print(filename);

    f = open(filename,"w+");

    f.write("gcloud vm counting report\n")
    f.write("\n")
    f.write("checked companies : %d / 28 \n"%(checked_company))
    f.write("\n")
    f.write("total vms : %d\n"%(total_vms))
    f.write("\n")

    for vm_count in vm_count_list  :
        f.write("%s %s vms : %s"%(vm_count['name'],vm_count['company'],vm_count['count']))

    f.write("\n")
    f.close();

  except Exception as ex:
      logger.info("write file 실패: %s " % ex) 

def writeAppend(text) :        
  logger = logging.getLogger("writeAppend")
  try:

    # 파일이름 + 날짜 

    postfix = datetime.datetime.today().strftime('%Y%m%d')

    filename = home_dir + "\\gcloud_vm_paasta_question_"+postfix+".txt";

    f = open(filename,"a+");

    f.write(text);

    f.close();

  except Exception as ex:
      logger.info("write append 실패: %s " % ex) 

def writeFile(text) :
  logger = logging.getLogger("writeFile")
  try:
    # 파일이름 + 날짜 

    postfix = datetime.datetime.today().strftime('%Y%m%d')

    filename = home_dir + "\\gcloud_vm_list_"+postfix+".xml";

    print(filename);

    f = open(filename,"w+");

    f.write(text);

    f.close();

  except Exception as ex:
      logger.info("write file 실패: %s " % ex) 


def composeQueryString(params,apiKey,secretKey) :
  logger = logging.getLogger("composeQueryString")
  try:

    params_with_apikey = params.copy();

    # add apiKey
    params_with_apikey['apiKey'] = apiKey;

    query_string = "" ;

    # make query_string for signature
    # after sort by name
    for name,value in sorted(params_with_apikey.items()) :
       
       value = urlSafe(value);

       if query_string is "":
           query_string = name + "=" + value;
       else :
           query_string = query_string + "&" + name + "=" + value;

    # make signature
  
    key = secretKey.encode("UTF-8");
    msg = query_string.lower().encode("UTF-8");

    signature1 = hmac.new(key, msg=msg, digestmod=hashlib.sha1).digest()

    signature2 = base64.b64encode(signature1)   

    signature = str(signature2, 'UTF-8');

    # make query string

    query_string = "" ;

    for name,value in params.items() :
       value = urlSafe(value);

       if query_string is "":
           query_string = name + "=" + value;
       else :
           query_string = query_string + "&" + name + "=" + value;

    
    query_string = query_string + "&apiKey=" + urlSafe(apiKey);
    query_string = query_string + "&signature=" + urlSafe(signature);

    return query_string; 

  except Exception as ex:
      logger.info("compose query 실패: %s " % ex) 

def urlSafe(value) :
  logger = logging.getLogger("urlSafe")
  try:

    encoding = parse.quote(value, encoding='UTF-8');

    out = re.sub("\\+", "%20", encoding);

    out = out.replace("/","%2F");

    return out;
  except Exception as ex:
      logger.info("url encoding 실패: %s " % ex) 

def readExcel() :
  logger = logging.getLogger("readExcel")
  try:
    key_list = []

    excel_document = openpyxl.load_workbook('KT 계정 api키값.xlsx')

    sheet = excel_document['KT 계정']

    for i in range(0,28) :
        name_cell_index = 'A' + str(2+i*3);
        company_cell_index = 'B' + str(2+i*3);
        api_key_cell_index = 'C' + str(2+i*3+1);
        security_key_cell_index = 'C' + str(2+i*3+2);

        key = { 'name' :  sheet[name_cell_index].value,
            'company' : sheet[company_cell_index].value,
            'api_key' : sheet[api_key_cell_index].value,
            'secret_key' : sheet[security_key_cell_index].value }
        key_list.append(key);


    return key_list;

  except Exception as ex:
      logger.info("readExcel 실패: %s " % ex) 

#
# main 
#

logger.info("start check_gcloud_paasta")

key_list = readExcel();
check_vms(key_list);

#request_vm_list()
#request_account_list()

check_paasta_bbs();



logger.info("end check_gcloud_paasta")

