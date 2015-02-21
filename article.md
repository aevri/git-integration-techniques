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

Here we have a git commit graph, with each commit represented as an impressive
drawing of a house. Note that the arrows point back at the parent commits, as
this is git. You will notice that there are two histories depicted, both are
painting the original house a new color. In the top history there are a number
of intermediate 'fixup' commits. The bottom history paints the house in one
commit.

If we re-imagine the task of painting the house as a coding task, it is
comparable to renaming a function. A naive search and replace might make
mistakes, so at least manual checking would probably be in order.  There could
be many call sites to visit, so you might want to save your work along the way.

Which of the histories is 'better'? Let us first state some facts, and then
make some contentious arguments!

- Fact 1: Each of the commits along the top take us closer to the goal than the
  previous commit, this means that each commit represented the best current
  effort at some point in time.

- Fact 2: If you make WIP commits and push them somewhere else as you progress,
  your work will be more robust to mice running across your keyboard and the
  cats that dash after them.

- Fact 3: No-one wants to live in a half-painted or over-painted house. Please
  think of these work-in-progress (WIP) commits as untestable and breaking the
  build.

- Fact 4: If you wanted to cherry-pick or revert the whole painting effort in
  the top path, you would have to do so with all of the commits. On the bottom
  path there is only one, self-contained commit to deal with.

- Fact 5: When bisecting over history later, you would need to give the WIP
  commits special treatment because they are untestable. The bottom history
  needs no special treatment.

- Fact 6: You can convert from the top history to an equivalent of the bottom
  history with just a bit of extra work. This work becomes easy with
  practice.

- Fact 7: Non-fast-forward pushes to refs that others share with you will
  complicate the work of those others. Perhaps not quite as much as it used to.

So now we have established some facts, what can we do?

From (1, 2) we can see that the top history is actually pretty appealing
whilst we are working towards a goal. Working that way frees us from thinking
too hard about leaving tidy commits behind as we try things out to move closer
to the goal.

From (3, 4, 5) we see that the joy of the top history at authoring
time turns a little sour. After the goal of painting the house is achieved,
we may wish we had got it done in one commit.

From (6, 7) we see that we can have the best of both worlds. To avoid the
pitfall of (7) we can work on a personal 'topic branch' until we are ready to
clean up our history and push it somewhere we share with others.

TODO: Green-to-green?

Remodelling the house
---------------------

<<house remodelling diagram>>

This example looks similar to the first but I assure you it is totally
different, let us see how.

- Fact 1: Each of the commits in the top history is a valid house. These
  represent useful, separate changes. All of them are buildable and testable.

- Fact 2: Each of the commits in the top history is independent, the commits
  could be re-ordered without merge conflicts.

Cherry-pick, revert, bisect, review.

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
