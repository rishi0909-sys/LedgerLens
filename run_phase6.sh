#!/bin/bash
set -e
source venv/bin/activate
export PYTHONPATH=.
python backend/multimodal/evidence.py
python backend/multimodal/calibration.py
python backend/multimodal/fusion.py
python backend/multimodal/evaluation.py
