import math

def minus(a,b=None,fac = 1):
    if b == None:
        return tuple(-x * fac for x in a)
    return tuple((x-y)* fac for x,y in zip(a,b))

def tupaddmult(a,b,fac=1):
    return tuple((x + y)*fac for x,y in zip(a,b))

def linear(a,b,dist):
    return tuple(x *(1 - dist)+ y * dist for x,y in zip(a,b))


def sinFrom(start,fin,dur):
    mid = tupaddmult(start,fin,1/2)
    
    def res(t):
        if t < dur /2 :
            f = math.sin(t*math.pi / dur)
            return linear(start,mid,f)
        else :
            f = math.sin((dur - t) * math.pi/dur)
            return linear(fin,mid,f)

    return res
