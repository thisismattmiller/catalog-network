#import postgresql, json, numpy, scipy.spatial
from __future__ import division
import json, os, math, string

class indexNodes:


	allNodes = []

	#xmlFile = "data/test.gexf"
	xmlFile = "data/io_gexf_latest.gexf"
	dataNodes = "data/nodes/"
	dataEdges = "data/edges/"
	dataCircles = "data/circles/"
	dataBase = "data/"
	dataIndexNodes = 'data/index/nodes/'
	dataTitles = "data/titles/"

	buildCounterNode = 0
	buildCounterNodeTotal = 0

	totalWidth = 0
	totalHeight = 0

	scaleFactor = 4.75

	gridSize = 25

	exclude = set(string.punctuation)


	#open the already built nodes and get their poition also get relevant titles and bnumbers
	def buildNodesIndex(self):

		#first build the image, we need to know how big it is
		with open(self.dataBase + "base.json", "r") as f:
			base = json.loads(f.read())
		
		self.totalWidth = base['width']
		self.totalHeight = base['height']

		allNodes = {}

		for file in os.listdir(self.dataNodes):

			if file.endswith('.json'):

				with open(self.dataNodes + file, "r") as f:

					nodes = json.loads(f.read())
					print ("Storing Nodes data", self.dataNodes + file, len(nodes))
					self.buildCounterNodeTotal = len(nodes)
					self.buildCounterNode = 0

					for node in nodes:
						allNodes[node['id']] = node

		#now load the list of titles that we made eariler in the generate_gexf.py process and connect the titles to the node via subject
		allTitles = {}
		for file in os.listdir(self.dataTitles):

			if file.endswith('.json'):

				with open(self.dataTitles + file, "r") as f:

					titles = json.loads(f.read())
					print ("Storing Title data", self.dataTitles + file, len(titles))
					self.buildCounterNodeTotal = len(titles)
					self.buildCounterNode = 0

					for title in titles:
						allTitles[title['normalized']] = title

		i = 0
		temp = []
		fileCounter = 0

		allLocations = {}

		allLocationsBounds = {}

		for x in allNodes:

			node = allNodes[x]

			node['cords'] = self.convertCoordinates(int(node['posX']),int(node['posY']))

			node['normalized'] = self.normalizeSubject(node['name'])
			color = (node['rgb'][0],node['rgb'][1],node['rgb'][2])
			color = self.rgb_to_hex( color )

			node['hex'] = color


			if node['normalized'] in allTitles:
				node['titles'] = allTitles[node['normalized']]['titles'][:5]


			#figure out it's location
			left = x = node['cords'][0]
			top = y = node['cords'][1]
			size = int(node['size']) * self.scaleFactor

			numberOfGrids = int(math.ceil(size / self.gridSize))

			allLocationsBounds[node['id']] = { "id" : node['id'], "x1" : x, "y1": y, "x2" : int(x + (size*2)), "y2" : int(y + (size*2)) }

			node['x1'] = x
			node['x2'] = int(x + (size*2))
			node['y1'] = y
			node['y2'] = int(y + (size*2))


			#print "This node is ", size, "x", x, "y", y, "left", left, "top", top, "numberOfGrids", numberOfGrids

			#loop through the node sizes and build all the possible 25x25 poisitons that could be contained in the node
			newLeft = left
			newTop = top

			locations = []
			tempIds = []

			#do the x's
			for n in range(1,numberOfGrids+1):
				newLeft += self.gridSize
				for n2 in range(1,numberOfGrids+1):
					newTop += self.gridSize
					idX = int(round(newLeft / self.gridSize) * self.gridSize)
					idY = int(round(newTop / self.gridSize) * self.gridSize)
					if str(idX) + "-" + str(idY) not in tempIds:
						locations.append([idX, idY])
						tempIds.append(str(idX) + "-" + str(idY))
			
			newLeft = left
			newTop = top

			for n in range(1,numberOfGrids+1):
				newTop += self.gridSize
				for n2 in range(1,numberOfGrids+1):
					newLeft += self.gridSize
					idX = int(round(newLeft / self.gridSize) * self.gridSize)
					idY = int(round(newTop / self.gridSize) * self.gridSize)

					if str(idX) + "-" + str(idY) not in tempIds:
						locations.append([idX, idY])
						tempIds.append(str(idX) + "-" + str(idY))


			for aLocation in locations:

				locationId = str(aLocation[0]) + '-' +  str(aLocation[1])

				if locationId in allLocations:
					allLocations[locationId]['nodes'].append( node['id'] )
				else:
					allLocations[locationId] = {"id" :locationId, "nodes" : [node['id']] }



			if node['id'] == 23767:
				print node
				print locations

			#trying to save some space
			node.pop("rgb", None)
			node.pop("community", None)
			node.pop("posX", None)
			node.pop("posY", None)
			node.pop("normalized", None)



			temp.append(node)
			i+=1

			

			if i == 100000:
				with  open(self.dataIndexNodes + str(fileCounter) + '.json', "w") as f:
					f.write(json.dumps(temp))

				temp = []
				fileCounter+=1
				i = 0



		with  open(self.dataIndexNodes + str(fileCounter) + '.json', "w") as f:
			f.write(json.dumps(temp))




	#convert the central point system to the top left system
	def convertCoordinates(self, x,y):

		if x < 0:
			x = (self.totalWidth/2) + abs(x)
		else:
			x = (self.totalWidth/2) - x

		if y < 0:
			y = (self.totalHeight/2) + abs(y)
		else:
			y = (self.totalHeight/2) - y

		return [int(x),int(y)]




	def normalizeSubject(self, subject):

		org = subject

		#no punctuations
		subject = ''.join(ch for ch in subject if ch not in self.exclude)

		#no spaces
		subject = "".join(subject.split())

		#no case
		subject = subject.lower()

		#so....all punctuation subject heading...
		if subject=='':
			subject = '???'

		#try for no diacritics
		try:

			subject = unicodedata.normalize('NFKD', subject).encode('ascii','ignore')

		except:

			subject = subject
			

		return subject



	def rgb_to_hex(self,rgb):
		
		colors = {
			
			"27ce62" : "386bbb",
			"27ce36" : "e18a1f",
			"27ce27" : "8eb463",
			"27bcce" : "d11824",
			"ce2777" : "6c426d",
			"6b27ce" : "fbf731",
			"2781ce" : "9e2e48",

			"ce8c27" : "5d918e",
			"ce8927" : "d8521e",
			"273ece" : "c4d640",
			"ce2768" : "465795",
			"ce27b4" : "edc127",
				
		}

		hex =  '%02x%02x%02x' % rgb

		if hex in colors:
			return "#" + colors[hex]
		else:
			return "#" + hex


if __name__ == "__main__":

	b = indexNodes()

	b.buildNodesIndex()


	



