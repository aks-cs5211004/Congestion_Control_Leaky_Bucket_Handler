import os
import sys


def routers():
    dst=sys.argv[2]
    ttl=1
    s=" "
    router=[]
    found=False
    while(found!=True):
        c=os.popen("ping"+ s+ dst+ s+ "-c 1" + s+ "-t" +s+ str(ttl)).read()
        l=c.split("\n")

        #find router
        if(l[1].split(s)[0]=="64"):
            found= True
            if(l[1].split(s)[4][0]=="("):
                router.append(l[1].split(s)[4][1:-2])
            else:
                router.append(l[1].split(s)[3])
        else:
            if(l[1]==''):
                router.append("")
                ttl=ttl+1
                continue
            elif (l[1].split(s)[2][0]=="("):
                router.append(l[1].split(s)[2][1:-1])
            else:
                router.append(l[1].split(s)[1])
            
        #increment ttl  
        ttl=ttl+1
    return(router)

def times(router):
    time=[]
    s=" "
    for rout in router:
        if(rout==""):
            time.append("*")
            continue
        c_known=os.popen("ping"+ s+ rout+ s+ "-c 1").read()
        l_known=c_known.split("\n")
        if(l_known[len(l_known)-2].split(s)[0]!="rtt"):
            time.append("*")
        else:
            time.append(l_known[len(l_known)-2].split(s)[3].split("/")[1])
    return time
    
    
    
    
router=routers()
time1=times(router)
time2=times(router)
time3=times(router)
s=" "
dst=sys.argv[2]
print("traceroute to "+router[len(router)-1]+s+"("+router[len(router)-1]+")"+", 64 hops max")
for i in range(len(router)):
    if(time1[i]=="*" and time2[i]=="*" and time3[i]=="*"):
        print(str(i+1)+s+s+s+"*"+s+s+"*"+s+s+"*")
    else:
        print(str(i+1)+s+s+s+str(router[i])+s+s+str(time1[i])+"ms"+s+s+str(time2[i])+"ms"+s+s+str(time3[i])+"ms")