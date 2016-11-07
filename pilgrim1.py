#! /usr/bin/python3
import os.path 
import test1
import moviepy.editor as mped

def getP1List(): 
    return  [
        {
            'n':'C-003b.png',
            'b1':(400,90,700,450),
            'b2':(150,20,2075,1372),
            't':38
        },
        {
            'n':'C-002.png',
            'b1':(212,50,1466,868),
            'b2':(80,20,2450,1350),        
            't':53
        },
        {
            'n':'C-004.png',
            'b1':(58,188,968,638),
            'b2':(622,26,2470,1252),        
            't':45
        },
        {
            'n':'C-001.png',
            'b1':(540,120,850,540),
            'b2':(20,40,1460,1150),        
            't':10
        }
    ]



def concatList(l,folder,sSize):
    res = []
    for a in l :
        c  = mped.ImageClip(os.path.join(folder,a['n']))
        b = test1.boundAnimClip(c,a['b1'],a['b2'], sSize,a['t'])
        res.append(b)
    
    return mped.concatenate_videoclips(res)
    

def makeVid1(size = (500.0,300.0)):
    
    l = getP1List()
    clip = concatList(l,"in/pilgrim",size)
    snd = mped.AudioFileClip("in/pilgrim/audio-1.wav")

    ltime = 0;
    for a in l:
        ltime += a['t']
    snd = snd.subclip(0,ltime)

    clip =clip.set_audio(snd)

    return clip
