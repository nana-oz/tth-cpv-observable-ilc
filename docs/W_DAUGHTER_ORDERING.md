# Reconstructed W-daughter ordering

For the two jets selected as the hadronic-W daughters, the remaining problem is to decide which jet should be used as the down-type analyser in

```math
O_{\ell D}=\Delta\phi(\ell,D).
```

The isolated-lepton charge determines the hadronic-W charge:

```math
Q_\ell>0:\quad W^-_{\mathrm{had}}\to D+\bar U,
```

```math
Q_\ell<0:\quad W^+_{\mathrm{had}}\to U+\bar D,
```

with

```math
D\in\{d,s\},\qquad U\in\{u,c\}.
```

The four possible strategies are summarized below.

## 1. Current naive q/qbar orientation

Define

```math
P_q(j)=P_u(j)+P_d(j)+P_s(j)+P_c(j),
```

```math
P_{\bar q}(j)=P_{\bar u}(j)+P_{\bar d}(j)+P_{\bar s}(j)+P_{\bar c}(j).
```

Each jet is first classified as q-like or qbar-like using

```math
P_q(j)-P_{\bar q}(j).
```

If the two jets have opposite preferences, the orientation is direct. If both are q-like, the jet with larger `P_q` is assigned as q. If both are qbar-like, the jet with larger `P_qbar` is assigned as qbar. The lepton charge then selects q as `D` for a hadronic `W-`, or qbar as `anti-D` for a hadronic `W+`.

The weakness is the same-sign case. For two q-like jets, the rule compares only the two `P_q` values and ignores whether the other jet is at all plausible as qbar. The analogous problem occurs for two qbar-like jets. It is therefore a useful baseline, but its conflict resolution is only one-sided.

## 2. Joint q/qbar assignment likelihood

Instead of classifying the jets separately, compare the two complete assignments:

```math
L_{12}^{q\bar q}=P_q(j_1)P_{\bar q}(j_2),
```

```math
L_{21}^{q\bar q}=P_q(j_2)P_{\bar q}(j_1).
```

Choose `j1 = q, j2 = qbar` when

```math
L_{12}^{q\bar q}>L_{21}^{q\bar q},
```

and choose the reverse assignment otherwise.

This method keeps the robust flavour sums used by the current baseline, but imposes the physical requirement that the pair contains one quark and one antiquark. It differs from the naive rule only in the both-q-like, both-qbar-like, or tie cases.

Among the simple fixed-pair methods, this is currently the most motivated choice. It is a small modification, uses the better-measured aggregated q/qbar information, and directly fixes the main weakness of the naive rule.

## 3. Direct W-decay-role likelihood

A more specific method uses the expected W-daughter roles directly. Define

```math
P_D=P_d+P_s,\qquad P_U=P_u+P_c,
```

```math
P_{\bar D}=P_{\bar d}+P_{\bar s},\qquad
P_{\bar U}=P_{\bar u}+P_{\bar c}.
```

For a hadronic `W-`, compare

```math
L_{12}^{W^-}=P_D(j_1)P_{\bar U}(j_2),
```

```math
L_{21}^{W^-}=P_D(j_2)P_{\bar U}(j_1).
```

For a hadronic `W+`, compare

```math
L_{12}^{W^+}=P_U(j_1)P_{\bar D}(j_2),
```

```math
L_{21}^{W^+}=P_U(j_2)P_{\bar D}(j_1).
```

The assignment with the larger score determines the down-type candidate.

This is more directly connected to the physical W decay than the q/qbar method. However, it depends on the finer separation of `u,d,s,c` and their antiparticles, which may be less reliable than the aggregated q/qbar information.

The sums and the likelihood are not competing ideas. The flavour sums define the probabilities for the physical roles, while the product of the two jet probabilities defines the pair-assignment likelihood.

## 4. CMS-inspired permutation model

A more general approach is to score complete jet-to-decay-role permutations with a neural network. In the CMS lepton+jets analysis, the network assigns jets to the leptonic-top b jet, hadronic-top b jet, down-type W daughter, and up-type W daughter. All allowed permutations are evaluated and the one with the largest network score is selected.

The same idea could be adapted here in two ways:

- keep the selected W pair fixed and train a classifier only for the two possible daughter orderings;
- score several complete ttH reconstruction candidates, allowing both the W-pair choice and the daughter ordering to change.

This can use kinematics and flavour information jointly, and is therefore more flexible than the factorized likelihoods above. It is also substantially more complex and less transparent.

Reference: CMS Collaboration, *Phys. Rev. D* **110**, 112016 (2024), Sec. VI, DOI: 10.1103/PhysRevD.110.112016.

## Summary

The four methods form a simple progression:

1. naive piecewise q/qbar orientation;
2. joint q/qbar assignment likelihood;
3. direct `D/U` W-decay-role likelihood;
4. learned event-level permutation scoring.

The joint q/qbar likelihood is the best-motivated current simple method. The direct W-role likelihood is potentially more physical if the fine-flavour scores are sufficiently reliable. The CMS-inspired model is the most general option, but it is a separate ML reconstruction problem.

The final comparison should still be made with the reconstructed `O_lD` Fisher information rather than assignment accuracy alone.
