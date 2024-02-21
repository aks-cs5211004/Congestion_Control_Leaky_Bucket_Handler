import hashlib
import math
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# SERVERS
# servername="vayu.iitd.ac.in"
servername="10.17.7.218"
# servername="10.17.7.134"
# servername="10.17.51.115"
# servername='10.17.6.5'
servername="127.1.1.0"
serverport=9802
server_socket = socket(AF_INET, SOCK_DGRAM)


# THE HUERISTICS?
cw=10
if(servername=='127.1.1.0'):
    diff_min=0.0084
else:
    diff_min=0.0084
diff_min_0=diff_min
diff=diff_min
rtt=0.001
timeout=2*rtt
s_recv=0.22
s_skip=0.85
window=1

# OTHER HELPER VARIABLES AND DATA STRUCTURES
skip=0
sqish=0
noreq=0
submit=""
sublist=[]
sendtime=[]
recvtime=[]
diff_of_data=1448
nol=0
k=[(i*diff_of_data) for i in range(cw)]
devrtt=0
duration_send=[]
duration_recv=[]
deploy_time=0
ts=0
squishstart=0
squishstate=0
equal=0
tsquish=0

# PLOTS ARRAYS
diff_array=[]
samplertt_array=[]
estimatrtt_array=[]
win_array=[]
timeout_array=[]

# LOCKS
lock1=threading.Lock()
lock2=threading.Lock()
lock3=threading.Lock()
lock4=threading.Lock()
lock5=threading.Lock()


# CLOSE
def CLOSE():
        server_socket.close()
        

# SUBMIT
def SUBMIT(submit):
    diff=0.04
    for i in range(len(sublist)):
        submit+=sublist[i]
    submit=submit[:len(submit)-1]
    result=hashlib.md5(submit.encode())
    print(result.hexdigest())
    sentence = "Submit: cs5211004@blue_flag\nMD5: "+str(result.hexdigest())+"\n\n"
    while(True):
        try:
            if(time.time()-ts>diff):
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
          
          
# INITITE CONNECTION(RESET) AND FIND NO. OF BYTES TO BE RECEIVED- MAKE THE DATA STRUCTURE "SUBLIST" ACCORDINGLY
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
    diff=0.1
    while(True):
            try:
                if(time.time()-ts>diff):
                    server_socket.sendto(sentence.encode(),(servername, serverport))
                    server_socket.settimeout(2)
                    st, serverAddress = server_socket.recvfrom(4096)
                    ts=time.time()
                    break
            except Exception as e:
                print("Server Error")
                ts=time.time()
                continue
    nol=int(st.decode().split("\n")[0].split(" ")[1])
    print("NOL: ", nol)
    print("Len of Sublist: ", nol//diff_of_data +1)
    sublist=["" for i in range((nol//diff_of_data)+1)]
    sendtime=[0 for i in range((nol//diff_of_data)+1)]
    recvtime=[0 for i in range((nol//diff_of_data)+1)]
    
    
# HELPER FUNCTIONS
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
    


# A THREAD FOR ONE CELL OF THE WINDOW
def implement_thread(i):
    # ALL VARIABLES DEFINED GLOBALLY
    global sublist
    global k
    global skip
    global sqish
    global cw
    global noreq
    global rtt
    global devrtt
    global timeout
    global diff
    global diff_min_0
    global diff_min
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
    global s_skip
    global s_recv
    global diff_array
    global samplertt_array
    global estimatrtt_array
    global timeout_array
    ts=time.time()
    
    # 
    while(check_filled(sublist,i)):
            lock5.acquire()
            k[i]=i*diff_of_data
            # print("Filled Sublist=",check_length(sublist))
            lock5.release()
            while(k[i]<=(nol//diff_of_data)*diff_of_data and (time.time()-ts>diff)):
                if(sublist[k[i]//diff_of_data]==""):
                            tempwindow=window
                            lock4.acquire()
                            if((k[i] )//diff_of_data<len(sublist) and sublist[(k[i] )//diff_of_data]==""):
                                sentence = "Offset: "+str(k[i] )+"\nNumBytes: "+str(diff_of_data)+"\n\n"
                                server_socket.sendto(sentence.encode(),(servername, serverport))
                                if(sublist[(k[i] )//diff_of_data]==""):
                                    sendtime[(k[i] )//diff_of_data]=time.time()
                                    duration_send.append([k[i] ,sendtime[(k[i] )//diff_of_data]-deploy_time])
                                ts=time.time()
                                noreq+=1
                            lock4.release()
                            
                        
                            try:
                                server_socket.settimeout(timeout)
                                st, serverAddress = server_socket.recvfrom(4096)
                                lis=st.decode().split("\n")
                                if(sublist[(int(lis[0].split(" ")[1]))//diff_of_data]=="" and lis[2]==""):
                                    recvtime[(int(lis[0].split(" ")[1]))//diff_of_data]=time.time()
                                if(sublist[(int(lis[0].split(" ")[1]))//diff_of_data]==""):
                                    lock1.acquire()
                                    lis=st.decode().split("\n")
                                    if(lis[2]!=""):
                                        tsquish=time.time()
                                        sqish+=1
                                        print("QISHED:..............",squishstart," diff= ",diff)
                                        squishstart+=1
                                        # 40 BECAUSE SOME QUISHES MAY GET SKIPPED
                                        if(squishstart>=40):
                                            window=1
                                            squishstart=0
                                            # ONCE SQUISHED WONT BE SQUISHED AGAIN ;UPDATE SENSITIVITY OF TIME DIFF UPDATES FOR CORRECT RECEIVED LINES AND SKIPS 
                                            diff_min_0=(0.35)*1.8*diff_min_0+ (1-0.35)*diff_min_0
                                            s_skip=min(1,1.3*s_skip)
                                            s_recv=min(1,s_recv/2)
                                        diff=max(max(diff_min,diff_min_0),(tsquish-sendtime[int(lis[0].split(" ")[1])//diff_of_data])/3)
                                        diff_array.append([diff,tsquish-deploy_time])
                                    else:
                                        
                                        squishstart=0
                                        listofk=[k[i]]
                                        if(int(lis[0].split(" ")[1]) in listofk):
                                            print("GOT   CORRECT LINE ",check_length(sublist), "diff ",diff)
                                            strtmp=""
                                            countuseless=0
                                            for j in range(3):
                                                countuseless+=len(lis[j])+1
                                            if(sublist[(int(lis[0].split(" ")[1]))//diff_of_data]==""):
                                                sublist[(int(lis[0].split(" ")[1]))//diff_of_data]=st.decode()[countuseless:]
                                                
                                                duration_recv.append([(int(lis[0].split(" ")[1])),recvtime[(int(lis[0].split(" ")[1]))//diff_of_data]-deploy_time])
                                                temp=int(lis[0].split(" ")[1])//diff_of_data
                                                if(sendtime[temp]<=recvtime[temp]):
                                                    # TIMEOUT UPDATES
                                                    if(rtt>recvtime[temp]-sendtime[temp]):
                                                        window+=1
                                                    else:
                                                        window=1
                                                    rtt=(1-0.18)*rtt+0.18*(recvtime[temp]-sendtime[temp])
                                                    devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                                    timeout=2*rtt+4*devrtt
                                                    
                                                    # DIFF UPDATE
                                                    diff_min=(s_recv)*diff_min/1.03+ (1-s_recv)*diff_min
                                                    # s_recv=max(s_recv/1.000002,0)
                                                    diff=max(max(diff_min,diff_min_0),rtt/3)
                                                    
                                                    # PLOTS
                                                    tupdate=time.time() 
                                                    diff_array.append([diff,tupdate-deploy_time])
                                                    estimatrtt_array.append([rtt,tupdate-deploy_time])
                                                    timeout_array.append([timeout,tupdate-deploy_time])
                                                    samplertt_array.append([recvtime[temp]-sendtime[temp],tupdate-deploy_time])
                                                    
                                                
                                                    
                                        else:
                                            print("GOT INCORRECT LINE ",check_length(sublist), "diff ",diff)
                                            strtmp=""
                                            countuseless=0
                                            for j in range(3):
                                                countuseless+=len(lis[j])+1
                                            if(sublist[(int(lis[0].split(" ")[1]))//diff_of_data]==""):
                                                sublist[(int(lis[0].split(" ")[1]))//diff_of_data]=st.decode()[countuseless:]
                                                
                                                duration_recv.append([(int(lis[0].split(" ")[1])),recvtime[(int(lis[0].split(" ")[1]))//diff_of_data]-deploy_time])
                                                temp=int(lis[0].split(" ")[1])//diff_of_data
                                                if(sendtime[temp]<=recvtime[temp]):
                                                    # TIMEOUT UPDATES
                                                    window=1
                                                    rtt=(1-0.4)*rtt+0.4*(recvtime[temp]-sendtime[temp])
                                                    devrtt=(1-0.25)*devrtt+0.25*abs(recvtime[temp]-sendtime[temp]-rtt)
                                                    timeout=2*rtt+4*devrtt
                                                    # DIFF UPDATES
                                                    diff=max(max(diff_min,diff_min_0),rtt/3)
                                                    # PLOTS
                                                    tupdate=time.time()
                                                    diff_array.append([diff,tupdate-deploy_time])
                                                    estimatrtt_array.append([rtt,tupdate-deploy_time])
                                                    timeout_array.append([timeout,tupdate-deploy_time])
                                                    samplertt_array.append([recvtime[temp]-sendtime[temp],tupdate-deploy_time])
                                                    
                                    lock1.release()
                            except Exception as e:
                                skip+=1
                                window=1

                                # DIFF UPDATE
                                diff_min=(s_skip)*(1.03)*diff_min+ (1-s_skip)*diff_min
                                # s_skip=min(s_skip*1.000002,1)
                                diff=max(max(diff_min,diff_min_0),rtt/2)
                                
                                # PLOTS
                                tupdate=time.time()
                                timeout_array.append([timeout,tupdate-deploy_time])
                                diff_array.append([diff,tupdate-deploy_time])
                                
                                
                k[i]=k[i]+diff_of_data*cw
                        
            
def main():
    
    tstart=time.time()
    global deploy_time
    global cw
    # START CONNECTION
    findNol()
    
    # MAKE THREADS; START NO. OF THREADS = CONGESTION WINDOW SIZE; JOIN AFTER SUBLIST GETS FILLED
    thread = []
    for i in range (cw):
            thread.append(threading.Thread(target=implement_thread, args=(i,)))  
    deploy_time=time.time()
    for i in range (cw):
            thread[i].start()
    for i in range (cw):
            thread[i].join()
            
            
    # submit and close
    SUBMIT(submit)
    CLOSE()
    
    
    # PLOTS
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
    
    diff_c=[k[0] for k in diff_array]
    time_c=[k[1] for k in diff_array]
    plot_send=plt.plot(time_c, diff_c,color= "green")
    plt.xlabel('Time(in seconds)') 
    plt.ylabel('Time Difference between 2 Requests') 
    plt.title('Time Difference vs Time Graph') 
    plt.show()
    
    estrtt_c=[k[0] for k in estimatrtt_array]
    samrtt_c=[k[0] for k in samplertt_array]
    time_c=[k[1] for k in samplertt_array]
    plot_send=plt.plot(time_c, estrtt_c,color= "orange")
    plot_send=plt.plot(time_c, samrtt_c,color= "yellow")
    plt.xlabel('Time(in seconds)') 
    plt.ylabel('Variation of Sample RTT and Estimated RTT') 
    plt.title('RTT vs Time Graph') 
    plt.show()
    
    timeout_c=[k[0] for k in timeout_array]
    time_c=[k[1] for k in timeout_array]
    plot_send=plt.plot(time_c, timeout_c,color= "red")
    plt.xlabel('Time(in seconds)') 
    plt.ylabel('Calculated Timeout(in s)') 
    plt.title('Timeout vs Time Graph') 
    plt.show()
    
    


    
main()