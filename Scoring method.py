import networkx
from operator import itemgetter
import matplotlib.pyplot as plt
import math

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Reading the data from amazon-books-copurchase.adjlist;
# assigning it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])
    
# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past
# (1) 
#     Geting the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.

purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph, purchasedAsin, radius=1)  
#plt.figure(figsize=(10,10))
#networkx.draw(purchasedAsinEgoGraph, node_size=100, node_color='b', edge_color='b', style='solid')
#plt.show()
# Recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
# (2) 
#     Using the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph
threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()
for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,weight=e['weight'])
# (3) 
#     Finding the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors
purchasedAsinNeighbors = [i for i in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)]

# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff
# (4) 
#     Note that, given an asin, you can get at the metadata associated with  
#     it using amazonBooks.
#     Now, a composite measure to make Top Five book 
#     recommendations based on one or more of the following metrics associated 
#     with nodes in purchasedAsinNeighbors: SalesRank, AvgRating, 
#     TotalReviews, DegreeCentrality, and ClusteringCoeff. 

salerank=[]
#for normalizong the rank
for i in purchasedAsinNeighbors:
    x=(1/(math.log10(1+amazonBooks[i]['SalesRank'])))
    salerank.append(x)
maxrank=max(salerank)
minrank=min(salerank)
#for normalizing the ratings
ratinglist=[]
for i in purchasedAsinNeighbors:
    x=amazonBooks[i]['AvgRating']*math.log10(1+amazonBooks[i]['TotalReviews'])
    ratinglist.append(x)
maxrating=max(ratinglist)
minrating=min(ratinglist)
#for normalizing the DegreeCentrality
deg_cen=[]
for i in purchasedAsinNeighbors:
    x=amazonBooks[i]['DegreeCentrality']
    deg_cen.append(x)
maxdeg=max(deg_cen)
mindeg=min(deg_cen)

rec_list=[]
for i in purchasedAsinNeighbors:
    group_similarity=purchasedAsinEgoTrimGraph.get_edge_data(i,purchasedAsin)['weight']
    rank=(1/(math.log10(1+amazonBooks[i]['SalesRank'])))
    std_rank=(rank-minrank)/(maxrank-minrank)
    rat=amazonBooks[i]['AvgRating']*math.log10(1+amazonBooks[i]['TotalReviews'])
    rat_std=(rat-minrating)/(maxrating-minrating)
    co_purchase_strength=((amazonBooks[i]['DegreeCentrality']-mindeg)/(maxdeg-mindeg))*amazonBooks[i]['ClusteringCoeff']
    c_score=group_similarity*(std_rank+rat_std+co_purchase_strength) 
    tup=(i,c_score)
    rec_list.append(tup)

recommendations=sorted(rec_list,key=itemgetter(1),reverse=True)
final=[]
l=0
if len(recommendations)>=5:
    for i,j in recommendations:
        final.append(i)
        l=l+1
        if l>4:
            break
else:
    for i,j in recommendations:
        final.append(i)


# Printing Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff)
# (5)   
print ("--------------------------------------------------------------")
for i in final:
    print ("ASIN = ", purchasedAsin) 
    print ("Title = ", amazonBooks[i]['Title'])
    print ("SalesRank = ", amazonBooks[i]['SalesRank'])
    print ("TotalReviews = ", amazonBooks[i]['TotalReviews'])
    print ("AvgRating = ", amazonBooks[i]['AvgRating'])
    print ("DegreeCentrality = ", amazonBooks[i]['DegreeCentrality'])
    print ("ClusteringCoeff = ", amazonBooks[i]['ClusteringCoeff'])

