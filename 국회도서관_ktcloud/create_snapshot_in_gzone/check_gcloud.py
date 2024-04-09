
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

import json
import time

#
# env  info
#

home_dir = "D:\\2024년\\국회도서관\\python"

api_host = "https://api.ucloudbiz.olleh.com"
path = "/gserver/v1/client/api"; 

apiKey = "l8rCH5D31Q8xOwTzoC1fFs2jq9nUtoM4ReZ-VinfnxuSUdu9lDHvEGcrstEF5YYSAXAUnFLcdgpwOfO7LRvXPQ";
secretKey =  "--ei9xhdYhYOddptuCSrdHWb1PHeIqMcFDRgjqxSZgnUwGznbN-VOe_mkDBV4NdEgafWeVe8VD_wz2e3jrrdTQ";

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

        if resp_status != 200 :
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




# APIs

def writeResultFile(checked_company,total_vms,vm_count_list) :        
  logger = logging.getLogger("writeResultFile")
  try:
    # 파일이름 + 날짜 

    postfix = datetime.datetime.today().strftime('%Y%m%d')

    filename = home_dir + "\\gcloud_vm_list_"+postfix+".txt";

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

       if query_string == "":
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

       if query_string == "":
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

##



def request_snapshot_list() :
  logger = logging.getLogger("request_snapshot_list")
  try:

# url param 

    params = { 'command' : 'listSnapshots',
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

# json parsing
    data = json.loads(resp.text);
    print(data['listsnapshotsresponse']['count']);


  except Exception as ex:
      logger.info("snapshot list 획득 실패: %s " % ex) 



def create_snapshot(volumeid) :
  logger = logging.getLogger("create_snapshot")
  try:

# url param 

    params = { 'command' : 'createSnapshot',
               'volumeid' : volumeid,
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

# json parsing
    data = json.loads(resp.text);
    print(data['createsnapshotresponse']);


  except Exception as ex:
      logger.info("create_snapshot 실패: %s " % ex) 


##




#
# main 
#

logger.info("start check_gcloud")

#request_vm_list()

#request_account_list()

#request_snapshot_list()

#create_snapshot('fffb0434-97ed-4414-8ac7-0a0664aaa94f');    # prd-db-02 
#time.sleep(3)

#create_snapshot('50df6caf-a21b-486c-a34d-b4c6d34de458');    # prd-db-02 
#time.sleep(3)

create_snapshot('37a4e7b5-8b56-407a-8109-04c3233a18f3');    # prd-db-02 
time.sleep(3)
create_snapshot('ec2adab8-8b2e-4b7d-a19f-afaa76a278d8');    # prd-db-02 
time.sleep(3)
create_snapshot('fa0b037f-79e4-464e-b421-c500ca162352');    # prd-db-02 
time.sleep(3)
create_snapshot('2a36a4f9-f05c-4b31-a160-486d6f5613fe');    # prd-db-02 
time.sleep(3)
create_snapshot('1b945514-4d3c-4a44-a56e-a325719d5637');    # prd-db-02 
time.sleep(3)
create_snapshot('e3a6d859-0b5f-45f2-869c-2518895cccbf');    # prd-db-02 
time.sleep(3)
create_snapshot('4e2d2211-6599-47da-8bdf-a4824a09472e');    # prd-db-02 
time.sleep(3)
create_snapshot('774dcce9-ab3a-4d40-8116-bd26335266bb');    # prd-db-02 
time.sleep(3)
create_snapshot('79e25066-e36b-4973-a66f-cafc2595170c');    # prd-db-02 
time.sleep(3)
create_snapshot('b246670d-c59f-4e33-86ed-1d4777735d6a');    # prd-db-02 
time.sleep(3)
create_snapshot('8b5c3b9c-6cf3-4c97-a0a8-ffabcfdc0ebc');    # prd-db-02 
time.sleep(3)
create_snapshot('0d280a9a-0016-4330-bfa3-6fbd285d7fc6');    # prd-db-02 
time.sleep(3)
create_snapshot('91d25d0b-5abe-4d80-a06f-13573e6e9131');    # prd-db-02 
time.sleep(3)
create_snapshot('72e47097-a402-4aea-bc82-e78fb724490a');    # prd-db-02 
time.sleep(3)


#create_snapshot('ebbbf0eb-9e7f-4ed1-a916-eb021ada7a9e');    # prd-lod-03 

logger.info("end check_gcloud")

