import phlsys_fs
import phlsys_subprocess

import gwet_teamcontent

run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext


def doWorkflow(g, workflow, workers):
    git_log_graph_params = ["--all", "--graph", "--oneline"]
    git_log_parents_message_params = ["--format=%f %h %p"]
    git_log_params_list = [
        git_log_graph_params, git_log_parents_message_params]
    graphs = simulate(workers, workflow, git_log_params_list)
    graph = graphs[0]
    connections = graphs[1]
    gwet_teamcontent.printContent(workflow, graph)
    namespace = ''.join(workflow.title().split())
    addToGraph(g, namespace, connections)


def simulate(workers, workflow, git_log_param_list_list):
    tempdir_name = "_workflow_tempdir"
    run("rm", "-rf", tempdir_name)
    run("mkdir", tempdir_name)

    graphs = []

    with chDirContext(tempdir_name):
        central_repo_name = "origin"
        createCentralizedRepoAndWorkers(
            central_repo_name,
            [w.name for w in workers])

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

        # graph the result on master
        with chDirContext(central_repo_name):
            for params in git_log_param_list_list:
                graphs.append(run("git", "log", *params).stdout)

    run("rm", "-rf", tempdir_name)
    return graphs


def createCentralizedRepoAndWorkers(central_repo_name, worker_names):
    run("mkdir", central_repo_name)
    with chDirContext(central_repo_name):
        run("git", "init", "--bare")
    for w in worker_names:
        run("git", "clone", central_repo_name, w)
    worker = worker_names[0]
    with chDirContext(worker):
        run("touch", "README")
        run("git", "add", "README")
        run("git", "commit", "README", "-m", "initial commit")
        run("git", "push", "origin", "master")
    for w in worker_names:
        with chDirContext(w):
            run("git", "pull")


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
