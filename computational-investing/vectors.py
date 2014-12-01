import sys

#TARGET=10
#LENGTH=4
#for vec in vectors(LENGTH, TARGET):
#    print [ v / float(TARGET) for v in vec ]

def vectors(length, target):
    """
    Generate all lists of whole numbers of given
    length that add up to the target value.
    """
    if length == 1:
        yield [target]
    else:
        for firstval in range(target+1):
            for rest in vectors(length-1, target-firstval):
                yield [firstval] + rest

if __name__ == '__main__':
    for vec in vectors(int(sys.argv[1]), int(sys.argv[2])):
        print vec

