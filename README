Git Workflow Experiments
========================

This is a small project to explore the git histories that emerge when you use
particular Git Workflows.

To install dependencies:
    $ sudo apt-get install python-networkx

To run grapher:
    $ ./commitgraph /path/to/repo

It will write the file
    commits.graphml

This contains all the commits from the repository, in 'graphml' format.

yEd is a free graph editor which understands 'graphml' and will let you load
the file in order to edit it:
    http://www.yworks.com/en/products_yed_about.html

Unfortunately 'yEd' won't render it very well to start with, you need to setup
a mapping for the node properties, instructions are here:
    http://thirld.com/blog/2012/01/31/making-yed-import-labels-from-graphml-files/

You should map the 'label' and 'color' properties.

----------------------------------------

To run the workflow experiments:
    $ python experiment.py

The program will print out the relevant content for a Confluence page.

It will also create a GraphML file:
    all.graphml
