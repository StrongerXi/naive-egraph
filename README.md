# Simple Computation Graph Optimization via EGraph

## Why
Motivating example from [egg documentation](https://docs.rs/egg/0.7.1/egg/tutorials/_01_background/index.html):

1. We'd like to perform rewrite `x * 2 / 2 ==> x`
2. A similar rewrite-rule might prevent (1) from happening: `x * 2 / 2 ==> (x << 1) / 2`
3. Essentially, we must search all rewrite paths simultaneously, which can be
   quite slow if implemented naively.


## What
E-Graph is a fast data structure for equivalence saturation.

I'm not a proof engineering expert, but I think this has a lot of potentials in
compiler optimizations. For instance, [Halide's simplification pass](https://github.com/halide/Halide/blob/main/src/Simplify_Sub.cpp#L35-L447)
essentially applies a series of rewrite rules in a __greedy__ manner, which
might cause it to miss certain optimization opportunities (e.g., see motivating
example).


## How
As far as I can see, ideally the implementation should
1. use union-find to speed up merging different equivalence classes (especially
   if they are large)
2. use cached structural hash to speed up matching subgraphs based on structure
3. know when to stop (avoid term explosion during rewrites)

This implementation kinda does (2) with a naive value-numbering.