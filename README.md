# Planning Tools

Planning Tools is a set of programs to help with the design planning process.
It contains programs to cluster user research data like product features or
user needs. It can import data from card sorts, fielded data describing
elements of interest, or manually entered pairwise comparisons. It can cluster
data using agglomerative ("bottom-up") hierarchical clustering or graph-based
methods, and it can output data as CSV spreadsheets for further processing.

## Quickstart

```
$ python3 -m venv planning_tools_env
$ cd planning_tools_env
$ source bin/activate
$ pip install git+https://github.com/johnjung/planning_tools.git
```

## matrix

The matrix command takes an unsorted similarity matrix and clusters it using
hierarchical clustering. For small data sets you can compare these values pairwise 
and enter them into a spreadsheet manually; for an example matrix look at [sample_data/fruits_and_vegetables.csv](./sample_data/fruits_and_vegetables.csv).

You can enter pairwise comparisons like this in any spreadsheet. All items being clustered should be listed
in row and column headers. These headers should be sorted the same way so that the cells on the diagonal from the top left to the bottom right
each receive a 1.0 score, meaning that every element is perfectly similar to itself.

A score of 0.0 means that the two elements being compared have nothing in common, while scores
in between indicate increasing amounts of similarity. 

Finally, in input data it's not necessary to include the upper triangle of the matrix (cells above the diagonal)
because those cells perfectly mirror the cells in the lower triangle- the matrix script will fill in the blanks. 

To take a look at an ASCII art visualization of the unsorted data in the terminal:

```
$ matrix to-ascii sample_data/fruits_and_vegetables.csv

                                                   s                                  
                                         r         t                                  
                                       g a         r                     p            
                             c         r s         a                     i            
                             u     a   a p c       w       p b   t       n            
                             c     v   p b h p     b c     o r o o       e l p b s   c
                           s u     o l e e e e c a e a     t o r m   g   a e e a p o a
                           q m   b c e f r r a e p r b   l a c a a p r   p t p n i n r
                           u b f e a m r r r c l p r b p i t c n t e a c p t p a n i r
                           a e i a d o u i i h e l i a e m o o g o a p o l u e n a o o
                           s r g n o n i e e e r e e g a e e l e e r e r e c r a c n t
                           h s s s s s t s s s y s s e s s s i s s s s n s e s s h s s
                                                                                      
             s q u a s h   @                               ,           =         ,    
       c u c u m b e r s     @   ,             *       ,     ,   *         , *     , ,
                 f i g s       @       , , =     , ,               , ,   ,     ,      
               b e a n s     ,   @             ,       =     =   ,           ,       =
         a v o c a d o s           @                                     ,     ,      
             l e m o n s             @ ,                 *     ,         ,            
     g r a p e f r u i t       ,     , @ , ,     , ,     ,     *   , ,   =     ,      
   r a s p b e r r i e s       ,       , @ , ,   , *               , =   ,     ,      
         c h e r r i e s       =       , , @ ,   = ,               , ,   ,     ,      
           p e a c h e s                 , , @   = ,               * ,   ,     ,      
             c e l e r y     *   ,             @       ,     ,   =         , *   , , ,
             a p p l e s       ,       , , = =   @ ,               = ,   ,     =      
 s t r a w b e r r i e s       ,       , * , ,   , @               , =   ,     ,      
           c a b b a g e                             @     ,               ,     ,    
                 p e a s     ,   =             ,       @     *   ,     ,   , =   , , =
               l i m e s             * ,                 @     ,         ,            
         p o t a t o e s   ,                         ,     @                       ,  
         b r o c c o l i     ,   =             ,       *     @   ,     ,   , =   , , *
           o r a n g e s             , *                 ,     @         ,     ,      
         t o m a t o e s     *   ,             =       ,     ,   @     ,   , *   , , ,
               p e a r s       ,       , , , *   = ,               @ =   ,     =      
             g r a p e s       ,       , = , ,   , =               = @   ,     ,      
                 c o r n   =                           ,     ,   ,     @     ,   , , ,
     p i n e a p p l e s       ,   , , = , , ,   , ,     ,     ,   , ,   @     =      
           l e t t u c e     ,                 ,     , ,     ,   ,         @ ,   = ,  
           p e p p e r s     *   ,             *       =     =   *     ,   , @   , , =
           b a n a n a s       ,   ,   , , , ,   = ,           ,   = ,   =     @      
           s p i n a c h   ,                   ,     , ,     ,   ,     ,   = ,   @ , ,
             o n i o n s     ,                 ,       ,   , ,   ,     ,   , ,   , @ ,
           c a r r o t s     ,   =             ,       =     *   ,     ,     =   , , @

```

Cluster the data:

```
$ matrix cluster --linkage_method=complete sample_data/fruits_and_vegetables.csv

                                             s                                        
                                           r t                                        
                                 p         a r     g                                  
                                 i         s a     r   c                              
                                 n     c   p w     a   u   t         b a   p          
                             p   e b   h   b b     p o c   o p   c   r v c o       l s
                           a e   a a   e g e e l   e r u c m e   a   o o a t s   o e p
                           p a p p n   r r r r e l f a m e a p b r   c c b a q   n t i
                           p c e p a f r a r r m i r n b l t p e r p c a b t u c i t n
                           l h a l n i i p i i o m u g e e o e a o e o d a o a o o u a
                           e e r e a g e e e e n e i e r r e r n t a l o g e s r n c c
                           s s s s s s s s s s s s t s s y s s s s s i s e s h n s e h
                                                                                      
             a p p l e s   @ = = , = , = , , ,     ,                                  
           p e a c h e s   = @ * , ,   , , , ,                                        
               p e a r s   = * @ , = , , = , ,     ,                                  
     p i n e a p p l e s   , , , @ = , , , , , , , = ,                 ,              
           b a n a n a s   = , = = @ , , , , ,     , ,                 ,              
                 f i g s   ,   , , , @ = , , ,     ,                                  
         c h e r r i e s   = , , , , = @ , , ,     ,                                  
             g r a p e s   , , = , , , , @ = =     ,                                  
   r a s p b e r r i e s   , , , , , , , = @ *     ,                                  
 s t r a w b e r r i e s   , , , , , , , = * @     ,                                  
             l e m o n s         ,             @ * , ,                                
               l i m e s         ,             * @ , ,                                
     g r a p e f r u i t   ,   , = , , , , , , , , @ *                                
           o r a n g e s         , ,           , , * @                                
       c u c u m b e r s                               @ * * * , , , ,           , ,  
             c e l e r y                               * @ = * , , , ,           , , ,
         t o m a t o e s                               * = @ * , , , ,         , , , ,
           p e p p e r s                               * * * @ , = = =         , , , ,
               b e a n s                               , , , , @ = = =                
           c a r r o t s                               , , , = = @ = *         , ,   ,
                 p e a s                               , , , = = = @ *         , , , ,
         b r o c c o l i                               , , , = = * * @         , , , ,
         a v o c a d o s         , ,                                   @              
           c a b b a g e                                                 @ ,       , ,
         p o t a t o e s                                                 , @ ,   ,    
             s q u a s h                                                   , @ =     ,
                 c o r n                                   , ,   , , ,       = @ ,   ,
             o n i o n s                               , , , ,   , , ,     ,   , @ , ,
           l e t t u c e                               , , , ,     , ,   ,       , @ =
           s p i n a c h                                 , , ,   , , ,   ,   , , , = @
```


## cardsort

This program builds a similarity matrix from card sort data by calculating the
[Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index) of each pair of
items.

For an example of how to structure your data, take a look at
[sample_data/beer_flavor_wheel.csv](./sample_data/beer_flavor_wheel.csv).

Each line in the file contains three columns. The first is a unique identifier
for each test- the sample data contains three tests. You can label these
whatever you would like, but here these are labelled 'A', 'B', and 'C'.

The second column contains an identifier, unique to that test, for each
grouping that a participant created during the ard sort- again, you could label
these whatever you would like, but in this case groupings are labelled '01',
'02', '03', etc.

The third column contains the item itself. So in the sample data, for test 'A',
'sherry' was placed into a group by itself, labelled '01', while 'tobacco' and
'leather' were placed together into a group labelled '02'.

To create a similarity matrix from this data, run the following command:

```console
$ cardsort to-matrix sample_data/beer_flavor_wheel.csv
```

This script works for both open card sorts, where participants can place items
into whatever groups they like, and closed card sorts, where a certain number
of groups re pre-selected before the test begins. 

## similarity

This script takes similarity data, similar to what Charles Owen described in
his book Structured Planning, and converts it to a similarity matrix. 

For an example of how to structure this data, see
[sample_data/chairs.csv](./sample_data/chairs.csv). (This example is from p. 146 
of Structured Planning.)

Data files should contain headers for each column of data, and a label for each
element in the first column. At the end of the file, after a blank line, are
four rows that describe each data element. The first of those rows is labelled
'field_type', which indicates if the data in this field is discrete
(non-orderable, like 'apples', 'oranges' and 'mangos') or continuous (like the
numbers 1, 2, 3, 4.)

The next row contains a weight for each field, followed by a match_difference
and no_match_difference, as described in Structured Planning.

To create a similarity matrix based on data like this:

```console
$ similarity to-matrix sample_data/chairs.csv
```

## Contributing

There are many ways to contribute to this software- your pull requests, bug
reports, feature requests, sample data sets, and use cases are all very
welcome.  Please contact the author for more information. 

## Author

John Jung
