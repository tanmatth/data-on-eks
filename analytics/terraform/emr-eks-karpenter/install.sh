#!/bin/bash

read -p "Enter the region: " region
export AWS_DEFAULT_REGION=$region

echo "Initializing ..."
terraform init || echo "\"terraform init\" failed"

# List of Terraform modules to apply in sequence
targets=(
  "module.vpc"
  "module.vpc_endpoints_sg"
  "module.vpc_endpoints"
  "module.eks"
  "module.ebs_csi_driver_irsa"
  "module.vpc_cni_irsa"
  "aws_eks_addon.vpc_cni"
  "module.eks_blueprints_kubernetes_addons"
  "module.kubernetes_data_addons"
  "module.emr_containers"
)

# Apply modules in sequence
for target in "${targets[@]}"
do
  echo "Applying module $target..."
  terraform apply -target="$target" -var="region=$region" -auto-approve
  apply_output=$(terraform apply -target="$target" -var="region=$region" -auto-approve 2>&1)
  if [[ $? -eq 0 && $apply_output == *"Apply complete"* ]]; then
    echo "SUCCESS: Terraform apply of $target completed successfully"
  else
    echo "FAILED: Terraform apply of $target failed"
    exit 1
  fi
done

# Final apply to catch any remaining resources
echo "Applying remaining resources..."
terraform apply -var="region=$region" -auto-approve
apply_output=$(terraform apply -var="region=$region" -auto-approve 2>&1)
if [[ $? -eq 0 && $apply_output == *"Apply complete"* ]]; then
  echo "SUCCESS: Terraform apply of all modules completed successfully"
else
  echo "FAILED: Terraform apply of all modules failed"
  exit 1
fi