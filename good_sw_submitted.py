import hashlib
import random
import select
import threading
import time
from socket import *

import matplotlib.pyplot as plt

# server
servername="vayu.iitd.ac.in"
# servername="10.17.7.218"
# servername="10.17.7.134"
# servername="10.17.51.115"
# servername='10.17.6.5'
servername="127.1.1.0"
serverport=9801
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.settimeout(0.0001)
sublist=[]



# Time array
duration_send = []
duration_recv = []
first_send_request=[]
new_lists_iter=[]
offset_iter=[]
timeout_update=[]
avg=[]
avgrtt=[]

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
        skip=0
        sqish=0
        noreq=0
        rate_0=0.004
        rate=0.008
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
                        st, serverAddress = server_socket.recvfrom(4096)
                        ts=time.time()
                        break
                except Exception as e:
                    ts=time.time()
                    continue
        nol=int(st.decode().split("\n")[0].split(" ")[1])
        sublist=["" for i in range((nol//rate_of_data)+1)]

        
        
        # SEND REQUESTS
            
        print("NOL: ", nol)
        k=0
        ts=time.time()
        while(check_filled(sublist)):
            print("Filled Sublist",check_length(sublist))
            offset_this_iter=[]
            temp=check_length(sublist)
            for i in range(len(sublist)):
                if(sublist[i]==""):
                    k=rate_of_data*i
                    sentence = "Offset: "+str(k)+"\nNumBytes: "+str(rate_of_data)+"\n\n"
                    if(time.time()-ts>rate):
                        try:
                            noreq+=1
                            samplertt=time.time()
                            server_socket.sendto(sentence.encode(),(servername, serverport))
                            ts=time.time()
                            tnow=time.time()
                            duration_send.append([k,tnow-deploy_time])
                            server_socket.settimeout(timeout)
                            st, serverAddress = server_socket.recvfrom(4096)
                            lis=st.decode().split("\n")
                            samplertt=time.time()-samplertt
                            
                            # avg.append(samplertt)
                            # rtt=sum(avg)/len(avg)
                            rtt=(1-0.3)*rtt+0.3*(samplertt)
                            devrtt=(1-0.25)*devrtt+0.25*abs(samplertt-rtt)
                            timeout=rtt+4*devrtt
                            # timeout=2*rtt
                            
                            if(lis[2]!=""):
                                sqish+=1
                                print("QISHED:................",k)
                            else:
                                if(int(lis[0].split(" ")[1])==k):
                                    strtmp=""
                                    countuseless=0
                                    for j in range(3):
                                        countuseless+=len(lis[j])+1
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                        sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        tnow_r=time.time()
                                        duration_recv.append([(int(lis[0].split(" ")[1])),tnow_r-deploy_time])
                                        offset_this_iter.append(int(lis[0].split(" ")[1]))
                                        offset_iter.append(offset_this_iter)
                                    # print("SERVER:",lis[0], " REM LINES: ",(nol-k))
                                else:
                                    # print("GOT INCORRECT LINE ",(int(lis[0].split(" ")[1])))
                                    strtmp=""
                                    countuseless=0
                                    for j in range(3):
                                        countuseless+=len(lis[j])+1
                                    if(sublist[(int(lis[0].split(" ")[1]))//rate_of_data]==""):
                                        sublist[(int(lis[0].split(" ")[1]))//rate_of_data]=st.decode()[countuseless:]
                                        tnow_r=time.time()
                                        duration_recv.append([(int(lis[0].split(" ")[1])),tnow_r-deploy_time])
                                        offset_this_iter.append(int(lis[0].split(" ")[1]))
                                        offset_iter.append(offset_this_iter)
                            
                        except Exception as e:
                            # print("SKIPPED ",k)
                            skip+=1
            new_lists_iter.append(check_length(sublist))
            timeout_update.append(timeout)
            avgrtt.append(rtt)
            
                        
        #Plomts
        j=0
        for i in range((nol//rate_of_data)+1):
            c=0
            for j in range (len(duration_send)):
                if(i*rate_of_data==duration_send[j][0] and c==0):
                    first_send_request.append(duration_send[j])
                    c=1
        
                
            
                
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
    
    # # Plomts
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
    # plt.ylim(2,3)
    plt.title('Offset vs Time Graph') 
    # plt.savefig("sw_100_seq_vs_time.jpg")
    plt.show()
    
    # print(len(duration_send))
    # print(len(duration_recv))
    # print(len(first_send_request))
    
    # diff=[duration_recv[k][1]-first_send_request[k][1] for k in range(len(duration_recv))]
    # offset=[k[0] for k in duration_recv]
    # plot_diff=plt.scatter(offset,diff,color= "orange",  
    #         marker= "o", s=30)
    # plt.xlabel('Offset') 
    # plt.ylabel('Time Difference(in seconds)') 
    # plt.title('Offset vs Time Difference Graph') 
    # plt.show()
    
    
    # iter=[k for k in range(len(new_lists_iter))]
    # new_iter=[k for k in new_lists_iter]
    # plot_new_iter=plt.plot(iter,new_iter,color= "red")
    # plt.xlabel('Iterations') 
    # plt.ylabel('Cummulative Number of Bytes Receives (*1448 bytes)') 
    # plt.title('Iterations Vs Number of Bytes received') 
    # plt.show()
    
    # iter=[k for k in range(len(offset_iter))]
    # offset=[k[0] for k in offset_iter]
    # plot_offset_iter=plt.scatter(iter,offset,color= "yellow", marker= "^", s=30)
    # plt.xlabel('Iterations in which data was received ') 
    # plt.ylabel('New Offsets Received') 
    # plt.title('Iterations Vs New Offset Received') 
    # plt.show()


    # x=[k for k in range(len(timeout_update))]
    # y=[k for k in timeout_update]
    # plot_timeout=plt.plot(x,y,color= "green")
    # plt.xlabel('Iterations') 
    # plt.ylabel('Updated timeout(in s)') 
    # plt.title('Iterations Vs Timeout') 
    # # plt.savefig("sw_100_diff.jpg")
    # plt.show()
    
    # x=[k for k in range(len(avgrtt))]
    # y=[k for k in avgrtt]
    # plot_timeout=plt.plot(x,y,color= "green")
    # plt.xlabel('Iterations') 
    # plt.ylabel('Updated RTT(in s)') 
    # plt.title('Iterations Vs RTT') 
    # # plt.savefig("sw_100_diff.jpg")
    # plt.show()
    
    


    
main()