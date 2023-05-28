#AACCTTTSSSSSSSSSSSSSS
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
import csv
import requests
import json
import re
import os
cnt=0
crash=False 
app = Flask(__name__)
CORS(app)

@app.route('/api/v1/categories',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def categories():
    global cnt
    global crash
    cnt+=1
    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method=='POST'):
        jsn  = request.json
        d={}
        category = jsn[0]
        with open('categories.csv','r') as csvFile:
            reader = csv.reader(csvFile)
            
            for row in reader:
                if(row[0]==category):
                    x = jsonify(d)
                    return(x,400)
        csvFile.close()
        row = [category,0]
        with open('categories.csv','a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        x = jsonify(d)
        return(x,201)
        
    elif (request.method=='GET'):
        cats = {}
        with open('categories.csv', 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                if(row[0]==""):
                    return(jsonify({}),204)
                    #print(row)
                cats[row[0]] = int(row[1])
        csvFile.close()
        x=jsonify(cats)
        return(x,200)

    else :
        x=jsonify({})
        return(x,405)


@app.route('/api/v1/categories/<categoryName>',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def delete(categoryName):
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'DELETE'):
        delete_string = categoryName.split('_')
        delete_string = " ".join(delete_string)
        if(delete_string=="All"):
            f1 = open('categories.csv','w+')
            f2 = open('upvotes.csv','w+')
            f3 = open('acts.csv','w+')
            f1.close()
            f2.close()
            f3.close()
        d={}
        clean_rows = []
        flag = 0 
        count_del = 0 
        with open('categories.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    if(" ".join(row[0].split('_'))==delete_string):
                        flag=1
                        count_del = int(row[1])
                    else:
                        clean_rows.append(row)
        print(clean_rows)
        if(flag==1):        
            with open('categories.csv','w') as csvFile:
                    writer = csv.writer(csvFile)
                    for row in clean_rows:
                        if(row[0]=="All"):
                            row[1] = int(row[1]) - count_del
                        writer.writerow(row)
            
            clean_rows=[]
            act_ids = []
            flag_1 = 0
            with open('acts.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    if(" ".join(row[4].split('_'))==delete_string):
                        flag_1=1
                        os.remove(row[5])
                        act_ids.append(row[0])
                    else:
                        clean_rows.append(row)
            if(flag_1==1):
                with open('acts.csv','w') as csvFile:
                    writer = csv.writer(csvFile)
                    for row in clean_rows:
                        writer.writerow(row)
            flag_1 = 0 
            clean_rows=[]
            with open('upvotes.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    if(row[0] in act_ids):
                        flag_1=1
                    else:
                        clean_rows.append(row)
            with open('upvotes.csv','w') as csvFile:
                    writer = csv.writer(csvFile)
                    for row in clean_rows:
                        writer.writerow(row)

            x = jsonify(d)

            return (x,200)
        else:
            x = jsonify(d)
            return (x,400)

    else :
        x = jsonify({})
        return(x,405)


@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def count(categoryName):
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'GET'):
        query_string = categoryName.split('_')
        query_string = " ".join(query_string)
        d=[]
        clean_rows = []
        flag = 0
        with open('categories.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    if(row[0]==query_string):
                        d = [row[1]] #changed this
                        flag = 1
        if(flag == 1):
            x = jsonify(d)
            return (x,200)
        else:
            x = jsonify(d)
            return (x,400)
    else :
        x = jsonify({})
        return(x,405)


@app.route('/api/v1/acts/upvote',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def upVote():
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif(request.method=='POST'):
        d = {}
        jsn  = request.json;
        actid = str(jsn[0])
        flag=0
        r = csv.reader(open('upvotes.csv')) # Here your csv file
        lines = list(r)
        for i in range(0,len(lines)):
            if (lines[i][0] == actid):
                lines[i][1] = str(int(lines[i][1])+1)
                d[actid] = lines[i][1]
                flag=1
        writer = csv.writer(open('upvotes.csv', 'w'))
        writer.writerows(lines)
        if(flag==0):
            return(jsonify({}),400)
        x = jsonify(d)
        return(x,200)

    else:
        return(jsonify({}),405)


@app.route('/api/v1/categories/<catName>/acts',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def getActs(catName):
    #for each act in acts.csv filter out acts
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'GET'):
        fp=open("categories.csv")
        lines=fp.readlines()
        j=[]
        for line in lines:
            cname=line.split(",")[0]
            j.append(cname)
        if(catName not in j):
            return(jsonify({}),400)
        if(request.args.get('start') != None): #CHECK THE LIST INDEX 
            startRange = int(request.args.get('start'))
            endRange = int(request.args.get('end'))
            if(startRange<1):
                return(jsonify({}),400)

            d=[]
            x = jsonify(d)
            clean_rows = []
            flag = 0
            i = 0 
            if(endRange-startRange>100):
                return(jsonify({}),413)
            j = 0
            l= [] 
            with open('acts.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    l.append(row)

            new=[]
            for i in range(len(l)-1,-1,-1):
                new.append(l[i])
            final=[]
            for u in range(startRange-1,endRange):
                final.append(new[u])
            f=[]
            for m in final:
                if(m[4]==catName):
                    f.append(m)
            for x in f:
                upv = 0
                file = open(row[5],mode='r')
                imgB = ""
                imgB = file.read()
                file.close()
                with open('upvotes.csv','r') as csvFile1:
                    reader1 = csv.reader(csvFile1)
                    for row1 in reader1:
                        if(row1[0] == l[i][0]):
                            upv = row1[1]
                d.append({'actid':x[0],'username':x[1],'timestamp':x[2],'caption':x[3],'upvotes':upv,'imgB64':imgB})
                print('here',x[3])
            if(endRange>len(l)):
                return(jsonify({}),400)             
            if(len(d)==0):
                return (x,204)
            x = jsonify(d)
            return (x,200)

            
        else:
            d = []
            flag=0
            with open('acts.csv','r') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    if(row[4]==catName):
                        flag=1
                        upv = 0
                        file = open(row[5],mode='r')
                        imgB = ""
                        imgB = file.read()
                        file.close()
                        with open('upvotes.csv','r') as csvFile1:
                            reader1 = csv.reader(csvFile1)
                            for row1 in reader1:
                                if(row1):
                                    if(row1[0] == row[0]):
                                        upv = row1[1]
                        print(row)
                        print(len(imgB),"\n")
                        d.append({'actid':row[0],'username':row[1],'timestamp':row[2],'caption':row[3],'upvotes':upv,'imgB64':imgB})
                        print('here',row[3])
            if(len(d)>100):
                return(jsonify({}),413)
            if(flag==0):
                return(jsonify({}),204)
            x = jsonify(d)
            return(x,200)

    else :
        return(jsonify({}),405)

@app.route('/api/v1/acts',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def uploadActs():
    #for each act in acts.csv filter out acts
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'POST'):    
        jsn=request.json
        #print(jsn)
        fp=open("categories.csv")
        lines=fp.readlines()
        categories=[]
        for line in lines:
            categories.append(line.split(",")[0])
        statv = 502
        users = []
        while(not(statv==200 or statv==204)):
            head = {'Content-Type':'application/json','Origin':'35.173.103.190'}
            url = 'http://Pablo-633175984.us-east-1.elb.amazonaws.com/api/v1/users'
            req = requests.get(url,headers=head)
            statv=req.status_code
            if(statv == 200):
                users = req.json()
        acts=[]
        with open('acts.csv','r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                acts.append(row[0])
        csvFile.close()
        #A-Z, a-z, 0-9, '+', '/', and '=
        allowed=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','+','/','=','\n']
        print('img ?')
        try:
            imc=str(jsn['imgB64'])
            l = set([imc[i] for i in range(len(imc))])
            print(l)
        except:
            return(jsonify({}),400)
        print('img2 ?')
        for x in imc:
            if(x not in allowed):
                return(jsonify({}),400)
        print('img done')
        if(str(jsn['actId']) in acts):
            return(jsonify({}),400)
        print('actid done')
        print(users)
        if(jsn['username'] not in users):
            return(jsonify({}),400)
        print('uname done')
        timestamp=jsn['timestamp']
        if (not re.match('[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]:[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', timestamp)):
            return(jsonify({}),400)
        print('time done')
        if(jsn['categoryName'] not in categories):
            return(jsonify({}),400)
        print('catname done')
        fp=open("acts.csv","a+")
        fp.write(str(jsn['actId'])+','+jsn['username']+','+jsn['timestamp']+','+jsn['caption']+','+jsn['categoryName']+','+"img"+str(jsn['actId'])+".txt\n")
        fp.close()
        fx=open("img"+str(jsn['actId'])+".txt","w+")
        fx.write(jsn['imgB64'])
        fc=open('categories.csv')
        cat=jsn['categoryName']
        gz=[]
        lines=fc.readlines()
        fc.close()
        for line in lines:
            line=line.rstrip('\n')
            catz,num=line.split(',')
            if(catz==cat):
                num=int(num)+1
            gz.append(catz+','+str(num)+"\n")
        fc=open("categories.csv","w+")
        for x in gz:
            fc.write(x)
        x = jsonify({})
        jk=open("upvotes.csv","a+")
        jk.write(str(jsn['actId'])+","+"0\n")
        jk.close()
        return(x,201)

    else :
        return(jsonify({}),405)


@app.route('/api/v1/acts/<actId>',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def delact(actId):
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)
    
    elif (request.method == 'DELETE'):  
        d = {}
        #print(actId)
        cat = ""
        r = csv.reader(open('acts.csv')) # Here your csv file
        lines = list(r)
        flag=0
        for i in range(0,len(lines)):
            if(lines[i][0] == str(actId)):
                flag=1
                cat = lines[i][4]
                txtf = lines[i][5]
                del lines[i]
                break
        writer = csv.writer(open('acts.csv', 'w'))
        writer.writerows(lines)
        if(flag==0):
            return(jsonify({}),400)
        r = open(txtf,'w')
        r = csv.reader(open('categories.csv')) # Here your csv file
        lines = list(r)
        for i in range(0,len(lines)):
            if(lines[i][0] == " ".join(cat.split('_'))):
                lines[i][1] = str(int(lines[i][1])-1)
        writer = csv.writer(open('categories.csv', 'w'))
        writer.writerows(lines)
        
        r = csv.reader(open('upvotes.csv')) # Here your csv file
        lines = list(r)
        for i in range(0,len(lines)):
            if(lines[i][0] == actId):
                del lines[i]
                break
        writer = csv.writer(open('upvotes.csv', 'w'))
        writer.writerows(lines)
        
        x = jsonify(d)
        return(x,200)

    else :
        return(jsonify({}),405)


@app.route('/api/v1/acts/count',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def getNUmActs():
    global cnt
    global crash
    cnt+=1

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'GET'):
        n=0
        with open('acts.csv','r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                n+=1
        x = jsonify([n])
        return(x,200)

    else :
        return(jsonify({}),405)


@app.route('/api/v1/_count',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def Foo1():
    global cnt
    global crash

    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'GET'):
        print("count - ",cnt)
        x=jsonify([cnt])
        return(x,200)

    elif (request.method == 'DELETE'):
        cnt=0
        x=jsonify({})
        return(x,200)


    else :
        return(jsonify({}),405)

@app.route('/api/v1/_health',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def Foo2():
    global crash
    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'GET'):
        return(jsonify({}),200)

    else:
        return(jsonify({}),405)

@app.route('/api/v1/_crash',methods=['GET','OPTIONS','POST','DELETE','PUT','HEAD'])
def Foo3():
    global crash
    if (crash == True):
        x=jsonify({})
        return(x,500)

    elif (request.method == 'POST'):
        crash = True
        return(jsonify({}),200)

    else:
        return(jsonify({}),405)

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=80,debug=True)