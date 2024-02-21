import hashlib
import math
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# servername="vayu.iitd.ac.in"
# servername="10.17.7.218"
# servername="10.17.7.134"
# servername="10.17.51.115"
# servername='10.17.6.5'
servername="127.1.1.0"
serverport=9802
server_socket = socket(AF_INET, SOCK_DGRAM)


# Parameters
cw=5
if(servername=='127.1.1.0'):
    rate_min=0.0084
else:
    rate_min=0.005
rate=rate_min
rtt=0.0001
timeout=2*rtt
window=1

# Variables
skip=0
sqish=0
noreq=0
submit=""
sublist=[]
sendtime=[]
recvtime=[]
rate_of_data=1448
nol=0
k=[(i*rate_of_data) for i in range(cw)]
devrtt=0
duration_send=[]
duration_recv=[]
deploy_time=0
ts=0
squishstart=0
squishstate=0
equal=0
tsquish=0

# Locks
lock1=threading.Lock()
lock2=threading.Lock()
lock3=threading.Lock()
lock4=threading.Lock()
lock5=threading.Lock()

def CLOSE():
        server_socket.close()
        
def SUBMIT(submit):
    rate=0.4
    for i in range(len(sublist)):
        submit+=sublist[i]
    submit=submit[:len(submit)-1]
    result=hashlib.md5(submit.encode())
    print(result.hexdigest())
    sentence = "Submit: cs5211004@blue_flag\nMD5: "+str(result.hexdigest())+"\n\n"
    while(True):
        try:
            if(time.time()-ts>rate):
                server_socket.sendto(sentence.encode(),(servername, serverport))
                server_socket.settimeout(2)
                st, serverAddress = server_socket.recvfrom(4096)
                ts=time.time()
                if(st.decode().split("\n")[0].split(" ")[0]=="Result:"):
                    print(st.decode())
                    break
                else:
                    continue
        except Exception as e:
                ts=time.time()
                continue
            
def findNol():
    global nol
    global sublist
    global sendtime
    global recvtime
    global ts
    # RESET
    sentence = "Reset\n\n"
    server_socket.sendto(sentence.encode(),(servername, serverport))
    
    # NOLines
    sentence = "SendSize\n\n"
    ts=0
    rate=0.4
    while(True):
            try:
                if(time.time()-ts>rate):
                    server_socket.sendto(sentence.encode(),(servername, serverport))
                    server_socket.settimeout(3)
                    st, serverAddress = server_socket.recvfrom(4096)
                    ts=time.time()
                    break
            except Exception as e:
                print("Server not working")
                ts=time.time()
                continue
    nol=int(st.decode().split("\n")[0].split(" ")[1])
    print("NOL: ", nol)
    print("Len of Sublist: ", nol//rate_of_data +1)
    sublist=["" for i in range((nol//rate_of_data)+1)]
    sendtime=[0 for i in range((nol//rate_of_data)+1)]
    recvtime=[0 for i in range((nol//rate_of_data)+1)]
    
    
def check_filled(list,i):
    for k  in range(i,len(sublist),cw):
        if(list[k]==""):
            return True
            break
    return False
def check_length(list):
    c=0
    for i  in range(len(list)):
        if(list[i]!=""):
            c+=1
    return c
    

def implement_thread(i):
    global sublist
    global k
    global skip
    global sqish
    global cw
    global noreq
    global rtt
    global devrtt
    global timeout
    global rate
    global rate_min
    global deploy_time
    global ts
    global duration_send
    global duration_recv
    global sendtime
    global recvtime
    global squishstart
    global squishstate
    global equal
    global window
    global tsquish
    max_cw=3
    tempwindow=1
    ts=time.time()
    while(check_filled(sublist,i)):
            lock5.acquire()
            k[i]=i*rate_of_data
            # print("Fulfilled Equation of Eminence ",check_length(sublist))
            lock5.release()
            while(k[i]<=(nol//rate_of_data)*rate_of_data and (time.time()-ts>rate)):
                # print(rate)
                if(sublist[k[i]//rate_of_data]=="" ):
                    
                            # print("REQUEST FOR: ",k[i])
                            tempwindow=window
                            lock4.acquire()
                            for win in range(min(math.floor(tempwindow),max_cw)):
                                if((k[i]+win*rate_of_data)//rate_of_data<len(sublist) and sublist[(k[i]+win*rate_of_data)//rate_of_data]==""):
                                    sentence = "Offset: "+str(k[i]+win*rate_of_data)+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                                    server_socket.sendto(sentence.encode(),(servername, serverport))
                                    if(sublist[(k[i]+win*rate_of_data)//rate_of_data]==""):
                                        sendtime[(k[i]+win*rate_of_data)//rate_of_data]=time.time()
                                        duration_send.append([k[i]+win*rate_of_data,sendtime[(k[i]+win*rate_of_data)//rate_of_data]-deploy_time])
                                    ts=time.time()
                                    noreq+=1
                                    # print("Sent req for->",k[i]+win*cw*rate_of_data)
                            lock4.release()
                            
                            
                            for win in range(min(math.floor(tempwindow),max_cw)):
                                try:
                                    server_socket.settimeout(timeout)
                                    st, serverAddress = server_socket.recvfrom(4096)
                                    lis=st.decode().split("\n")
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=="" and lis[2]==""):
                                        recvtime[(int(st.decode().split("\n")[0].split(" ")[1]))//rate_of_data]=time.time()
                                    # print("Revd req for->",(int(lis[0].split(" ")[1])))
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                        lock1.acquire()
                                        lis=st.decode().split("\n")
                                        if(lis[2]!=""):
                                            tsquish=time.time()
                                            sqish+=1
                                            print("QISHED:..............",squishstart," rate= ",rate)
                                            
                                            
                                            squishstart+=1
                                            if(squishstart>=50 and check_length(sublist)<20):
                                                window=1
                                                squishstart=0
                                                rate_min=(0.35)*15*rate_min+ (1-0.35)*rate_min
                                                rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                            if(squishstart>=50 and 100>check_length(sublist)>20):
                                                window=1
                                                squishstart=0
                                                rate_min=(0.35)*10*rate_min+ (1-0.35)*rate_min
                                                rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                            if(squishstart>=50 and 300>check_length(sublist)>100):
                                                window=1
                                                squishstart=0
                                                rate_min=(0.35)*8*rate_min+ (1-0.35)*rate_min
                                                rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                            if(squishstart>=50 and 600>check_length(sublist)>300):
                                                window=1
                                                squishstart=0
                                                rate_min=(0.35)*4*rate_min+ (1-0.35)*rate_min
                                                rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                            if(squishstart>=50 and check_length(sublist)>600):
                                                window=1
                                                squishstart=0
                                                rate_min=(0.35)*2*rate_min+ (1-0.35)*rate_min
                                                rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                            rate=max(rate_min,(tsquish-sendtime[int(lis[0].split(" ")[1])//rate_of_data])/3)
                                        else:
                                            if(squishstart!=0):
                                                squishstart=0
                                            listofk=[(k[i]+win*rate_of_data) for win in range(min(math.floor(tempwindow),max_cw))]
                                            if(int(lis[0].split(" ")[1]) in listofk):
                                                if(rate_min==rate): 
                                                    equal=1
                                                else:
                                                    equal=0
                                                print("GOT   CORRECT LINE ",check_length(sublist)," rate_min=",rate_min, " rate=",rate, " RTT=",-sendtime[int(lis[0].split(" ")[1])//rate_of_data]+recvtime[int(lis[0].split(" ")[1])//rate_of_data]," ",math.floor(window))
                                                strtmp=""
                                                countuseless=0
                                                for j in range(3):
                                                    countuseless+=len(lis[j])+1
                                                if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                                    sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                                    
                                                    duration_recv.append([(int(lis[0].split(" ")[1])),recvtime[(int(lis[0].split(" ")[1]))//rate_of_data]-deploy_time])
                                                    temp=int(lis[0].split(" ")[1])//rate_of_data
                                                    if(sendtime[temp]<=recvtime[temp]):
                                                        if(rtt>recvtime[temp]-sendtime[temp]):
                                                            window+=1/window
                                                        else:
                                                            window=1
                                                        rtt=(1-0.125)*rtt+0.125*(recvtime[temp]-sendtime[temp])
                                                        devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                                        timeout=3*rtt+4*devrtt
                                                        rate_min=(0.4)*rate_min/1.0005+ (1-0.4)*rate_min
                                                        # rate_min=(0.5)*rate+0.5*(rate_min)
                                                        rate=max(rate_min,rtt/3)
                                                        
                                            else:
                                                if(rate_min==rate): 
                                                    equal=1
                                                else:
                                                    equal=0
                                                print("GOT INCORRECT LINE ",check_length(sublist), " rate_min=",rate_min, " rate=",rate, " RTT=",-sendtime[int(lis[0].split(" ")[1])//rate_of_data]+recvtime[int(lis[0].split(" ")[1])//rate_of_data], " ",math.floor(window))
                                                strtmp=""
                                                countuseless=0
                                                for j in range(3):
                                                    countuseless+=len(lis[j])+1
                                                if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                                    sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                                    duration_recv.append([(int(lis[0].split(" ")[1])),recvtime[(int(lis[0].split(" ")[1]))//rate_of_data]-deploy_time])
                                                    temp=int(lis[0].split(" ")[1])//rate_of_data
                                                    if(sendtime[temp]<=recvtime[temp]):
                                                        if(rtt>recvtime[temp]-sendtime[temp]):
                                                            window+=1/window
                                                        else:
                                                            window=1
                                                        rtt=(1-0.125)*rtt+0.125*(recvtime[temp]-sendtime[temp])
                                                        devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                                        timeout=3*rtt+4*devrtt
                                                        rate=max(rate_min,rtt/3)
                                        lock1.release()
                                except Exception as e:
                                    # print("Skip")
                                    skip+=1
                                    window=1
                                    if(check_length(sublist)<20):
                                        rate_min=(0.7)*1.05*rate_min+ (1-0.7)*rate_min
                                    if(100>check_length(sublist)>20):
                                        rate_min=(0.7)*1.01*rate_min+ (1-0.7)*rate_min
                                    if(300>check_length(sublist)>100):
                                        rate_min=(0.7)*1.005*rate_min+ (1-0.7)*rate_min
                                    if(600>check_length(sublist)>300):
                                        rate_min=(0.7)*1.003*rate_min+ (1-0.7)*rate_min
                                    if(check_length(sublist)>600):
                                        rate_min=(0.7)*1.002*rate_min+ (1-0.7)*rate_min
                                    rate=max(rate_min,timeout/2)
                k[i]=k[i]+rate_of_data*cw
                        
            
def main():
    
    tstart=time.time()
    global deploy_time
    global cw
    findNol()
    
    
    thread = []
    for i in range (cw):
            thread.append(threading.Thread(target=implement_thread, args=(i,)))  
    deploy_time=time.time()
    for i in range (cw):
            thread[i].start()
    for i in range (cw):
            thread[i].join()
            
            
            
    SUBMIT(submit)
    CLOSE()
    
    
    # Plomts
    send=[k[0] for k in duration_send]
    recv=[k[0] for k in duration_recv]
    timeline_send=[k[1] for k in duration_send]
    timeline_recv=[k[1] for k in duration_recv]
    plot_recv=plt.scatter(recv, timeline_recv,color= "orange",  
            marker= "*", s=60)
    plot_send=plt.scatter(send, timeline_send,color= "blue",  
            marker= "o", s=5)
    plt.legend([plot_recv,plot_send],["Recvd Lines","Send Request"])
    plt.xlabel('Offset') 
    plt.ylabel('Time(in seconds)') 
    plt.title('Offset vs Time Graph') 
    plt.show()


    
main()