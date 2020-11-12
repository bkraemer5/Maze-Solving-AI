import pygame
import math
import random
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Maze Bot")

# COLORS
EMPTY_COLOR = (52, 58, 64)
START_COLOR = (251, 195, 188)
END_COLOR = (239, 99, 81)
BARRIER_COLOR = (0, 0, 0)
LINE_COLOR = (73, 80, 87)
OPEN_COLOR = (239, 99, 81)
CLOSED_COLOR = (243, 131, 117)
PATH_COLOR = (255, 255, 255)

# --- START NODE CLASS ---

# Nodes indicate each spot on the grid
class Node:
	def __init__(self, row, col, width, maxRow):
		# row, col = index in grid
		self.row = row
		self.col = col

		# position = grid coordinate * width for each node (20)
		# for drawing the squares
		self.x = row * width
		self.y = col * width

		# width = 20
		self.width = width

		#total rows = 40
		self.maxRow = maxRow

		# neighbors are the nodes on the top, bottom, left, and right
		self.neighbors = []

		self.color = EMPTY_COLOR

	def drawOnGrid(self, window):
		pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

	def getPosition(self):
		return self.row, self.col

	def isStart(self):
		return self.color == START_COLOR

	def isEnd(self):
		return self.color == END_COLOR

	def isClosed(self):
		return self.color == CLOSED_COLOR

	def isOpen(self):
		return self.color == OPEN_COLOR

	def isBarrier(self):
		return self.color == BARRIER_COLOR

	def reset(self):
		self.color = EMPTY_COLOR

	def start(self):
		self.color = START_COLOR

	def end(self):
		self.color = END_COLOR

	def close(self):
		self.color = CLOSED_COLOR

	def open(self):
		self.color = OPEN_COLOR

	def barrier(self):
		self.color = BARRIER_COLOR

	def optimalPath(self):
		self.color = PATH_COLOR

	def setNeighbors(self, grid):
		self.neighbors = []

		# DOWN
		if self.row < self.maxRow - 1 and not grid[self.row + 1][self.col].isBarrier():
			self.neighbors.append(grid[self.row + 1][self.col])

		# UP
		if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():
			self.neighbors.append(grid[self.row - 1][self.col])

		# LEFT
		if self.col < self.maxRow - 1 and not grid[self.row][self.col + 1].isBarrier():
			self.neighbors.append(grid[self.row][self.col + 1])

		# RIGHT
		if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():
			self.neighbors.append(grid[self.row][self.col - 1])

# --- END NODE CLASS ---



# given set of previously visited nodes, change color of nodes to optimal path color
def drawOptimalPath(prevNodes, currentNode, draw):
	while currentNode in prevNodes:
		currentNode = prevNodes[currentNode]
		currentNode.optimalPath()
		draw()

def drawGridLines(window, maxRow, width):
	box = width // maxRow
	for i in range(maxRow):
		# HORIZONTAL LINES
		pygame.draw.line(window, LINE_COLOR, (0, i * box), (width, i * box))
		# VERTICAL LINES
		pygame.draw.line(window, LINE_COLOR, (i * box, 0), (i * box, width))

def draw(window, grid, maxRow, width):
	window.fill(EMPTY_COLOR)

	for row in grid:
		for node in row:
			node.drawOnGrid(window)

	drawGridLines(window, maxRow, width)
	pygame.display.update()

def retrieveClickedNode(position, grid, maxRow, width):
	box = width // maxRow

	row = position[0] // box # converting y position
	col = position[1] // box # converting x position

	return grid[row][col]

# HEURISTIC
# using manhattan distance
def h(node1_pos, node2_pos):
	x1, y1 = node1_pos
	x2, y2 = node2_pos
	return abs(x1 - x2) + (y1 - y2)

# AI Algorithm
def AI(draw, grid, startNode, endNode):
	# count keeps track of when we inserted the item
	count = 0
	# we are using a pritority queue because it implements heap sort
	open_set = PriorityQueue()
	# insert the first tuple with count = 0 and startNode
	# tuple = (f, when-last-visited, node)
	open_set.put((0, count, startNode))
	previous = {}
	g = {}
	f = {}
	# set each node to have value of infinity
	for row in grid:
		for node in row:
			g[node] = float("inf")
			f[node] = float("inf")
	g[startNode] = 0
	f[startNode] = g[startNode] + h(startNode.getPosition(), endNode.getPosition())

	# since the priority queue doesn't tell us if a node is already in the queue,
	# open_hash will be a separate list to check
	open_hash = {startNode}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		# grabs first element in priority queue, & the node thats inside it
		currentNode = open_set.get()[2]
		open_hash.remove(currentNode)

		if currentNode == endNode:
			drawOptimalPath(previous, endNode, draw)
			endNode.end()
			return True

		for neighbor in currentNode.neighbors:
			weight = 1
			g_temp = g[currentNode] + weight

			if g_temp < g[neighbor]:
				previous[neighbor] = currentNode
				g[neighbor] = g_temp
				f[neighbor] = g_temp + h(neighbor.getPosition(), endNode.getPosition())
				if neighbor not in open_hash:
					count += 1
					open_set.put((f[neighbor], count, neighbor))
					open_hash.add(neighbor)
					neighbor.open()
		draw()

		if currentNode != startNode:
			currentNode.close()

	return False




def main(window, width):
	numRows = 40
	grid = []

	box = width // numRows  # integer division (800 / 40 = 20)

	# loop initializes nodes within each cell of the grid
	for i in range(numRows):
		grid.append([])
		for j in range(numRows):
			node = Node(i, j, box, numRows)
			grid[i].append(node)

	# indicates whether or not we have already set the start/end nodes
	startNode = None
	endNode = None

	# boolean to check whether the program is running
	running = True

	while running:
		draw(window, grid, numRows, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if pygame.mouse.get_pressed()[0]:
				position = pygame.mouse.get_pos()
				node = retrieveClickedNode(position, grid, numRows, width)
				if not startNode and node != endNode:
					startNode = node
					node.start()

				elif not endNode and node != startNode:
					endNode = node
					node.end()

				elif node != startNode and node != endNode:
					node.barrier()

			if event.type == pygame.KEYDOWN:
				# the spacebar starts the AI algorithm
				if event.key == pygame.K_SPACE and startNode and endNode:
					for row in grid:
						for node in row:
							node.setNeighbors(grid)
					AI(lambda: draw(window, grid, numRows, width), grid, startNode, endNode)
				# 'c' resets the board
				if event.key == pygame.K_c:
					startNode = None
					endNode = None
					grid = []
					for i in range(numRows):
						grid.append([])
						for j in range(numRows):
							node = Node(i, j, box, numRows)
							grid[i].append(node)
				# 'p' creates a preset maze
				if event.key == pygame.K_p:
					startNode = None
					endNode = None
					grid = []
					for i in range(numRows):
						grid.append([])
						for j in range(numRows):
							node = Node(i, j, box, numRows)
							if random.randint(1, 101) > 70:
								node.barrier()
							grid[i].append(node)
	pygame.quit()

main(WINDOW, WIDTH)


