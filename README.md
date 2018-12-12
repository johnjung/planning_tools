# insight_matrix

An insight matrix is a symmetric matrix...

I use the hierarchical clustering from the numpy python library to get a sort
order for the matrix.  Then I reorder the matrix and return a reordered Excel
spreadsheet to the user. 

## Quickstart

```
docker build -t insight_matrix https://github.com/johnjung/insight_matrix.git
docker run --rm -it -p 5000:5000 insight_matrix start
```
