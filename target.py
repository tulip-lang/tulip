def entry_point(argv):
    print "Hello, world"
    print argv
    return 0

def target(*args):
    return (entry_point, None)
