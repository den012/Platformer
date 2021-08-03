import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 55
cols = 20
margin = 100
screen_width = 1595
screen_height =970

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')


#load images
bg_img = pygame.image.load('background/bg.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
blob_img = pygame.image.load('img/blob.png')
platform_x_img = pygame.image.load('img/platform_x.png')
platform_y_img = pygame.image.load('img/platform_y.png')
lava_img = pygame.image.load('img/lava.png')
coin_img = pygame.image.load('img/coin.png')
exit_img = pygame.image.load('img/exit.png')
save_img = pygame.image.load('img/save_btn.png')
load_img = pygame.image.load('img/load_btn.png')
spikes=pygame.image.load('background/spikes.png')
dirtImg=pygame.image.load('summer/tile100.png')
grassImg=pygame.image.load('summer/tile084.png')
grassStanga=pygame.image.load('summer/tile083.png')
grassDreapta=pygame.image.load('summer/tile085.png')
platSimpla=pygame.image.load('summer/tile020.png')
plat1=pygame.image.load('summer/tile035.png')
plat2=pygame.image.load('summer/tile036.png')
plat3=pygame.image.load('summer/tile037.png')
floare=pygame.image.load('summer/tile023.png')
ciuperca=pygame.image.load('summer/tile039.png')
weed=pygame.image.load('summer/tile026.png')
coin=pygame.image.load('summer/tile006.png')
indicator=pygame.image.load('summer/tile141.png')
pamant=pygame.image.load('background/tile_munte.png')


#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(30):
	r = [0] * 30
	world_data.append(r)


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(30):
		#vertical lines
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		#horizontal lines
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(30):
		for col in range(30):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirtImg, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grassImg, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					#grass stanga
					img = pygame.transform.scale(grassStanga, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 4:
					#grass dreapta
					img = pygame.transform.scale(grassDreapta, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#plat simpl
					img = pygame.transform.scale(platSimpla, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					#plat1
					img = pygame.transform.scale(plat1, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 7:
					#plat2
					img = pygame.transform.scale(plat2, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 8:
					#plat3
					img = pygame.transform.scale(plat3, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col]==9:
					#lava
					img = pygame.transform.scale(lava_img, (tile_size, int(tile_size*1.5)))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==10:
					#exit
					img = pygame.transform.scale(exit_img, (tile_size,tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==11:
					#spikes
					img = pygame.transform.scale(spikes, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==12:
					#weed
					img = pygame.transform.scale(weed, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==13:
					#tree
					img = pygame.transform.scale(coin, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==14:
					img=pygame.transform.scale(indicator,(tile_size,tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col]==15:
					img=pygame.transform.scale(ciuperca,(tile_size,tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))

					


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(screen_width // 2 - 350, screen_height-50, save_img)
load_button = Button(screen_width // 2 + 50, screen_height-950, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	screen.blit(bg_img, (0, 0))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, white, tile_size, screen_height - 60)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, screen_height - 40)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#check that the coordinates are within the tile area
			if x < 30 and y < 30:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 16:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 16
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()