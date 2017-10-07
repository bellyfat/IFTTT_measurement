import os, sys, requests, json, time
class HueController(object):
  def __init__(self, userId = None):
    if userId is None:
      self.userId = "0NpI8eMp-dg8zVPVyxpIoS6zdg6jQfl2HObgpaah"
    else:
      self.userId = userId
    self.initHueAddress()

  def tuneLightLevel(self, lightId, lightLevel):
    data = {
        "bri" : lightLevel,
    }
    jsonData = json.dumps(data)
    requestUrl = self.hueAddress + "api/{}/lights/{}/state".format(self.userId, lightId)
    response = requests.put(requestUrl, data = jsonData)
    responseObj = json.loads(response.text)
    if "success" in responseObj[0]:
      return True
    else:
      print(("error message: ", response.text))
      return False

  def getState(self, lightId):
      if self.isLightOn(lightId):
          return 1
      else:
          return 0

  def setState(self, lightId, state):
      if state == 1:
          return self.turnonLight(lightId)
      elif state == 0:
          return self.turnoffLight(lightId)

  def getLight(self, lightId):
    retryLimit = 5
    currRetry = 0
    while True:
        try:
            requestUrl = self.hueAddress + "api/{}/lights/{}/".format(self.userId, lightId)
            response = requests.get(requestUrl)
            responseObj = json.loads(response.text)
            break
        except Exception as e:
            if currRetry < retryLimit:
                currRetry += 1
                continue
            raise e
    return responseObj

  def isLightOn(self, lightId):
    hueLightObj = self.getLight(lightId)
    return True if hueLightObj["state"]["on"] else False
  def isLightAlert(self, lightId):
    hueLightObj = self.getLight(lightId)
    return True if hueLightObj["state"]["alert"] == "lselect"  else False
  def isLightEffect(self, lightId):
    hueLightObj = self.getLight(lightId)
    return False if hueLightObj["effect"]["none"] else True

  def toggleLight(self, lightId):
    hueLightObj = self.getLight(lightId)
    toggleValue = False if hueLightObj["state"]["on"] else True
    data = {
        "on" : toggleValue,
    }
    jsonData = json.dumps(data)
    requestUrl = self.hueAddress + "api/{}/lights/{}/state".format(self.userId, lightId)
    response = requests.put(requestUrl, data = jsonData)
    responseObj = json.loads(response.text)
    if "success" in responseObj[0]:
      return True
    else:
      print(("error message: ", response.text))
      return False

  def clearAlert(self, lightId):
      self.alertLight(lightId, "none")

  def alertLight(self, lightId, alertStatus = "lselect"):
    while True:
      try:
        data = {
            "alert" : alertStatus,
        }
        jsonData = json.dumps(data)
        requestUrl = self.hueAddress + "api/{}/lights/{}/state".format(self.userId, lightId)
        response = requests.put(requestUrl, data = jsonData)
        responseObj = json.loads(response.text)
        if "success" in responseObj[0]:
          return True
        else:
          print(("error message: ", response.text))
          return False
      except Exception as e:
        print("exception during turning off light, resume")
        continue

  def turnoffLight(self, lightId):
    while True:
      try:
        data = {
            "on" : False,
        }
        jsonData = json.dumps(data)
        requestUrl = self.hueAddress + "api/{}/lights/{}/state".format(self.userId, lightId)
        response = requests.put(requestUrl, data = jsonData)
        responseObj = json.loads(response.text)
        if "success" in responseObj[0]:
          return True
        else:
          print(("error message: ", response.text))
          return False
      except Exception as e:
        print("exception during turning off light, resume")
        continue

  def turnonLight(self, lightId):
    while True:
      try:
        data = {
            "on" : True,
        }
        jsonData = json.dumps(data)
        requestUrl = self.hueAddress + "api/{}/lights/{}/state".format(self.userId, lightId)
        response = requests.put(requestUrl, data = jsonData)
        responseObj = json.loads(response.text)
        if "success" in responseObj[0]:
          return True
        else:
          print(("error message: ", response.text))
          return False
      except Exception as e:
        print("exception during turning on light, resume", e)
        continue

  def initHueAddress(self):
    url = "https://www.meethue.com/api/nupnp"
    response = requests.get(url)
    resObj = json.loads(response.text)
    self.hueAddress = "Http://" + resObj[0]["internalipaddress"] + "/"

import socket
import http.client as httplib
import io

class SSDPResponse(object):
    class _FakeSocket(io.StringIO):
        def makefile(self, *args, **kw):
            return self
    def __init__(self, response):
        r = httplib.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.usn = r.getheader("usn")
        self.st = r.getheader("st")
        self.cache = r.getheader("cache-control").split("=")[1]
    def __repr__(self):
        return "<SSDPResponse({location}, {st}, {usn})>".format(**self.__dict__)

def discover(service, timeout=5, retries=1, mx=3):
    group = ("239.255.255.250", 1900)
    message = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}','MX: {mx}','',''])
    socket.setdefaulttimeout(timeout)
    responses = {}
    for _ in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.format(*group, st=service, mx=mx), group)
        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break
    return list(responses.values())
if __name__ == "__main__":
  userId = "0NpI8eMp-dg8zVPVyxpIoS6zdg6jQfl2HObgpaah"
  controller = HueController(userId)
  lightId = 2
  controller.getLight(lightId)
  sys.exit(1)
  controller.alertLight(lightId, "lselect")
  sys.exit(1)
  #tune test
  testLimit = 5
  startLightLevel = 50
  sleepInterval = 1
  endLightLevel = 250
  lightLevelList = [25, 250]
  controller.turnonLight(lightId)
  for i in range(1, testLimit + 1):
    controller.tuneLightLevel(lightId, lightLevelList[i % 2])
    time.sleep(sleepInterval)

  #toggle lights
  controller.tuneLightLevel(lightId, endLightLevel)
  sleepInterval = 2
  testLimit = 5
  for i in range(testLimit):
    controller.toggleLight(lightId)
    time.sleep(sleepInterval)

