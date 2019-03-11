# insight_matrix

An insight matrix is a tool to discover relationships between items. If you
take a set of items, and compare every item against every item, you get a
similarity matrix. Then you can use hierarchical clustering on that similarity
matrix to automatically extract groups. [I put together these notes for an
overview of this kind of
clustering](http://johnjung.us/hierarchical-clustering.pdf).

This program takes an Excel spreadsheet with similarity information as input.
Then it returns as output a copy of that spreadsheet with a new, sorted
worksheet attached.

For small sets of items you can do pairwise comparisons manually. I like to do
card sorts to collect similarity data when sets have up to about a hundred
items.  Programmatic techniques should be appropriate for even larger groups. 

## Quickstart

```
docker build -t insight_matrix https://github.com/johnjung/insight_matrix.git
docker run --rm -it -p 5000:5000 insight_matrix start
curl -X POST -F 'spreadsheet=@test_data/fruits.xlsx' http://0.0.0.0:5000/sort > sorted_matrix.xlsx
```

## TODO

Look at ways to use graphs for clustering. [These slides describe some algorithms.] (https://www.csc2.ncsu.edu/faculty/nfsamato/practical-graph-mining-with-R/slides/pdf/Graph_Cluster_Analysis.pdf)

## Contributing

Please contact the author with pull requests, bug reports, and feature
requests.

## Author

John Jung

## Acknowledgements

Vijay Kumar, professor at the Institute of Design, first introduced me to this
technique. You can read about it and other methods in his book, [101 Design
Methods](http://www.101designmethods.com).
