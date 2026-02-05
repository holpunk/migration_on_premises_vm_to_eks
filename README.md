# Migration Simulation: On-Premises to Amazon EKS

This project simulates the migration of a legacy on-premises application (VM-based) to a containerized environment on Amazon EKS (Elastic Kubernetes Service). It provides a "Click-to-Migrate" pipeline that provisions infrastructure, containerizes the application, and deploys it using industry-standard tools.

## 🚀 Overview

The pipeline automates the entire migration journey:
1.  **Infrastructure Provisioning**: Sets up a VPC, EKS Cluster, and ECR Registry using **Terraform**.
2.  **Containerization**: Builds a Docker image for the Python Flask application.
3.  **Deployment**: Pushes the image to ECR and deploys it to EKS using **Ansible**.
4.  **Verification**: Exposes the application via a LoadBalancer and verifies accessibility.

## 📝 Assumptions

-   **Deployment Location**: The EKS cluster is intended to be deployed within a **Workload OU** (Organizational Unit).
-   **Compliance**: The infrastructure is assumed to be created and managed in accordance with organizational compliance standards.

## 🛠 Tech Stack

-   **Terraform**: Infrastructure as Code (IaC) for AWS resources (VPC, EKS, ECR).
-   **Ansible**: Configuration management and orchestration for the build & deploy process.
-   **Docker**: Container runtime for packaging the application.
-   **Kubernetes (EKS)**: Container orchestration platform.
-   **Python (Flask)**: The sample "legacy" web application.
-   **DORA Metrics**: Integrated tracking for deployment frequency and success rates.

## 📋 Prerequisites

Ensure you have the following tools installed and configured:

-   [AWS CLI](https://aws.amazon.com/cli/) (configured with `aws configure`)
-   [Terraform](https://www.terraform.io/) (v1.0+)
-   [Ansible](https://www.ansible.com/) (v2.9+)
-   [Docker](https://www.docker.com/) (Running daemon)
-   [kubectl](https://kubernetes.io/docs/tasks/tools/)
-   `python3` and `pip`

## 🚦 Usage

The entire process is driven by the `pipeline.sh` script.

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd migration_on_premises_vm_to_eks
    ```

2.  **Run the Migration Pipeline**:
    ```bash
    chmod +x pipeline.sh
    ./pipeline.sh
    ```

### What Happens When You Run It?
1.  **Terraform** initializes and applies the configuration, creating:
    -   A VPC (`migration-vpc`)
    -   An EKS Cluster (v1.27)
    -   An ECR Repository
2.  **Ansible** takes over to:
    -   Log in to ECR.
    -   Build the Flask app Docker image.
    -   Push the image to the new ECR repo.
    -   Template Kubernetes manifests with the dynamic ECR URL.
    -   Apply the Deployment and Service to EKS.
    -   Wait for the LoadBalancer URL.
3.  **Output**: The script will print the final public URL where your application is running.

## 🔒 Security & Encryption

-   **Data in Transit**: All communication between your local machine and AWS (API calls, Docker push) is encrypted via **HTTPS/TLS**.
-   **Data at Rest**:
    -   **ECR Images**: Encrypted using default AWS-managed keys (SSE-S3).
    -   **EKS Secrets**: Stored in `etcd`, encrypted by the underlying AWS EBS encryption for the control plane.
-   **Network**: The VPC uses private subnets for workloads and public subnets for LoadBalancers. No VPN is required as all API access uses secure public endpoints.

## 📂 Project Structure

```
.
├── ansible/               # Ansible playbooks & templates
│   ├── playbook.yml       # Main deployment logic
│   └── templates/         # Kubernetes YAML templates (Jinj2)
├── app/                   # Source code for the Flask application
├── dora/                  # Scripts for tracking DORA metrics
├── terraform/             # Terraform IaC configurations
│   ├── main.tf            # AWS resources (VPC, EKS, ECR)
│   ├── outputs.tf         # Outputs passed to Ansible
│   └── variables.tf       # Customizable variables
└── pipeline.sh            # Master script to run the full simulation
```
