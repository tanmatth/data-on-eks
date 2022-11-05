#---------------------------------------------------------------
# Deploy Batch Processing Gateway
# https://github.com/apple/batch-processing-gateway/tree/main/helm/batch-processing-gateway
#---------------------------------------------------------------
module "batch_processing_gateway" {
  source = "github.com/aws-ia/terraform-aws-eks-blueprints//modules/kubernetes-addons/helm-addon?ref=v4.12.0"
  helm_config = {
    name             = "batch-processing-gateway"
    chart            = "${path.module}/helm/batch-processing-gateway"
    repository       = null
    version          = "0.1.0"
    namespace        = "bpg"
    create_namespace = false
    description      = "Argo workflows Helm chart deployment configuration"
    timeout          = 300
  }

  addon_context = {
    aws_caller_identity_account_id = data.aws_caller_identity.current.account_id
    aws_caller_identity_arn        = data.aws_caller_identity.current.arn
    aws_eks_cluster_endpoint       = module.eks_blueprints.eks_cluster_endpoint
    aws_partition_id               = data.aws_partition.current.partition
    aws_region_name                = data.aws_region.current.name
    eks_cluster_id                 = module.eks_blueprints.eks_cluster_id
    eks_oidc_issuer_url            = local.eks_oidc_issuer_url
    eks_oidc_provider_arn          = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${local.eks_oidc_issuer_url}"
    tags                           = local.tags
    irsa_iam_role_path             = "/"
    irsa_iam_permissions_boundary  = ""
  }

  irsa_config = {
    kubernetes_namespace              = "bpg"
    kubernetes_service_account        = "bpg"
    create_kubernetes_namespace       = true
    create_kubernetes_service_account = true
    irsa_iam_policies                 = [aws_iam_policy.bpg.arn]
  }
}

#---------------------------------------------------------------
# IAM Policy for BPG IRSA
#---------------------------------------------------------------
resource "aws_iam_policy" "bpg" {
  description = "IAM role policy for bpg S3 Logs"
  name        = "${local.name}-bpg-irsa"
  policy      = data.aws_iam_policy_document.bpg.json
}

#---------------------------------------------------------------
# RDS Postgres Database for Apache BPG Metadata
#---------------------------------------------------------------
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 5.0"

  identifier = "bpg"

  engine               = "postgres"
  engine_version       = "14.3"
  family               = "postgres14"
  major_engine_version = "14"
  instance_class       = "db.m6i.xlarge"

  storage_type      = "io1"
  allocated_storage = 100
  iops              = 3000

  db_name                = "bpg"
  username               = "bpg"
  create_random_password = false
  password               = sensitive(aws_secretsmanager_secret_version.postgres.secret_string)
  port                   = 5432

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  backup_retention_period = 5
  skip_final_snapshot     = true
  deletion_protection     = false

  performance_insights_enabled = false
  #  performance_insights_retention_period = 7
  #  create_monitoring_role                = true
  #  monitoring_interval                   = 60
  #  monitoring_role_name                  = "bpg-metastore"
  #  monitoring_role_use_name_prefix       = true
  #  monitoring_role_description           = "BPG Postgres Metastore for monitoring role"

  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    }
  ]

  tags = local.tags
}

#---------------------------------------------------------------
# Postgres Metastore DB Master password
#---------------------------------------------------------------
resource "random_password" "postgres" {
  length  = 16
  special = false
}
#tfsec:ignore:aws-ssm-secret-use-customer-key
resource "aws_secretsmanager_secret" "postgres" {
  name                    = "bpg"
  recovery_window_in_days = 0 # Set to zero for this example to force delete during Terraform destroy
}

resource "aws_secretsmanager_secret_version" "postgres" {
  secret_id     = aws_secretsmanager_secret.postgres.id
  secret_string = random_password.postgres.result
}

#---------------------------------------------------------------
# PostgreSQL RDS security group
#---------------------------------------------------------------
module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = local.name
  description = "Complete PostgreSQL example security group"
  vpc_id      = module.vpc.vpc_id

  # ingress
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    },
  ]

  tags = local.tags
}
