# Planning Tools

v.0.0.1

This repository contains scripts to help with different design methods used in the planning process.

### Insight Matrix

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

### Quickstart

```
$ python3 -m venv design_methods_env
$ source design_methods_env/bin/activate
$ git clone https://github.com/johnjung/design_methods.git
$ cd design_methods
$ python insight_matrix.py --help
```

#### View some sample data in the terminal.
```
$ cat sample_data/fruits_and_vegetables.csv | ./insight_matrix.py show -

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
                                                                                      
             s q u a s h   @                                                          
       c u c u m b e r s     @                                                        
                 f i g s       @                                                      
               b e a n s     ,   @                                                    
         a v o c a d o s           @                                                  
             l e m o n s             @                                                
     g r a p e f r u i t       ,     , @                                              
   r a s p b e r r i e s       ,       , @                                            
         c h e r r i e s       =       , , @                                          
           p e a c h e s                 , , @                                        
             c e l e r y     *   ,             @                                      
             a p p l e s       ,       , , = =   @                                    
 s t r a w b e r r i e s       ,       , * , ,   , @                                  
           c a b b a g e                             @                                
                 p e a s     ,   =             ,       @                              
               l i m e s             * ,                 @                            
         p o t a t o e s   ,                         ,     @                          
         b r o c c o l i     ,   =             ,       *     @                        
           o r a n g e s             , *                 ,     @                      
         t o m a t o e s     *   ,             =       ,     ,   @                    
               p e a r s       ,       , , , *   = ,               @                  
             g r a p e s       ,       , = , ,   , =               = @                
                 c o r n   =                           ,     ,   ,     @              
     p i n e a p p l e s       ,   , , = , , ,   , ,     ,     ,   , ,   @            
           l e t t u c e     ,                 ,     , ,     ,   ,         @          
           p e p p e r s     *   ,             *       =     =   *     ,   , @        
           b a n a n a s       ,   ,   , , , ,   = ,           ,   = ,   =     @      
           s p i n a c h   ,                   ,     , ,     ,   ,     ,   = ,   @    
             o n i o n s     ,                 ,       ,   , ,   ,     ,   , ,   , @  
           c a r r o t s     ,   =             ,       =     *   ,     ,     =   , , @

```

#### Fill the upper triangle with data from the lower triangle.
```
$ cat sample_data/fruits_and_vegetables.csv | ./insight_matrix.py fill --upper - | ./insight_matrix.py show -

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

#### Cluster data.
```
$ cat sample_data/fruits_and_vegetables.csv | ./insight_matrix.py fill --upper - | ./insight_matrix.py cluster --linkage_method=average - | ./insight_matrix.py show -

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

#### Get clustered data as CSV. 
```
$ cat sample_data/fruits_and_vegetables.csv | ./insight_matrix.py fill --upper - | ./insight_matrix.py cluster --linkage_method=average - > clustered_data.csv
```

## Contributing

Please contact the author with pull requests, bug reports, and feature
requests.

## Author

John Jung
