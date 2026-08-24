#!/usr/bin/env bash
set -euo pipefail

# Accept mode argument (default to 'minimal')
MODE="${1:-minimal}"

# Validate allowed modes
case "${MODE}" in
    minimal|minimal_2|minimal_w2|full)
        ;;
    *)
        echo "Error: Invalid mode '${MODE}'. Must be one of: minimal, minimal_2, minimal_w2, full."
        exit 1
        ;;
esac

CONFIG="configs/analysis_ml_superdataset_lr_catboost_v2.yaml"
FEAT_DIR="outputs/ml_superdataset/features_v2"
MODEL_DIR="outputs/ml_superdataset/model_v2/lD_auxiliary/${MODE}/catboost"

BASE_OUT="outputs/ml_superdataset/ml_observable_v2/lD_auxiliary/catboost"
TARGET_OUT="outputs/ml_superdataset/ml_observable_v2/lD_auxiliary/${MODE}/catboost"

echo "=== Running template generation in '${MODE}' mode ==="

for process in sm cpv; do
    if [[ "${process}" == "sm" ]]; then
        FEAT_FILE="${FEAT_DIR}/reco_sm/features_sm_reco_higgs_rest_chunk1_79.csv"
    else
        FEAT_FILE="${FEAT_DIR}/reco_cpv/features_reco_higgs_rest_chunk1_79.csv"
    fi

    for flavor in electron muon; do
        python3 scripts/build_ml_observable.py \
            --config "${CONFIG}" \
            --features "${FEAT_FILE}" \
            --model "${MODEL_DIR}/${flavor}/cpv_catboost.cbm" \
            --lepton-flavor "${flavor}" \
            --output-tag "reco_${process}" \
            --version v2

        mkdir -p "${TARGET_OUT}"
        mv "${BASE_OUT}"/*_${flavor}_reco_${process}* "${TARGET_OUT}/"
    done
done

echo "=== Running Fisher evaluation in '${MODE}' mode ==="

for flavor in electron muon; do
    python3 scripts/evaluate_fisher.py \
        --template "${TARGET_OUT}/template_test_${flavor}_reco_cpv_bins.csv" \
        --sm-template "${TARGET_OUT}/template_test_${flavor}_reco_sm_bins.csv" \
        --luminosity-scale 8000
done

echo "Done! All tasks completed for '${MODE}' mode."