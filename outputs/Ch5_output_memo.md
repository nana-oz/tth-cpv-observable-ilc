## 1. Data Preparation (Ch. 5.1)

### 1.1 Check/Edit `export_features.py`
In `export_features.py` fixed:
-  Reconstructed top/anti-top slot. Modified `export_reco()` function to correctly assign top/anti-top daughters based on the lepton charge.
-  Deleted `O_b`, `O_top`, `O_lnu`, `y45`, `y56`, `y67`, and other information for kinfit that are not useful, such as `top_n`, `n_constraint`, `n_unmeasured`. (Just commented them out.)

In `export_features.py` and its output (`.csv` file), checked that they exist:
- Event Infomration: `event_id`, `chunk_id` (named `chunk` in `.csv`), `split`, `weight` (`weight_interference_signed`, `weight_interference_abs`, `weight_training`), `label`
- Lepton information: `lepton_E/theta/phi/mass`
- W_daughter information: `wjet_quark_E/theta/phi/mass`, `wjet_antiquark_E/theta/phi/mass`, `w_orientation_margin`
- Neutrino information: `nu_fit_px//py/pz/E`
- bbar from top: `top_b_E/theta/phi/mass`, `antitop_bbar_E/theta/phi/mass`
- Invariant mass: `mW_had_prefit`, `mW_had_postfit`, `mt_had_prefit`, `mt_had_postfit`, `mt_lep_prefit`, `mt_lep_postfit`, `mH_prefit`, `mH_postfit`
- Flavor tagging/assginment/KinFit score: `fitchi2`, `final_selection_score`, `final_fit_score`, `final_flavor_score`
- Helpful for debugging: `idx_W1`, `idx_W2`, `idx_W_quark`, `idx_W_antiquark`

Added:
- Lepton information: `lepton_px/py/pz/pt`
- Neutrino information: `nu_fit_pt/theta/phi`
- Invariant mass: `m_ttbar`
- - W_daughter information: `L12`, `L21` (down_assignment_probablity)

Missing (still need to add):

### 1.2 Prepare ML Analysis Configs
Create `analysis_ml_superdataset_lr.yaml`:
- Sample is set to `manifest: configs/samples.yaml`, `gen_sample: tthcpv_gen_elpr`, `reco_sample: tthcpv_reco_elpr`, `sm_gen_sample: tth_sm_gen_elpr`, and `sm_reco_sample: tth_sm_reco_elpr`
- Frame is set to `default_frame: higgs_rest`
- Split is set to `train: 0.6`, `validation: 0.2`, `test: 0.2`, and `seed: 20260720`
- Weights is set to `training_weight: weight_training`, `template_weight: weight_interference_signed`, and `sm_template_weight: weight_sm`
- Outputs is set to `base_dir: outputs/ml_superdataset`

Test Run <br>
Input (Write arguments.txt for the feature-export HTCondor workflow and then submit condor):
```
python3 make_arguments.py \
  --config ../../configs/analysis_ml_superdataset_lr.yaml \
  --chunks 0

condor_submit submit_export_features.sub
```

Output: 
```
condor/export_feature/arguments.txt

outputs/ml_superdataset/features/features_reco_higgs_rest_chunk0.csv
outputs/ml_superdataset/features/features_reco_higgs_rest_chunk0.meta.json
```


### 1.3  Run the whole condor workflow to get all ML dataset for the tth-cpv and tth-sm eLpR
Input 1 (cpv, chunk0-79, gen-level, higgs_rest frame):
```
python3 make_arguments.py \
  --config ../../configs/analysis_ml_superdataset_lr.yaml \
  --chunks 1-79 \
  --component interference \
  --level gen
  
condor_submit submit_export_features.sub
```
**STATUS: Run Complete**

Input 2 (sm, chunk0-79, gen-level, higgs_rest frame):
```
python3 make_arguments.py \
  --config ../../configs/analysis_ml_superdataset_lr.yaml \
  --chunks 1-79 \
  --component sm \
  --level gen
  
condor_submit submit_export_features.sub
```
**STATUS: Error**

Input 3 (cpv, chunk0-79, reco-level, higgs_rest frame):
```
python3 make_arguments.py \
  --config ../../configs/analysis_ml_superdataset_lr.yaml \
  --chunks 1-79 \
  --component interference \
  --level reco
  
condor_submit submit_export_features.sub
```
**STATUS: Run Complete**

Input 4 (sm, chunk0-79, reco-level, higgs_rest frame):
```
python3 make_arguments.py \
  --config ../../configs/analysis_ml_superdataset_lr.yaml \
  --chunks 1-79 \
  --component sm \
  --level reco
  
condor_submit submit_export_features.sub
```
**STATUS: Run Complete**

### 1.4  Write a new script `/scripts/merge_feature_chunks.py`

Condition for the new code:
- Merge the 80 chunk-level CSV files produced by `export_features.py` into a single superdataset, without recomputing selections, splits, weights, or features [x]
- check that all chunks are present, the schemas are identical, and there are no duplicated events [x]
- keep `lepton_flavor` so electron and muon channels can be selected later at training time [x]
- report the total event count and the electron/muon train/validation/test and ± label counts [x]
- write the merged dataset plus simple metadata under `outputs/ml_superdataset/features/` [x]

To Run (example: sm, gen)
```
python3 ../../scripts/merge_feature_chunks.py \
  --model sm \
  --level gen \
  --chunks 1-79 
```

Output file example:
```
outputs/ml_superdataset/features/reco_cpv/features_reco_higgs_rest_chunk1_79.csv
outputs/ml_superdataset/features/reco_cpv/features_reco_higgs_rest_chunk1_79.meta.json
```

Status:
- gen, cpv **Not Run Yet**
- gen, sm **Features not produced**
- reco, cpv **Run Complete**
- reco, sm **Run Complete**

## 2. BDT Baseline Comparison (Ch. 5.2)
### 2.1 Modify Files Used for ML
Modify `analysis_ml_superdataset_lr.yaml` --> Complete

Modify the `/scripts/train_cpv_model.py` --> Complete
```
    # TODO: down_type_daughter is a virtual object.
    #
    # For features such as:
    #     down_type_daughter_E
    #     down_type_daughter_theta
    #     down_type_daughter_phi
    #     down_type_daughter_mass
    #
    # use:
    #     idx_W_down_candidate
    #     idx_W_quark
    #     idx_W_antiquark
    #
    # to decide whether the selected down-type jet corresponds to
    # wjet_quark or wjet_antiquark, then read the requested variable
    # from that object.
    #
    # Example logic:
    #
    # if feature_name.startswith("down_type_daughter_"):
    #     variable = feature_name.removeprefix("down_type_daughter_")
    #     ...
    #     return to_float(row[f"{selected_prefix}_{variable}"])


    # TODO: virtual auxiliary feature.
    #
    # w_assignment_likelihood_selected does not exist directly in the CSV.
    # Resolve it from L12 preference or L21 preference by the w_orientation_status
    # If it is L12 preference then return to L12
    # if feature_name == "w_assignment_likelihood_selected":
    #     ...
    #     return selected_L


    # TODO: electron / muon must be trained separately.
    # Do the next uncommented code under this for loop with two lepton flavors
    # for lepton_flavor in training_cfg["lepton_flavors"]:
    #     flavor_rows = [...] Judge if the lepton is muon or electron.
    #
    # Each category must produce an independent model and metadata file.


    # TODO: after electron/muon category splitting is implemented,
    # add the lepton flavor to the output path, for example:
    #
    #     model/lD/electron/
    #     model/lD/muon/
    # Also the meta data path also need to change later

```

### 2.2 Look if the loss function converges, check the precision 
Sample Input:
```
python3 scripts/train_cpv_model.py \
        --config configs/analysis_ml_superdataset_lr.yaml \
        --features outputs/ml_superdataset/features/reco_cpv/features_reco_higgs_rest_chunk0.csv \
        --feature-set lD
```

Check logloss:
- electron ==> NOT CONVERGED! 
[0]     validation_0-logloss:0.69313 <br>
[100]   validation_0-logloss:0.79783 <br>
[200]   validation_0-logloss:0.89286 <br>
[300]   validation_0-logloss:0.99513 <br>
[400]   validation_0-logloss:1.05155 <br>
[499]   validation_0-logloss:1.12075

- muon ==> NOT CONVERGED!
[0]     validation_0-logloss:0.69839 <br>
[100]   validation_0-logloss:0.73968 <br>
[200]   validation_0-logloss:0.81167 <br>
[300]   validation_0-logloss:0.87425 <br>
[400]   validation_0-logloss:0.92209 <br>
[499]   validation_0-logloss:0.96869




