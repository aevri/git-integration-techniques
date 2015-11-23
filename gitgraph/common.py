"""A dumping ground for all source prior to re-organisation."""

import contextlib
import os
import subprocess

# networkx must be installed before use
#   $ sudo apt-get install python3-networkx
#
import networkx


def write_graphml(graph, filename):

    # write the graph in the 'graphml' format, this is useful because the
    # 'yEd' editor will allow us to load the graph and manipulate it into a
    # form that we are happy with
    graphml = '\n'.join(networkx.generate_graphml(graph))
    with open(filename, "w") as f:
        f.write(graphml)


class Colours(object):

    # colours from clrs.cc
    navy = "#001f3f"
    blue = "#0074D9"
    aqua = "#7FDBFF"
    teal = "#39CCCC"
    olive = "#3D9970"
    green = "#2ECC40"
    lime = "#01FF70"
    yellow = "#FFDC00"
    orange = "#FF851B"
    red = "#FF4136"
    maroon = "#85144b"
    fuchsia = "#F012BE"
    purple = "#B10DC9"
    black = "#111111"
    gray = "#AAAAAA"
    silver = "#DDDDDD"


def make_graph(commits):
    graph = networkx.DiGraph()

    next_parent0 = None

    for subject, name, parents, _decorations, merge_base in commits:

        is_no_ff = False
        if len(parents) > 1:
            for p in parents:
                if merge_base.startswith(p):
                    is_no_ff = True
                    break

        label = ""
        color = Colours.red
        if len(parents) > 1:
            if is_no_ff:
                color = Colours.black
            else:
                color = Colours.maroon
        elif len(parents) == 0:
            color = Colours.orange

        if next_parent0 is None or name == next_parent0:
            is_parent0_lineage = True
        else:
            is_parent0_lineage = False

        graph.add_node(name, label=label, color=color)

        for i, p in enumerate(parents):
            if is_parent0_lineage and not i:
                edge_color = Colours.orange
            else:
                edge_color = Colours.black
            p_name = p
            graph.add_edge(name, p_name, color=edge_color)

        if is_parent0_lineage and parents:
            next_parent0 = parents[0]

    return graph


def yield_commits(repo, range_=None):
    git_args = ["git", "log", "--format=%f:%h:%p:%d"]
    if range_:
        git_args.append(range_)
    else:
        git_args.append("--all")

    for line in repo.yield_stdout(*git_args):
        commit_info = line.split(':')
        subject = commit_info[0]
        name = commit_info[1]
        parents = commit_info[2].split()
        decorations = commit_info[3].strip().strip('()').split()
        if len(parents) > 1:
            merge_base = git_merge_base(repo, *parents)
        elif len(parents) == 1:
            merge_base = parents[0]
        else:
            merge_base = None
        yield subject, name, parents, decorations, merge_base


class GitRepo():

    """A callable wrapper for a git repository."""

    def __init__(self, working_copy_path):
        """Init a new GitRepo, locked to the specified 'working_copy_path'.

        :working_copy_path: string path to the working path repository

        """
        self._working_copy_path = working_copy_path

    def yield_stdout(self, *args):
        """Yield the lines of output from invoking git with '*args'.

        Note that you should iterate through all the lines of output or the
        process may not finish.

        :*args: a list of arguments to supply to git
        :returns: list of strings representing the lines from git

        """
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            cwd=self._working_copy_path)

        with process:
            for line in process.stdout:
                yield line

    def __call__(self, *args):
        """Return the lines of output from invoking git with '*args'.

        :*args: a list of arguments to supply to git
        :returns: list of strings representing the lines from git

        """
        command = ('git',) + args
        return ''.join(list(self.yield_stdout(*command)))


def git_merge_base(repo, *commits):
    return repo('merge-base', *commits)


# TODO: write a docstring with doctests when we have a tempdir helper
@contextlib.contextmanager
def chDirContext(newDir):
    savedPath = os.getcwd()
    os.chdir(newDir)
    try:
        yield
    finally:
        os.chdir(savedPath)
