def addToGraph(g, namespace, connections_text):
    """Parse the connections_text and create a graph from it.

    Uses the Solarized color scheme.

    """
    # XXX: this should be split up, we may want to create a standlone tool which
    #      can map out arbitrary git repositories

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
