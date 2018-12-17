# 0<=xi<N,M, whatever: Easier to code and doesn't really matter anyway because at no point is xi itself xor-ed to anything.
#Generating complete random f takes too long
#Interim measure until we have a better way of generating f or a pre-defined f:
#Set x according to user
#Set f according to user
#Optionally, generate x at random, set f(x) to be user choice, and generate f(x) at random as needed.

import secrets

def setf(allowed, f):
    for item in allowed:
        index = ','.join(item)
        f[index] = 1
    return f

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

def xgen(M, N, k):
    x = ''
    #print('Generating inputs...')
    for i in range(k):
        xi = 0
        if (i == 0):
            xi = secrets.randbelow(M)
        else:
            xi = secrets.randbelow(N)
        x = x + str(xi) + ','
    if (x[-1] == ','):
        x = x[:-1]
    #print('Inputs generated!')
    return x

def randomness(N, k, kprime):
    #print('Generating common randomness...')
    
    ralli = produceistring(N, kprime)
    talli = []
    for j in range(3, kprime + 2):
        talli = talli + produceistring(N, kprime + 2 - j)
    jalli = []
    for j in range(kprime + 2, k + 1):
        jalli.append(produceistring(N, k - j + 1))
    qalli = produceistring(N, k - kprime - 1)

    r = dict()
    t = dict()
    qj = []
    q = dict()

    for item in ralli:
        r[item] = secrets.randbits(1)

    for item in talli:
        t[item] = secrets.randbits(1)

    for j in range(kprime + 2, k + 1):
        nj = dict()
        for item in jalli[j-kprime-2]:
            nj[item] = secrets.randbits(1)
        qj.append(nj)

    for item in qalli:
        xorsum = 0
        rem = item.split(',')
        for j in range(kprime + 2, k + 1):
            thisj = j - kprime - 2
            sec = ','.join(rem[thisj:])
            need = qj[thisj][sec]
            xorsum = xorsum ^ need
        q[item] = xorsum

    #print('Randomness generated!')
    return r, t, qj, q

def share(slno, xi, rbits, N, k, kprime, f, s):
    r, t, qj, q = rbits
    if (slno==1):
        #print('alice')
        alice = dict()
        x1 = xi
        #i_{k'+2},...i_{k}
        ialice1 = produceistring(N, k-kprime-1)
        #i_{2}, ..., i_{k'+1}
        ialice2 = produceistring(N, kprime)
        for i in ialice1:
            si = s ^ q[i]
            for i2 in ialice2:
                full = x1 + ',' + i2 + ',' + i
                try:
                    if (f[full] == 0):
                        si = si ^ r[i2]
                except KeyError:
                    f[full] = 0
                    si = si ^ r[i2]
            alice[i] = si
        return [alice]

    elif (slno==2):
        #print('bob', slno, xi)
        bob2 = [dict(), dict()]
        #i_{2}, ..., i_{k'+1}
        ialice2 = produceistring(N, kprime)
        x2 = xi
        for i in ialice2:
            ilist = i.split(',')
            i2 = ilist[0]
            if not (i2 == x2):
                bob2[0][i] = r[i]
            else:
                sec = ','.join(ilist[1:])
                #print(slno, i, r[i], sec, t[sec])
                res = r[i] ^ t[sec]
                bob2[1][i] = res
        #print(bob2)
        return bob2

    elif (slno > 2) and (slno <= kprime):
        #print('bob', slno, xi)
        xj = xi
        j = slno
        bobj = [dict(), dict()]
        ibobj = produceistring(N, kprime + 2 - j)
        for i in ibobj:
            ilist = i.split(',')
            ij = ilist[0]
            sec = ','.join(ilist[1:])
            if not (ij == xj):
                bobj[0][i] = t[i]
            else:
                res = t[i] ^ t[sec]
                bobj[1][i] = res
        #print(slno, bobj)
        #print(bobj)
        return bobj

    elif (slno == (kprime+1)):
        #print('bob', slno)
        bobprime = dict()
        xprime = xi
        for i in range(N):
            if not (str(i) == xprime):
                bobprime[str(i)] = t[str(i)]
        return [bobprime]

    else:
        #print('charlie', slno)
        xj = xi
        j = slno
        thisj = slno - kprime - 2
        charliej = dict()
        if (j < k):
            icharliej = produceistring(N, k - j)
            for i in icharliej:
                full = xj + ',' + i
                #print(qj[thisj])
                charliej[full] = qj[thisj][full]
        else:
            charliej[xj] = qj[thisj][xj]
        return [charliej]

def encode(M, N, k, kprime, x, f, s):
    rbits = randomness(N, k, kprime)
    print('rbits', rbits)
    #print('Encoding...')
    
    shares = []
    xlist = x.split(',')
    for i in range(1, k+1):
        shares.append(share(i, xlist[i-1], rbits, N, k, kprime, f, s))
        
    #print('Encoding done!')
    #print(k, len(shares))
    return shares
    
def runOnce(m, n, kval, ch, sval):
    M = m
    N = n
    k = kval
    kprime = int((k - 1) / 2)
    s = sval
    x = xgen(M, N, k)
    print('x', x)
    f = dict()
    f[x] = ch

    dist = encode(M, N, k, kprime, x, f, s)
    return dist, f, x
