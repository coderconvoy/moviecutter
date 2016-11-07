import time
import numpy as np

import threading
import pygame as pg



pg.init()
pg.display.set_caption('MoviePy')


def apreview(clip, fps=22050,  buffersize=4000, nbytes= 2,
                 audioFlag=None, videoFlag=None):
    """
    Plays the sound clip with pygame.
    
    Parameters
    -----------
    
    fps
       Frame rate of the sound. 44100 gives top quality, but may cause
       problems if your computer is not fast enough and your clip is
       complicated. If the sound jumps during the preview, lower it
       (11025 is still fine, 5000 is tolerable).
        
    buffersize
      The sound is not generated all at once, but rather made by bunches
      of frames (chunks). ``buffersize`` is the size of such a chunk.
      Try varying it if you meet audio problems (but you shouldn't
      have to).
    
    nbytes:
      Number of bytes to encode the sound: 1 for 8bit sound, 2 for
      16bit, 4 for 32bit sound. 2 bytes is fine.
    
    audioFlag, videoFlag:
      Instances of class threading events that are used to synchronize
      video and audio during ``VideoClip.preview()``.
    
    """
                 
    pg.mixer.quit()
    
    pg.mixer.init(fps, -8 * nbytes, clip.nchannels, 1024)
    totalsize = int(fps*clip.duration)
    pospos = np.array(list(range(0, totalsize,  buffersize))+[totalsize])
    tt = (1.0/fps)*np.arange(pospos[0],pospos[1])
    sndarray = clip.to_soundarray(tt,nbytes=nbytes, quantize=True)
    chunk = pg.sndarray.make_sound(sndarray)
    
    if (audioFlag is not None) and (videoFlag is not None):
        audioFlag.set()
        videoFlag.wait()
        
    channel = chunk.play()

    for i in range(1,len(pospos)-1):
        tt = (1.0/fps)*np.arange(pospos[i],pospos[i+1])
        sndarray = clip.to_soundarray(tt,nbytes=nbytes, quantize=True)
        chunk = pg.sndarray.make_sound(sndarray)
        while channel.get_queue():
            time.sleep(0.003)
            if (videoFlag!= None):
                if not videoFlag.is_set():
                    channel.stop()
                    del channel
                    return
        channel.queue(chunk)




pg.init()
pg.display.set_caption('MoviePy')

def vpreview(clip, fps=15, audio=True, audio_fps=22050,
             audio_buffersize=3000, audio_nbytes=2):
    
    # compute and splash the first image
    screen = pg.display.set_mode(clip.size)
    
    audio = audio and (clip.audio is not None)
    
    if audio:
        # the sound will be played in parrallel. We are not
        # parralellizing it on different CPUs because it seems that
        # pygame and openCV already use several cpus it seems.
        
        # two synchro-flags to tell whether audio and video are ready
        videoFlag = threading.Event()
        audioFlag = threading.Event()
        # launch the thread
        audiothread = threading.Thread(target=clip.audio.preview,
            args = (audio_fps,audio_buffersize, audio_nbytes,
                    audioFlag, videoFlag))
        audiothread.start()
    
    img = clip.get_frame(0)
    imdisplay(img, screen)
    if audio: # synchronize with audio
        videoFlag.set() # say to the audio: video is ready
        audioFlag.wait() # wait for the audio to be ready
    
    result = []
    
    t0 = time.time()
    for t in np.arange(1.0 / fps, clip.duration-.001, 1.0 / fps):
        
        img = clip.get_frame(t)
        
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_ESCAPE):
                    
                    if audio:
                        videoFlag.clear()
                    print( "Keyboard interrupt" )
                    return result
                    
            elif event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()
                rgb = img[y,x]
                result.append({'time':t, 'position':(x,y),
                                'color':rgb})
                print( "time, position, color : ", "%.03f, %s, %s"%(
                             t,str((x,y)),str(rgb)))
                    
        t1 = time.time()
        time.sleep(max(0, t - (t1-t0)) )
        imdisplay(img, screen)
