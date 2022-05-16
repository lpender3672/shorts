
def list_splitter(i): # splits string list [12345] => [12 3 45] as i => [a c b]
    n = len(i)
    if len(i) % 2 == 0:
        a ,b = i[ 0 : n // 2 ] ,i[ n // 2 : n]
        c = ""
    else:
        a ,b = i[0 : n // 2 ], i[ n // 2 + 1 : len(i)]
        c = i[len(i) // 2]
    return a, c ,b


def increment_centre(a, c, b):
    n = int(a + c)
    n += 1
    return str(n) + b


def mirror(i):
    a, c, b = list_splitter(i)
    b = a[::-1]
    return a + c + b


def get_next_smallest_palindrome(number):
    if type(number) is not int:
        raise TypeError("error in get_next_smallest_palindrome type(number) must be an integer")

    a, c, b = list_splitter(str(number))

    if a == b[::-1]:  # if already palindrome

        ## add one to centre
        n = increment_centre(a, c, b)
        return int(mirror(str(n)))

    n = int(mirror(str(number)))
    # works for cases a c b where a > b because mirroring a to b
    # will give a larger number

    if n < number:  # if a c b where b > a so mirroring will make a smaller palindrome

        a, c, b = list_splitter(str(n))

        # add one to centre:
        # works because everything on the right is smaller than the centre
        # so it is the next smallest palindrome
        n = increment_centre(a, c, b)
        n = int(mirror(str(n)))

    return int(n)

print(get_next_smallest_palindrome(8567))


