#!/usr/bin/env python
# encoding: utf-8

import sys

# networkx must be installed before use
#   $ sudo apt-get install python-networkx
import networkx as nx

# important to read - the graphml won't render nicely by default:
# http://thirld.com/blog/2012/01/31/making-yed-import-labels-from-graphml-files/

import phlsys_fs
import phlsys_subprocess

import gwet_graph
import gwet_simulate
import gwet_teamcontent
import gwet_workflow

run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext


class Worker():
    """Simulate a person working with a supplied workflow.

    The worker has a name and is assigned a project to work on, they will
    perform the work in supplied list of items.
    """

    def __init__(self, name, project, items):
        self.name = name
        self.project = project
        self.items = items

    def work(self, workflow):
        yield  # XXX: we must yield immediately due to a quirk of simulate()
        workflow.start_project(self.name, self.project)
        for item in self.items:
            workflow.do_item(self.name, self.project, item)
            yield
        workflow.finish_project(self.name, self.project)


def main():
    # setup our workers
    alice = Worker("Alice", "wonderland", ["sleep", "awake"])
    bob = Worker("Bob", "zoo", ["build zoo", "fix zoo", "rebuild zoo"])
    charley = Worker("Charley", "sez", ["one", "two", "three", "four", "five"])
    dorian = Worker("Dorian", "painting", ["nose", "eyes", "hair", "grin"])

    # the workers will participate in all of these workflows
    workers = [alice, bob, charley, dorian]
    workflows = [
        gwet_workflow.RebaseMasterWorkflow(),
        gwet_workflow.RebaseTopicFfOnlyWorkflow(),
        gwet_workflow.RebaseTopicNoFfWorkflow(),
        gwet_workflow.SquashTopicWorkflow(),
        gwet_workflow.MergeTopicWorkflow(),
        gwet_workflow.MergeTopicCatchupWorkflow(),
        gwet_workflow.SvnWorkflow(),
        gwet_workflow.SvnPullWorkflow()
    ]

    # we'll be building a graph of all the commits on master at the end
    # of each simulation
    g = nx.DiGraph()

    # run all the simulations
    for workflow in workflows:
        doWorkflow(g, workflow, workers)

    # write the graph in the 'graphml' format, this is useful because the
    # 'yEd' editor will allow us to load the graph and manipulate it into a
    # form that we are happy with
    graphml = '\n'.join(nx.generate_graphml(g))
    with open("all.graphml", "w") as f:
        f.write(graphml)


def doWorkflow(g, workflow, workers):
    tempdir_name = "_workflow_tempdir"
    run("rm", "-rf", tempdir_name)
    run("mkdir", tempdir_name)

    central_repo_name = "origin"
    with chDirContext(tempdir_name):
        createCentralizedRepoAndWorkers(
            central_repo_name,
            [w.name for w in workers])
        gwet_simulate.execute(workers, workflow)

        # graph the result on master
        with chDirContext(central_repo_name):
            text_graph = run("git", "log", "--graph", "--oneline").stdout
            connections = run("git", "log", "--format=%f %h %p").stdout

    run("rm", "-rf", tempdir_name)

    gwet_teamcontent.printContent(workflow, text_graph)
    namespace = ''.join(workflow.title().split())
    gwet_graph.addToGraph(g, namespace, connections)


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


if __name__ == "__main__":
    sys.exit(main())
