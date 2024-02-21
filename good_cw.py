import hashlib
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# server
# servername='10.194.1.66'
servername='10.17.7.218'
# servername='127.1.1.0'
serverport=9801
server_socket = socket(AF_INET, SOCK_DGRAM)


# Variables
cw=10
skip=0
sqish=0
noreq=0
rate_min=0.017
rate=0
submit=""
sublist=[]
rate_of_data=1448
nol=0
k=[(i*rate_of_data) for i in range(cw)]
rtt_0=0.000018
rtt=0.000018
timeout=2*rtt
devrtt=0
duration_send=[]
duration_recv=[]
deploy_time=0
ts=0

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
    ts=time.time()
    while(check_filled(sublist,i)):
            lock5.acquire()
            k[i]=i*rate_of_data
            # print("Fulfilled Equation of Eminence ",check_length(sublist))
            lock5.release()
            while(k[i]<=(nol//rate_of_data)*rate_of_data):
                    if(sublist[k[i]//rate_of_data]==""):
                        if(time.time()-ts>rate):
                            try:
                                server_socket.settimeout(timeout)
                                lock4.acquire()
                                samplertt=time.time()
                                sentence = "Offset: "+str(k[i])+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                                server_socket.sendto(sentence.encode(),(servername, serverport))
                                ts=time.time()
                                tnow=time.time()
                                duration_send.append([k[i],tnow-deploy_time])
                                noreq+=1
                                lock4.release()
                            
                                st, serverAddress = server_socket.recvfrom(4096)
                                lis=st.decode().split("\n")
                                tnow_r=time.time()
                                duration_recv.append([(int(lis[0].split(" ")[1])),tnow_r-deploy_time])
                                
                                lock1.acquire()
                                samplertt=time.time()-samplertt
                                rtt=(1-0.3)*rtt+0.3*(samplertt)
                                devrtt=(1-0.25)*devrtt+0.25*abs(samplertt-rtt)
                                timeout=rtt+4*devrtt
                                rate=max(rtt,rate_min)
                                # rate=max(200*rtt/cw,rate_min)
                                # print(rate)
                                lis=st.decode().split("\n")
                                if(lis[2]!=""):
                                    sqish+=1
                                    print("QISHED:..............",k[i])
                                    lock1.release()
                                else:
                                    if(int(lis[0].split(" ")[1])==k[i]):
                                        strtmp=""
                                        countuseless=0
                                        for j in range(3):
                                            countuseless+=len(lis[j])+1
                                        sublist[k[i]//rate_of_data]=st.decode()[countuseless:]
                                        # print("SERVER:",lis[0])
                                        lock1.release()
                                    else:
                                        strtmp=""
                                        countuseless=0
                                        for j in range(3):
                                            countuseless+=len(lis[j])+1
                                        sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        lock1.release()
                            except Exception as e:
                                skip+=1
                    k[i]=k[i]+rate_of_data*cw
                            
            
def main():
    
    # Make Initial connection
    global deploy_time
    tstart=time.time()
    findNol()
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
    # print("NOREQ=",noreq)
    
    # tend=time.time()
    # print(tend-tstart)
    
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
    # plt.savefig("sw_100_seq_vs_time.jpg")
    plt.show()


    
main()