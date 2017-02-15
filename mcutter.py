import time
import moviepy.editor as mped
from math import floor

from moviepy.decorators import ( apply_to_mask,
                                 apply_to_audio,
                                 outplace)

import numpy as np
import pygame as pg
import threading
from queue import Queue
import json

def inR(n,low,top):
    if n < low : return False
    if n > top : return False
    return True

def fl_aud(fnc):
    def resf(t):
        if isinstance(t,float):
            return fnc(t)
        return [fnc(x) for x in t]

    return resf

def cutConcat2(clip,data,sbak=-0.3):
    """Data can either be a json array or a file which contains it"""
    if isinstance(data,str) :
        #doesn't handle file error as this needs to be passed up
        f = open(data,'r')
        data = json.load(f)
        f.close()
    if len(data) %2 == 1 :
        data.Append(clip.duration)
    
    newDuration = 0;
    lastp = 0
    for i,m in enumerate(data):
        if i %2 == 0 :
            lastp = m
        else:
            newDuration += m - lastp


    def offset1(t):
        last = 0
        for i,m in enumerate(data):
            if i %2 ==0:
                last = m
            else:
                if t < m - last:
                    return t + last
                t -= (m - last)
        return 0

    
    def resf(gf,t):
        if isinstance(t,np.ndarray):
            off = offset1(t[0]) - t[0] + sbak
            mov = np.add(off,t)
            return gf(mov)
        return gf(offset1(t))

    

    return clip.fl(resf,apply_to=['mask','audio']).set_duration(newDuration)
    
    

def cutConcat(clip,data,pr=True):
    """Data can either be a json array or a file which contains it"""
    if isinstance(data,str) :
        #doesn't handle file error as this needs to be passed up
        f = open(data,'r')
        data = json.load(f)
        f.close()

    n = len(data)
    last = 0
    clips = []
    for i, c in enumerate(data + [clip.duration]):
        if i %2 == 0:
            last = c
        else :
            clips.append(clip.subclip(last,c))
            if pr:
                print(n - i)

    return mped.concatenate_videoclips(clips)

            
        



def imdisplay(imarray, screen,data, progress = 0):
    clip = data['clip']
    a = pg.surfarray.make_surface(imarray.swapaxes(0,1)) 
    screen.blit(a,(0,0))

    scale = clip.size[0] / clip.duration 

    color1 = pg.Color("salmon")
    color2 = pg.Color("light salmon")
    longTop = clip.size[1] + 30
    twenTop = clip.size[1]
    twenScale = clip.size[0]/20

    pMin = progress - 10
    pMax = progress + 10
    

    if data['mode'] == "jump" :
        color1 = pg.Color("cyan")
        color2 = pg.Color("light cyan")
    elif data['mode'] == "play":
        color1 = pg.Color("gray")
        color2 = pg.Color("white")

    pg.draw.rect(screen,pg.Color("black"),(0,twenTop,clip.size[0],60))

    last = 0 
    incut = False
    for a in data['marks'] + [clip.duration]:
        if incut:
            if inR(a,pMin,pMax)or inR(last,pMin,pMax) or inR(progress,last,a):
                pg.draw.rect(screen,color1,((last - pMin)*twenScale,twenTop,(a - last)*twenScale,30))
            pg.draw.rect(screen,color1,(last*scale,longTop,(a-last)*scale,30))
        else:
            if inR(a,pMin,pMax)or inR(last,pMin,pMax) or inR(progress,last,a):
                pg.draw.rect(screen,color2,((last - pMin)*twenScale,twenTop,(a -last)*twenScale,30))
            pg.draw.rect(screen,color2,(last*scale,longTop,(a-last)*scale,30))
        last = a 
        incut = not incut
        
    
    
    l = data['live']

    if l >=0 :
        dist = l * scale
        pg.draw.rect(screen,pg.Color("lime green"),(dist,longTop,4,30))
        if inR(l,pMin,pMax):
            pg.draw.rect(screen,pg.Color("lime green"),((l - pMin) * twenScale,twenTop,2,30))
        

        
    dist = progress * scale
    pg.draw.rect(screen,pg.Color("black"),(clip.size[0]/2 - 1,twenTop + 10,2,20))
    pg.draw.rect(screen,pg.Color("black"),(dist-1,longTop + 10,2,20))
    
    pg.display.flip()

def vidPreview(clip,marks = None,fname = None,minafps=4000):
    if marks is None:
        marks = []
        if fname != None:
            try:
                f = open(fname,'r')
                marks = json.load(f)
                f.close()
            except:
                pass
    data = { 'clip':clip,
            'live': -1, 
            'marks': marks,
            'mode':"play"
        }

    h = clip.size[1] + 60

    screen = pg.display.set_mode((clip.size[0],h))
    
    q = Queue()
    
    #TODO back later and add audio
    if clip.audio is not None:
        audioThread = threading.Thread(target=audPreview,args=[ clip.audio ] , kwargs={'q':q , 'minfps':minafps})
        audioThread.start()

    t0 = time.time()
    pause = -1
    t = t0
    pLast = False

    def goLoc(nt):
        nonlocal pause,t,t0,q,pLast
        if nt < 0:
            nt = 0

        pLast = False
        if pause >= 0:
            pause = nt
            return
        t = time.time()
        t0 = t - nt
        q.put(("go",nt))
        
            
    def prog():
        if pause >= 0:
            return pause
        return min(t - t0,clip.duration-0.001)

    while True: 
        t = time.time() 

        if data['mode'] == "stop" and pLast != False:
            for m in data['marks']:
                if m > pLast and m <= prog():
                    pause = m
                    q.put("pause") 
        if data['mode'] == "jump" and pLast != False:
            nMark = data['marks'][-1]
            for m in reversed(data['marks']):
                if m > pLast and m<= prog():
                    if m == nMark:
                        pause = m
                        q.put("pause") 
                        break
                    goLoc(nMark)
                    break
                nMark = m

        img = clip.get_frame(prog())
        imdisplay(img,screen,data,prog())

        pLast = prog()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN :
                if event.key == pg.K_ESCAPE:
                    pg.display.quit()
                    q.put("quit")
                    return data['marks']
                if event.key == pg.K_w:
                    if fname != None:
                        try :
                            f = open(fname,'w')
                            json.dump(data['marks'],f)
                            f.close()
                            print("Saved to " + fname + "\n")
                        except:
                            pass
                elif event.key == pg.K_a :
                    winner = 0
                    for m in data['marks'] + [data['live']]:
                        if m >winner and m < prog():
                            winner = m
                    goLoc(winner)
                elif event.key == pg.K_s :
                    winner = clip.duration
                    for m in data['marks'] + [data['live']]:
                        if m < winner and m > prog():
                            winner = m
                    goLoc(winner)
                elif event.key == pg.K_l : 
                    data['marks'] = [x for x in data['marks'] if x != prog()]
                    
                    data['live'] = prog()
                elif event.key == pg.K_m :
                    m = data['live']
                    if m >= 0 :
                        data['live'] = -1
                        data['marks'].append(m)
                        data['marks'].sort()
                elif event.key == pg.K_LEFT:
                    goLoc(prog() - 0.05)
                elif event.key == pg.K_RIGHT:
                    goLoc(prog() + 0.05)
                elif event.key == pg.K_UP:
                    goLoc(prog() - 3)
                elif event.key == pg.K_DOWN:
                    goLoc(prog() + 3)
                elif event.key == pg.K_SPACE:
                    if pause >= 0:
                        t0 = time.time() - pause
                        q.put(("go",pause))
                        pause = -1
                    else:
                        pause =prog()
                        q.put("pause")
                elif event.key == pg.K_1:
                    data['mode'] = "play"
                elif event.key == pg.K_2:
                    data['mode'] = "stop"
                elif event.key == pg.K_3:
                    data['mode'] = "jump"


            elif event.type == pg.MOUSEBUTTONDOWN:
                mp = pg.mouse.get_pos()
                if mp[1] < clip.size[1]:
                    print(prog(),mp)
                elif mp[1] < clip.size[1] + 30:
                    d = (mp[0]*20/clip.size[0]) - 10
                    goLoc(prog() + d)
                    print(prog())
                else:
                    d = clip.duration * mp[0]/clip.size[0]
                    goLoc(d)
                    print(prog())
                




def audPreview(clip, fps = 11025, minfps = 4000, buffersize = 1000,nBytes = 2, q=None):
    if q is None :
        print("No Queue")
    pg.mixer.quit()
    pg.mixer.init(fps, -8 * nBytes,clip.nchannels,1024)

    
    t0 = time.time()
    pause = -1
    channel = None
    fRate = 1.0 / fps
    moved = True
    hasq = False #moviepy has queue loaded
     
    while True: 
        if moved:
            t = time.time() 
            moved = False
        elif not hasq :
            t = time.time()
            moved = False
            if fps > minfps :
                fps = floor(fps * 0.9)
                print("afps=",fps)
                pg.mixer.quit()
                pg.mixer.init(fps, -8 * nBytes, clip.nchannels,1024)
                moved = True
                fRate = 1.0 / fps
        else:
            t += fRate*buffersize 

        if t - t0  +fRate * buffersize < clip.duration:
        
            tt =  np.arange(t - t0,t - t0 + fRate*buffersize,fRate)

            snd = clip.to_soundarray(tt,fps=fps,nbytes=nBytes,quantize=True)
            chunk = pg.sndarray.make_sound(snd)

            if channel is None :
                channel = chunk.play()
            else:
                channel.queue(chunk)

        hasq = False
        while channel.get_queue():
            hasq = True
            time.sleep(0.003)
        

        try :
            action = q.get(False)
            if action == "pause":
                action = q.get(True)
            if action == "quit" :
                print("quitting")
                return
            if action[0] == "go":
                t0 = time.time() - action[1]
                moved = True
        except :
            pass
        
