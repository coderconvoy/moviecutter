import time
import moviepy.editor as mped
import numpy as np
import pygame as pg
import threading
from queue import Queue
import json


def imdisplay(imarray, screen,data, progress = 0):
    clip = data['clip']
    a = pg.surfarray.make_surface(imarray.swapaxes(0,1)) 
    screen.blit(a,(0,0))


    pg.draw.rect(screen,pg.Color("red"),(0,clip.size[1],clip.size[0],30))
        
    scale = clip.size[0] / clip.duration 
    
    bartop = clip.size[1]
    l = data['live']
    if l >=0 :
        dist = l * scale
        pg.draw.rect(screen,pg.Color("lime green"),(dist,bartop,4,30))

    for m in data['marks']:
        dist = m * scale
        pg.draw.rect(screen,pg.Color("blue"),(dist,bartop,4,25))
        
    dist = progress * scale
    pg.draw.rect(screen,pg.Color("black"),(dist,clip.size[1] + 10,4,20))
    pg.display.flip()

def vidPreview(clip,marks = None,fname = None):
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
            'mode':"stop"
        }

    h = clip.size[1] + 30

    screen = pg.display.set_mode((clip.size[0],h))
    
    q = Queue()
    
    #TODO back later and add audio
    if clip.audio is not None:
        audioThread = threading.Thread(target=audPreview,args=[ clip.audio ] , kwargs={'q':q})
        audioThread.start()

    t0 = time.time()
    pause = -1
    t = t0

    def goLoc(nt):
        nonlocal pause,t0,q
        if pause >= 0:
            pause = nt
            return
        t0 = time.time() - nt
        q.put(("go",nt))
        
            
    def prog():
        if pause >= 0:
            return pause
        return min(t - t0,clip.duration)


    while True: 
        t = time.time() 
        if pause >= 0:
            img = clip.get_frame(pause)
            imdisplay(img,screen,data,pause)
            time.sleep(0.01)
        elif t0 + clip.duration > t:
            img = clip.get_frame(t - t0)
            imdisplay(img,screen,data,t-t0)

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
                elif event.key == pg.K_LEFT:
                    goLoc(prog() - 0.03)
                elif event.key == pg.K_RIGHT:
                    goLoc(prog() + 0.03)
                elif event.key == pg.K_SPACE:
                    if pause >= 0:
                        t0 = time.time() - pause
                        q.put(("go",pause))
                        pause = -1
                    else:
                        pause =prog()
                        q.put("pause")
            elif event.type == pg.MOUSEBUTTONDOWN:
                d = clip.duration * pg.mouse.get_pos()[0]/clip.size[0]
                goLoc(d)
                




def audPreview(clip, fps = 22050, buffersize = 1000,nBytes = 2, q=None):
    if q is None :
        print("No Queueu")
    pg.mixer.quit()
    pg.mixer.init(fps, -8 * nBytes,clip.nchannels,1024)

    
    t0 = time.time()
    pause = -1
    channel = None
    fRate = 1.0 / fps
    moved = True
     
    while True: 
        if moved:
            t = time.time() 
            moved = False
        else:
            t += fRate*buffersize 

        if t - t0  +fRate * buffersize < clip.duration:
        
            tt =  np.arange(t - t0,t - t0 + fRate*buffersize,fRate)

            snd = clip.to_soundarray(tt,nbytes=nBytes,quantize=True)
            chunk = pg.sndarray.make_sound(snd)

            if channel is None :
                channel = chunk.play()
            else:
                channel.queue(chunk)

        while channel.get_queue():
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
        
