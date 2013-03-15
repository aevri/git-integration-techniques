import phlsys_fs
import phlsys_subprocess

run = phlsys_subprocess.run
chDirContext = phlsys_fs.chDirContext


def execute(workers, workflow):

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
