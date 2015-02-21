Git Integration Techniques
==========================

As we become proficient at managing our changes with Git, we are presented with
many different options for integrating them. We choose between better work or
less work, preserving history or fixing it, simple histories or rich ones. Each
of these choices we have made become apparent in the commit graphs we leave
behind.

These choices can be very divisive within teams, with strong feelings on each
side. Here I will offer some diagrams and commentary to help explore the
territory. I hope these will prove useful tools for thinking and arguing about
these choices.

Painting the house
------------------

<<house painting diagram>>

Here we have a git commit graph, with each commit represented as a picture of a
house. Note that the arrows point back at the parent commits, as this is git.
You will notice that there are two histories depicted, both are painting the
original house a new color. In the top history there are a number of
intermediate 'fixup' commits. The bottom history paints the house in one
commit.

If we re-imagined the task of painting the house as a coding task, it would be
comparable to renaming a popular function. A naive search and replace might
just replace too much, so at least manual checking would probably be in order.
There could be many call-sites to visit, so you might want to make checkpoints
along the way.

Which of the histories is 'better'? Let us amass the facts and then compare the
arguments!

Fact: 

Green-to-green.

Bisect.

Cherry-pick.

Revert.

- Fixup

- Squash

- Separate changes

Remodelling the house
---------------------

<<house remodelling diagram>>

Topic merge
-----------

<<topic merge diagram>>

- Introduce 4 workers
- Are these fixup commits?
- Are these commits dependent?
- These commits are not dependent

Topic catchup merge
-------------------

- Merge to reconcile conflicts early, is rebasing an option?
- Merge from fear of falling behind, this is what fear looks like

Master merge-o-geddon
---------------------

- Work on 'master'
- SVN-like, pull+push
- What SVN with merging might look like

Master-rebase
-------------

- Work on 'master'
- SVN-like, pull+push
- What SVN ported to Git looks like
- Minimal merge conflicts

Topic-rebase-noff
-----------------

- Preserve branchy-ness
- Lose independence
- No catchup merges

Topic-rebase-ffonly
-------------------

- Lose branchy-ness
- Lose independence
- No catchup merges

Topic-squash
------------

- Lose branchy-ness
- Lose independence
- No catchup merges
- Lose history

Summary
-------

- All together

? Technique: Branch from topic, rewrite history, merge back to defunct topic
<< table of trade-offs? >>
