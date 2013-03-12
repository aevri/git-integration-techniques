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


def svnWorkflow():
    workflow_name = "svn-workflow"
    run("rm", "-rf", workflow_name)
    run("mkdir", workflow_name)
    with chDirContext(workflow_name):
        createCentralizedRepoAndWorkers()
        for w in WORKER_NAMES:
            with chDirContext(w):
                createNewFileAndCommitAppends(w, COMMIT_WORDS)
                run("git", "pull", "--rebase")
                run("git", "push", "origin", "master")


def pullWorkflow():
    workflow_name = "pull-workflow"
    run("rm", "-rf", workflow_name)
    run("mkdir", workflow_name)
    with chDirContext(workflow_name):
        createCentralizedRepoAndWorkers()
        for w in WORKER_NAMES:
            with chDirContext(w):
                createNewFileAndCommitAppends(w, COMMIT_WORDS)
                run("git", "pull")
                run("git", "push", "origin", "master")


def manypullWorkflow():
    workflow_name = "manypull-workflow"
    run("rm", "-rf", workflow_name)
    run("mkdir", workflow_name)
    with chDirContext(workflow_name):
        createCentralizedRepoAndWorkers()
        for word in COMMIT_WORDS.split():
            for worker in WORKER_NAMES:
                with chDirContext(worker):
                    createNewFileAndCommitAppends(worker, word)
                    run("git", "pull")
                    run("git", "push", "origin", "master")


svnWorkflow()
pullWorkflow()
manypullWorkflow()
