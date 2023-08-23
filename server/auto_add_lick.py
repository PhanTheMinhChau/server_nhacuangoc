import re
from threading import Thread
import requests
import uuid
import subprocess
import undetected_chromedriver as uc
import time

se = requests.Session()
se.cookies.set("shopee_token", 'fqpX6+gfGVnaT3KkeKUlToHwomLszSXIV0seSqfyEOdRRXee1UFTVPBitotVZbTZ', domain=".shopee.vn")
se.get("https://shopee.vn/api/v4/account/basic/get_account_info").json()
driver = uc.Chrome(headless=False,use_subprocess=False)
driver.get("https://shopee.vn/")
driver.execute_script("document.cookie = 'SPC_EC="+se.cookies.get_dict()["SPC_EC"]+"'")
driver.get("https://shopee.vn/")
driver.get("https://live.shopee.vn/pc/setup")

#a = input("Thiết lập xong?")

au = se.post("https://banhang.shopee.vn/webchat/api/coreapi/v1.2/mini/login").json()["token"]
pattern = r'(https://shopee\.vn/p\S*|https://shp\.ee\S*|https://shope.ee/\S*|https://shopee\.vn/.*?\.\d+\.\d+\?\S*)'
ss = str(se.get("https://live.shopee.vn/webapi/v1/session").json()["data"]["session"]["session_id"])
requests.packages.urllib3.disable_warnings()


def put_it(url, data):
  #se.put(url, data=data, verify=False).json()
  script = """
function sendPutRequestWithXHR(ss, data) {
  const url = `"""+url+"""`;
  const requestData = JSON.stringify("""+data+""");
  return new Promise(function(resolve, reject) {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const responseData = JSON.parse(xhr.responseText);
          resolve(responseData);
        } catch (error) {
          reject(error);
        }
      } else {
        reject(new Error(`Request failed with status ${xhr.status}`));
      }
    };
    xhr.onerror = function() {
      reject(new Error("Network error"));
    };
    xhr.send(requestData);
  });
}
sendPutRequestWithXHR(4, 4)
"""
  driver.execute_script(script)


def remove_duplicates(lst):
    tuple_list = [tuple(sub_list) for sub_list in lst]
    unique_tuples = set(tuple_list)
    unique_list = [list(sub_tuple) for sub_tuple in unique_tuples]
    return unique_list


def read(last_mess_id, shop_id, id):
  se.put(f"https://banhang.shopee.vn/webchat/api/v1.2/conversations/{id}/read", headers={'Authorization': f'Bearer {au}'},
       data ='{"last_read_message_id":"'+str(last_mess_id)+'","shop_id":'+str(shop_id)+'}', verify=False)


def unread(shop_id, id):
  se.put(f"https://banhang.shopee.vn/webchat/api/v1.2/conversations/{id}/unread", headers={'Authorization': f'Bearer {au}'},
       data ='{"shop_id":'+str(shop_id)+'}', verify=False)


def send_mess(claimer, text, id):
  try:
    requests.post("https://banhang.shopee.vn/webchat/api/v1.2/messages",
                headers={'Authorization': f'Bearer {au}'},
                data = ('{"request_id":"'+str(uuid.uuid4())+'","to_id":'+str(claimer)+',"type":"text","content":{"text":"'+text+'"},"shop_id":523480043,"chat_send_option":{"force_send_cancel_order_warning":false,"comply_cancel_order_warning":false},"device_id":"383f613d-7c27-4543-8e2e-fba628c16f6c","conversation_id":"'+id+'"}').encode(),verify=False).json()
  except:
    requests.post("https://banhang.shopee.vn/webchat/api/v1.2/messages",
                headers={'Authorization': f'Bearer {au}'},
                data = ('{"request_id":"'+str(uuid.uuid4())+'","to_id":'+str(claimer)+',"type":"text","content":{"text":"'+text+'"},"shop_id":523480043,"chat_send_option":{"force_send_cancel_order_warning":false,"comply_cancel_order_warning":false},"device_id":"383f613d-7c27-4543-8e2e-fba628c16f6c","conversation_id":"'+id+'"}').encode(),verify=False).json()
    

def re_find_link(id, to_id, shop_id):
  links = []
  for i in requests.get(f'https://banhang.shopee.vn/webchat/api/v1.2/conversations/{id}/messages?offset=0&limit=20&direction=older', headers={'Authorization': f'Bearer {au}'},verify=False).json():
    try:
      if len(i["content"]['text']) > 250 and i["from_user_name"] == "ngoc.le.1301":
        continue
      if i["from_user_name"] == "ngoc.le.1301":
        break
      if i["created_timestamp"] < 1692720000 and int(time.time()) > 1692720000:
        break
      links = links + re.findall(pattern, i["content"]['text'])
    except:
      pass
  return list(set(links))
  

def find_link(id, to_id, shop_id):
  links = []
  for i in requests.get(f'https://banhang.shopee.vn/webchat/api/v1.2/conversations/{id}/messages?offset=0&limit=20&direction=older', headers={'Authorization': f'Bearer {au}'}, verify=False).json():
    try:
      if len(i["content"]['text']) > 250 and i["from_user_name"] == "ngoc.le.1301":
        continue
      if i["from_user_name"] == "ngoc.le.1301":
        break
      if i["created_timestamp"] < 1692720000 and int(time.time()) > 1692720000:
        break
      links = links + re.findall(pattern, i["content"]['text'])
    except:
      pass
  get_stt(list(set(links)), to_id, id,shop_id)

    
def extract_two_numbers_after_question_mark(link):
    pattern = r'(\d+)\.(\d+)\?'
    match = re.search(pattern, link)
    if match:
        number1 = match.group(1)
        number2 = match.group(2)
        return [number1, number2]
    else:
      return [1]-1


def extract_two_numbers_after_question_mark1(link):
    try:
      pattern = r'product/(\d+)\/(\d+)'
      match = re.search(pattern, link)
      if match:
          number1 = match.group(1)
          number2 = match.group(2)
          return [number1, number2]
      else:
        return [1]-1
    except:
      return extract_two_numbers_after_question_mark(link)


def get_stt(links, to_id, id, shop_id):
    url = f"https://live.shopee.vn/webapi/v1/session/{ss}/add_items"
    li_item = []
    text = ""
    data = {'items': []}
    for i in links:
      try:
        if i.count("shp.ee/") != 0:
          li_item.append(re.search(r'product%2F(.*?)%3F', requests.head(i).headers['location']).group(1).split("%2F"))
        elif i.count("shope.ee/") != 0:
          li_item.append(extract_two_numbers_after_question_mark1(requests.head(i).headers['location']))
        elif i.count("https://shopee.vn/product/") != 0:
          li_item.append(extract_two_numbers_after_question_mark1(i))
        else:
          li_item.append(extract_two_numbers_after_question_mark(i))
      except:
        pass
    item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
    for item in li_item:
      shop_id = item[0]
      item_id = item[1]
      try:
        text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
      except:
        data["items"].append({'shop_id': int(shop_id), 'item_id': int(item_id)})
        #stt = requests.get(f"https://live.shopee.vn/api/v1/session/{ss}", verify=False).json()["data"]["session"]["items_cnt"]+1
    if data["items"] != []:
      put_it(url, str(data).replace("'", '"'))
      item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
      item_list.reverse()
      for item in li_item:
        item_id = item[1]
        try:
          text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
        except:
          try:
            item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
            text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
          except:
            pass
    if text == "" and len(links) != 0:
      get_stt1(links, to_id, id, shop_id)
      #print("lỗi nè")
    else:
      print("ok " + text + str(len(links)) + " fist" + str(len(li_item)))
    if text != "":
      new_links = re_find_link(id, to_id, shop_id)
      if len(links) == len(new_links):
        send_mess(to_id," ".join(str(x) for x in sorted(list(set([int(x) for x in text.split()]))))+" ạ", id)
      else:
        print(new_links)
        get_stt(new_links, to_id, id, shop_id)

    
def get_stt1(links, to_id, id, shop_id):
    url = f"https://live.shopee.vn/webapi/v1/session/{ss}/add_items"
    li_item = []
    text = ""
    data = {'items': []}
    for i in links:
      try:
        if i.count("shp.ee/") != 0:
          li_item.append(re.search(r'product%2F(.*?)%3F', requests.head(i).headers['location']).group(1).split("%2F"))
        elif i.count("shope.ee/") != 0:
          li_item.append(extract_two_numbers_after_question_mark1(requests.head(i).headers['location']))
        elif i.count("https://shopee.vn/product/") != 0:
          li_item.append(extract_two_numbers_after_question_mark1(i))
        else:
          li_item.append(extract_two_numbers_after_question_mark(i))
      except:
        pass
    item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
    for item in li_item:
      shop_id = item[0]
      item_id = item[1]
      try:
        text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
      except:
        data["items"].append({'shop_id': int(shop_id), 'item_id': int(item_id)})
        #stt = requests.get(f"https://live.shopee.vn/api/v1/session/{ss}", verify=False).json()["data"]["session"]["items_cnt"]+1
    if data["items"] != []:
      #put_it(url, str(data).replace("'", '"'))
      item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
      for item in li_item:
        item_id = item[1]
        try:
          text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
        except:
          pass
    if text == "" and len(links) != 0:
      item_list = se.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
      for item in li_item:
        item_id = item[1]
        try:
          text = text + str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " "
        except:
          pass
    print("ok " + text + str(len(links))+ " - " + str(len(li_item)))
    if text != "":
      new_links = re_find_link(id, to_id, shop_id)
      if len(links) == len(new_links):
        send_mess(to_id," ".join(str(x) for x in sorted(list(set([int(x) for x in text.split()]))))+" ạ", id)
      else:
        get_stt(new_links, to_id, id, shop_id)


while True:
    try:
        try:
            ss = str(se.get("https://live.shopee.vn/webapi/v1/session").json()["data"]["session"]["session_id"])
        except:
            pass
        time.sleep(5)
        while se.get("https://live.shopee.vn/webapi/v1/session").json()["data"]["session"]["start_time"] != 0:
          try:
              time.sleep(1)
              for i in requests.get('https://banhang.shopee.vn/webchat/api/v1.2/conversations?direction=older&unread_only=true', headers={'Authorization': f'Bearer {au}'}, verify=False).json():
                try:
                  te = i["latest_message_content"]['text'].lower()
                  if te.count("/product/") != 0 or te.count("gắn") != 0 or te.count("add") != 0 or te.count("thêm") != 0 or te.count("lên") != 0 or te.count("gim") != 0 or te.count("ghim") != 0 or te.count("https://shope.ee/") != 0 or te.count("link") == 1 or te.count("https://shp.ee") != 0:
                    read(i['latest_message_id'],i['shop_id'],i['id'])
                    Thread(target=find_link, args=(i['id'],i['to_id'],i['shop_id'])).start()
                except:
                  pass
          except:
            pass
        #re.findall(pattern, input_text)
    except:
        pass

