#! /usr/bin/python3
import math
import moviepy.editor as mped

def title1(t1,sSize): 
    tc1 = mped.TextClip(t1,color="white", font="Ariel", fontsize=100).set_duration(10)
    center = (
                (sSize[0] - tc1.w)/2,
                (sSize[1] - tc1.h)/2
            )

    tc1 = tc1.set_pos(
                lambda t : (center[0] + t* 10, center[1] - t*5)
                )
    return tc1 
    

def boundClip(clip, bounds,sSize):
    scaleF = min(sSize[0]/bounds[2],sSize[1]/bounds[3])
    
    clip = clip.resize(scaleF)
    
    nbounds = tuple(scaleF*x for x in bounds) 
    clip = clip.set_pos((-nbounds[0],-nbounds[1]))
    return (scaleF,-nbounds[0],-nbounds[1])

def boundAnimClip(clip,bounds1,bounds2,sSize,time =None):
    if time== None:
        time = clip.duration
    
    def scroll1(getframe,t):
        frac = t/ time
        frame = getframe(t)
        dx = bounds2[0] * frac + bounds1[0] * (1-frac)
        dy = bounds2[1] * frac + bounds1[1] * (1-frac)
        dw = bounds2[2] * frac + bounds1[2] * (1-frac)
        dh = bounds2[3] * frac + bounds1[3] * (1-frac)

        frameRegion = frame[dy:dy+dh,dx:dx+dw]
        return frameRegion


    clip = clip.fl(scroll1)
    clip = clip.resize(sSize)
    clip = clip.set_duration(time)

    return clip


if __name__ == "__main__":
    print("Hello Main")
