#!/bin/bash
set -e
source venv/bin/activate
export PYTHONPATH=.
export KMP_DUPLICATE_LIB_OK=True
export OMP_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false
python backend/multimodal/evidence.py
python backend/multimodal/calibration.py
python backend/multimodal/fusion.py
python backend/multimodal/evaluation.py
