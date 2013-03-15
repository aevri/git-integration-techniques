#!/usr/bin/env python
# encoding: utf-8

import phlsys_subprocess

run = phlsys_subprocess.run


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
