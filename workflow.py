#!/usr/bin/env python
# encoding: utf-8

import phlsys_fs
import phlsys_subprocess


run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext

CENTRAL_REPO_NAME = "origin"


def createCentralizedRepoAndWorkers(worker_names):
    run("mkdir", CENTRAL_REPO_NAME)
    with chDirContext(CENTRAL_REPO_NAME):
        run("git", "init", "--bare")
    for w in worker_names:
        run("git", "clone", CENTRAL_REPO_NAME, w)
    worker = worker_names[0]
    with chDirContext(worker):
        run("touch", "README")
        run("git", "add", "README")
        run("git", "commit", "README", "-m", "initial commit")
        run("git", "push", "origin", "master")
    for w in worker_names:
        with chDirContext(w):
            run("git", "pull")


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


class WorkflowBase(object):

    def start_project(self, name, project):
        pass

    def update(self, name, project):
        pass

    def do_item(self, name, project, item):
        raise Exception("should override this")

    def finish_project(self, name, project):
        raise Exception("should override this")


class RebaseMasterWorkflow(WorkflowBase):

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)

    def finish_project(self, name, project):
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")


class SvnWorkflow(WorkflowBase):

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")

    def finish_project(self, name, project):
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")


class SvnPullWorkflow(WorkflowBase):

    def do_item(self, name, project, item):
        commitAppendToProjectFile(name, project, item)
        run("git", "pull")
        run("git", "push", "origin", "master")

    def finish_project(self, name, project):
        run("git", "pull")
        run("git", "push", "origin", "master")


class RebaseTopicFfOnlyWorkflow(WorkflowBase):

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


class RebaseTopicNoFfWorkflow(WorkflowBase):

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


def scheduleWork(workflow, workers):
    tempdir_name = "_workflow_tempdir"
    run("rm", "-rf", tempdir_name)
    run("mkdir", tempdir_name)
    with chDirContext(tempdir_name):
        createCentralizedRepoAndWorkers([w.name for w in workers])

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

        with chDirContext(CENTRAL_REPO_NAME):
            graph = run("git", "log", "--all", "--graph", "--oneline").stdout
            print graph

alice = Worker("Alice", "wonderland", ["sleep", "awake"])
bob = Worker("Bob", "zoo", ["build zoo", "fix zoo", "rebuild zoo", "party"])
charley = Worker("Charley", "says", ["one", "two", "three", "four", "five"])
dorian = Worker("Dorian", "painting", ["nose", "eyes", "hair", "vacuous grin"])

workers = [alice, bob, charley, dorian]

scheduleWork(RebaseMasterWorkflow(), workers)
scheduleWork(SvnWorkflow(), workers)
scheduleWork(SvnPullWorkflow(), workers)
scheduleWork(RebaseTopicFfOnlyWorkflow(), workers)
scheduleWork(RebaseTopicNoFfWorkflow(), workers)
scheduleWork(MergeTopicWorkflow(), workers)
scheduleWork(MergeTopicCatchupWorkflow(), workers)
