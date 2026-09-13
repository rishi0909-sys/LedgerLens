#!/bin/bash
set -e
source venv/bin/activate
export PYTHONPATH=.
python backend/multimodal/evidence_tx_doc.py
python backend/multimodal/evidence_seq.py
python backend/multimodal/evidence_graph.py
python backend/multimodal/evidence_merge.py
python backend/multimodal/calibration.py
python backend/multimodal/fusion.py
python backend/multimodal/evaluation.py
