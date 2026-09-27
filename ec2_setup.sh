#!/bin/bash
# One-shot setup for a fresh Ubuntu 22.04 EC2 instance (r6i.2xlarge or bigger recommended:
# 64GB+ RAM removes the local-machine OOM crashes this project hit repeatedly on 16GB).
#
# Usage on the instance, after `scp`-ing this repo up:
#   bash ec2_setup.sh
set -euo pipefail

sudo apt update -y
sudo apt install -y python3-pip python3-venv unzip

cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r code/business_entity_resolution/requirements.txt

echo ""
echo "Setup done. Activate with:  source .venv/bin/activate"
echo "Run e.g.:"
echo "  cd code/business_entity_resolution"
echo "  export AMLC_ROOT=\"$(pwd)/../..\""
echo "  python -m src.baseline.run_baseline --split test --out ../../output"
echo "  python -m src.baseline.token_blocking --split train --sample-s1 200000 --sweep"
