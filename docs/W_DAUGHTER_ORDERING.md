# Reconstructed W-daughter ordering for the semileptonic analyser

## Status and scope

This note isolates the reconstructed hadronic-W daughter-ordering problem that
enters the semileptonic observable

```math
O_{\ell D}=\Delta\phi(\ell,D),
```

where `D` denotes the down-type daughter of the hadronically decaying W boson.
The purpose is to define the current reference method, organize several
possible improvements, and specify how they should be compared.

This is a reconstruction-method note, not a requirement that all methods be
implemented during the summer project. The immediate project baseline remains
valid with the current method. The alternatives are documented so that later
work can be compared using the same conventions and performance criteria.

The methods discussed here are:

1. **Method N — current naive baseline:** piecewise quark/antiquark
   orientation with one-sided conflict resolution;
2. **Method Q — joint quark/antiquark pair assignment:** the former Option B2;
3. **Method W — direct W-decay-role assignment:** the former Option B1;
4. **Method P — CMS-inspired permutation scoring:** an event-level learned
   assignment model, with several possible levels of complexity.

The final method must be selected from reconstruction-level CP sensitivity,
not from flavour-assignment accuracy alone.

---

## 1. Why the ordering problem matters

In a direct semileptonic decay,

```math
t\to bW^+,
\qquad
\bar t\to \bar bW^-,
```

with

```math
W^+\to U+\bar D,
\qquad
W^-\to D+\bar U,
```

where

```math
U\in\{u,c\},
\qquad
D\in\{d,s\}.
```

The charged lepton identifies the charge of the leptonic W and therefore the
charge of the hadronic W:

```math
Q_{W,\mathrm{had}}=-Q_\ell.
```

Hence the final analyser mapping is

```math
Q_\ell>0:
\qquad
W^-_{\mathrm{had}}\to D+\bar U,
\qquad
j_{\mathrm{ana}}=j_D,
```

and

```math
Q_\ell<0:
\qquad
W^+_{\mathrm{had}}\to U+\bar D,
\qquad
j_{\mathrm{ana}}=j_{\bar D}.
```

At generator level these roles are read from the decay tree. At reconstruction
level the two jets selected as the hadronic W daughters are initially an
unordered pair. The analysis must infer which reconstructed jet should be used
as the down-type analyser.

This decision affects the sign and shape of `O_lD`. An incorrect daughter
ordering does not merely reduce a conventional classification score; it can
move an event to a different angular bin and alter the signed CPV-interference
template. The relevant endpoint is therefore the Fisher information retained
by the reconstructed observable.

---

## 2. Separate W-pair selection from W-daughter ordering

Two reconstruction problems must be kept distinct.

### 2.1 W-pair selection

From the full reconstructed jet collection, identify the two jets assigned to
the hadronic W decay.

In the current project this decision is made by the production kinematic-fit
candidate selection. Reconstructed observables use the selected candidate with

```text
accepted == 1
fit_success == 1
```

and do not independently replace the selected W pair in the feature exporter.

### 2.2 W-daughter ordering

Given the selected unordered pair

```math
\{j_1,j_2\},
```

assign the physical daughter roles. Depending on the method, the role space is

```math
(q,\bar q),
```

or directly

```math
(D,\bar U)\quad\text{for }W^-,
```

and

```math
(U,\bar D)\quad\text{for }W^+.
```

Methods N, Q, and W keep the W pair fixed and address only the second problem.
A CMS-inspired model can be restricted to the same fixed-pair problem, or it
can be extended to rerank complete kinematic-fit candidates and thereby address
both pair selection and daughter ordering.

These scopes must not be mixed in a performance table. A method that changes
the selected W pair is solving a larger problem than a fixed-pair orientation
rule.

---

## 3. Common flavour-score notation

For one reconstructed jet `j`, define the aggregated Weaver light-flavour
scores

```math
P_q(j)
=
P_u(j)+P_d(j)+P_s(j)+P_c(j),
```

```math
P_{\bar q}(j)
=
P_{\bar u}(j)+P_{\bar d}(j)+P_{\bar s}(j)+P_{\bar c}(j).
```

The current signed discriminator is

```math
s_{q\bar q}(j)
=
P_q(j)-P_{\bar q}(j).
```

For direct W-role assignment, also define

```math
P_D(j)
=
P_d(j)+P_s(j),
```

```math
P_U(j)
=
P_u(j)+P_c(j),
```

```math
P_{\bar D}(j)
=
P_{\bar d}(j)+P_{\bar s}(j),
```

```math
P_{\bar U}(j)
=
P_{\bar u}(j)+P_{\bar c}(j).
```

These quantities are classifier outputs or sums of classifier outputs. Unless
calibration has been demonstrated in the relevant phase space, products of
these quantities should be described as **assignment scores** or
**pseudo-likelihoods**, not automatically as physical likelihoods.

The initial scope retains the project truth policy in which the analyser study
uses light W daughters `u,d,s,c` and their antiparticles. Physical W decays
containing a b daughter are outside this initial comparison unless the common
truth and reconstruction definitions are explicitly extended.

---

## 4. Method N — current naive baseline

### 4.1 Definition

The current implementation is

```text
src/ilc_tth_cpv/flavor.py::orient_w_pair
```

and first classifies each selected W jet as quark-like or antiquark-like:

```math
s_{q\bar q}(j)\geq 0
\quad\Longrightarrow\quad
j\text{ is q-like},
```

```math
s_{q\bar q}(j)<0
\quad\Longrightarrow\quad
j\text{ is qbar-like}.
```

It then applies a piecewise rule.

#### Opposite preferences

If the two jets have opposite signs of `s_qqbar`, the signs determine the
orientation directly:

```math
j_1\text{ q-like},\ j_2\text{ qbar-like}
\quad\Longrightarrow\quad
j_1=q,\ j_2=\bar q,
```

and conversely for the reversed signs.

The stored status is

```text
opposite_preferences
```

and the current margin is the smaller absolute signed score:

```math
m_N
=
\min\left(
|s_{q\bar q}(j_1)|,
|s_{q\bar q}(j_2)|
\right).
```

#### Both jets are q-like

If

```math
s_{q\bar q}(j_1)\geq0,
\qquad
s_{q\bar q}(j_2)\geq0,
```

compare only the two quark scores. The jet with larger `P_q` is assigned as the
quark and the other jet is forced to be the antiquark:

```math
P_q(j_1)>P_q(j_2)
\quad\Longrightarrow\quad
j_1=q,\ j_2=\bar q.
```

The stored status is

```text
both_q_like
```

and the margin is

```math
m_N
=
|P_q(j_1)-P_q(j_2)|.
```

#### Both jets are qbar-like

If

```math
s_{q\bar q}(j_1)<0,
\qquad
s_{q\bar q}(j_2)<0,
```

compare only the two antiquark scores. The jet with larger `P_qbar` is assigned
as the antiquark and the other jet is forced to be the quark:

```math
P_{\bar q}(j_1)>P_{\bar q}(j_2)
\quad\Longrightarrow\quad
j_1=\bar q,\ j_2=q.
```

The stored status is

```text
both_qbar_like
```

and the margin is

```math
m_N
=
|P_{\bar q}(j_1)-P_{\bar q}(j_2)|.
```

Exact decision-score ties retain the original W-slot ordering and are labelled

```text
tie_slot_order
```

rather than being silently treated as a confident physical decision.

### 4.2 Mapping to the down-type analyser

After the pair has been oriented as `q/qbar`, the isolated-lepton charge is
used in the standard way:

```text
positive lepton:
    W- is hadronic
    the oriented quark jet is D

negative lepton:
    W+ is hadronic
    the oriented antiquark jet is anti-D
```

Thus Method N performs no explicit up-type-versus-down-type classification. It
uses the W charge to convert a `q/qbar` orientation into the desired analyser.

### 4.3 Why this is called naive

The method is deterministic, easy to test, and suitable as a reference
baseline. Its weakness is localized in the same-sign cases.

For two q-like jets it compares only

```math
P_q(j_1)\quad\text{and}\quad P_q(j_2),
```

without asking whether the jet forced into the antiquark role has a plausible
`P_qbar`. For two qbar-like jets it makes the analogous one-sided comparison.
The method therefore resolves a pair-level conflict through a single-role
score.

A neutral description is

> sign classification with one-sided conflict resolution.

The word *naive* refers to this conflict-resolution rule, not to the entire
kinematic-fit reconstruction chain.

---

## 5. Method Q — joint quark/antiquark pair assignment

Method Q is the smallest direct replacement for the same-sign part of Method
N. It retains the aggregated light-quark scores but compares the two complete
physical assignments.

### 5.1 Assignment scores

For the selected pair, define

```math
A_{12}^{q\bar q}:
\qquad
j_1=q,
\quad
j_2=\bar q,
```

```math
A_{21}^{q\bar q}:
\qquad
j_2=q,
\quad
j_1=\bar q.
```

The two scores are

```math
L_{12}^{q\bar q}
=
P_q(j_1)P_{\bar q}(j_2),
```

```math
L_{21}^{q\bar q}
=
P_q(j_2)P_{\bar q}(j_1).
```

Choose `A_12` if

```math
L_{12}^{q\bar q}>L_{21}^{q\bar q},
```

and choose `A_21` otherwise, with explicit handling of numerical ties.

### 5.2 Log-odds form

The comparison can be written as

```math
\Delta_Q
=
\log\frac{L_{12}^{q\bar q}}{L_{21}^{q\bar q}}
=
\log\frac{P_q(j_1)}{P_{\bar q}(j_1)}
-
\log\frac{P_q(j_2)}{P_{\bar q}(j_2)}.
```

Method Q therefore orders the jets by their quark-versus-antiquark log odds.
For implementation, the probabilities should be protected by a documented
small positive floor before taking logarithms.

A natural assignment-separation measure is

```math
C_Q^{\mathrm{sep}}=|\Delta_Q|.
```

An additional absolute pair-compatibility measure is

```math
C_Q^{\mathrm{abs}}
=
L_{12}^{q\bar q}+L_{21}^{q\bar q}.
```

These quantities answer different questions:

- `C_sep` measures how strongly the two allowed orientations are separated;
- `C_abs` measures how compatible the selected pair is with either light
  `q/qbar` assignment.

A large ratio between two extremely small scores is not necessarily a
high-quality W-daughter assignment, so both concepts can be useful.

### 5.3 Exact relation to Method N

If the two jets have opposite `q/qbar` preferences, Method N and Method Q must
agree. For example,

```math
\frac{P_q(j_1)}{P_{\bar q}(j_1)}\geq1,
\qquad
\frac{P_q(j_2)}{P_{\bar q}(j_2)}<1
```

implies

```math
L_{12}^{q\bar q}>L_{21}^{q\bar q}.
```

Therefore Method Q can change the current decision only in

```text
both_q_like
both_qbar_like
tie_slot_order
```

events.

There is a second useful limiting result. If the tagger were a strictly
normalized binary classifier satisfying

```math
P_q(j)+P_{\bar q}(j)=1
```

for every jet, then

```math
L_{12}^{q\bar q}-L_{21}^{q\bar q}
=
P_q(j_1)-P_q(j_2).
```

In that idealized binary case, comparing the pair scores is equivalent to
comparing the two quark probabilities. Method Q becomes distinct because the
actual multiclass outputs can leave different amounts of probability in other
flavour categories for the two jets.

### 5.4 Illustrative same-sign example

Consider

```text
jet 1:
    P(q)    = 0.60
    P(qbar) = 0.40

jet 2:
    P(q)    = 0.55
    P(qbar) = 0.01
```

Both jets are individually q-like. Method N assigns jet 1 as `q` because it has
larger `P(q)`. The corresponding pair score is

```math
L_{12}^{q\bar q}
=
0.60\times0.01
=
0.006.
```

The reverse assignment has

```math
L_{21}^{q\bar q}
=
0.55\times0.40
=
0.22.
```

Method Q therefore assigns jet 2 as `q` and jet 1 as `qbar`. The point is not
that jet 2 is the more quark-like object in isolation; it is that the reverse
complete assignment is much more compatible with the requirement that one jet
must take each role.

### 5.5 What Method Q does not do

Method Q improves only the pairwise `q/qbar` orientation. It does not perform
explicit `U/D` identification. The down-type analyser is still obtained by
combining the oriented pair with the isolated-lepton charge.

This is why Method Q is the most direct first alternative to the existing
baseline: it changes one local decision while preserving the current W pair,
object definitions, and lepton-charge mapping.

---

## 6. Method W — direct W-decay-role assignment

Method W uses the known hadronic-W charge and compares the two allowed daughter
assignments directly.

### 6.1 Reconstructed W minus

For

```math
W^-\to D+\bar U,
```

define

```math
A_{12}^{W^-}:
\qquad
j_1=D,
\quad
j_2=\bar U,
```

```math
A_{21}^{W^-}:
\qquad
j_2=D,
\quad
j_1=\bar U.
```

The assignment scores are

```math
L_{12}^{W^-}
=
P_D(j_1)P_{\bar U}(j_2),
```

```math
L_{21}^{W^-}
=
P_D(j_2)P_{\bar U}(j_1).
```

If

```math
L_{12}^{W^-}>L_{21}^{W^-},
```

jet 1 is the down-type candidate. Otherwise jet 2 is the down-type candidate,
again with an explicit tie policy.

The log-score difference is

```math
\Delta_W^{W^-}
=
\log\frac{P_D(j_1)}{P_{\bar U}(j_1)}
-
\log\frac{P_D(j_2)}{P_{\bar U}(j_2)}.
```

### 6.2 Reconstructed W plus

For

```math
W^+\to U+\bar D,
```

define

```math
A_{12}^{W^+}:
\qquad
j_1=U,
\quad
j_2=\bar D,
```

```math
A_{21}^{W^+}:
\qquad
j_2=U,
\quad
j_1=\bar D.
```

The assignment scores are

```math
L_{12}^{W^+}
=
P_U(j_1)P_{\bar D}(j_2),
```

```math
L_{21}^{W^+}
=
P_U(j_2)P_{\bar D}(j_1).
```

The jet in the selected `anti-D` role is the down-type analyser candidate.
The corresponding log-score difference is

```math
\Delta_W^{W^+}
=
\log\frac{P_U(j_1)}{P_{\bar D}(j_1)}
-
\log\frac{P_U(j_2)}{P_{\bar D}(j_2)}.
```

### 6.3 Difference from Method Q

Method Q works in the role space

```math
(q,\bar q).
```

Method W works in the more specific role space

```math
(D,\bar U)
```

or

```math
(U,\bar D).
```

It therefore uses both particle-versus-antiparticle information and
up-type-versus-down-type information. It targets the actual W daughter roles
rather than constructing a `q/qbar` intermediate assignment.

The appropriate claim is that Method W

> enforces the allowed charge and up-type/down-type structure of the hadronic
> W decay.

It should not automatically be described as the complete W-decay likelihood.
A complete model would also specify channel priors and correlations.

### 6.4 Possible CKM-aware extension

A more explicit W-decay score could retain the allowed flavour channels:

```math
L_{ab}^{W^-}
=
\sum_{D\in\{d,s\}}
\sum_{U\in\{u,c\}}
\pi_{UD}
P_D(j_a)P_{\bar U}(j_b),
```

with

```math
\pi_{UD}\propto|V_{UD}|^2.
```

The analogous expression applies to `W+`. This extension requires a careful
interpretation of the tagger outputs and of the flavour priors used in its
training. It is not necessary for the first Method W test.

### 6.5 Main risk

Method W relies on the fine flavour components

```math
u,d,s,c,\bar u,\bar d,\bar s,\bar c.
```

Several of these categories can have weaker separation than the aggregated
`q/qbar` problem. More detailed scores help only when they contain usable and
sufficiently calibrated information. A factorized hard-assignment rule can
become less stable when it multiplies noisy or poorly calibrated fine-flavour
components.

Consequently, Method W is physically more targeted than Method Q but is not
assumed to be better before the reconstruction-level information comparison.

---

## 7. Method P — CMS-inspired permutation scoring

### 7.1 Reference strategy in the CMS lepton-plus-jets analysis

The CMS top-pair lepton-plus-jets reconstruction described in Sec. VI of
Ref. [1] uses a neural network to score complete jet-to-decay-role
permutations. The network input includes the charged-lepton four-momentum,
missing transverse momentum, and up to eight jets represented by their
four-momenta and b-tagging categories.

The four top-decay jets are presented in the role order

```text
b jet from the leptonic top
b jet from the hadronic top
down-type W daughter
up-type W daughter
```

and the remaining jets are appended in descending transverse momentum. During
training, all possible assignments of the four decay roles are supplied for
each event. For 4, 5, 6, 7, and 8 jets this gives respectively

```text
24, 120, 360, 840, 1680
```

permutations. A correct permutation receives target one and the others target
zero. At inference, the permutation with the highest network score is used.

This is qualitatively different from Methods N, Q, and W. Those methods combine
per-jet flavour scores after the W pair has already been selected. A
permutation model can learn a score

```math
S_\theta(X,\pi),
```

where `X` is the full event representation and `pi` is a complete assignment of
reconstructed objects to decay roles.

It can therefore use information such as

- W- and top-mass consistency;
- leptonic-versus-hadronic top assignment;
- b-tagging information;
- W-daughter angular and energy correlations;
- competition among several candidate jets;
- correlations that are absent from a factorized product of per-jet flavour
  scores.

### 7.2 Difference between ttbar and ttH

The CMS reference problem contains the four principal top-decay jet roles

```math
(b_\ell,b_h,j_D,j_U).
```

The present process also contains the Higgs decay

```math
H\to b\bar b,
```

so a full event assignment must account for at least

```math
(b_\ell,b_h,j_D,j_U,b_H,\bar b_H).
```

This adds combinatorics and new approximate exchange symmetries. In particular,
the two Higgs b jets need not be given an artificial ordered identity unless a
specific observable requires it.

A direct copy of the CMS architecture is therefore not the correct design
statement. The transferable idea is **permutation scoring**, which should be
adapted to the existing ttH kinematic-fit candidate structure.

### 7.3 Method P0 — fixed-pair swap classifier

The smallest CMS-inspired model keeps the selected W pair fixed and scores only
the two allowed internal orderings.

For each event the alternatives are

```math
\pi_{12}
=
(j_1\text{ in role 1},j_2\text{ in role 2}),
```

```math
\pi_{21}
=
(j_2\text{ in role 1},j_1\text{ in role 2}).
```

The roles may be `q/qbar` or directly `D/anti-U` and `U/anti-D`. Inputs can
include

- both W-jet four-momenta;
- all available Weaver flavour scores for both jets;
- isolated-lepton charge and four-momentum;
- reconstructed W and top masses;
- selected-candidate kinematic-fit quantities;
- b-jet and Higgs-candidate information already associated with the selected
  candidate.

This model solves the same fixed-pair problem as Methods Q and W and therefore
provides the cleanest learned comparison.

### 7.4 Method P1 — top-K kinematic-fit candidate reranker

A larger but still structured extension keeps the kinematic fit as a candidate
generator. Instead of using only the nominal best candidate, retain the top-K
candidates and learn a score for each candidate and each W-daughter ordering.

The model can then improve jointly

- which two jets form the W pair;
- which b jet belongs to each top side;
- which W jet is the down-type analyser.

This approach preserves the strong mass-constraint and fit information already
encoded in the reconstruction while allowing a learned event-level reranking.
It also makes the comparison with the current pipeline interpretable through
candidate rank and recovered-versus-destroyed event categories.

### 7.5 Method P2 — full ttH event-level permutation model

The most general version enumerates assignments of reconstructed jets to all
principal ttH decay roles and learns a complete event-level score.

This is a separate reconstruction project rather than a small variation of the
current orientation helper. It requires decisions about

- the maximum jet multiplicity;
- treatment of additional radiation;
- exchange symmetry of the Higgs b pair;
- nonreconstructable training events;
- class imbalance across very large permutation sets;
- whether the network score is calibrated across events with different numbers
  of candidates;
- how the model interacts with, replaces, or reuses the current kinematic fit.

Method P2 is documented as a long-term direction. It should not be required for
the first `O_lD` reconstruction result.

---

## 8. Unified assignment formulation

All methods can be written as a decision over an allowed assignment set
`A(X)`:

```math
\hat a
=
\operatorname*{arg\,max}_{a\in\mathcal A(X)} S(X,a).
```

The methods differ in the assignment space and score construction.

| Method | Pair fixed? | Assignment space | Score construction | Event context |
| --- | ---: | --- | --- | --- |
| N | yes | `q/qbar` swap | piecewise sign rule and one-sided score comparison | no |
| Q | yes | `q/qbar` swap | factorized joint `q/qbar` score | no |
| W | yes | `D/anti-U` or `U/anti-D` swap | factorized W-role score | W charge only |
| P0 | yes | two W-daughter orderings | learned permutation score | selected-event context |
| P1 | top-K | candidate and daughter ordering | learned candidate score | full candidate context |
| P2 | no | full ttH jet-role permutation | learned event-level score | full event |

This table also defines fair comparisons. Methods N, Q, W, and P0 can be
compared on exactly the same selected W pair. P1 and P2 must additionally be
evaluated for W-pair and full-permutation correctness.

---

## 9. Statistical interpretation of the flavour scores

### 9.1 Calibration

A multiclass classifier output is useful for ranking without necessarily being
a calibrated posterior probability. Before interpreting a product such as

```math
P_D(j_1)P_{\bar U}(j_2)
```

as a likelihood, calibration should be checked in the relevant reconstructed
sample and kinematic region.

Useful diagnostics include

- reliability curves for aggregated `q/qbar` probabilities;
- reliability curves for `D`, `U`, `anti-D`, and `anti-U` sums;
- calibration as a function of jet energy and polar angle;
- comparison between electron and muon event categories;
- dependence on whether the selected W pair is truth-correct.

For the initial comparison, the scores can be used as deterministic assignment
scores even without a full calibration programme, provided the terminology is
kept precise.

### 9.2 Training priors

Classifier outputs generally approximate a training-distribution posterior

```math
P_{\mathrm{train}}(f\mid x),
```

which includes the class priors used during training. If flavour categories
were balanced or reweighted, these outputs are not automatically physical
W-decay posteriors.

A formal prior correction would start from

```math
p(x\mid f)
\propto
\frac{P_{\mathrm{train}}(f\mid x)}{\pi_f^{\mathrm{train}}},
```

followed by the desired physical priors. This is a possible later refinement,
not a prerequisite for the first Method Q test.

### 9.3 Correlation and factorization

Methods Q and W assume a factorized score of the form

```math
S(j_1,j_2;a)
\approx
S_1(j_1;a_1)S_2(j_2;a_2).
```

The two reconstructed jets are not physically independent: their kinematics,
flavour composition, and selection are correlated by the common W decay and by
the kinematic fit. A permutation model is one way to learn these correlations
explicitly.

The factorized methods remain valuable because they are transparent, cheap,
and easy to diagnose. Their role is not to claim an exact generative model but
to test whether the physical pair constraint already improves the final
observable.

---

## 10. Validation and comparison protocol

### 10.1 Freeze the common event population

For a valid method comparison, use the same

- polarization sample;
- direct electron/muon semileptonic truth policy;
- `H -> bb` policy;
- reconstructed acceptance and fit-success requirements;
- selected kinematic-fit candidate, for fixed-pair methods;
- frame and angular convention;
- electron and muon category definitions;
- SM and signed CPV-interference normalizations;
- angular binning and luminosity scale.

Changing the event population at the same time as the ordering rule prevents a
clean interpretation.

### 10.2 Two complementary evaluation populations

#### Fixed-pair diagnostic population

Use truth matching to select events for which the current reconstructed W pair
contains the two correct W daughters. On this diagnostic subset, compare only
the daughter-ordering performance.

Relevant quantities are

```math
A_{q/\bar q\mid\mathrm{correct\ pair}},
```

and

```math
A_{D\mid\mathrm{correct\ pair}}.
```

This sample isolates the orientation problem but is not the headline physics
population.

#### End-to-end accepted reconstruction population

Use the complete accepted reconstruction baseline, including events with an
incorrect selected W pair. This population contains the actual combination of

- W-pair mistakes;
- daughter-ordering mistakes;
- angular resolution and migration;
- invalid or low-compatibility flavour assignments;
- lepton reconstruction effects.

The reconstruction-level Fisher information must be evaluated on this full
population.

Truth labels are diagnostics only and must never be passed as analysis inputs.

### 10.3 Minimum assignment metrics

For each method, report at least

```text
fraction of accepted events for which the decision changes relative to Method N
truth-labelled q/qbar orientation accuracy
truth-labelled down-type-candidate accuracy
accuracy conditional on a truth-correct W pair
accuracy in opposite-preference events
accuracy in both-q-like events
accuracy in both-qbar-like events
invalid or tie fraction
```

For Methods Q and W, also inspect the score-separation and absolute-compatibility
distributions. For a permutation model, inspect the best-versus-second-best
score gap and candidate-rank distributions.

### 10.4 Required CP-information metric

For lepton category

```math
c\in\{e,\mu\},
```

calculate

```math
I_c
=
\sum_i
\frac{\nu_{1,ci}^2}{\nu_{0,ci}},
```

where `nu0` is the SM yield and `nu1` is the signed CPV-interference yield in
angular bin `i`.

The independent categories combine as

```math
I_{e+\mu}=I_e+I_\mu.
```

Do not merge electron and muon bin yields before evaluating the headline
Fisher information.

For each alternative method `m`, report

```math
\Delta I_m
=
I_m-I_N,
```

and

```math
R_m
=
\frac{I_m}{I_N},
```

where `I_N` is the current naive-baseline result on the same event population.

A method with higher assignment accuracy can have lower Fisher information if
it removes informative events, changes migrations unfavourably, or improves
mostly in phase-space regions with little CP sensitivity.

### 10.5 Category studies instead of immediate hard cuts

Low-confidence assignments should not automatically be discarded. A useful
comparison is

1. one inclusive category;
2. separate high- and low-confidence categories combined at likelihood level;
3. one hard confidence cut.

If the categories are statistically independent, their Fisher information
adds. A hard cut is justified only when it improves the final combined
sensitivity, not merely the retained-sample purity.

---

## 11. Oracle ceilings and loss decomposition

Before investing in a complex assignment model, estimate how much information
is available to recover.

### 11.1 Orientation oracle

Keep the reconstructed four-momenta and the currently selected W pair, but use
truth only to choose the correct internal daughter ordering. Denote the result

```math
I_{\mathrm{oracle\ orientation}}.
```

Then

```math
\Delta I_{\mathrm{orientation}}
=
I_{\mathrm{oracle\ orientation}}-I_N
```

is the maximum information that any fixed-pair ordering improvement could
recover on that reconstruction population.

### 11.2 Pair-plus-orientation oracle

Use truth to select the correct reconstructed W-daughter jets when a suitable
matched pair exists, and orient them correctly. Denote this result

```math
I_{\mathrm{oracle\ pair+orientation}}.
```

The additional gap

```math
\Delta I_{\mathrm{pairing}}
=
I_{\mathrm{oracle\ pair+orientation}}
-I_{\mathrm{oracle\ orientation}}
```

estimates the information loss attributable to W-pair selection beyond the
internal ordering problem.

### 11.3 Decision gate

A practical sequence is

1. measure the frequency of same-sign Method N cases;
2. measure how often Method Q changes the decision;
3. calculate the fixed-pair orientation-oracle gap;
4. implement Method Q if the gap and changed-event population are non-negligible;
5. test Method W if fine-flavour diagnostics indicate usable additional
   separation;
6. consider Method P0 or P1 only if a substantial information gap remains.

This prevents a large ML reconstruction project from being started when the
available fixed-pair information ceiling is already small.

---

## 12. Recommended diagnostic output fields

The feature table should make each decision reproducible. A future common
interface can include

```text
w_ordering_method
w_assignment_forward_score
w_assignment_reverse_score
w_assignment_log_ratio
w_assignment_separation
w_assignment_absolute_compatibility
w_assignment_status
idx_W_quark
idx_W_antiquark
idx_W_down_candidate
down_candidate_source
w_orientation_changed_from_naive
```

Truth-labelled diagnostic exports may additionally contain

```text
truth_W_pair_correct
truth_qqbar_orientation_correct
truth_down_candidate_correct
```

provided these fields are never used in the physics observable construction or
as model inputs.

For permutation methods, useful additional fields are

```text
permutation_score_best
permutation_score_second
permutation_score_gap
candidate_rank_selected
number_of_candidates_scored
```

Any added columns must be documented in `docs/DATA_SCHEMA.md` when an
implementation is introduced.

---

## 13. Minimal convention and unit tests

Each fixed-pair method should satisfy the following tests.

1. Exchanging input labels `W1` and `W2` recovers the same physical analyser
   jet, although the raw slot index changes.
2. Positive lepton charge selects the `D` role of a hadronic `W-`.
3. Negative lepton charge selects the `anti-D` role of a hadronic `W+`.
4. Missing, zero, or non-finite lepton charge produces an invalid analyser
   rather than a default ordering.
5. Exact assignment-score ties are explicitly labelled and have a documented
   deterministic policy.
6. Zero or extremely small flavour scores do not produce non-finite log ratios.
7. Method Q agrees with Method N for opposite-preference events.
8. The final `O_lD` is invariant under a pure relabelling of the two selected W
   input slots after the physical assignment is recomputed.

Performance tests based on truth accuracy and Fisher information are separate
from these convention tests.

---

## 14. Recommended implementation priority

The methods have different scientific scope and implementation cost.

### First comparison: Method N versus Method Q

This is the most motivated immediate test because it

- changes only the current same-sign conflict resolution;
- uses already exported aggregated light-flavour information;
- keeps the W pair and all later observable definitions fixed;
- directly addresses a concrete inconsistency in the naive rule;
- provides a clean baseline for any later method.

### Second comparison: Method W

Method W is the next transparent physics-driven test. It should be attempted
when the fine-flavour scores and truth-labelled diagnostics are available and
show useful `U/D` information.

### Longer-term comparison: Method P0 or P1

A fixed-pair learned permutation scorer is the fairest first ML extension. A
top-K candidate reranker is the natural next step if the pair-selection oracle
gap is important. A full ttH event permutation model should be treated as a
separate reconstruction study.

The preferred method is whichever yields the highest validated
reconstruction-level Fisher information under the frozen comparison
conditions. Simplicity is a secondary advantage when the Fisher results are
statistically equivalent.

---

## 15. Future extensions

### 15.1 Soft assignment

Methods N, Q, W, and the CMS reference strategy ultimately make a hard maximum
score choice. For Methods Q and W one can define normalized assignment weights

```math
w_{12}
=
\frac{L_{12}}{L_{12}+L_{21}},
\qquad
w_{21}=1-w_{12}.
```

A future likelihood can marginalize over the two assignments rather than
choosing only one. Directly averaging the two angular values is not generally
optimal because `Delta phi` is periodic and because the assignment posterior
and CP likelihood need not combine linearly.

More defensible uses of the soft information include

- confidence categories;
- a two-dimensional observable consisting of the angle and assignment score;
- posterior-weighted template construction with a documented probabilistic
  model;
- a learned CP observable that receives both candidate assignments and their
  scores.

### 15.2 Calibration-aware assignment

Calibrate the aggregated or role-specific flavour scores before forming pair
products, or train a small calibrator directly on the two-jet assignment task.
Calibration should be validated separately from ranking performance.

### 15.3 Joint pair selection and ordering

If the pair-selection oracle gap dominates, the relevant next problem is not a
more elaborate fixed-pair orientation. It is joint scoring of the W-pair choice
and daughter ordering, preferably over a controlled top-K candidate set before
attempting a full combinatorial model.

### 15.4 Alternative optimization targets

A classifier trained only for assignment accuracy is not guaranteed to
maximize CP sensitivity. Later studies may compare

- permutation cross-entropy;
- down-type assignment accuracy;
- differentiable approximations to binned Fisher information;
- end-to-end likelihood objectives.

Any such study must retain a transparent comparison with Methods N, Q, and W.

---

## 16. Summary

The reconstructed W-daughter problem forms a clear hierarchy.

```text
Method N:
    current piecewise q/qbar heuristic

Method Q:
    compare the two complete q/qbar assignments

Method W:
    compare the two charge-specific W-decay-role assignments

Method P:
    learn a joint event-level permutation score
```

Method N is the reference baseline. Method Q is the smallest constrained
replacement and can differ only in the same-sign or tie categories. Method W
uses more detailed physical role information but depends on finer flavour
separation. Method P is qualitatively broader because it can use full event
kinematics and, in its larger variants, modify the selected W pair itself.

Classification metrics are required to understand each method, but the final
criterion is

```math
I_{\mathrm{reco}}(O_{\ell D}),
```

calculated separately for electron and muon categories and combined through

```math
I_{e+\mu}=I_e+I_\mu.
```

Oracle studies should first determine whether the dominant recoverable loss
comes from W-pair selection or from ordering within the selected pair.

---

## References

[1] A. Hayrapetyan et al. (CMS Collaboration), “Measurements of polarization
and spin correlation and observation of entanglement in top quark pairs using
lepton + jets events from proton-proton collisions at sqrt(s) = 13 TeV,”
*Physical Review D* **110**, 112016 (2024), Sec. VI.
[doi:10.1103/PhysRevD.110.112016](https://doi.org/10.1103/PhysRevD.110.112016)

[2] Current project implementation:
[`src/ilc_tth_cpv/flavor.py`](../src/ilc_tth_cpv/flavor.py)

[3] Current project workflow and Chapter 4 context:
[`docs/PROJECT_NOTE_FULL.md`](PROJECT_NOTE_FULL.md)

[4] Current kinematic-fit and jet-assignment stage:
[`docs/KINFIT_JET_ASSIGNMENT.md`](KINFIT_JET_ASSIGNMENT.md)
