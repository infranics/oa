
import requests
import json
import logging
import time

# env info

token_api_endpoint = "https://api.ucloudbiz.olleh.com/gd1/identity/auth/tokens"
flavor_api_endpoint = "https://api.ucloudbiz.olleh.com/gd1/server/flavors"
image_api_endpoint = "https://api.ucloudbiz.olleh.com/gd1/image/images"
network_api_endpoint = "https://api.ucloudbiz.olleh.com/gd1/nc/IpAddress"
server_api_endpoint = "https://api.ucloudbiz.olleh.com/gd1/server/servers"

# log
logging.basicConfig(filename='.\\create_prd-gitlab.log',
                    level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(message)s')

logging.Formatter(datefmt='%m-%d,%H:%M:%S.%f')

#
# functions
#

# get token

token_body = {
    "auth": {
        "identity": {
            "methods": ["password"], 
            "password": {
                    "user": {
                        "domain": {"id": "default"}, 
                        "name": "aaasaasify@systeer.com", 
                        "password": "aaaaSysmaster77!!"
                    }
            }
        }, 
        "scope": {
                "project": {
                    "domain": {"id": "default"}, 
                    "name": "aaasaasify@systeer.com"
                }
        }
    }
}    

def get_token(username, password):
    logger = logging.getLogger("get_token")
    try:
        token_headers = {'Content-Type': 'application/json; charset=utf-8'}

        token_body['auth']['identity']['password']['user']['name'] = username       
        token_body['auth']['identity']['password']['user']['password'] = password      
        token_body['auth']['scope']['project']['name'] = username        


        logger.info("get_token request header:\n%s" % token_headers)
        logger.info("get_token request body:\n%s" % token_body)
       
        resp = requests.post(token_api_endpoint, headers=token_headers, data=json.dumps(token_body))

        # 결과
        logger.info("get_token response status: %d" % resp.status_code);
        logger.info("get_token response headers:\n%s" % resp.headers);
        logger.info("get_token response body:\n%s" % resp.text);
        logger.info("get_token token:\n%s" % resp.headers['X-Subject-Token']);


        # token이 header에 반환된다, token은 1시간 유효하다 
        return resp.headers['X-Subject-Token']

    except Exception as ex:
        logger.info("get_token 실패: %s " % ex) 

def get_flavors(token):
    logger = logging.getLogger("get_flavors")
    try:

        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }


        logger.info("get_flavors request header:\n%s" % token_headers)

        resp = requests.get(flavor_api_endpoint, headers=token_headers)
        
        # 결과
        logger.info("get_flavors response status: %d" % resp.status_code);
        logger.info("get_flavors response headers:\n%s" % resp.headers);
        logger.info("get_flavors response body:\n%s" % json.dumps(resp.text,indent=2));

    except Exception as ex:
        logger.info("get_flavors 실패: %s " % ex) 


def get_images(token):
    logger = logging.getLogger("get_images")
    try:

        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }


        logger.info("get_images request header:\n%s" % token_headers)

        resp = requests.get(image_api_endpoint, headers=token_headers)
        
        # 결과
        logger.info("get_images response status: %d" % resp.status_code);
        logger.info("get_images response headers:\n%s" % resp.headers);
        logger.info("get_images response body:\n%s" % resp.text);

    except Exception as ex:
        logger.info("get_images 실패: %s " % ex) 

def get_network(token):
    logger = logging.getLogger("get_network")
    try:

        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }


        logger.info("get_network request header:\n%s" % token_headers)

        resp = requests.get(network_api_endpoint, headers=token_headers)
        
        # 결과
        logger.info("get_network response status: %d" % resp.status_code);
        logger.info("get_network response headers:\n%s" % resp.headers);
        logger.info("get_network response body:\n%s" % resp.text);

    except Exception as ex:
        logger.info("get_network 실패: %s " % ex) 


# server list 갯수 10개
servers_body = {
        "limit" : 10
}    

def get_servers(token):
    logger = logging.getLogger("get_servers")
    try:

        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }


        logger.info("get_servers request header:\n%s" % token_headers)

        resp = requests.get(server_api_endpoint, headers=token_headers, data=json.dumps(servers_body))
        
        # 결과
        logger.info("get_servers response status: %d" % resp.status_code);
        logger.info("get_servers response headers:\n%s" % resp.headers);
        logger.info("get_servers response body:\n%s" % resp.text);

    except Exception as ex:
        logger.info("get_servers 실패: %s " % ex) 

# create vm
server_body = {
  "server": {
    "name": "nodedriver",
    "key_name": "SaaSifyKey",
    "flavorRef": "7f56ce4a-5b56-4b53-be63-f4dda5216b63",
    "availability_zone": "DX-M1",
    "networks": [
      {
        "uuid": "a3f25a44-efaa-47d7-bdd4-b78032662d68"
      }
    ],
    "block_device_mapping_v2": [
      {
        "destination_type": "volume",
        "boot_index": "0",
        "source_type": "image",
        "volume_size": 50,
        "uuid": "84a10047-cbd8-4fb3-a743-85600a7b6961"
      }
    ]
  }
}

def create_sample_server(token):
    logger = logging.getLogger("create_sample_server")
    try:
        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }

        logger.info("create_sample_server request header:\n%s" % token_headers)
        logger.info("create_sample_server request body:\n%s" % server_body)
       
        resp = requests.post(server_api_endpoint, headers=token_headers, data=json.dumps(server_body))

        # 결과
        logger.info("create_sample_server response status: %d" % resp.status_code);
        logger.info("create_sample_server response headers:\n%s" % resp.headers);
        logger.info("create_sample_server response body:\n%s" % resp.text);

    except Exception as ex:
        logger.info("create_sample_server 실패: %s " % ex) 


def create_server(token, server_name, key_name, flavor_id, zone_name,  network_id, image_id):
    logger = logging.getLogger("create_server")
    try:
        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }
        server_body = {
  "server": {
    "name": server_name,
    "key_name": key_name,
    "flavorRef": flavor_id,
    "availability_zone": zone_name,
    "networks": [
      {
        "uuid": network_id 
      }
    ],
    "block_device_mapping_v2": [
      {
        "destination_type": "volume",
        "boot_index": "0",
        "source_type": "image",
        "volume_size": 50,
        "uuid": image_id 
      }
    ]
  }
}

        logger.info("create_server request header:\n%s" % token_headers)
        logger.info("create_server request body:\n%s" % server_body)
       
        resp = requests.post(server_api_endpoint, headers=token_headers, data=json.dumps(server_body))

        # 결과
        logger.info("create_server response status: %d" % resp.status_code);
        logger.info("create_server response headers:\n%s" % resp.headers);
        logger.info("create_server response body:\n%s" % resp.text);

        # server id
        data = json.loads(resp.text)
        logger.info("create_server server_Id: %s" %  data['server']['id']);
        return  data['server']['id']
    except Exception as ex:
        logger.info("create_server 실패: %s " % ex) 


def delete_server(token, server_id):
    logger = logging.getLogger("delete_server")
    try:


        delete_url = server_api_endpoint + '/' + server_id

        token_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'X-Auth-Token': token }

        logger.info("delete_server request header:\n%s" % token_headers)
       
        resp = requests.delete(delete_url, headers=token_headers)

        # 결과
        logger.info("delete_server response status: %d" % resp.status_code);
        logger.info("delete_server response headers:\n%s" % resp.headers);
        logger.info("delete_server response body:\n%s" % resp.text);

    except Exception as ex:
        logger.info("delete_server 실패: %s " % ex) 


#
# my env
#

my_username = "nanet@systeer.com"
my_password = "tltmxldj1!@#"

my_server_name = "prd-gitlab"
my_key_name = "nanet-keypair"
#my_flavor_id = "cc39e701-1d52-475d-b4cb-5b61f2216239"   # 2x4.itl
my_flavor_id = "76a41bb5-9949-478b-8f89-ed9d89848154" # 4x8.itl 
my_zone_name = "DX-G"
my_network_id = "100d31da-875c-47e2-99a9-f7b3cd6dde66"  # DMZ
#my_network_id = "3651c07f-21dd-46de-be0f-b086ddf0ef43"  # private

my_image_id = "5b55125e-53ce-4a19-981f-2375ab4e4523"    # rocky-9.2-64bit-231023 
#my_image_id = "6e21cd06-a05a-4801-bc58-ce15c96389e1"    # rocky-8.8-64bit-231023


#
# main
#
logger = logging.getLogger("main")
logging.info('start gitlab')


my_token = get_token(my_username, my_password)

#get_flavors(my_token)
#get_images(my_token)
#get_network(my_token)
#get_servers(my_token)
#create_sample_server(my_token)

server_id = create_server(my_token, "prd-gitlab", my_key_name, my_flavor_id, my_zone_name, my_network_id, my_image_id )

#time.sleep(10)

#server_id = create_server(my_token, "testvm02", my_key_name, my_flavor_id, my_zone_name, my_network_id, my_image_id )

#delete_server(my_token, "907c3554-cae0-4419-882d-665e75ce9e6f");
#time.sleep(10)
#delete_server(my_token, "89824ea4-9d87-40bb-98ab-c791c5b6eedd");

logging.info('end prd-gitlab')

