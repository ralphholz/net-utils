#!/usr/bin/env python3

import ipaddress
import re
import sys
import csv
import numpy as np


def matchIPToPrefixlist(ip,ases,pfxes):
    resas = {}
    respfx = {}
    unannounced = list()
    j=0

    for i in ip:
        # IPv6 address as integer, to compare with numpy
        thishost = int(ipaddress.IPv4Address(i))

        resg = np.greater_equal(thishost, npfxLow)
        resl = np.less_equal(thishost,npfxHigh)

        match = resg * resl

        matchindex = np.argwhere(match==True)
        # This can return multiple matches!
        # IPs can be in multiple announced prefixes (sub delegations)
        # In our case we are only focussing on the longest prefix, so we need to find it:

        matchpfx = []
        matchsubnets = []

        # First: get all matching prefixes
        for m in matchindex:
            matchpfx.append(pfxlist[m[0]])
            # Extract subnet mask to compare it.
            matchsubnets.append(pfxlist[m[0]][1])

        # This is the ID of the longest prefix in matchpfx
        if len(matchsubnets) == 0:
            unannounced.append(i);
            pfxes.append("-");
            ases.append("-");
            continue
        else:
            longestprefix = matchsubnets.index(max(matchsubnets))

        # Retrieve the longest prefix
        realmatch = matchpfx[longestprefix]
        net = realmatch[0] + "/" + str(realmatch[1])
        netas = realmatch[2]
        pfxes.append(net);
        ases.append(netas);
        j=j+1;
        try:
            respfx[net] += 1
        except KeyError:
            respfx[net] = 1

        try:
            resas[netas] += 1
        except KeyError:
            resas[netas] = 1

    return (resas,respfx,unannounced)





# NOTE: Modify here for MWN or IXP or both
source =  " "

filename=sys.argv[1];
pfxfile=sys.argv[2];

##pfxfile = 'ip2as/routeviews-rv6-20150906-1200.pfx2as'
pfxlist = []

with open(pfxfile, 'r') as pf:
    readcsv = csv.reader(pf, delimiter='\t')
    for row in readcsv:
        pfxlist.append([row[0], int(row[1]), row[2]])
pf.close()
print("Done reading pfx input file");

pfxdate = re.findall('\d{8}', pfxfile)
print("Using Caida Prefix2AS mapping from:", pfxdate)

# Total ASes, total pfx:
pfxperAS = {}
subnetsizes = [0]*129
for pfx in pfxlist:
    try:
        pfxperAS[pfx[2]] =  pfxperAS[pfx[2]] + 1
    except KeyError:
        pfxperAS[pfx[2]] = 1
    try:
        subnetsizes[pfx[1]] = subnetsizes[pfx[1]] + 1
    except KeyError:
        subnetsizes[pfx[1]] = 1
    
totalASes = len(pfxperAS)
totalPrefixes = len(pfxlist)
print("Total ASes:    ", totalASes)
print("Total Prefixes:", totalPrefixes)

## Turn prefix list into numpy array of lowest and highest address
print("Converting pfxes to numpy array"); 
npfxLow = np.empty(0)
npfxHigh = np.empty(0)

for p in pfxlist:
    thisnet = ipaddress.IPv4Network(p[0]+"/"+str(p[1]))
    
    npfxLow  = np.append(npfxLow, int(thisnet[0]))
    npfxHigh = np.append(npfxHigh, int(thisnet[thisnet.num_addresses-1]))
    
## benchmark: reading takes ~5 seconds

print("Done converting pfxes to numpy array"); 

#
### Load data file to analyze
#datalist = []
#
fh = open(filename, 'r');
#    for line in fh.readlines():
#        datalist.append(line.strip())
#fh.close()
#
#
#datalist2 = []
#chunksize = 15000
#
#for i in range(0,len(datalist), chunksize):
#    # Well, I expected an KeyError here, but obviously python is smart when using ranges to subindex lists
#    datalist2.append(datalist[i:i+chunksize])
#
#


ips = list();
ases=list();
pfxes=list();

### Goal memory-efficient readline
def ipReadline(i):


    with open(filename) as fh:
        for line in fh:
                ips.append(line.strip())
        
    return matchIPToPrefixlist(ips,ases,pfxes)
###

fh2 =open(filename+".aspfx.csv",'w');

print("Starting to read from data file ...")
ipReadline(0)
print("Done reading from data file, writing out ...")
for i in np.arange(len(ips)):
    #print (ips[i] + "," + ases[i] + "," + pfxes[i]);
    fh2.write(ips[i] + "," + ases[i] + "," + pfxes[i]+ "\n");
fh.close()


