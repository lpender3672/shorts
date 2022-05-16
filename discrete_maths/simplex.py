from data import table

def simplex(tab):

  initialrowcount = tab.rowcount
  # initial row length
  Negatives = True
  i = 0
  fullthetacollumn = []
  while Negatives:
    # last row in table take smallest Value
    finalrow = tab.getrow((i+1) * initialrowcount - 1)
    
    
    smallestval = min(finalrow)
    smallestvalindex = finalrow.index(smallestval)

    if smallestval >= 0: #

      Negatives = False
      continue
    
    # getcells above that row and calculate thetas for each row above
    pivotcolumn = tab.getcollumn(smallestvalindex)[i*initialrowcount:-1]
    valuecolumn = tab.getcollumn(tab.collumncount - 1)[i*initialrowcount:-1]
    
    thetacolumn = []
    for s,v in zip(pivotcolumn, valuecolumn):
      if s == 0:
        thetacolumn.append(999999) # div by 0 is infinity
      else:
        thetacolumn.append(v/s)

    fullthetacollumn += thetacolumn + [0]

    # take the smallest value of theta above 0
    for theta in sorted(thetacolumn):
      if theta > 0:
        thetaval = theta
        break
    pivotcolumnindex = smallestvalindex
    pivotrowindex = i*initialrowcount + thetacolumn.index(thetaval)
    pivotval = tab.getitem(pivotcolumnindex, pivotrowindex)

    # add initialrowlength more rows
    for r in range(initialrowcount):
      tab.addrow([0 for k in range(tab.collumncount)])


    identityrowindex = pivotrowindex + initialrowcount

    # at the row (table.rowcount - initialrowlength + pivotrow) set to (lambda self,i: self.tab[pivotrow][i] / pivot)
    tab.setrow(identityrowindex, lambda self,i: self.tab[pivotrowindex][i] / pivotval)

    # reapeat for table.rowcount
    for rowindex in range((i+1)*initialrowcount, (i+2) * initialrowcount):
      
      if rowindex == identityrowindex:
        tab.rownames.append(tab.collumnnames[pivotcolumnindex])
        continue
      tab.rownames.append(tab.rownames[rowindex - initialrowcount])
      # C = cell(table.rowcount - initialrowlength + pivotrow , pivotcolumn)
      C = tab.getitem(pivotcolumnindex, rowindex - initialrowcount)
      
      # setrow(rownumber,  lambda self,i: self.tab[table.rowcount - initialrowlength + rownumber][i] + C * self.tab[table.rowcount - originalrowlength + pivotrow][i])
      key = lambda self,i: self.tab[rowindex - initialrowcount][i] - C * self.tab[identityrowindex][i]
      tab.setrow(rowindex, key)
    
    i+=1
  fullthetacollumn += list(0 for i in range(initialrowcount))
  tab.collumnnames.append("theta")
  tab.addcollumn(fullthetacollumn)
  
  return tab