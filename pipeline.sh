#!/bin/bash
set -e

# Configuration
export AWS_REGION="eu-central-1"

echo "=== Starting Migration Simulation Pipeline ==="

echo "--- Step 1: Infrastructure Provisioning (Terraform) ---"
cd terraform
terraform init
terraform apply -auto-approve
ECR_URL=$(terraform output -raw ecr_repository_url)
CLUSTER_NAME=$(terraform output -raw cluster_name)
cd ..

echo "Infrastructure Ready."
echo "ECR URL: $ECR_URL"
echo "Cluster Name: $CLUSTER_NAME"


# Generate a simulated commit hash for this run
COMMIT_HASH=$(date +%s | md5sum | head -c 8 || echo "sim-$(date +%s)")
echo "Simulated Commit Hash: $COMMIT_HASH"

echo "--- Step 2: Build & Deploy (Ansible) ---"
cd ansible
# Install requirements if needed (e.g. collections)
ansible-galaxy collection install community.docker kubernetes.core

ansible-playbook playbook.yml \
  --extra-vars "ecr_repository_url=$ECR_URL cluster_name=$CLUSTER_NAME commit_hash=$COMMIT_HASH"

echo "--- DORA Metrics Report ---"
python3 ../dora/track.py report

echo "=== Pipeline Completed Successfully ==="
