import hashlib
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# server
servername='127.0.0.1'
serverport=9801
server_socket = socket(AF_INET, SOCK_DGRAM)


# Variables
cw_0=500
cw=10
skip=0
sqish=0
noreq=0
rate_0=0.00305
rate_min=0.005
rate=0.005
submit=""
sublist=[]
rate_of_data=1448
nol=0
k=[(i*rate_of_data) for i in range(cw)]
rtt_0=0.000018
rtt=0.000018
timeout=2*rtt
devrtt=0
duration_recv=[]
duration_req=[]
deploy_time=0

# Locks
lock1=threading.Lock()
lock2=threading.Lock()
lock3=threading.Lock()
lock4=threading.Lock()
lock5=threading.Lock()

#SERVER FUNCTIONS
def CLOSE():
        server_socket.close()
        # print("Server Socket Closed")
        
def SUBMIT(submit):
    rate=0.004
    # f1=open("data.txt","w")
    for i in range(len(sublist)):
        submit+=sublist[i]
    submit=submit[:len(submit)-1]
    # f1.write(submit)
    # f1.close()
    result=hashlib.md5(submit.encode())
    print(result.hexdigest())
    sentence = "Submit: cs5211004@blue_flag\nMD5: "+str(result.hexdigest())+"\n\n"
    while(True):
        try:
            if(time.time()-ts>rate):
                server_socket.sendto(sentence.encode(),(servername, serverport))
                server_socket.settimeout(1)
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
    # RESET
    sentence = "Reset\n\n"
    server_socket.sendto(sentence.encode(),(servername, serverport))
    # NOLines
    sentence = "SendSize\n\n"
    while(True):
            try:
                if(time.time()-ts>rate):
                    server_socket.sendto(sentence.encode(),(servername, serverport))
                    st, serverAddress = server_socket.recvfrom(4096)
                    ts=time.time()
                    break
            except Exception as e:
                ts=time.time()
                continue
    nol=int(st.decode().split("\n")[0].split(" ")[1])
    print("NOL: ", nol)
    sublist=["" for i in range((nol//rate_of_data)+1)]
    print(len(sublist))
    

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
    global duration_recv
    global duration_req
    while(k[i]<=(nol//rate_of_data)*rate_of_data):
            if(sublist[k[i]//rate_of_data]!=""):
                    k[i]=k[i]+rate_of_data*cw
                    continue
            try:
                if(time.time()-ts>rate):
                    samplertt=time.time()
                    server_socket.settimeout(timeout)
                    sentence = "Offset: "+str(k[i])+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                    lock4.acquire()
                    server_socket.sendto(sentence.encode(),(servername, serverport))
                    duration_req[k[i]//rate_of_data]=time.time()-deploy_time
                    lock4.release()
                    noreq+=1
                    st, serverAddress = server_socket.recvfrom(4096)
                    lis=st.decode().split("\n")
                    duration_recv[(int(lis[0].split(" ")[1]))//rate_of_data]=time.time()-deploy_time

                    
                    lock3.acquire()
                    samplertt=time.time()-samplertt
                    rtt=(1-0.3)*rtt+0.3*(samplertt)
                    devrtt=(1-0.25)*devrtt+0.25*abs(samplertt-rtt)
                    timeout=rtt+4*devrtt
                    rate=max(rtt/cw,rate_min)
                    print("Estimate of rate ",rate)
                    lock3.release()
                    
                    lock1.acquire()
                    lis=st.decode().split("\n")
                    ts=time.time()
                    if(lis[2]!=""):
                        sqish+=1
                        print("QISHED:..............",k[i])
                        lock1.release()
                        continue
                    else:
                        if(int(lis[0].split(" ")[1])==k[i]):
                            strtmp=""
                            countuseless=0
                            for j in range(3):
                                countuseless+=len(lis[j])+1
                            sublist[k[i]//rate_of_data]=st.decode()[countuseless:]
                            k[i]=k[i]+rate_of_data*cw
                            print("SERVER:",lis[0])
                            lock1.release()
                            continue
                        else:
                            strtmp=""
                            countuseless=0
                            for j in range(3):
                                countuseless+=len(lis[j])+1
                            sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                            lock1.release()
                            continue
            except Exception as e:
                lock2.acquire()
                ts=time.time()
                print("SKIPPED ",k[i])
                skip+=1
                lock2.release()
                continue
                
            
def main():
    
    # Make Initial connection
    global deploy_time
    global duration_recv
    global duration_req
    ts=time.time()
    findNol()
    duration_recv=[0 for i in range(nol//rate_of_data +1)]
    duration_req=[0 for i in range(nol//rate_of_data +1)]
    # Create threads
    thread = []
    for i in range (cw):
            thread.append(threading.Thread(target=implement_thread, args=(i,)))  
    # Start Threads
    
    deploy_time=time.time()
    for i in range (cw):
            thread[i].start()
    
    # Join Threads
    for i in range (cw):
            thread[i].join()
            
    SUBMIT(submit)
    CLOSE()
    print("NOREQ=",noreq)
    
    te=time.time()
    print(te-ts)
    
    # Plomts
    x=[i for i in range(len(duration_recv))]
    y=[k for k in duration_recv]
    z=[k for k in duration_req]
    diff=[duration_recv[k]-duration_req[k] for k in range(len(duration_recv))]
    plt.plot(x, y, color='blue') 
    plt.plot(x, z,'go',color='black')
    plt.xlabel('Bytes/Sequence number') 
    plt.ylabel('Time') 
    plt.title('Sequence number vs Time Graph') 
    
    plt.savefig("seq_time_cw.jpg")


    
main()