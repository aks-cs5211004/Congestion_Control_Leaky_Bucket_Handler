import hashlib
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# server
servername='10.184.27.253'
# servername='127.0.0.1'
serverport=9801
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.settimeout(0.0001)
sublist=[]



# Time array
first_send_request=[]
new_lists_iter=[]
offset_iter=[]
timeout_update=[]
avgrtt=[]
sendtime=[]
recvtime=[]

# Data Structures

# Functions

#SERVER FUNCTIONS
def CLOSE():
        server_socket.close()
        print("Server Socket Closed")
        
def SUBMIT(submit):
    rate=0.004
    f1=open("data1.txt","w")
    for i in range(len(sublist)):
        submit+=sublist[i]
    submit=submit[:len(submit)-1]
    f1.write(submit)
    f1.close()
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
            
            
def check_filled(list):
    for i  in range(len(list)):
        if(list[i]==""):
            return True
            break
    return False
def check_length(list,):
    c=0
    for i  in range(len(list)):
        if(list[i]!=""):
            c+=1
    return c
            
    
def server_recv(deploy_time):
        global sublist
        global first_send_request
        global new_lists_iter
        global sendtime
        global avgrtt
        global recvtime
        skip=0
        sqish=0
        noreq=0
        rate_0=0.00305
        rate=0.004
        submit=""
        rate_of_data=1448
        RTTavg=0
        timeout=0.0001
        rtt=0
        samplertt=0
        devrtt=0
        temp=0
        # RESET
        sentence = "Reset\n\n"
        server_socket.sendto(sentence.encode(),(servername, serverport))
        
        # NOLines
        sentence = "SendSize\n\n"
        ts=0
        while(True):
                try:
                    if(time.time()-ts>rate):
                        server_socket.sendto(sentence.encode(),(servername, serverport))
                        ts=time.time()
                        st, serverAddress = server_socket.recvfrom(4096)
                        break
                except Exception as e:
                    ts=time.time()
                    continue
        nol=int(st.decode().split("\n")[0].split(" ")[1])
        sublist=["" for i in range((nol//rate_of_data)+1)]
        sendtime=[0 for i in range((nol//rate_of_data)+1)]
        recvtime=[0 for i in range((nol//rate_of_data)+1)]
        
        
        # SEND REQUESTS
            
        print("NOL: ", nol)
        k=0
        ts=time.time()
        while(check_filled(sublist)):
            print("Filled Sublist",check_length(sublist))
            for i in range(len(sublist)):
                if(sublist[i]==""):
                    k=rate_of_data*i
                    sentence = "Offset: "+str(k)+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                    if(time.time()-ts>rate):
                        try:
                            
                            noreq+=1
                            # print("REQUEST FOR: ",k)
                            sendtime[k//rate_of_data]=time.time()
                            server_socket.sendto(sentence.encode(),(servername, serverport))
                            ts=time.time()
                            
                            server_socket.settimeout(timeout)
                            st, serverAddress = server_socket.recvfrom(4096)
                            lis=st.decode().split("\n")
                            recvtime[(int(lis[0].split(" ")[1]))//rate_of_data]=time.time()
                        
                            if(lis[2]!=""):
                                sqish+=1
                                print("QISHED:.............................",k)
                            else:
                                if(int(lis[0].split(" ")[1])==k):
                                    # print("GOT CORRECT:",(int(lis[0].split(" ")[1])))
                                    strtmp=""
                                    countuseless=0
                                    for j in range(3):
                                        countuseless+=len(lis[j])+1
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                        sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        
                                    temp=int(lis[0].split(" ")[1])//rate_of_data
                                    rtt=(1-0.125)*rtt+0.125*(recvtime[temp]-sendtime[temp])
                                    devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                    timeout=rtt+4*devrtt

                                    
                                else:
                                    # print("GOT INCORRECT LINE **************** ",(int(lis[0].split(" ")[1])))
                                    strtmp=""
                                    countuseless=0
                                    for j in range(3):
                                        countuseless+=len(lis[j])+1
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                        sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        
                                    temp=int(lis[0].split(" ")[1])//rate_of_data
                                    rtt=(1-0.08)*rtt+0.08*(recvtime[temp]-sendtime[temp])
                                    devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                    timeout=rtt+4*devrtt
                                    
                                    try:
                                        server_socket.settimeout(0.0000000000000001)
                                        st, serverAddress = server_socket.recvfrom(4096)
                                        lis=st.decode().split("\n")
                                        print("Trying To get Correct and Got it? Check k",(int(lis[0].split(" ")[1])))
                                        recvtime[(int(lis[0].split(" ")[1]))//rate_of_data]=time.time()
                                        strtmp=""
                                        countuseless=0
                                        for j in range(3):
                                            countuseless+=len(lis[j])+1
                                        if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                            sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        temp=int(lis[0].split(" ")[1])//rate_of_data
                                        rtt=(1-0.125)*rtt+0.125*(recvtime[temp]-sendtime[temp])
                                        devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                        timeout=rtt+4*devrtt
                                        
                                    except Exception as e:
                                        print("Not able to get Correct")
                                        skip+=1
                        except Exception as e:
                            # print("SKIPPED ",k)
                            skip+=1
                            
        
        SUBMIT(submit)
        print("SKIPS",skip)
        print("SQIUSHS",sqish)
        print("NO. OF REQUESTS ",noreq)
        CLOSE()

def main():
    # Make Initial connection
    ts=time.time()
    server_recv(ts)
    te=time.time()
    print(te-ts)
main()