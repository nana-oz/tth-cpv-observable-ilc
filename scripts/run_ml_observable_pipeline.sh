#!/bin/bash
set -e   # stop immediately if any command fails, rather than continuing silently

# Default configuration
FRAME="${1:-higgs_rest}"       # Pass frame as argument (e.g., ./run_ml_observable_pipeline.sh lab), defaults to higgs_rest
CHUNK_TAG="${2:-chunk1_79}"    # Combined dataset chunk tag
FEATURE_SET="${4:-lD}"         # Feature set from config (e.g., lD)
MODEL_TYPE="${5:-xgboost}"     # xgboost or catboost
VERSION="${5:-v2}"             # v2 or original (v1)

# Configure version suffix logic
if [ "$VERSION" = "v2" ]; then
  VER_SUFFIX="_v2"
  CFG_VER="_v2"
else
  VER_SUFFIX=""
  CFG_VER=""
fi

# Determine directory suffix based on frame
if [ "$FRAME" = "higgs_rest" ]; then
  FEATURES_DIR="outputs/ml_superdataset/features${VER_SUFFIX}/${MODEL_TYPE}"
  CONFIG="configs/analysis_ml_superdataset_lr${CFG_VER}.yaml"
  MODEL_BASE_DIR="outputs/ml_superdataset/model${VER_SUFFIX}/${MODEL_TYPE}"
  OBS_BASE_DIR="outputs/ml_superdataset/ml_observable${VER_SUFFIX}/${MODEL_TYPE}"
else
  FEATURES_DIR="outputs/ml_superdataset_${FRAME}/${MODEL_TYPE}/features${VER_SUFFIX}"
  CONFIG="configs/analysis_ml_superdataset_lr${CFG_VER}_${FRAME}.yaml"
  MODEL_BASE_DIR="outputs/ml_superdataset_${FRAME}/model${VER_SUFFIX}/${MODEL_TYPE}"
  OBS_BASE_DIR="outputs/ml_superdataset_${FRAME}/ml_observable${VER_SUFFIX}/${MODEL_TYPE}"
fi

# Model extension handling
if [ "$MODEL_TYPE" = "xgboost" ]; then
  MODEL_EXT="json"
else
  MODEL_EXT="cbm"
fi

SPLIT="test"   # Final ML templates are evaluated on the independent test set

echo "=========================================================="
echo " Running Combined ML Pipeline"
echo " Version:     ${VERSION}"
echo " Frame:       ${FRAME}"
echo " Chunk Tag:   ${CHUNK_TAG}"
echo " Feature Set: ${FEATURE_SET}"
echo " Model Type:  ${MODEL_TYPE}"
echo " Config:      ${CONFIG}"
echo " Features:    ${FEATURES_DIR}"
echo "=========================================================="

# 1. Train CP Classifier on combined RECO CPV superdataset
echo "--> Step 1: Training $MODEL_TYPE model on combined RECO features..."
python3 scripts/train_cpv_model${VER_SUFFIX}.py \
  --config $CONFIG \
  --features $FEATURES_DIR/reco_cpv/features_reco_${FRAME}_${CHUNK_TAG}.csv \
  --feature-set $FEATURE_SET

# 2. Build ML Observables on combined test set
echo "--> Step 2: Building ML Observables..."

for level in gen reco; do
  for lepton in electron muon; do

    MODEL_PATH="${MODEL_BASE_DIR}/${FEATURE_SET}/${lepton}/cpv_${MODEL_TYPE}.${MODEL_EXT}"

    # Generate CPV and SM templates on the combined test set
    python3 scripts/build_ml_observable.py \
      --config $CONFIG \
      --features $FEATURES_DIR/${level}_cpv/features_${level}_${FRAME}_${CHUNK_TAG}.csv \
      --model $MODEL_PATH \
      --split $SPLIT \
      --lepton-flavor $lepton \
      --weight-column weight_template \
      --output-tag "${level}_${CHUNK_TAG}"

    python3 scripts/build_ml_observable.py \
      --config $CONFIG \
      --features $FEATURES_DIR/${level}_sm/features_sm_${level}_${FRAME}_${CHUNK_TAG}.csv \
      --model $MODEL_PATH \
      --split $SPLIT \
      --lepton-flavor $lepton \
      --weight-column weight_sm \
      --output-tag "sm_${level}_${CHUNK_TAG}"

  done
done

# 3. Calculate Fisher Information on combined templates
echo "--> Step 3: Calculating Fisher Information..."

for level in gen reco; do
  for lepton in electron muon; do

    TEMPLATE="${OBS_BASE_DIR}/template_${SPLIT}_${lepton}_${level}_${CHUNK_TAG}_bins.csv"
    SM_TEMPLATE="${OBS_BASE_DIR}/template_${SPLIT}_${lepton}_sm_${level}_${CHUNK_TAG}_bins.csv"

    echo "Evaluating Fisher Info: ML (${FEATURE_SET}) | ${level} | ${lepton} | ${CHUNK_TAG}"

    python3 scripts/evaluate_fisher.py \
      --template "$TEMPLATE" \
      --sm-template "$SM_TEMPLATE" \
      --luminosity-scale 8000

  done
done

echo "ML pipeline complete."