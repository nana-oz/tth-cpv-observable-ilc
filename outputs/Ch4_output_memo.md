## Confirmation of .csv file and .json file 

Running the code (from Ch 4.1.4):

#### Export the CPV-interference generator features
```
python3 scripts/export_features.py \
  --config configs/analysis_angular_lr.yaml \
  --level gen \
  --chunk 0
```

Produced:
```
outputs/angular_lr/features/features_gen_higgs_rest_chunk0.csv
outputs/angular_lr/features/features_gen_higgs_rest_chunk0.meta.json
```

Output Message:
```
generator truth-channel selection:
  events_channel_selected: 2073
  events_hbb: 7204
  events_read: 12500
  events_truth_selected: 2072
  higgs_mode::H->WW: 2713
  higgs_mode::H->bb: 7204
  higgs_mode::H->gg: 1039
  higgs_mode::H->other: 716
  higgs_mode::H->tautau: 828
  missing_truth_object::wjet_antiquark: 1
  rejected_incomplete_truth_objects: 1
  rejected_non_hbb: 5296
  rejected_non_semileptonic_emu: 5131
  ttbar_mode::dileptonic: 1333
  ttbar_mode::hadronic: 5676
  ttbar_mode::semileptonic_emu: 3638
  ttbar_mode::semileptonic_tau: 1853
wrote 2072 rows
```

Confirmed that `.csv` file contains (only first few rows are checked):
- `O_W` and `O_lD` columns with finite values (not all-NaN)
- `lepton_pdg` column with 11, -11, 13, or -13
- `lepton_flavor` column with `electron` or `muon`

Confirmed that `.json` file contains (reflects):
- truth_selection (`"higgs_decay": "H->bb"`, `"ttbar_decay": "semileptonic_emu"`)


#### Export the SM generator features
```
python3 scripts/export_features.py \
  --config configs/analysis_angular_lr.yaml \
  --level gen \
  --component sm \
  --chunk 0
```

Produced:
```
outputs/angular_lr/features/features_sm_gen_higgs_rest_chunk0.csv
outputs/angular_lr/features/features_sm_gen_higgs_rest_chunk0.meta.json
```

Output Message:
```
generator truth-channel selection:
  events_channel_selected: 1941
  events_hbb: 6653
  events_read: 11505
  events_truth_selected: 1938
  higgs_mode::H->WW: 2439
  higgs_mode::H->bb: 6653
  higgs_mode::H->gg: 992
  higgs_mode::H->other: 653
  higgs_mode::H->tautau: 768
  missing_truth_object::wjet_antiquark: 3
  rejected_incomplete_truth_objects: 3
  rejected_non_hbb: 4852
  rejected_non_semileptonic_emu: 4712
  ttbar_mode::dileptonic: 1254
  ttbar_mode::hadronic: 5207
  ttbar_mode::semileptonic_emu: 3375
  ttbar_mode::semileptonic_tau: 1669
wrote 1938 rows
```

Confirmed that `.csv` file contains (only first few rows are checked):
- `O_W` and `O_lD` columns with finite values (not all-NaN)
- `lepton_pdg` column with 11, -11, 13, or -13
- `lepton_flavor` column with `electron` or `muon`

Confirmed that `.json` file contains (reflects):
- truth_selection (`"higgs_decay": "H->bb"`, `"ttbar_decay": "semileptonic_emu"`)
