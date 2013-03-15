#!/usr/bin/env python
# encoding: utf-8

import sys

import networkx as nx
import phlsys_fs
import phlsys_subprocess


run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext


def main():
    alice = Worker("Alice", "wonderland", ["sleep", "awake"])
    bob = Worker("Bob", "zoo", ["build zoo", "fix zoo", "rebuild zoo"])
    charley = Worker("Charley", "sez", ["one", "two", "three", "four", "five"])
    dorian = Worker("Dorian", "painting", ["nose", "eyes", "hair", "grin"])

    workers = [alice, bob, charley, dorian]
    workflows = [
        RebaseMasterWorkflow(),
        RebaseTopicFfOnlyWorkflow(),
        RebaseTopicNoFfWorkflow(),
        SquashTopicWorkflow(),
        MergeTopicWorkflow(),
        MergeTopicCatchupWorkflow(),
        SvnWorkflow(),
        SvnPullWorkflow()
    ]

    g = nx.DiGraph()

    for workflow in workflows:
        doWorkflow(g, workflow, workers)

    graphml = '\n'.join(nx.generate_graphml(g))
    with open("all.graphml", "w") as f:
        f.write(graphml)


def doWorkflow(g, workflow, workers):
    git_log_graph_params = ["--all", "--graph", "--oneline"]
    git_log_parents_message_params = ["--format=%f %h %p"]
    git_log_params_list = [
        git_log_graph_params, git_log_parents_message_params]
    graphs = simulate(workers, workflow, git_log_params_list)
    #graph = graphs[0]
    connections = graphs[1]
    #printTeamContent(workflow, graph)
    namespace = ''.join(workflow.title().split())
    addToGraph(g, namespace, connections)


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


def printTeamContent(workflow, graph):
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


class Worker():

    def __init__(self, name, project, items):
        self.name = name
        self.project = project
        self.items = items

    def work(self, workflow):
        yield
        workflow.start_project(self.name, self.project)
        for item in self.items:
            workflow.do_item(self.name, self.project, item)
            yield
        workflow.finish_project(self.name, self.project)


class WorkflowBase(object):

    def title(self):
        raise Exception("should override this")

    def description(self):
        raise Exception("should override this")

    def workflow(self):
        raise Exception("should override this")

    def start_project(self, name, project):
        pass

    def update(self, name, project):
        pass

    def do_item(self, name, project, item):
        raise Exception("should override this")

    def finish_project(self, name, project):
        raise Exception("should override this")


class RebaseMasterWorkflow(WorkflowBase):

    def title(self):
        return "Rebase on Master"

    def description(self):
        return "Commit on master, rebase often, push when done"

    def workflow(self):
        return """
            .. commit some work ..
            $ git pull --rebase
            .. commit some work ..
            $ git pull --rebase
            $ git push origin master
            """

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")


class RebaseTopicFfOnlyWorkflow(WorkflowBase):

    def title(self):
        return "Topic branches, rebase, ff-only merge"

    def description(self):
        return "Work on a topic branch, rebase often; ff-only merge to master"

    def workflow(self):
        return """
            $ git checkout -b mywork
            .. commit some work ..
            $ git fetch
            $ git rebase origin/master
            .. commit some work ..
            $ git fetch
            $ git rebase origin/master

            $ git checkout master
            $ git merge origin/master --ff-only
            $ git merge mywork --ff-only
            $ git branch -d mywork
            $ git push origin master
            """

    def start_project(self, name, project):
        run("git", "checkout", "-b", project)

    def update(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")
        run("git", "checkout", "-B", "master", "origin/master")
        run("git", "merge", project, "--ff-only")
        run("git", "branch", "-d", project)
        run("git", "push", "origin", "master")


class SquashTopicWorkflow(WorkflowBase):

    def title(self):
        return "Topic branches, squash"

    def description(self):
        return "Work on a topic branch, squash work back to master when done"

    def workflow(self):
        return """
            $ git checkout -b mywork
            .. commit some work ..
            .. commit some work ..

            $ git fetch
            $ git checkout master
            $ git merge origin/master --ff-only
            $ git merge mywork --squash
            $ git commit
            $ git branch -D mywork
            $ git push origin master
            """

    def start_project(self, name, project):
        run("git", "checkout", "-b", project)

    def update(self, name, project):
        pass

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "fetch")
        run("git", "checkout", "-B", "master", "origin/master")
        run("git", "merge", project, "--squash")
        run("git", "commit", "-m", project + " (" + name + ")")
        run("git", "branch", "-D", project)
        run("git", "push", "origin", "master")


class RebaseTopicNoFfWorkflow(WorkflowBase):

    def title(self):
        return "Topic branches, rebase, no-ff merge"

    def description(self):
        return "Work on a topic branch, rebase often; no-ff merge to master"

    def workflow(self):
        return """
            $ git checkout -b mywork
            .. commit some work ..
            $ git fetch
            $ git rebase origin/master
            .. commit some work ..
            $ git fetch
            $ git rebase origin/master

            $ git checkout master
            $ git merge origin/master --ff-only
            $ git merge mywork --no-ff
            $ git branch -d mywork
            $ git push origin master
            """

    def start_project(self, name, project):
        run("git", "checkout", "-b", project)

    def update(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")
        run("git", "checkout", "-B", "master", "origin/master")
        run("git", "merge", project, "--no-ff")
        run("git", "branch", "-d", project)
        run("git", "push", "origin", "master")


class MergeTopicWorkflow(WorkflowBase):

    def title(self):
        return "Topic branches, merge"

    def description(self):
        return "Work on a topic branch, merge back to master"

    def workflow(self):
        return """
            $ git checkout -b mywork
            .. commit some work ..
            .. commit some work ..

            $ git fetch
            $ git checkout master
            $ git merge origin/master
            $ git merge mywork
            $ git branch -d mywork
            $ git push origin master
            """

    def start_project(self, name, project):
        run("git", "checkout", "-b", project)

    def update(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "fetch")
        run("git", "checkout", "-B", "master", "origin/master")
        run("git", "merge", project)
        run("git", "branch", "-d", project)
        run("git", "push", "origin", "master")


class MergeTopicCatchupWorkflow(WorkflowBase):

    def title(self):
        return "Topic branches, merge catchup"

    def description(self):
        return "Work on a topic branch, merge catch-up, merge back to master"

    def workflow(self):
        return """
            $ git checkout -b mywork
            .. commit some work ..
            $ git fetch
            $ git merge origin/master
            .. commit some work ..
            $ git fetch
            $ git merge origin/master

            $ git checkout master
            $ git merge origin/master
            $ git merge mywork
            $ git branch -d mywork
            $ git push origin master
            """

    def start_project(self, name, project):
        run("git", "checkout", "-b", project)

    def update(self, name, project):
        run("git", "fetch")
        run("git", "rebase", "origin/master")

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)
        run("git", "fetch")
        run("git", "merge", "origin/master")

    def finish_project(self, name, project):
        run("git", "fetch")
        run("git", "checkout", "-B", "master", "origin/master")
        run("git", "merge", project)
        run("git", "branch", "-d", project)
        run("git", "push", "origin", "master")


class SvnWorkflow(WorkflowBase):

    def title(self):
        return "The SVN workflow"

    def description(self):
        return "Work on master, rebase and push every individual commit"

    def workflow(self):
        return """
            .. commit some work ..
            $ git pull --rebase
            $ git push origin master
            .. commit some work ..
            $ git pull --rebase
            $ git push origin master
            """

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")

    def finish_project(self, name, project):
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")


class SvnPullWorkflow(WorkflowBase):

    def title(self):
        return "The SVN workflow, merge-o-geddon"

    def description(self):
        return "Work on master, pull and push every individual commit"

    def workflow(self):
        return """
            .. commit some work ..
            $ git pull
            $ git push origin master
            .. commit some work ..
            $ git pull
            $ git push origin master
            """

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)
        run("git", "pull")
        run("git", "push", "origin", "master")

    def finish_project(self, name, project):
        run("git", "pull")
        run("git", "push", "origin", "master")


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


def commitAppendToFile(filename, text, message):
    with open(filename, "a") as f:
        f.write(text + "\n")
    run("git", "add", filename)
    run("git", "commit", filename, "-m", message)


def commitAppendToProjectFile(name, project, item):
    commitAppendToFile(
        project,
        item,
        project + ": " + item + " (" + name + ")")


def unindent(s):
    s = s.strip()
    lines = s.splitlines()
    lines = [l.strip() for l in lines]
    s = '\n'.join(lines)
    return s


if __name__ == "__main__":
    sys.exit(main())
