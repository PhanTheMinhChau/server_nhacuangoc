from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask import request
import requests
from time import sleep, time, strftime, localtime
import re
from threading import Thread
import urllib.parse
import undetected_chromedriver as uc

# def item_ud():
#     global item_list1
#     item_list1 = requests.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=510").json()["data"]["items"]

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
    pattern = r'product/(\d+)\/(\d+)'
    match = re.search(pattern, link)
    if match:
        number1 = match.group(1)
        number2 = match.group(2)
        return [number1, number2]
    else:
      return [1]-1


def session_ud():
    global ss
    ss = str(session.get("https://live.shopee.vn/webapi/v1/session").json()["data"]["session"]["session_id"])


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


def getstt(link):
    Thread(target=session_ud, args=()).start()
    links = [link]
    url = f"https://live.shopee.vn/webapi/v1/session/{ss}/add_items"
    li_item = []
    text = ""
    data = {'items': []}
    for i in links:
      if i.count("shp.ee/") != 0:
        li_item.append(re.search(r'product%2F(.*?)%3F', requests.head(i).headers['location']).group(1).split("%2F"))
      elif i.count("shope.ee/") != 0:
        li_item.append(extract_two_numbers_after_question_mark1(requests.head(i).headers['location']))
      elif i.count("https://shopee.vn/product/") != 0:
        li_item.append(extract_two_numbers_after_question_mark1(i))
      else:
        try:
          li_item.append(extract_two_numbers_after_question_mark(i))
        except:
          pass
    item_list = session.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
    for item in li_item:
      shop_id = item[0]
      item_id = item[1]
      try:
        return [str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " ", ss]
      except:
        data["items"].append({'shop_id': int(shop_id), 'item_id': int(item_id)})
        #stt = requests.get(f"https://live.shopee.vn/api/v1/session/{ss}", verify=False).json()["data"]["session"]["items_cnt"]+1
    if data["items"] != []:
      put_it(url, str(data).replace("'", '"'))
      item_list = session.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
      for item in li_item:
        item_id = item[1]
        try:
          return [str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " ", ss]
        except:
          item_list = session.get(f"https://live.shopee.vn/api/v1/session/{ss}/more_items?offset=0&limit=500", verify=False).json()["data"]["items"]
          return [str(next(item for item in item_list if item["item_id"] == int(item_id))["id"]) + " ", ss]


def check_oder(oder_id):
  try:
    data = session.get("https://affiliate.shopee.vn/api/v1/report/list?page_size=20&page_num=1&purchase_time_s="+str(0)+"&purchase_time_e="+str(int(time()))+f"&order_sn={oder_id}").json()["data"]["list"][0]
    return {
        "err":0,
        "purchase_time" : strftime('%d/%m/%Y %H:%M:%S', localtime(data["purchase_time"])),
        "conversion_status" : data["conversion_status"],
        "checkout_complete_time" : strftime('%d/%m/%Y %H:%M:%S', localtime(data["checkout_complete_time"])),
        "oder_id":oder_id
    }
  except:
    return {"err":1,
            "oder_id":oder_id}


# def check_oder(oder_id):
#   try:
#     data = session.get("https://affiliate.shopee.vn/api/v1/report/list?page_size=20&page_num=1&purchase_time_s="+str(0)+"&purchase_time_e="+str(int(time()))+f"&order_sn={oder_id}").json()["data"]["list"][0]
#     return {
#         "err":0,
#         "purchase_time" : strftime('%d/%m/%Y %H:%M:%S', localtime(data["purchase_time"])),
#         "conversion_status" : data["conversion_status"],
#         "checkout_complete_time" : strftime('%d/%m/%Y %H:%M:%S', localtime(data["checkout_complete_time"])),
#         "oder_id":oder_id
#     }
#   except:
#     return {"err":1,
#             "oder_id":oder_id}


session = requests.Session()
session.cookies.set("shopee_token", "fqpX6+gfGVnaT3KkeKUlToHwomLszSXIV0seSqfyEOdRRXee1UFTVPBitotVZbTZ", domain=".shopee.vn")
session.get("https://shopee.vn/api/v4/account/basic/get_account_info", verify=False)
#Khởi tạo session

driver = uc.Chrome(headless=False,use_subprocess=False)
driver.get("https://shopee.vn/")
driver.execute_script("document.cookie = 'SPC_EC="+session.cookies.get_dict()["SPC_EC"]+"'")
driver.get("https://shopee.vn/")
driver.get("https://live.shopee.vn/pc/setup?API")

session_ud()
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET'] )
@cross_origin(origin='*')
def home():
    return "hi lô"


@app.route('/additem', methods=['POST'] )
@cross_origin(origin='*')
def add_item():
    try:
        num = getstt(request.get_json(force=True)['url']),
        return jsonify(
            item_id=num[0][0],
            #short_link=f"https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D{ss1}%23share&deep_and_deferred=1&utm_campaign=-&utm_content=wsxeko----&utm_medium=affiliates&utm_source=an_17333510032&utm_term=8uenxb6rxikf"
            short_link="https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D"+num[0][1]+"%23share"
            )
    except:
        try:
            return jsonify(
                item_id=num[0][0],
                #short_link=f"https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D{ss1}%23share&deep_and_deferred=1&utm_campaign=-&utm_content=wsxeko----&utm_medium=affiliates&utm_source=an_17333510032&utm_term=8uenxb6rxikf"
                short_link="https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D"+num[0][1]+"%23share"
                )
        except:
            return jsonify(
                item_id="Vui lòng thử lại",
                #short_link=f"https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D{ss1}%23share&deep_and_deferred=1&utm_campaign=-&utm_content=wsxeko----&utm_medium=affiliates&utm_source=an_17333510032&utm_term=8uenxb6rxikf"
                short_link=f"https://shopee.vn/universal-link?redir=https%3A%2F%2Flive.shopee.vn%2Fmiddle-page%3Ftype%3Dlive%26id%3D46464%23share"
                )


@app.route('/checkoder', methods=['POST'] )
@cross_origin(origin='*')
def check_oders():
    oders = request.get_json(force=True)['oders']
    pattern = r"\b[0-9A-Z]{14}\b"  # Mẫu tìm kiếm: 15 ký tự chữ hoặc số liên tiếp
    matches = re.findall(pattern, oders)
    return check_oder(matches[0])
    # text = []
    # for i in matches:
    #   try:
    #     check = check_oder(i)["conversion_status"]
    #     if check == 1:
    #       text.append(i + " - đơn đang xử lý")
    #     if check == 2:
    #       text.append(i + " - có đơn")
    #     if check == 3:
    #       text.append(i + " - đơn bị hủy")
    #     if check == 4:
    #       text.append(i + " - chưa thanh toán")
    #   except:
    #     text.append(i + " - rớt")
    # return text


@app.route('/checkoder1', methods=['GET'] )
@cross_origin(origin='*')
def check_oders1():
    oderid = request.args.get('oderid')
    try:
        check = check_oder(oderid)["conversion_status"]
        if check == 1:
          return "đơn đang xử lý"
        if check == 2:
          return "có đơn"
        if check == 3:
          return "đơn bị hủy"
        if check == 4:
          return "chưa thanh toán"
    except:
        return "rớt"


@app.route('/getlink', methods=['GET'] )
@cross_origin(origin='*')
def getlink():
    link = request.args.get('url')
    return session.get(link, verify=False).url


if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5001)


