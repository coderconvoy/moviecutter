import moviepy.editor as mped
import moviecutter.movement as mvm

def longLine(s):
    return max([len(v) for v in s.split("\n")])

def simple(size,main,sub=None,author=None,duration=5):
    mainfs = size[0]*1.5/longLine(main)
    mc = mped.TextClip(main,fontsize=mainfs,color="white")
    mc= mc.set_position(((size[0] - mc.size[0])/2, (size[1] - mc.size[1])/4)).set_duration(duration)
    group = [mc]

    if sub != None :
        ms = mped.TextClip(sub,fontsize=min(size[0]/longLine(sub),mainfs-2),color="white")
        ms = ms.set_position(((size[0] - ms.size[0])/2,size[1] /2)).set_duration(duration)
        group.append(ms)

    if author != None :
        aut = mped.TextClip(author, fontsize=min(mainfs-4,size[0]/longLine(author)),color= "white")
        aut = aut.set_position(mvm.minus(size,aut.size)).set_duration(duration)
        group.append(aut)
         

    return mped.CompositeVideoClip(group,size=size)



def codeBox(message,rect,fontsize,duration=9):
    x,y,w,h = rect
    bak = mped.ColorClip((w,h),(255,255,255),duration=duration)
    
    t = mped.TextClip(message,font='Courier-bold',fontsize=fontsize,color="blue",method="caption",align="west").set_duration(duration)
    
    return mped.CompositeVideoClip([bak,t],size=(w,h)).set_pos((x,y))



   
def blueInfo(message,wsize,start=0, cenpos=None, duration = 9,bcol= None,align='center'):
    sx ,sy = wsize

    if cenpos == None :
        cenpos = (sx / 2,sy/2)
    px,py = cenpos
    dx = min( px, sx-px)
    res = mped.TextClip(message, font='Courier-bold',fontsize = dx*2.5/longLine(message),color="blue",align=align).set_duration(duration)
    rsx,rsy = res.size

    if bcol == None:
        return res.set_position((px-rsx/2, py -rsy/2)).set_start(start)
    

    # add Background Square
    colClip = mped.ColorClip(res.size,bcol,duration=duration)
    

    return mped.CompositeVideoClip([colClip,res],size=res.size).set_position((px-rsx/2,py-rsy/2)).set_start(start)

    
    
    
    

