import phlsys_fs
import phlsys_subprocess

run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext


def execute(workers, workflow):

    jobsDirs = [(w.work(workflow), w.name) for w in workers]
    next_jobsDirs = []

    # complete all the jobs from the workers
    while jobsDirs:
        for (j, d) in jobsDirs:
            with chDirContext(d):
                try:
                    j.next()
                    next_jobsDirs.append((j, d))
                except StopIteration:
                    pass
        jobsDirs = next_jobsDirs
        next_jobsDirs = []


# XXX: this doesn't really belong here and should be split up,
#      we may want to create a standlone tool which can map out
#      arbitrary git repositories
def addToGraph(g, namespace, connections_text):
    # parse the text and create a graph
    # render the graph as graphml

    # http://thirld.com/blog/2012/01/31/making-yed-import-labels-from-graphml-files/

    lines = connections_text.splitlines()
    for l in lines:
        commit_info = l.split()
        subject = commit_info[0]
        name = namespace + "_" + commit_info[1]
        parents = commit_info[2:]

        label = ""
        color = "#fdf6e3"

        project_to_color = [
            ["sez", "#b58900"],
            ["painting", "#cb4b16"],
            ["zoo", "#dc322f"],
            ["wonderland", "#d33682"],
            ["merge", "#eee8d5"],
            ["initial", "#839496"],
        ]
        for pc in project_to_color:
            if subject.startswith(pc[0]):
                color = pc[1]

        g.add_node(name, label=label, color=color)
        for p in parents:
            p_name = namespace + "_" + p
            g.add_edge(name, p_name)
