

def pascal(n):

    a = [[1]]
    for i in range(n-1):
        a.append( [1] + [ a[i][j] + a[i][j+1] for j in range(i) ] + [1] )
    return a

print(pascal(4))

