from flask import Flask
from flask import request as req
import requests
import sys
requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/home')
def get():
  sys.stderr.write("\n----------calling pyserver----------\n")
  sys.stderr.write("headers: " + str(req.headers) + "\n")
  sys.stdout.flush()
  # r = requests.get('http://python-api.resiliency-dev.svc.cluster.local/index', headers=req.headers) # works only in nonprod dev namespace since it's hardcoded
  # r = requests.get('https://python-api.preview-internal.graingercloud.com/index', verify=False, headers=req.headers)
  # return r.text, r.status_code
  return 'hello', 200

@app.route('/internal')
def getInternal():
  sys.stderr.write("\n----------calling pyserver internal ur----------\n")
  sys.stderr.write("headers: " + str(req.headers) + "\n")
  sys.stdout.flush()
  # r = requests.get('http://python-api.server.svc.cluster.local/index')
  r = requests.get('http://python-api/index')
  #r = requests.get('http://python-api.resiliency.svc.cluster.local/index')
  return r.text, r.status_code

@app.route('/download/<file_name>')
def getDown(file_name):
  sys.stderr.write("\n----------calling download pyserver ----------\n")
  sys.stderr.write("headers: " + str(req.headers) + "\n")
  sys.stderr.write("filename is: " + file_name + "\n")
  sys.stdout.flush()
  #url = 'https://python-api-dev.nonprod-internal.graingercloud.com/static/' + file_name
  url = 'http://python-api.resiliency-dev.svc.cluster.local/static/' + file_name
  #r = requests.get('http://python-api/static/<file_name>', headers=req.headers)
  r = requests.get(url, headers=req.headers)
  return r.text, r.status_code

@app.route('/internal/download/<file_name>')
def getDownInternal(file_name):
  sys.stderr.write("\n----------calling internal download pyserver ----------\n")
  sys.stderr.write("headers: " + str(req.headers) + "\n")
  sys.stderr.write("filename is: " + file_name + "\n")
  sys.stdout.flush()
  url = 'http://python-api/static/' + file_name
  r = requests.get(url, headers=req.headers)
  return r.text, r.status_code

@app.route('/health-check')
def getHealthCheck():
    return 'UP'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)
