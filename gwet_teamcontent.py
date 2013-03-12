def unindent(s):
    s = s.strip()
    lines = s.splitlines()
    lines = [l.strip() for l in lines]
    s = '\n'.join(lines)
    return s


def printContent(workflow, graph):
    print "h2. " + unindent(workflow.title())
    print unindent(workflow.description())
    print
    print "Each worker does:"
    print "{code}"
    print unindent(workflow.workflow())
    print "{code}"
    print "History:"
    print "{code}"
    print graph.strip()
    print "{code}"
    print
