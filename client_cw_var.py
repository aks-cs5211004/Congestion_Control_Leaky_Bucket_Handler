import hashlib
import random
import select
import threading
import time
from socket import *

# server
servername='127.0.0.1'
serverport=9801
server_socket = socket(AF_INET, SOCK_DGRAM)


# Variables
cw_0=500
cw=1
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
k=0
rtt_0=0.000018
rtt=0.18
timeout=2*rtt
devrtt=0
stop_thread=[0 for i in range(10000)]
thread=[]
counter=0

# Locks
lock1=threading.Lock()
lock2=threading.Lock()
lock3=threading.Lock()

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
    global thread
    global counter
    global stop_thread
    while(k<=(nol//rate_of_data)*rate_of_data):
            if(sublist[k//rate_of_data]!=""):
                    k=k+rate_of_data*cw
                    continue
            if(stop_thread[i]==1):
                thread.pop()
                break
            try:
                if(time.time()-ts>rate):
                    samplertt=time.time()
                    server_socket.settimeout(timeout)
                    sentence = "Offset: "+str(k)+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                    server_socket.sendto(sentence.encode(),(servername, serverport))
                    noreq+=1
                    st, serverAddress = server_socket.recvfrom(4096)
                    # lock3.acquire()
                    counter+=1
                    if(counter>=cw):
                        counter=0
                        cw+=1
                        print("New creation ")
                        make_thread(cw+1) 
                    # samplertt=time.time()-samplertt
                    # rtt=(1-0.125)*rtt+0.125*(samplertt)
                    # devrtt=(1-0.25)*devrtt+0.25*abs(samplertt-rtt)
                    # timeout=rtt+4*devrtt
                    # print("Estimate of rate ",rate)
                    # lock3.release()
                    lock1.acquire()
                    lis=st.decode().split("\n")
                    ts=time.time()
                    if(lis[2]!=""):
                        sqish+=1
                        print("QISHED:..............",k)
                        lock1.release()
                        continue
                    else:
                        if(int(lis[0].split(" ")[1])==k):
                            strtmp=""
                            countuseless=0
                            for j in range(3):
                                countuseless+=len(lis[j])+1
                            sublist[k//rate_of_data]=st.decode()[countuseless:]
                            k=k+rate_of_data*cw
                            # print("SERVER:",lis[0])
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
                # lock2.acquire()
                ts=0
                # print("SKIPPED ",k)
                # for i in range(cw//2+1,cw):
                #     kill_thread(i)
                # cw=cw//2+1
                skip+=1
                # lock2.release()
                continue
                
            
            
def kill_thread(i):
    global stop_thread
    stop_thread[i]=1

def make_thread(i):
    global thread
    thread.append(threading.Thread(target=implement_thread, args=(i,)))  
    thread[i].start()
    
def main():
    
    # Make Initial connection
    ts=time.time()
    findNol()
    global thread
    global cw
    # Create threads
    for i in range (cw):
            thread.append(threading.Thread(target=implement_thread, args=(i,)))  
    # Start Threads
    
    for i in range (cw):
            thread[i].start()
            
    for i in range (cw):
            thread[i].join()
    
            
    SUBMIT(submit)
    CLOSE()
    print("NOREQ=",noreq)
    
    te=time.time()
    print(te-ts)


    # Plots
    # x=[k[0] for k in duration]
    # y=[k[1] for k in duration]
    # plt.plot(x, y) 
    # plt.xlabel('x - axis') 
    # plt.ylabel('y - axis') 
    # plt.title('My first graph!') 
    # plt.show() 

    
main()