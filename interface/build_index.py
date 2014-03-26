from pyelasticsearch import ElasticSearch
import os, json

class index:


	dataNodes = "data/nodes/"
	dataEdges = "data/edges/"
	dataCircles = "data/circles/"
	dataBase = "data/"
	dataIndexNodes = 'data/index/nodes/'
	dataTitles = "data/titles/"


	def indexNodes(self):

		es = ElasticSearch('http://0.0.0.0:9200')

		i = 0
		for file in os.listdir(self.dataIndexNodes):

			if file.endswith('.json'):

				with open(self.dataIndexNodes + file, "r") as f:

					nodes = json.loads(f.read())
					print ("Indexing Node data", self.dataIndexNodes + file, len(nodes))

					bulkCount = 0
					bulkAry = []

					for node in nodes:




						i += 1

						if (i < 170000):
							continue

						bulkCount = bulkCount + 1
						bulkAry.append(node);

						if bulkCount == 1000:

							es.bulk_index('nodes','node',bulkAry, id_field='id')
							bulkCount = 0
							bulkAry = []


						print i

					if len(bulkAry) != 0:
						es.bulk_index('nodes','node',bulkAry, id_field='id')
	



if __name__ == "__main__":

	b = index()

	b.indexNodes()