import pygame as py
from sys import exit

width, height = 800, 800
py.init()
screen = py.display.set_mode((width, height))

#frame rate:
#1 frame/sseconds. 100frame/second. 60 fps is a good in between .
# 60 fps ceileing and 60fps floor
clock = py.time.Clock()
test_front = py.font.Font(None, 50)

#surface : Display surface/ game window. a regular surface is a image(color, image , txt) Need to be display on the surface
bs = py.image.load(('images/back_groundlvl1.png')).convert()
#surface : Display surface/ game window. a regular surface is a image(color, image , txt) Need to be display on the surface
bs = py.transform.scale(bs, (width,height))
text_surface = test_front.render('Welcome to Pacman', False, 'Black' )

while True:
    for event in py.event.get():  
        if event.type == py.QUIT:
            py.quit()
            exit()
    screen.blit(bs,(0, 0))
    screen.blit(text_surface,(250,300))
    py.display.update()
    clock.tick(60) # the true loop should not run faster then 60 times per second f = 60 H => T = 1/60 a tick every 0.166