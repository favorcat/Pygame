""" blocks.py - Copyright 2016 Kenichiro Tanaka """

#
# 2019.07.21 
# 작정자: 고은영 
# 기능추가
#  1. PADDLE의 윈도우벽 좌우 밖으로 나가는것 수정
#  2. 점수 화면출력 블록1개당 10점추가
#  3. 게임 볼 갯수 3개로 설정
#  4. Beep음 Sound 추가
#  5. 게임 Level추가 레벨이 올라갈수록 PADDLE 가로크기가 줄어듬 

import sys
import math
import random
import pygame
import winsound
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, Rect

SURFACE = pygame.display.set_mode((600, 800))


class Block:
    """ 블록, 공, 패들 오브젝트 """
    def __init__(self, col, rect, speed=0):
        self.col = col
        self.rect = rect
        self.speed = speed
        self.dir = random.randint(-45, 45) + 270

    def move(self):
        """ 공을 움직인다 """
        self.rect.centerx += math.cos(math.radians(self.dir))\
             * self.speed
        self.rect.centery -= math.sin(math.radians(self.dir))\
             * self.speed

    def draw(self):
        """ 블록, 공, 패들을 그린다 """
        if self.speed == 0:
            pygame.draw.rect(SURFACE, self.col, self.rect)
        else:
            pygame.draw.ellipse(SURFACE, self.col, self.rect)

#---------------------------------------------------------------------

class Game:
    def __init__(self):
        # 게임 초기화

        pygame.init()
        pygame.key.set_repeat(5, 5)
        pygame.display.set_caption('블록격파 게임') #제목표시줄에 타이틀      

        self.FPSCLOCK = pygame.time.Clock()
        self.BLOCKS = []
        
        self.BALL = Block((242, 242, 0), Rect(300, 400, 20, 20), 10)
        self.running = True
        self.clock = pygame.time.Clock()
        self.myfont = pygame.font.SysFont(None, 80)
        self.score_font = pygame.font.SysFont(None,30)  #폰트 설정
        self.mess_clear = self.myfont.render("Cleared!", True, (255, 255, 0))
        self.mess_over = self.myfont.render("Game Over!", True, (255, 255, 0))
        self.score = 0  # 스코어    
        self.level = 1  # 게임 레벨  
        self.fps = 30
        self.paddle_x=100  #PADDLE가로 크기  레벨이 증가하면 줄어듬


    def new(self):
        # start a new game
        self.balls = 3  # 게임당 볼 갯수
        self.colors = [(255, 0, 0), (255, 165, 0), (242, 242, 0),
              (0, 128, 0), (128, 0, 128), (0, 0, 250)]

        self.PADDLE = Block((242, 242, 0), Rect(300, 700, self.paddle_x, 30))

        for ypos, color in enumerate(self.colors, start=0): #블록을 생성
            for xpos in range(0, 5):
                self.BLOCKS.append(Block(color,
                                Rect(xpos * 100 + 60, ypos * 50 + 40, 80, 30)))

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:

            self.tick()

            SURFACE.fill((153, 153, 153))
            self.BALL.draw()
            self.PADDLE.draw()

            for block in self.BLOCKS:
                block.draw()

            if len(self.BLOCKS) == 0:   #남은 블록이 없으면 Clear
                SURFACE.blit(self.mess_clear, (200, 400))
                pygame.display.update()
                self.wait_for_key()
                self.playing = False  #Run Loop 종료
                self.BALL.rect.centery=350 # New Ball의 생성위치
                self.BALL.dir=-50          # New Ball 방향  
                self.level = self.level+1  # 레벨 증가 
                if self.paddle_x > 40 :    # 최소크기 40
                    self.paddle_x = self.paddle_x - 20   #PADDLE 크기 줄어듬   


            if self.BALL.rect.centery > 800 : #볼을 PADDLE로 커버못하면
                self.balls = self.balls - 1
                if self.balls == 0 :  #Game over
                    
                    self.playing = False  #Run Loop 종료
                    self.running = False  #Game 종료
                else :
                    #self.wait_for_key()
                    self.BALL.rect.centery=350 #New Ball의 생성위치
                    self.BALL.dir=-50          #New Ball 방향

            score_text = self.score_font.render("Level:"+ str(self.level)+"  Balls:"+str(self.balls)+
                                                "  Score:"+ str(self.score) , True, (255, 255, 0))

            SURFACE.blit(score_text,(20,10))    #점수 출력
            if self.running == False : 
                SURFACE.blit(self.mess_over, (150, 400))
            pygame.display.update()
            if self.running == False : self.wait_for_key()


            self.FPSCLOCK.tick(self.fps)


    def tick(self):
        """ 프레임별 처리 """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False  #Game Loop 종료
  
            elif event.type == KEYDOWN:
                if event.key == K_LEFT and self.PADDLE.rect.centerx > self.paddle_x/2 :  #PADDLE가 좌측 윈도우벽(0) 체크
                    self.PADDLE.rect.centerx -= 10  # x좌표
                elif event.key == K_RIGHT and self.PADDLE.rect.centerx < 600-(self.paddle_x/2) :  #PADDLE가 우측 윈도우벽(600) 체크
                    self.PADDLE.rect.centerx += 10

        if self.BALL.rect.centery < 1000:  # Ball x좌표가 1000이하이면 볼Move
            self.BALL.move()

        # 블록과 볼이 충돌체크
        prevlen = len(self.BLOCKS)
        for x in self.BLOCKS :
            if x.rect.colliderect(self.BALL.rect) :
                self.score = self.score + 10   #블록이 격파되면 점수 10점 추가

        self.BLOCKS = [x for x in self.BLOCKS
              if not x.rect.colliderect(self.BALL.rect)]  #격파된 블록제거하고 블록 재설정

        if len(self.BLOCKS) != prevlen:      #블록이 격파되면 볼 진행방향 바꿈
            self.BALL.dir *= -1
            winsound.Beep(5000, 1)

        # 패들과 볼 충돌체크
        if self.PADDLE.rect.colliderect(self.BALL.rect):
            self.BALL.dir = 90 + (self.PADDLE.rect.centerx - self.BALL.rect.centerx) \
                / self.PADDLE.rect.width * 80
            winsound.Beep(2000, 2)

        # 벽과 충돌?
        if self.BALL.rect.centerx < 0 or self.BALL.rect.centerx > 600:
            self.BALL.dir = 180 - self.BALL.dir
        if self.BALL.rect.centery < 0:
            self.BALL.dir = - self.BALL.dir
            self.BALL.speed = 15

#-------------------------------------------------------

    def wait_for_key(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP: #키보드를 누를때
                    waiting = False


#-------------------------------------------------------

g = Game()

while g.running:
    g.new()
    g.run()

winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
pygame.quit()


