from data import network, vertex, table
import equation as eq
import math, time
import sys
import simplex
import dijkstras



def quicksortiteration(l): # bad code
  p = math.ceil((len(l)-1)/2)
  pivot = l[p]
  a,b = l[0:p],l[p+1:len(l)]
  afin,bfin = [],[]
  for item in a:
    if item > pivot:
      bfin.append(item)
  for item in a:
    if item < pivot:
      afin.append(item)
  for item in b:
    if item < pivot:
      afin.append(item)
  for item in b:
    if item > pivot:
      bfin.append(item)
  return [afin,pivot,bfin]
    


net = network(["S", "A", "B","C","D","T"])

# net.addarc(from, to, weight, directional?)

net.addarc("S", "A", 5)
net.addarc("S", "B", 6)
net.addarc("S", "C", 2)
net.addarc("C", "B", 2)
net.addarc("A", "D", 4)
net.addarc("B", "D", 4)
net.addarc("B", "T", 8)
net.addarc("D", "T", 3)
net.addarc("C", "T", 12)

  
"""
shortestpath = dijkstras.dijkstras(net, "S")  
for key in shortestpath.vertexes:
  v = shortestpath.vertexes[key]
  print(v.name, v.step, v.values[1:])
"""

tab = table(0,6) # 6 rows in the table

tab.collumnnames = ["x","y","z","r","s","v"] # ignore theta

#             x   y   z r s    v 
tab.addrow([ 15, 25, 40,1,0, 700])  # r
tab.addrow([  1,  2, 4 ,0,1,  60])  # s
tab.addrow([ -5, -9,-15,0,0,   0])  # p

tab.rownames = ["r",
                "s",
                "p"]

# P must always be at bottom row
# V must always be at the end collumn
 


#tab.setrow(1, lambda self,i: self.tab[0][i]/2) sets row 1 to row 0/2
#   setrow(replace row index, lamda self,i: self.tab[copy row index][i])
# works well

#tab.addrow([1,2,3,4,5])
tab = simplex.simplex(tab)

print("finished table")
tab.printsimplex()
