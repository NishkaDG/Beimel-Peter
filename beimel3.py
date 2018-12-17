import secrets

def randgen(num):
    bits = bin(secrets.randbits(num))[2:]
    lbits = len(bits)
    if lbits < num:
        pad = num - lbits
        for i in range(pad):
            bits = '0' + bits
    return bits

def share(i, xi, N, f, q, r, s):
    if (i==1):
        outalice = []
        for i3 in range(N):
            #print('s0', s)
            si3 = s ^ int(q[i3])
            mss = 0
            for i2 in range(N):
                full = str(xi) + ',' + str(i2) + ',' + str(i3)
                try:
                    if (f[full] == 0):
                        mss = mss ^ int(r[i2])
                except KeyError:
                    f[full] = 0
                    mss = mss ^ int(r[i2])
            #print(si3, mss)
            si3 = int(si3) ^ int(mss)
            outalice.append(si3)
        return outalice

    elif (i==2):
        outbob = []
        for j in range(N):
            if not (j == xi):
                outbob.append(int(r[j]))
        return outbob

    elif (i==3):
        #print(q)
        return [int(q[int(xi)])]

    else:
        print(i, 'Sorry, this protocol only works for 3 members. Try beimelOdd for larger parties.')
        return []

def encode(x, M, N, f, s):
    #q = randgen(N)
    #r = randgen(N)
    x1, x2, x3 = x.split(',')

    alice = share(1, x1, N, f, q, r, s)
    bob = share(2, x2, N, f, q, r, s)
    charlie = share(3, x3, N, f, q, r, s)

    return alice, bob, charlie

def reconstruct(outalice, outbob, outcharlie, x):
    x1, x2, x3 = x.split(',')
    res = outalice[int(x3)-1] ^ outcharlie[0]
    for i2 in outbob:
        res = res ^ i2
    return res
