#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-minimal}"
FRAME="${2:-higgs_rest}"

case "${MODE}" in
    minimal|minimal_2|minimal_w2|minimal_nufit|full|wbjets)
        ;;
    *)
        echo "Error: Invalid mode '${MODE}'. Must be one of: minimal, minimal_2, minimal_w2, minimal_nufit, full, wbjets."
        exit 1
        ;;
esac

if [[ "${FRAME}" == "higgs_rest" ]]; then
    FRAME_SUFFIX=""
else
    FRAME_SUFFIX="_${FRAME}"
fi

CONFIG="configs/analysis_ml_superdataset_lr_catboost_v2${FRAME_SUFFIX}.yaml"
FEAT_DIR="outputs/ml_superdataset/features_v2"
MODEL_BASE="outputs/ml_superdataset/model_v2${FRAME_SUFFIX}"
OBS_BASE="outputs/ml_superdataset/ml_observable_v2${FRAME_SUFFIX}"

if [[ "${MODE}" == "wbjets" ]]; then
    MODEL_DIR="${MODEL_BASE}/lD_auxiliary_wbjets/catboost"
    TARGET_OUT="${OBS_BASE}/lD_auxiliary_wbjets/catboost"
else
    MODEL_DIR="${MODEL_BASE}/lD_auxiliary/${MODE}/catboost"
    TARGET_OUT="${OBS_BASE}/lD_auxiliary/${MODE}/catboost"
fi

echo "=== Running template generation in '${MODE}' mode (${FRAME} frame) ==="

for process in sm cpv; do
    if [[ "${process}" == "sm" ]]; then
        FEAT_FILE="${FEAT_DIR}/reco_sm/features_sm_reco_${FRAME}_chunk1_79.csv"
    else
        FEAT_FILE="${FEAT_DIR}/reco_cpv/features_reco_${FRAME}_chunk1_79.csv"
    fi

    for flavor in electron muon; do
        python3 scripts/build_ml_observable.py \
            --config "${CONFIG}" \
            --features "${FEAT_FILE}" \
            --model "${MODEL_DIR}/${flavor}/cpv_catboost.cbm" \
            --lepton-flavor "${flavor}" \
            --output-tag "reco_${process}" \
            --out-dir "${TARGET_OUT}" \
            --version v2
    done
done

echo "=== Running Fisher evaluation in '${MODE}' mode (${FRAME} frame) ==="

for flavor in electron muon; do
    python3 scripts/evaluate_fisher.py \
        --template "${TARGET_OUT}/template_test_${flavor}_reco_cpv_bins.csv" \
        --sm-template "${TARGET_OUT}/template_test_${flavor}_reco_sm_bins.csv" \
        --luminosity-scale 8000
done

echo "Done! All tasks completed for '${MODE}' mode (${FRAME} frame)."