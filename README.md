# Recommender System Design
 Developed a recommendation system using Amazon Product Co-purchase data to make Book Recommendations using Network Analysis with a composite scoring technique.
 
 Description of the composite score:
Metrics used:
*	Edge weight
*	Degree Centrality
*	Clustering Coefficient
*	Sales Rank
*	Total Reviews
*	Average Ratings
The edge weight was used as it deals with the group similarity. This is important as it deals with the relevance with each other. The product of degree centrality and clustering coefficient was used as it talks about the strength of the co-purchase network. Moreover, the degree centrality was min max normalized and it is multiplied with the clustering coefficient which varies from 0-1. The reciprocal of log(1+salerank) is also included as it deals with the performance of the book with min max normalized. The log is considered to scale down the value and the reciprocal is taken to account for the rank category. 1 is added to the sales rank to account for the book that contains rank 1 as this term would yield an undefined value. Finally the product of average ratings and log(total reviews) was considered to account for the product rating. The log was used to scale down the values. Moreover, this term was also min max normalized.

Score= Edge weight * (rank feature + rating feature +strength of co purchase)

