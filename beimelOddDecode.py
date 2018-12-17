#If f(x) = 0 (i.e players do not want to reveal) then return 0
#Because then impossible (literally 0% probability) to recover all the relevant r anyway (because none of the parties have sent that).

import secrets

def lex_gen(bounds):
    elem = [0] * len(bounds)
    #print('elem', elem)
    while True:
        yield elem
        i = 0
        while elem[i] == bounds[i] - 1:
            elem[i] = 0
            i += 1
            if i == len(bounds):
                raise StopIteration
        elem[i] += 1

def cart_product(lists):
    bounds = [len(lst) for lst in lists]
    #print('bounds', bounds)
    for elem in lex_gen(bounds):
        yield [lists[i][elem[i]] for i in range(len(lists))]

def produceistring(grp, num):
    base = []
    for item in range(grp):
        base.append(str(item))
    lst = [base] * num
    cp = cart_product(lst)
    res = []
    for item in cp:
        res.append(','.join(item))
    return res

def calcR(ilist, istr, xsub, bob):
    if (len(xsub) == 0):
        return 0
    elif (ilist[0] == xsub[0]):
        #print('Equal', ilist[0], xsub[0])
        nxtlst = ilist[1:]
        nxtstr = ','.join(nxtlst)
        nxtx = xsub[1:]
        nxtbob = bob[1:]
        res = bob[0][1][istr] ^ calcR(nxtlst, nxtstr, nxtx, nxtbob)
        return res
    else:
        res = bob[0][0][istr]
        return res

def decode(shares,f, x, k, N):
    #print('Decoding...')
    try:
        kprime = (k - 1) // 2
        alice = shares[0][0]
        bob = shares[1:(kprime+1)]
        
        charlie = shares[(kprime+1):]
        xlist = x.split(',')
        kplust = xlist[kprime+1:]
        suff = ','.join(kplust)

        #print(shares)
        res = alice[suff]

        mid = produceistring(N, kprime)
        for i in mid:
            full = xlist[0] + ',' + i + ',' + suff
            try:
                if (f[full] == 0):
                    ilist = i.split(',')
                    subx = xlist[1:kprime+1]
                    #print(len(bob), len(subx))
                    res = res ^ calcR(ilist, i, subx, bob)
            except KeyError:
                f[full] = 0
                ilist = i.split(',')
                subx = xlist[1:kprime+1]
                #print(len(bob), len(subx))
                res = res ^ calcR(ilist, i, subx, bob)
        #print('Decoding done!')


        reqq = 0

        #print(k)
        #print(len(shares))
        #print(len(alice))
        #print(len(bob))
        #print(len(charlie))
        for j in range(kprime+2, k+1):
            thisj = j - kprime - 2
            #print(charlie[thisj])
            part = charlie[thisj][0]
            thisi = ','.join(kplust[thisj:])
            reqq = reqq ^ part[thisi]

        res = res ^ reqq

        return res
    
    except KeyError:
        print('Could not decode. Unauthorised subset. Returning a random bit')
        return secrets.randbits(1)

    except IndexError:
        print('Could not decode. Unauthorised subset. Returning a random bit.')
        return secrets.randbits(1)
