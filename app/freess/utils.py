from PIL import Image

import zbarlight
import socket
import requests


def get_QR(file_path):
  # file_path = '../../server03.png'
  if isinstance(file_path, basestring):
    with open(file_path, 'rb') as image_file:
      image = Image.open(image_file)
      image.load()
  else:
    image = Image.open(file_path)
  codes = zbarlight.scan_codes('qrcode', image)
  return codes[0]


def get_country_by_addr(addr):
  host = socket.gethostbyname(addr)
  #url = "http://ip.taobao.com/service/getIpInfo.php?ip="
  url = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip="
  resp = requests.get(url + host)
  json_data = resp.json()
  ret = json_data["country"]
  return ret
