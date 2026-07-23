## Ch.3 Step 1 - Generator and Reconstructed Events Output

### Generator Output
sample     : tthcpv_gen_elpr (chunk 0) <br>

#### STDHEP and sidecar paths
stdhep     : /data/dust/user/zhangyuy/analysis/tth/events_physsim/production/cpv_tth/eL.pR/I01234_0/generator/stdhep/E550-Test.Ptthcpv.Gphyssim.eL.pR.I01234_0.0.stdhep <br>
sidecar    : /data/dust/user/zhangyuy/analysis/tth/events_physsim/production/cpv_tth/eL.pR/I01234_0/generator/sidecars/E550-Test.Ptthcpv.Gphyssim.eL.pR.I01234_0.0.tthcpv_me.csv <br>

#### sidecar/alignment counts
sidecar rows=12500 skipped=0 aligned=12500 <br>

#### positive and negative weight counts
weight check: ok=True n_pos=6298 n_neg=6202 signed_sum=0.00303872 fb <br>

#### one event's t , t¯ , Higgs, b / b¯, and hadronic W daughter identities
=== event 1 (stdhep #0) w_signed=+3.16534e-05 fb

  higgs         : pdg= +25 E=  162.66 GeV <br>
  top           : pdg=  +6 E=  176.37 GeV <br>
  antitop       : pdg=  -6 E=  183.44 GeV <br>
  top_b         : pdg=  +5 E=   53.06 GeV <br>
  antitop_bbar  : pdg=  -5 E=   66.61 GeV <br>
  wjet_quark    : pdg=  +1 E=   52.82 GeV <br>
  wjet_antiquark: pdg=  -2 E=   64.01 GeV <br>
  lepton        : MISSING <br>
  neutrino      : MISSING <br>
  frame lab        : O_W = -0.9702 rad <br>
  frame higgs_rest : O_W = -0.0235 rad <br>
  frame ttbar_rest : O_W = -1.3729 rad <br>


### Reco Output

#### Input SLICO File Path
`/data/dust/user/zhangyuy/analysis/tth/events_physsim/production/cpv_tth/eL.pR/I01234_0/complete_reco/complete_reco_kinfit_ready_E550-Test.Ptthcpv.Gphyssim.eL.pR.I01234_0.0_sgv.slcio' <br>


#### Inspect in particular OutputErrorFlowJets6, RefinedJets6, ISOElectrons, and ISOMuons
=== event #0 run=1 event=0 <br>

OutputErrorFlowJets6 n=6: <br>
  jet 0: E= 114.54 GeV  weaver[] <br>
  jet 1: E=  87.19 GeV  weaver[] <br>
  jet 2: E=  69.66 GeV  weaver[] <br>
  jet 3: E=  56.75 GeV  weaver[] <br>
  jet 4: E=  51.40 GeV  weaver[] <br>
  jet 5: E=  47.07 GeV  weaver[] <br>

RefinedJets6 n=6 <br>
  jet 0: E= 114.54 GeV  weaver[mc_d=0.210, mc_g=0.177, mc_ubar=0.175, mc_sbar=0.136] <br>
  jet 1: E=  87.19 GeV  weaver[mc_dbar=0.180, mc_u=0.180, mc_sbar=0.169, mc_d=0.133] <br>
  jet 2: E=  69.66 GeV  weaver[mc_b=0.734, mc_bbar=0.252, mc_cbar=0.006, mc_g=0.005] <br>
  jet 3: E=  56.75 GeV  weaver[mc_cbar=0.733, mc_g=0.097, mc_b=0.060, mc_bbar=0.029] <br>
  jet 4: E=  51.40 GeV  weaver[mc_bbar=0.499, mc_b=0.381, mc_c=0.094, mc_g=0.018] <br>
  jet 5: E=  47.07 GeV  weaver[mc_g=0.197, mc_s=0.160, mc_sbar=0.155, mc_u=0.145] <br>

ISOMuons: n=0

ISOElectrons: n=0


## Ch.3 Step 2 - Inspect the Underlying LCIO Records Directly

### Generator Event
1. incoming electron direction
2. the parent/daughter chain for t , t ¯ , H , and the two hadronic W daughters

### Reco Event
1. run/event number: 
2. collection names and sizes
3. the six-jet collections
4. isolated-lepton collection
5. any PID parameters visible for the jets

These notes establish intuition for what the later CSV columns actually mean; dumpevent itself is not a selection or physics-result tool.


