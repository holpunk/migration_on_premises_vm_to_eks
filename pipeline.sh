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

echo "--- Step 2: Build & Deploy (Ansible) ---"
cd ansible
# Install requirements if needed (e.g. collections)
ansible-galaxy collection install community.docker kubernetes.core

ansible-playbook playbook.yml \
  --extra-vars "ecr_repository_url=$ECR_URL cluster_name=$CLUSTER_NAME"

echo "=== Pipeline Completed Successfully ==="
