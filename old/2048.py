import random,replit,time
normalgroup = [[8,8,16,32],
               [2,0,0,0],
               [8,8,16,0],
               [0,0,0,0]]
positions,rotations=["up","left","down","right"],[90,180,270]
def equalizer(group,a):
  l=[]
  for i in range(3):
    b=i+1
    if group[a][4-b]==group[a][4-(b+1)] and group[a][4-b] != 0 :
      l.append([a,b,group[a][4-b]])
  return l
def theadder(group,a):
  pairs = equalizer(group,a)
  if len(pairs) == 3:
        group[a][3],group[a][2]=group[a][3]*2,0
        group[a][1],group[a][0]=group[a][1]*2,0
  else:
    for i in range(len(pairs)):
        if len(pairs)==2 and pairs[0][2]==pairs[1][2]:
          if group[a][3]==group[a][2]:
            group[a][3]=group[a][3]*2
            group[a][2]=0
        else:
          group[pairs[i][0]][4-pairs[i][1]] = group[pairs[i][0]][4-pairs[i][1]]*2
          group[pairs[i][0]][4-(pairs[i][1]+1)]=0
  sort(group,False)
def sort(group,boolean):
  for i in range(3):
    for i in range(4):
      a=i
      for i in range(3):
        b=i+1
        if group[a][4-b] == 0 and group[a][4-(b+1)] != 0:
            group[a][4-b]=group[a][4-(b+1)]
            group[a][4-(b+1)]=0
      if boolean:
        theadder(group,a)
  return group
def rotated(l):
    list_of_tuples = zip(*l[::-1])
    return [list(elem) for elem in list_of_tuples]
def rotate(angle,l):
  for i in range(int(angle/90)):
    a=rotated(l)
    l=a
  return a
def randomplacements(group):
  history = 0
  num=random.randint(1,10)
  x,y=random.randint(0,3),random.randint(0,3) # have you ever seen a more efficient method?
  if group[x][y]==0:
    if num <= 6: 
      group[x][y] = 4
    else: 
      group[x][y] = 2
  elif history > 100:
    print("YOU LOOSE")
    group=0
  else:
    history+=1
    randomplacements(group)
  return group
print("type left right up or down")
normalgroup=randomplacements(normalgroup)
for i in range(4):
 print(normalgroup[i])
while True:
  move=input("ENTER A MOVE")
  for i in range(3):
    if move.lower() == positions[i]:
          temp=rotate(rotations[2-i],sort(rotate(rotations[i],normalgroup),True))
    elif move.lower()=="right":
      temp=sort(normalgroup,True)
  try: temp
  except NameError:
    print("type left right up or down")
  else:
    normalgroup=randomplacements(temp)
    if normalgroup == 0:
      break
    for i in range(4):
      print(temp[i])
      if 2048 in normalgroup[i]:
        print("winner")
        break