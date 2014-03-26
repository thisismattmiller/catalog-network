#import postgresql, json, numpy, scipy.spatial
#from math import isinf
from __future__ import division
import xml.etree.ElementTree as etree
from pgmagick import Image, DrawableCircle, DrawableText, Geometry, Color, ColorRGB, CompositeOperator as co, ResolutionType, DrawableList, TypeMetric, DrawableRectangle, DrawableLine, DrawableStrokeOpacity, DrawableStrokeWidth, DrawableStrokeColor
import sys, math, json, os,operator



class buildNetworkImage:


	allNodes = []

	xmlFile = "data/io_gexf_latest.gexf"

	dataNodes = "data/nodes/"
	dataEdges = "data/edges/"
	dataCircles = "data/circles/"
	dataBase = "data/"


	buildCounterNode = 0
	buildCounterNodeTotal = 0


	totalWidth = 0
	totalHeight = 0

	scaleFactor = 4.75

	def xml2Json(self):

		print ("Parsing xml file",self.xmlFile)
		tree = etree.parse(self.xmlFile)
		print ("Root")
		root = tree.getroot()
		nodes = root.find('{http://www.gexf.net/1.2draft}graph').find('{http://www.gexf.net/1.2draft}nodes')
		xSmall = Xlarge = Ysmall = Ylarge = 0

		print ("Reading Edges")
		e = i = fileCounter = 0

		edges = root.find('{http://www.gexf.net/1.2draft}graph').find('{http://www.gexf.net/1.2draft}edges')

		temp = []

		for edge in edges:
			id = edge.get('id')
			source = edge.get('source')
			target = edge.get('target')
			weight = edge.get('weight')

			if id == None:
				id = 0
			if source == None:
				source = 0
			if target == None:
				target = 0
			if weight == None:
				weight = 0

			output = {"id" : int(id), "source" : int(source), "target" : int(target), "weight" : int(float(weight))}

			temp.append(output)

			if i == 100000:
				with  open(self.dataEdges + str(fileCounter) + '.json', "w") as f:
					f.write(json.dumps(temp))

				temp = []
				fileCounter+=1
				i = 0

			e+=1
			i+=1
			print e,"          \r",


		with  open(self.dataEdges + str(fileCounter) + '.json', "w") as f:
			f.write(json.dumps(temp))


		print ("Reading Nodes")
		n = i = fileCounter = 0
		temp = []

		for node in nodes:

			n+=1
			print n,"          \r",

			name = node.get('label')
			id = node.get('id')
			size = node.find('{http://www.gexf.net/1.2draft/viz}size').get('value')
			posX = float(node.find('{http://www.gexf.net/1.2draft/viz}position').get('x'))
			posY = float(node.find('{http://www.gexf.net/1.2draft/viz}position').get('y'))
			community = node.find('{http://www.gexf.net/1.2draft}attvalues').find('{http://www.gexf.net/1.2draft}attvalue').get('value')
			rgb = node.find('{http://www.gexf.net/1.2draft/viz}color').get('r') +  "," + node.find('{http://www.gexf.net/1.2draft/viz}color').get('g') + ',' + node.find('{http://www.gexf.net/1.2draft/viz}color').get('b')

			self.allNodes.append([name, size, posX,posY, community, rgb, id])
			#cords.append([posX,posY])

			if posX < xSmall:
				xSmall = posX
			if posX > Xlarge:
				Xlarge = posX
			if posY < Ysmall:
				Ysmall = posY
			if posY > Ylarge:
				Ylarge = posY

			output = {"name" : name, "id" : int(id), "size" : int(float(size)), "posX" : posX, "posY" : posY, "community" : int(community), "rgb" : [int(x) for x in rgb.split(",")] }
			temp.append(output)

			if i == 100000:
				with  open(self.dataNodes + str(fileCounter) + '.json', "w") as f:
					f.write(json.dumps(temp))
				temp = []
				fileCounter+=1
				i = 0

			i+=1


		with  open(self.dataNodes + str(fileCounter) + '.json', "w") as f:
			f.write(json.dumps(temp))


		self.totalWidth = int(math.ceil((abs(xSmall) + abs(Xlarge)) / 100.0)) * 100
		self.totalHeight = int(math.ceil((abs(Ysmall) + abs(Ylarge)) / 100.0)) * 100

		with  open(self.dataBase  + 'base.json', "w") as f:
			f.write(json.dumps({ "nodes" : n, "edges" : e, "height" : self.totalHeight, "width" : self.totalWidth  }))

		print("total width: ",self.totalWidth, "total height",self.totalHeight)




	def reportNodes(self):

		#first build the image, we need to know how big it is
		with open(self.dataBase + "base.json", "r") as f:
			base = json.loads(f.read())
		
		self.totalWidth = base['width']
		self.totalHeight = base['height']



		communities = {}
		sizes = {}

		for file in os.listdir(self.dataNodes):
			if file.endswith('.json'):
				with open(self.dataNodes + file, "r") as f:
					nodes = json.loads(f.read())
					print ("Building Nodes", self.dataNodes + file, len(nodes))
					self.buildCounterNodeTotal = len(nodes)
					self.buildCounterNode = 0

					for node in nodes:

						if str(node['community']) in communities:
							communities[str(node['community'])]['count'] += 1
						else:
							color = (node['rgb'][0],node['rgb'][1],node['rgb'][2])
							color = self.rgb_to_hex( color )
							communities[str(node['community'])] = { "count" : 1, "rgb" : node['rgb'], "hex" : color }


						if str(node['size']) in sizes:
							sizes[str(node['size'])]['count'] += 1
						else:
							sizes[str(node['size'])] = { "count" : 1 }

						cords = self.convertCoordinates(int(node['posX']),int(node['posY']))
						print cords, node['name']

						
		communities_sorted = sorted(communities.iteritems(), key=operator.itemgetter(1))

		with open("report_community", 'w') as f:

			for x in communities_sorted:
				f.write(str(x) + "\n\n")

					
		sizes_sorted = sorted(sizes.iteritems(), key=operator.itemgetter(1))

		with open("report_size", 'w') as f:

			for x in sizes_sorted:
				f.write(str(x) + "\n\n")





	def buildNodes(self):
		

		for file in os.listdir(self.dataNodes):
			if file.endswith('.json'):
				with open(self.dataNodes + file, "r") as f:
					nodes = json.loads(f.read())
					print ("Building Nodes", self.dataNodes + file, len(nodes))
					self.buildCounterNodeTotal = len(nodes)
					self.buildCounterNode = 0

					for node in nodes:
						self.buildNodeImage(node)




	def buildNodeImage(self,node):
		

		self.buildCounterNode+=1

		node['name'] = node['name'].encode("utf-8")


		print "{0:.2f}".format(self.buildCounterNode / (self.buildCounterNodeTotal) * 100)," percent complete of this batch                                         \r",

		scale = self.scaleFactor

		#if node['size'] > 10:

		#cale = 4.75

		#if node['size'] < 900:
		#	scale = 4




		circleHeight = int(float(node['size'])*scale)
		circleWidth = int(float(node['size'])*scale)


		canvasHeight = int(circleHeight *2)
		canvasWidth = int(circleWidth* 2) 


		im = Image(Geometry(10,10), 'transparent')
		fontsize = self.returnFontSize(canvasHeight)
		im.fontPointsize(fontsize)
		tm = TypeMetric()
		im.fontTypeMetrics(node['name'], tm)

		if tm.textWidth() > canvasWidth:
			canvasWidth = int(tm.textWidth()) + 5

		im = Image(Geometry(canvasWidth,canvasHeight), 'transparent')
		im.density("72x72")
		im.magick('RGB')
		im.resolutionUnits(ResolutionType.PixelsPerInchResolution)

		im.strokeAntiAlias(True)

		color = (node['rgb'][0],node['rgb'][1],node['rgb'][2])

		color = self.rgb_to_hex( color )
		im.fillColor(color);

		im.strokeWidth(2);

		if circleWidth <= 20:
			im.strokeColor("transparent");
		else:
			im.strokeColor("black");

		if circleWidth <= 50:
			im.strokeWidth(1);


		circle = DrawableCircle( canvasWidth/2 , canvasHeight/2, (canvasWidth/2) + (circleWidth/2), (canvasHeight/2) + (circleHeight/2))
		im.draw(circle)

		im.fillColor("white");
		im.strokeColor("black");
		im.strokeWidth(1);



		fontsize = self.returnFontSize(canvasHeight)
		im.fontPointsize(fontsize)

		

		tm = TypeMetric()
		im.fontTypeMetrics(node['name'], tm)

		textWidth = tm.textWidth()
		textHeight = tm.textHeight()


		if fontsize <= 30:
			im.strokeColor("transparent")
		

		text = DrawableText((canvasWidth / 2) - (textWidth/2), canvasHeight/2 + 6 , node['name'])
		im.draw(text)
		


		im.write(self.dataCircles + str(node['id']) + '.png')






	def edgeTest(self):

		#first build the image, we need to know how big it is
		with open(self.dataBase + "base.json", "r") as f:
			base = json.loads(f.read())
		
		self.totalWidth = base['width']
		self.totalHeight = base['height']



		print ("Creating large base image", int(self.totalWidth), 'x',int(self.totalHeight) )
		#im = Image(Geometry(int(self.totalWidth), int(self.totalHeight)), Color("black"))
		im = Image(Geometry(5000, 5000), Color("black"))

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


		totalEdges = 0
		for file in os.listdir(self.dataEdges):	

			if file.endswith('.json'):

				with open(self.dataEdges + file, "r") as f:

					edges = json.loads(f.read())
					print ("Building Image Edges", self.dataEdges + file, len(edges))
					self.buildCounterNodeTotal = len(edges)
					self.buildCounterNode = 0

					drawlist = DrawableList()

					for edge in edges:

						sourcePos = allNodes[edge['source']]['posX'], allNodes[edge['source']]['posY']
						targetPos = allNodes[edge['target']]['posX'], allNodes[edge['target']]['posY']


						width = abs(sourcePos[0]-targetPos[0])
						height = abs(sourcePos[1]-targetPos[1])

						

						dx = targetPos[0] - sourcePos[0]
						dy = targetPos[1] - sourcePos[1] 

						dxdy = (dx*dx) + (dy*dy)

						dist = math.sqrt( dxdy )

						dxdy = (dx*dx) + (dy*dy)

						dist = math.sqrt( dxdy )

						#midpoint
						mx = (targetPos[0] + sourcePos[0]) / 2
						my = (targetPos[1] + sourcePos[1]) / 2


					

						#print width, height, dist
						totalEdges+=1

				 		color = (allNodes[edge['source']]['rgb'][0],allNodes[edge['source']]['rgb'][1],allNodes[edge['source']]['rgb'][2])

						color = self.rgb_to_hex( color )



						
						drawlist.append(DrawableStrokeColor(color))
						drawlist.append(DrawableStrokeOpacity(0.25))
						drawlist.append(DrawableLine(0,height,width,0))


						#line = Image(Geometry(int(width), int(height)), Color("black"))
						#line.strokeColor("blue");

						#line.draw(drawlist)


						cords = self.convertCoordinates(int(mx),int(my))

						print str(totalEdges),  "                   \r",
						sys.stdout.flush()

						#line.write(str(edge['id']) + 'line.png')
						
						#im.composite(line, int(cords[0]), int(cords[1]), co.OverCompositeOp)



						if totalEdges > 1000:

							im.draw(drawlist)

							print ("")
							print ("Writing large file out")
							im.write('base.png')
							sys.exit()


		print totalEdges
		sys.exit()



	def buildImageNodes(self):

		#first build the image, we need to know how big it is
		with open(self.dataBase + "base.json", "r") as f:
			base = json.loads(f.read())
		
		self.totalWidth = base['width']
		self.totalHeight = base['height']



		print ("Creating large base image", int(self.totalWidth), 'x',int(self.totalHeight) )
		im = Image(Geometry(int(self.totalWidth), int(self.totalHeight)), Color("black"))
		#im = Image(Geometry(int(50000), int(50000)), Color("black") )




		#im.strokeColor("blue");
		#im.strokeOpacity(0.15)

		# allNodes = {}

		# for file in os.listdir(self.dataNodes):

		# 	if file.endswith('.json'):

		# 		with open(self.dataNodes + file, "r") as f:

		# 			nodes = json.loads(f.read())
		# 			print ("Storing Nodes data", self.dataNodes + file, len(nodes))
		# 			self.buildCounterNodeTotal = len(nodes)
		# 			self.buildCounterNode = 0

		# 			for node in nodes:


		# 				allNodes[node['id']] = node

		# 				# if node['id'] in allNodes:
		# 				# 	allNodes[node['id']].append(node)
		# 				# else:
		# 				# 	allNodes[node['id']] = [node]


		# totalEdges = 0
		# for file in os.listdir(self.dataEdges):	

		# 	if file.endswith('.json'):

		# 		with open(self.dataEdges + file, "r") as f:

		# 			edges = json.loads(f.read())
		# 			print ("Building Image Edges", self.dataEdges + file, len(edges))
		# 			self.buildCounterNodeTotal = len(edges)
		# 			self.buildCounterNode = 0

		# 			for edge in edges:

		# 				sourcePos = allNodes[edge['source']]['posX'], allNodes[edge['source']]['posY']
		# 				targetPos = allNodes[edge['target']]['posX'], allNodes[edge['target']]['posY']






		# 				width = abs(sourcePos[0]-targetPos[0])
		# 				height = abs(sourcePos[1]-targetPos[1])

						

		# 				dx = targetPos[0] - sourcePos[0]
		# 				dy = targetPos[1] - sourcePos[1] 

		# 				dxdy = (dx*dx) + (dy*dy)

		# 				dist = math.sqrt( dxdy )

		# 				dxdy = (dx*dx) + (dy*dy)

		# 				dist = math.sqrt( dxdy )

		# 				#midpoint
		# 				mx = (targetPos[0] + sourcePos[0]) / 2
		# 				my = (targetPos[1] + sourcePos[1]) / 2


		# 				if dist <= 10000:
		# 					#print width, height, dist
		# 					totalEdges+=1

		# 			 		color = (allNodes[edge['source']]['rgb'][0],allNodes[edge['source']]['rgb'][1],allNodes[edge['source']]['rgb'][2])

		# 					color = self.rgb_to_hex( color )



		# 					drawlist = DrawableList()
		# 					drawlist.append(DrawableStrokeColor(color))
		# 					drawlist.append(DrawableStrokeOpacity(0.25))
		# 					drawlist.append(DrawableLine(0,height,width,0))


		# 					line = Image(Geometry(int(width), int(height)), Color("black"))
		# 					#line.strokeColor("blue");

		# 					line.draw(drawlist)


		# 					cords = self.convertCoordinates(int(mx),int(my))

		# 					print str(totalEdges),  "                   \r",
		# 					sys.stdout.flush()

		# 					#line.write(str(edge['id']) + 'line.png')
							
		# 					im.composite(line, int(cords[0]), int(cords[1]), co.OverCompositeOp)


		# 				if totalEdges > 1000:

		# 					print ("")
		# 					print ("Writing large file out")
		# 					im.write('base.png')
		# 					sys.exit()


		# print totalEdges
		# sys.exit()


		# for file in os.listdir(self.dataEdges):

		# 	if file.endswith('.json'):

		# 		with open(self.dataEdges + file, "r") as f:

		# 			edges = json.loads(f.read())
		# 			print ("Building Image Edges", self.dataEdges + file, len(edges))
		# 			self.buildCounterNodeTotal = len(edges)
		# 			self.buildCounterNode = 0

		# 			for edge in edges:

		# 				sourcePos = self.convertCoordinates(allNodes[edge['source']]['posX'], allNodes[edge['source']]['posY'])
		# 				targetPos = self.convertCoordinates(allNodes[edge['target']]['posX'], allNodes[edge['target']]['posY'])
		# 				im.draw(DrawableLine(sourcePos[0],sourcePos[1],targetPos[0],targetPos[1]))
		# 				print sourcePos, targetPos



		# sys.exit()





	def buildImage(self):


		#first build the image, we need to know how big it is
		with open(self.dataBase + "base.json", "r") as f:
			base = json.loads(f.read())
		
		self.totalWidth = base['width']
		self.totalHeight = base['height']



		print ("Creating large base image", int(self.totalWidth), 'x',int(self.totalHeight) )
		im = Image(Geometry(int(self.totalWidth), int(self.totalHeight)), Color("black"))


		#throw a logo onnn
		#layer = Image('logo.png')
		#im.composite(layer, 0, 0, co.OverCompositeOp)


		for file in os.listdir(self.dataNodes):

			if file.endswith('.json'):

				with open(self.dataNodes + file, "r") as f:

					nodes = json.loads(f.read())
					print ("Building Image Nodes", self.dataNodes + file, len(nodes))
					self.buildCounterNodeTotal = len(nodes)
					self.buildCounterNode = 0

					for node in nodes:

						self.buildCounterNode+=1

						print (self.buildCounterNode / self.buildCounterNodeTotal * 100)," percent complete of this batch                                         \r",
						layer = Image(self.dataCircles + str(node['id']) +'.png')

						cords = self.convertCoordinates(node['posX'],node['posY'])

						im.composite(layer, int(cords[0]), int(cords[1]), co.OverCompositeOp)


		print ("")
		print ("Writing large file out")
		im.write('base.png')




	def returnFontSize(self, canvasHeight):

		fontsize = 10 * (canvasHeight/50)

		if fontsize < 15:
			fontsize = 15

		
		return fontsize




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



#im = Image(Geometry(129674, 129527), Color("yellow"))
#sys.exit()


if __name__ == "__main__":

	b = buildNetworkImage()

	b.xml2Json()

	b.reportNodes()

	b.buildNodes()
	
	b.buildImage()

	






