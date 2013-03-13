#!/usr/bin/env python
# encoding: utf-8

import phlsys_fs
import phlsys_subprocess


run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext

CENTRAL_REPO_NAME = "origin"
WORKER_NAMES = ["alice", "bob", "charlie", "dorian"]
COMMIT_WORDS = "one two three"


def createCentralizedRepoAndWorkers():
    run("mkdir", CENTRAL_REPO_NAME)
    with chDirContext(CENTRAL_REPO_NAME):
        run("git", "init", "--bare")
    for w in WORKER_NAMES:
        run("git", "clone", CENTRAL_REPO_NAME, w)
    worker = WORKER_NAMES[0]
    with chDirContext(worker):
        run("touch", "README")
        run("git", "add", "README")
        run("git", "commit", "README", "-m", "initial commit")
        run("git", "push", "origin", "master")
    for w in WORKER_NAMES:
        with chDirContext(w):
            run("git", "pull")


def createNewFileAndCommitAppends(filename, words):
    run("touch", filename)
    for word in words.split():
        run("git", "add", filename)
        with open(filename, "a") as f:
            f.write(word + "\n")
        run("git", "commit", filename, "-m", filename + ": " + word)


class SvnStrategy():

    def update(self):
        pass

    def land(self):
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "master")


class SvnPullStrategy():

    def update(self):
        pass

    def land(self):
        run("git", "pull")
        run("git", "push", "origin", "master")


def doWork(integration_strategy):
    tempdir_name = "_workflow_tempdir"
    run("rm", "-rf", tempdir_name)
    run("mkdir", tempdir_name)
    with chDirContext(tempdir_name):
        createCentralizedRepoAndWorkers()
        for word in COMMIT_WORDS.split():
            for worker in WORKER_NAMES:
                with chDirContext(worker):
                    integration_strategy.update()
                    createNewFileAndCommitAppends(worker, word)
                    integration_strategy.land()
        with chDirContext(CENTRAL_REPO_NAME):
            graph = run("git", "log", "--all", "--graph", "--oneline").stdout
            print graph


doWork(SvnStrategy())
doWork(SvnPullStrategy())
