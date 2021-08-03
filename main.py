import pygame
from pygame import mixer
from pygame.constants import HIDDEN
import pickle
from os import pardir, path
from time import time
from os.path import dirname, join
from pygame.locals import *
import time

import parallax

pygame.mixer.pre_init(44100,-16,2,512)
mixer.init()
pygame.init()

WIDTH,HEIGHT=1595,970
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Platformer')

bg = parallax.ParallaxSurface((WIDTH,HEIGHT), pygame.RLEACCEL)

directory = dirname(__file__)
bg.add(join(directory, 'background/bg.png'),5)
bg.add(join(directory, 'paralax_img/mt2.png'),1)
bg.add(join(directory, 'paralax_img/mount1.png'),2)
bg.add(join(directory, 'paralax_img/nori.png'),1)

clock=pygame.time.Clock()
fps=75

#load images
#bg=pygame.image.load('background/bg.png')
#bg=pygame.transform.scale(bg,(WIDTH,HEIGHT))
restartImage=pygame.image.load('buttons/restart_btn.png')
restartImage=pygame.transform.scale(restartImage,(250,100))
message=pygame.image.load('buttons/over.png')
startButton=pygame.image.load('buttons/start_btn.png')
startButton=pygame.transform.scale(startButton,(250,100))
exitButton=pygame.image.load('buttons/exit_btn.png')
exitButton=pygame.transform.scale(exitButton,(250,100))
menuBg=pygame.image.load('background/bg1.png')
menuBg=pygame.transform.scale(menuBg,(WIDTH,HEIGHT))
gameName=pygame.image.load('buttons/gameName.png')

#load sounds
coinFx=pygame.mixer.Sound('music/coin.wav')
coinFx.set_volume(0.5)
jumpFx=pygame.mixer.Sound('music/jump.wav')
jumpFx.set_volume(0.5)
gameOverFx=pygame.mixer.Sound('music/game_over.wav')
gameOverFx.set_volume(0.5)

pygame.mixer.music.load('music/music.wav')
pygame.mixer.music.play(-1,0.0,5000)

#var
tileSize=55
gameOver=0
mainMenu=True
level=1
maxLevel=4
score=0
startTransition=False

#parallax
speed=0
t_ref=0


font=pygame.font.Font('ka1.ttf',30)
fontEnd=pygame.font.Font('ka1.ttf',40)
color=(0,0,0)
BLACK=(0,0,0)
RED=(255,0,0)
#draw text
def drawText(text,font,color,x,y):
    img=font.render(text,True,color)
    screen.blit(img,(x,y))

def drawGrid():
    for line in range(0,15):
        pygame.draw.line(screen,(255,255,255),(0,line*tileSize),(WIDTH,line*tileSize))
    for line in range(0,26):
        pygame.draw.line(screen,(255,255,255),(line*tileSize,0),(line*tileSize,HEIGHT))

def resetLevel(level):
    player.reset(20,HEIGHT)
    lavaGroup.empty()
    exitGroup.empty()
    spikesGroup.empty()
    weedGroup.empty()
    signGroup.empty()
    coinGroup.empty()
    magicGroup.empty()

    if path.exists(f'level{level}_data'):
        pickleIn=open(f'level{level}_data','rb')
        worldData=pickle.load(pickleIn)
    world=World(worldData)  

    return world

class Button():
    def __init__(self,x,y,image):
        self.image=image
        self.message=image
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.clicked=False

    def draw(self):
        action=False
        #get mouse position
        pos=pygame.mouse.get_pos()
        #check mouseover conllision
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
                action=True
                self.clicked=True
        if pygame.mouse.get_pressed()[0]==0:
            self.clicked=False

        screen.blit(self.image,self.rect)
        screen.blit(self.message,self.rect)
        return action

class Player:
    def __init__(self,x,y):
        self.reset(x,y)

#calculate new player position
#check collision at new position
#adjust player position

    def update(self,gameOver):
        deltaX=0
        deltaY=0
        walkCooldown=5
        if gameOver==0:
            #key input
            key=pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jump==False and self.jumpCount<2:
                jumpFx.play()
                self.velUp=-14
                self.jump=True
                self.jumpCount+=1
                self.touchedGround=False
            if key[pygame.K_UP]==False:
                self.jump=False
            if self.touchedGround==True:
                self.jumpCount=0
            if key[pygame.K_LEFT] and self.rect.x>0:
                deltaX-=4
                self.counter+=1
                self.direction=-1
            if key[pygame.K_RIGHT] and self.rect.x<1550:
                deltaX+=4
                self.counter+=1
                self.direction=1
            if key[pygame.K_LEFT]==False and key[pygame.K_RIGHT]==False:
                self.counter=0
                self.index=0
                if self.direction==1:
                    self.image=self.imagesIdleRight[self.index]
                if self.direction==-1:
                    self.image=self.imagesIdleLeft[self.index]


            #animation
            if self.counter>walkCooldown:
                self.counter=0
                self.index+=1
                if self.index>=len(self.imagesRight):
                    self.index=0
                if self.direction==1:
                    self.image=self.imagesRight[self.index]
                if self.direction==-1:
                    self.image=self.imagesLeft[self.index]
                    
            #gravity
            self.velUp+=1
            if self.velUp>10:
                self.velUp=10
            deltaY+=self.velUp

            #check collision
            for tile in world.tileList:
                #check for col in x direction
                if tile[1].colliderect(self.rect.x+deltaX,self.rect.y,self.width,self.height):
                    deltaX=0
                #check for col in y direction
                if tile[1].colliderect(self.rect.x,self.rect.y+deltaY,self.width,self.height):
                    #check if below the ground
                    if self.velUp<0:
                        deltaY=tile[1].bottom-self.rect.top
                        self.velUp=0
                    #above the ground
                    elif self.velUp>=0:
                        deltaY=tile[1].top-self.rect.bottom
                        self.velUp=0
                        self.touchedGround=True
                #check for lava col
                if pygame.sprite.spritecollide(self,lavaGroup,False):
                    gameOver=-1
                    gameOverFx.play()
                #check collision with exit door
                if pygame.sprite.spritecollide(self,exitGroup,False):
                    gameOver=1
                #check collision with spikes
                if pygame.sprite.spritecollide(self,spikesGroup,False):
                    gameOver=-1
                    gameOverFx.play()
                #check collison with magic flower
                if pygame.sprite.spritecollide(self,magicGroup,False):
                    pass
                
            #update coord
            self.rect.x+=deltaX
            self.rect.y+=deltaY

        elif gameOver==-1 and self.index<len(self.deadImage):
            #self.image=self.deadImage[self.index]
            #self.index+=1
            self.image=self.ghost
            self.rect.y-=3

        screen.blit(self.image,self.rect)
        #pygame.draw.rect(screen,(255,0,255),self.rect,3)

        return gameOver

    def reset(self,x,y):
        frame0r=pygame.image.load('run/tile000.png')
        frame0r=pygame.transform.scale(frame0r,(52,100))
        frame1r=pygame.image.load('run/tile001.png')
        frame1r=pygame.transform.scale(frame1r,(52,100))
        frame2r=pygame.image.load('run/tile002.png') 
        frame2r=pygame.transform.scale(frame2r,(52,100))
        frame3r=pygame.image.load('run/tile003.png') 
        frame3r=pygame.transform.scale(frame3r,(52,100))
        frame4r=pygame.image.load('run/tile004.png') 
        frame4r=pygame.transform.scale(frame4r,(52,100))
        frame5r=pygame.image.load('run/tile005.png')
        frame5r=pygame.transform.scale(frame5r,(52,100))

        frame0l=pygame.transform.flip(frame0r,True,False)
        frame1l=pygame.transform.flip(frame1r,True,False)
        frame2l=pygame.transform.flip(frame2r,True,False)
        frame3l=pygame.transform.flip(frame3r,True,False)
        frame4l=pygame.transform.flip(frame4r,True,False)
        frame5l=pygame.transform.flip(frame5r,True,False)

        idle0r=pygame.image.load('idle/tile000.png')
        idle0r=pygame.transform.scale(idle0r,(52,100))
        idle1r=pygame.image.load('idle/tile001.png')
        idle1r=pygame.transform.scale(idle1r,(52,100))
        idle2r=pygame.image.load('idle/tile002.png')
        idle2r=pygame.transform.scale(idle2r,(52,100))
        idle3r=pygame.image.load('idle/tile003.png')
        idle3r=pygame.transform.scale(idle3r,(52,100))

        idle0l=pygame.transform.flip(idle0r,True,False)
        idle1l=pygame.transform.flip(idle0r,True,False)
        idle2l=pygame.transform.flip(idle0r,True,False)
        idle3l=pygame.transform.flip(idle0r,True,False)

        die0=pygame.image.load('die/tile000.png')
        die0=pygame.transform.scale(die0,(52,100))
        die1=pygame.image.load('die/tile001.png')
        die1=pygame.transform.scale(die1,(52,100))
        die2=pygame.image.load('die/tile002.png')
        die2=pygame.transform.scale(die2,(52,100))
        die3=pygame.image.load('die/tile003.png')
        die3=pygame.transform.scale(die3,(52,100))
        die4=pygame.image.load('die/tile004.png')
        die4=pygame.transform.scale(die4,(52,100))
        die5=pygame.image.load('die/tile005.png')
        die5=pygame.transform.scale(die5,(52,100))
        die6=pygame.image.load('die/tile006.png')
        die6=pygame.transform.scale(die6,(52,100))
        die7=pygame.image.load('die/tile007.png')
        die7=pygame.transform.scale(die7,(52,100))

        self.imagesRight=[frame0r,frame1r,frame2r,frame3r,frame4r,frame5r]
        self.imagesLeft=[frame0l,frame1l,frame2l,frame3l,frame4l,frame5l]
        self.imagesIdleRight=[idle0r,idle1r,idle2r]
        self.imagesIdleLeft=[idle0l,idle1l,idle2l]
        self.deadImage=[die0,die1,die2,die3,die4,die5,die6]
        self.ghost=pygame.image.load('die/ghost.png')
        self.index=0
        self.jumpIndex=0
        self.counter=0
        self.image=self.imagesRight[self.index]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.velUp=0
        self.jump=False
        self.direction=0
        self.jumpCount=0
        self.touchedGround=False

class World():
    def __init__(self,data):
        self.tileList=[]

        #img
        dirtImg=pygame.image.load('summer/tile100.png')
        grassImg=pygame.image.load('summer/tile084.png')
        grassStanga=pygame.image.load('summer/tile083.png')
        grassDreapta=pygame.image.load('summer/tile085.png')
        platSimpla=pygame.image.load('summer/tile020.png')
        plat1=pygame.image.load('summer/tile035.png')
        plat2=pygame.image.load('summer/tile036.png')
        plat3=pygame.image.load('summer/tile037.png')

        rowCount=0
        for row in data:
            colCount=0
            for tile in row:
                if tile==1:
                    img=pygame.transform.scale(dirtImg,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==2:
                    img=pygame.transform.scale(grassImg,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==3:
                    img=pygame.transform.scale(grassStanga,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==4:
                    img=pygame.transform.scale(grassDreapta,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==5:
                    img=pygame.transform.scale(platSimpla,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==6:
                    img=pygame.transform.scale(plat1,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==7:
                    img=pygame.transform.scale(plat2,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==8:
                    img=pygame.transform.scale(plat3,(tileSize,tileSize))
                    imgRect=img.get_rect()
                    imgRect.x=colCount*tileSize
                    imgRect.y=rowCount*tileSize
                    tile=(img,imgRect)
                    self.tileList.append(tile)
                if tile==9:
                    lava=Lava(colCount*tileSize,rowCount*tileSize)
                    lavaGroup.add(lava)
                if tile==10:
                    exit=Exit(colCount*tileSize,rowCount*tileSize)
                    exitGroup.add(exit)
                if tile==11:
                    spike=Spike(colCount*tileSize,rowCount*tileSize)
                    spikesGroup.add(spike)
                if tile==12:
                    weed=Weed(colCount*tileSize,rowCount*tileSize)
                    weedGroup.add(weed)
                if tile==13:
                    coin=Coin(colCount*tileSize+(tileSize//2),rowCount*tileSize+(tileSize//2))
                    coinGroup.add(coin)
                if tile==14:
                    sign=Sign(colCount*tileSize,rowCount*tileSize)
                    signGroup.add(sign)
                if tile==15:
                    flower=Flower(colCount*tileSize,rowCount*tileSize)
                    magicGroup.add(flower)
                colCount+=1
            rowCount+=1
    def draw(self):
        for tile in self.tileList:
            screen.blit(tile[0],tile[1])
            #pygame.draw.rect(screen,(255,255,255),tile[1],2)

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('background/lava.png')
        self.image=pygame.transform.scale(img,(tileSize,int(tileSize*1.5)))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('background/exit.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class Spike(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('background/spikes.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class Weed(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('summer/tile026.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class Sign(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('summer/tile141.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y               

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('summer/tile006.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)

#magic flower
class Flower(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('summer/tile039.png')
        self.image=pygame.transform.scale(img,(tileSize,tileSize))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

'''class ScreenFade():
    def __init__(self,direction,colour,speed):
        self.direction=direction
        self.colour=colour
        self.speed=speed
        self.fadeCounter=0

    def fade(self):
        fadeComplete=False
        self.fadeCounter+=self.speed
        if self.direction==2:
            pygame.draw.rect(screen,self.colour,(0-self.fadeCounter,0,WIDTH//2,HEIGHT))
            pygame.draw.rect(screen,self.colour,(WIDTH//2+self.fadeCounter,0,WIDTH,HEIGHT))
            pygame.draw.rect(screen,self.colour,(0,0-self.fadeCounter,WIDTH,HEIGHT//2))
            pygame.draw.rect(screen,self.colour,(0,HEIGHT//2+self.fadeCounter,WIDTH,HEIGHT))
        if self.direction==1:
            pygame.draw.rect(screen,self.colour,(0-self.fadeCounter,0,WIDTH,HEIGHT))'''

class ScreenFade():
    def __init__(self,direction,colour,speed):
        self.direction=direction
        self.colour=colour
        self.speed=speed

    def fade(self):
        self.fadeCounter=0

        if self.direction==2:
            while self.fadeCounter<=1:
                width = self.fadeCounter*WIDTH
                height = self.fadeCounter*HEIGHT
                pygame.draw.rect(screen,self.colour,pygame.Rect(WIDTH//2-(width//2),HEIGHT//2-(height//2),width,height))
                '''
                pygame.draw.rect(screen,self.colour,pygame.Rect(WIDTH//2,0,WIDTH,HEIGHT))
                pygame.draw.rect(screen,self.colour,pygame.Rect(0,0,WIDTH,HEIGHT//2))
                pygame.draw.rect(screen,self.colour,pygame.Rect(0,+self.fadeCounter,WIDTH,HEIGHT))
                '''
                pygame.display.update()
                self.fadeCounter+=self.speed/30
                time.sleep(0.025)
            
        if self.direction==1:
            pygame.draw.rect(screen,self.colour,(0-self.fadeCounter,0,WIDTH,HEIGHT))

#create screen fade
levelupFade=ScreenFade(2,BLACK,2)
menuFade=ScreenFade(2,BLACK,2)

player=Player(20,HEIGHT)
lavaGroup=pygame.sprite.Group()
exitGroup=pygame.sprite.Group()
spikesGroup=pygame.sprite.Group()
weedGroup=pygame.sprite.Group()
signGroup=pygame.sprite.Group()
coinGroup=pygame.sprite.Group()
magicGroup=pygame.sprite.Group()

#load level data and create world
if path.exists(f'level{level}_data'):
    pickleIn=open(f'level{level}_data','rb')
    worldData=pickle.load(pickleIn)
world=World(worldData)

restartButton=Button(WIDTH/2-150,HEIGHT/2+100,restartImage)
message=Button(WIDTH/2-450,HEIGHT/2-300,message)
startButton=Button(WIDTH/2-200,HEIGHT/2+100,startButton)
exitButton=Button(WIDTH/2-200,HEIGHT/2+250,exitButton)
name=Button(WIDTH/2-500,HIDDEN/2+200,gameName)

run=True
while run:
    clock.tick(fps)
    if mainMenu==True:
        screen.blit(menuBg,(0,0))
        name.draw()
        if startButton.draw():
            mainMenu=False
            menuFade.fade()
        if exitButton.draw():
            run=False
            menuFade.fade()
    else:

        #parallax background
        bg.scroll(speed)  # Move the background with the set speed
        t = pygame.time.get_ticks()
        if (t - t_ref) > 60:
            bg.draw(screen)

        #screen.blit(bg,(0,0))
        world.draw()
        
        if gameOver==0:
            if pygame.sprite.spritecollide(player,coinGroup,True):
                score+=1
                coinFx.play()
            drawText('Score: '+str(score),font,color,tileSize-10,10)
            drawText('Level: '+str(level),font,color,tileSize+200,10)
        lavaGroup.draw(screen)  
        exitGroup.draw(screen)
        spikesGroup.draw(screen)
        weedGroup.draw(screen)
        signGroup.draw(screen)
        coinGroup.draw(screen)
        magicGroup.draw(screen)
        gameOver=player.update(gameOver)

        if startTransition==True:
            if levelupFade.fade():
                startTransition=False
                levelupFade.fadeCounter=0
            if menuFade.fade():
                startTransition=False
                menuFade.fadeCounter=0

        if gameOver==-1:
            message.draw()
            if restartButton.draw():
                score=0
                level=1
                worldData=[]
                world=resetLevel(level)
                gameOver=0

        if gameOver==1:
            levelupFade.fade()
            level+=1
            if level<=maxLevel:
                #go to next level
                worldData=[]
                world=resetLevel(level)
                gameOver=0
            else:
                screen.blit(menuBg,(0,0))
                drawText('CONGRATULATIONS!!! you have completed the game with score: '+str(score),font,color,150,200)
                drawText('Try to beat my 28 high score!!',fontEnd,color,450,300)
                drawText('GOOD LUCK!!!',fontEnd,color,700,400)
                if restartButton.draw():
                    score=0
                    level=1
                    worldData=[]
                    world=resetLevel(level)                             
                    gameOver=0
                    

    #drawGrid()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False

        if event.type == KEYDOWN and event.key == K_RIGHT:
            speed += 2
        if event.type == KEYUP and event.key == K_RIGHT:
            speed -= 2
        if event.type == KEYDOWN and event.key == K_LEFT:
            speed -= 2
        if event.type == KEYUP and event.key == K_LEFT:
            speed += 2

    pygame.display.update()
pygame.quit()