#!/usr/bin/env python
# encoding: utf-8

import sys

# networkx must be installed before use
#   $ sudo apt-get install python-networkx
import networkx as nx

import gwet_workflow
import gwet_simulate


def main():
    alice = Worker("Alice", "wonderland", ["sleep", "awake"])
    bob = Worker("Bob", "zoo", ["build zoo", "fix zoo", "rebuild zoo"])
    charley = Worker("Charley", "sez", ["one", "two", "three", "four", "five"])
    dorian = Worker("Dorian", "painting", ["nose", "eyes", "hair", "grin"])

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

    g = nx.DiGraph()

    for workflow in workflows:
        gwet_simulate.doWorkflow(g, workflow, workers)

    graphml = '\n'.join(nx.generate_graphml(g))
    with open("all.graphml", "w") as f:
        f.write(graphml)


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


if __name__ == "__main__":
    sys.exit(main())
