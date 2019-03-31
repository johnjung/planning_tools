import numpy

a = [0.0, 0.5, 1.0]

count, bin_start = numpy.histogram(a, bins=101, range=(0.0, 1.0))

total = sum(count) 

# histogram max is the largest non-zero bin.
h_max = max(count[1:])

i = 0
total_count = 0
while i < len(bin_start) - 1:
  print('{:.2f}: {} {}'.format(
    bin_start[i],
    count[i], 
    1.0 * count[i] / total_count
  ))
  total_count = total_count + count[i]
  i = i + 1

# FREQUENCY CLASS, NUMBER, PERCENT, CUMULATIVE PERCENT, CUMULATIVE REMAINDER
# see S.P, p. 159.

# then you're gonna set a threshold from phase 1 to make a non-directed
# graph where all links are at or above threshold strength.
