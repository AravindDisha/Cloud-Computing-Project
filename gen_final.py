from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS, cross_origin
import csv
import requests
import docker
import time
import threading
import math
import json
import re



app = Flask(__name__)
CORS(app)

def start_cont(i,rem):
    global cid
    global stats
    global activeC
    global image
    global vname
    global vbind
    global ports
    client = docker.from_env()
    
    lock.acquire()
    if(rem == 0): #restart
        if(stats[i] == 1):
            print('already started at %d'%(ports[i]))
        else:
            cid[i] = client.containers.run(image,detach=True,ports={'80':ports[i]},volumes={vname:{'bind':vbind,'mode':'rw'}})
            stats[i] = 1
    else: #scale-up
        cid.append(client.containers.run(image,detach=True,ports={'80':ports[i]},volumes={vname:{'bind':vbind,'mode':'rw'}}))
        stats.append(1)
        activeC+=1
    print('started at %d '%(ports[i]))
    lock.release()

def kill_cont(i,rem):
    global cid
    global stats
    global activeC
    global ports
    lock.acquire()
    cid[i].kill()
    if(rem == 1): #scale-down
        activeC-=1
        cid.pop()
        stats.pop()
    else: #kill b4 restart
        stats[i] = 0
    lock.release()
    print('killed container at %d '%(ports[i]))

@app.route('/')
def starting():
    print("^.^")
    return(jsonify({}),200)


@app.route('/stop')
def stopping():
    global activeC
    global cid
    for i in range(activeC-1,-1,-1):
        kill_cont(i,1)
    return 'Killed all containers'

@app.route('/<path:path>',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def catch_api(path):
    global count
    global cid
    global activeC
    global started
    global portn
    global ports

    started = True
    if(check_url(request.path)==True):
        lock.acquire()
        count = count + 1
        lock.release()
    else:
        return(jsonify({}),405)

    lock.acquire()
    portn = (portn+1)%activeC
    lock.release()

    while(stats[portn]==0):
        portn=(portn+1)%activeC
    try :
        resp = requests.request(
            method=request.method,
            url='http://localhost:'+ str(ports[portn])+request.path,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)
        print('\ntrying : '+str(ports[portn]))
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        print(resp.content)
    except Exception as e:
        print('\n--------------------------------------------------------------------')
        print(e)
        print('--------------------------------------------------------------------\n')
        response = 'Error: You want path: %s' % path

    return response




def the_app_call():
    app.run(host='0.0.0.0',port=80,debug=False)

def check():
    global cid
    global activeC
    global stats
    global ports
    global health_url

    while (True):
        time.sleep(1)
        for i in range(activeC):
            try:
                head = {'Content-Type':'application/json'}
                url = 'http://localhost:'+str(ports[i])+health_url
                req = requests.get(url,headers=head)
                if(req.status_code == 500):
                    lock.acquire()
                    try:
                        stats[i] = 0
                    except:
                        print('')
                    lock.release()
            except:
                continue
def restart():
    global stats
    global cid
    global activeC
    while(True):
        time.sleep(1)
        for i in range(activeC):
            if(stats[i]==0):
                kill_cont(i,0)
                start_cont(i,0)

def auto_scale():
    global activeC
    global started
    global count
    global ports
    global poll_url
    global scale
    global maxC
    

    while(started == False):
        time.sleep(1)
    while(True):
        time.sleep(119)
        poll = 0
        for i in range(activeC):
            head = {'Content-Type':'application/json'}
            url = 'http://localhost:'+str(ports[i])+poll_url
            req = requests.get(url,headers=head)
            if(req.status_code==200):
                poll+=req.json()[0]
            req = requests.delete(url,headers=head)

        print('count is %d'%count)
        #print('poll is %d'%poll)

        try:
            x = min([i for i in list(scale.keys()) if(i > poll)])
            num = max(0,scale[x])
        except:
            num = maxC

        if(activeC < num):
            for i in range(activeC,num):
                start_cont(i,1)
        if(activeC > num):
            for i in range(activeC-1,num-1,-1):
                kill_cont(i,1)
        count=0

def create_cont1():
    global activeC
    if(activeC==0):
         start_cont(0,1)

def build_route_pattern(route):
    route_regex = re.sub(r'(<\w+>)', r'(?P\1[a-zA-Z0-9 ]+)', route)
    return re.compile("^{}$".format(route_regex))

def check_url(path):
    global paths
    for i in paths:
        try:
            match = i.match(path)
            x = match.groupdict()
        except:
            continue
        return True
    return False

def init():
    global started
    global count
    global cid
    global stats
    global activeC
    global portn

    global paths
    global vname
    global vbind
    global image
    global poll_url
    global health_url
    global scale
    global ports
    global maxC

    started = False
    count = 0
    cid = []
    stats = []
    activeC = 0
    portn = 0 

    paths = []
    vname = "new_vol"
    vbind = "/"
    image = ""
    poll_url = ""
    health_url = ""
    scale = {}
    ports = []
    maxC = 1

if __name__ == '__main__':
    
    init()

    global vname
    global vbind
    global paths
    global image
    global poll_url
    global health_url
    global scale
    global ports

    with open('specs.txt') as json_file:  
        data = json.load(json_file)
        
        image = data['docker_image']
        
        vname = data['volume']['name']
        
        client = docker.from_env()
        vbind = data['volume']['bind']
        vs = [ i.name for i in client.volumes.list()]
        if(not vname in vs):
            client.volumes.create(name=vname, driver='local')

        pths = data['api calls']
        for p in pths:
            paths.append(build_route_pattern(p))

        poll_url = data["polling"]

        health_url = data["health"]

        ports = data["ports"]

        maxC = data["max_containers"]

        for p in data["scaling"]:
            scale[int(p)] = data['scaling'][p]
    

    lock = threading.Lock() 

    t1 = threading.Thread(target=the_app_call) 
    t2 = threading.Thread(target=check)
    t3 = threading.Thread(target=restart)
    t4 = threading.Thread(target=auto_scale)
    t5 = threading.Thread(target=create_cont1)
    t1.start()
    print('app started')

    t5.start()
    t5.join()

    t2.start()
    print('checking started')
    t3.start()
    print('restart after check started')

    while(started == False):
        time.sleep(1)
    t4.start()
    print('Auto-scale started')
    t1.join()
    t2.join()
    t3.join()
    t4.start()
    