import boto3
import os
from datetime import datetime, timezone
from botocore.exceptions import ClientError, NoCredentialsError


def get_session():
    """
    Create a boto3 session using credentials from environment variables.
    These come from the .env file the user fills in.
    """
    return boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    )


def safe_collect(name, fn):
    """
    Run a collector function. If it fails (permission denied, service not
    available in region, etc.) return an empty result with the error noted.
    This means one broken service never crashes the whole scan.
    """
    try:
        return fn()
    except ClientError as e:
        code = e.response["Error"]["Code"]
        return {"service": name, "error": code, "count": 0, "resources": [], "cost": 0.0}
    except Exception as e:
        return {"service": name, "error": str(e), "count": 0, "resources": [], "cost": 0.0}


def collect_ec2(session, region):
    ec2 = session.client("ec2", region_name=region)
    response = ec2.describe_instances()
    instances = []
    cost = 0.0

    # Rough hourly cost map by instance type (on-demand Linux, us-east-1)
    cost_map = {
        "t2.micro": 0.0116,  "t2.small": 0.023,  "t2.medium": 0.0464,
        "t3.micro": 0.0104,  "t3.small": 0.0208, "t3.medium": 0.0416,
        "t3.large": 0.0832,  "m5.large": 0.096,  "m5.xlarge": 0.192,
    }

    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            state = inst["State"]["Name"]
            itype = inst.get("InstanceType", "unknown")
            # Only running instances cost money
            monthly = round(cost_map.get(itype, 0.05) * 730, 2) if state == "running" else 0.0
            cost += monthly

            name_tag = next(
                (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), inst["InstanceId"]
            )
            instances.append({
                "name": name_tag,
                "id": inst["InstanceId"],
                "type": itype,
                "state": state,
                "cost": monthly,
                "az": inst.get("Placement", {}).get("AvailabilityZone", region),
            })

    return {
        "id": "ec2",
        "iconKey": "ec2",
        "name": "EC2",
        "desc": f"Virtual servers — {len(instances)} instance{'s' if len(instances) != 1 else ''}",
        "count": len(instances),
        "region": region,
        "status": "running" if any(i["state"] == "running" for i in instances) else "stopped",
        "cost": round(cost, 2),
        "about": "Elastic Compute Cloud gives you resizable virtual servers. You pay per hour an instance is running.",
        "resources": instances,
    }


def collect_lambda(session, region):
    lmb = session.client("lambda", region_name=region)
    paginator = lmb.get_paginator("list_functions")
    functions = []

    for page in paginator.paginate():
        for fn in page["Functions"]:
            functions.append({
                "name": fn["FunctionName"],
                "id": fn["FunctionArn"],
                "type": f"{fn.get('Runtime','unknown')} — {fn.get('MemorySize',128)}MB",
                "state": "idle",
                "cost": 0.0,  # Lambda free tier covers most hobby usage
            })

    return {
        "id": "lambda",
        "iconKey": "lambda",
        "name": "Lambda",
        "desc": f"Serverless functions — {len(functions)} function{'s' if len(functions) != 1 else ''}",
        "count": len(functions),
        "region": region,
        "status": "free" if functions else "idle",
        "cost": 0.0,
        "about": "Lambda runs your code without managing servers. Free tier: 1M requests and 400,000 GB-seconds per month.",
        "resources": functions,
    }


def collect_s3(session):
    s3 = session.client("s3")
    response = s3.list_buckets()
    buckets = []

    for b in response.get("Buckets", []):
        buckets.append({
            "name": b["Name"],
            "id": f"s3://{b['Name']}",
            "type": "S3 Bucket",
            "state": "active",
            "cost": 0.0,
            "created": b["CreationDate"].strftime("%Y-%m-%d"),
        })

    return {
        "id": "s3",
        "iconKey": "s3",
        "name": "S3",
        "desc": f"Object storage — {len(buckets)} bucket{'s' if len(buckets) != 1 else ''}",
        "count": len(buckets),
        "region": "Global",
        "status": "running" if buckets else "idle",
        "cost": 0.0,
        "about": "S3 stores files, backups, and static assets. Free tier: 5GB standard storage per month.",
        "resources": buckets,
    }


def collect_vpc(session, region):
    ec2 = session.client("ec2", region_name=region)

    vpcs = ec2.describe_vpcs()["Vpcs"]
    nat_gateways = ec2.describe_nat_gateways()["NatGateways"]

    # NAT gateways cost ~$0.045/hour = $32.85/month each
    active_nats = [n for n in nat_gateways if n["State"] == "available"]
    nat_cost = round(len(active_nats) * 0.045 * 730, 2)

    resources = []
    for vpc in vpcs:
        name = next((t["Value"] for t in vpc.get("Tags", []) if t["Key"] == "Name"), vpc["VpcId"])
        resources.append({
            "name": name,
            "id": vpc["VpcId"],
            "type": "VPC" + (" (default)" if vpc.get("IsDefault") else ""),
            "state": "active",
            "cost": 0.0,
        })

    for nat in active_nats:
        resources.append({
            "name": "NAT Gateway",
            "id": nat["NatGatewayId"],
            "type": "NAT Gateway — billing per hour",
            "state": "active",
            "cost": round(0.045 * 730, 2),
        })

    total_count = len(vpcs) + len(active_nats)

    return {
        "id": "vpc",
        "iconKey": "vpc",
        "name": "VPC",
        "desc": f"Virtual network — {len(vpcs)} VPC, {len(active_nats)} NAT gateway{'s' if len(active_nats) != 1 else ''}",
        "count": total_count,
        "region": region,
        "status": "idle" if active_nats else "free",
        "cost": nat_cost,
        "about": "Your Virtual Private Cloud is the private network for all AWS resources. NAT Gateways charge per hour even with no traffic — delete idle ones.",
        "resources": resources,
    }


def collect_route53(session):
    r53 = session.client("route53")
    zones = r53.list_hosted_zones()["HostedZones"]

    resources = []
    for z in zones:
        resources.append({
            "name": z["Name"].rstrip("."),
            "id": z["Id"].replace("/hostedzone/", ""),
            "type": "Public hosted zone" if not z["Config"]["PrivateZone"] else "Private hosted zone",
            "state": "active",
            "cost": 0.50,  # $0.50/hosted zone/month
        })

    total_cost = round(len(zones) * 0.50, 2)

    return {
        "id": "route53",
        "iconKey": "route53",
        "name": "Route 53",
        "desc": f"DNS — {len(zones)} hosted zone{'s' if len(zones) != 1 else ''}",
        "count": len(zones),
        "region": "Global",
        "status": "running" if zones else "idle",
        "cost": total_cost,
        "about": "Route 53 manages your domain DNS. Each hosted zone costs $0.50/month plus $0.40 per million queries.",
        "resources": resources,
    }


def collect_cloudwatch(session, region):
    logs = session.client("logs", region_name=region)
    paginator = logs.get_paginator("describe_log_groups")
    groups = []

    for page in paginator.paginate():
        for g in page["logGroups"]:
            groups.append({
                "name": g["logGroupName"],
                "id": g["logGroupName"],
                "type": "Log group",
                "state": "active",
                "cost": 0.0,
                "size_mb": round(g.get("storedBytes", 0) / 1024 / 1024, 2),
            })

    return {
        "id": "cloudwatch",
        "iconKey": "cloudwatch",
        "name": "CloudWatch",
        "desc": f"Logs + monitoring — {len(groups)} log group{'s' if len(groups) != 1 else ''}",
        "count": len(groups),
        "region": region,
        "status": "free",
        "cost": 0.0,
        "about": "CloudWatch collects logs from Lambda and other services. Free tier: 5GB ingestion and 3 dashboards per month.",
        "resources": groups,
    }


def collect_apigateway(session, region):
    apigw = session.client("apigateway", region_name=region)
    apis = apigw.get_rest_apis()["items"]

    resources = []
    for api in apis:
        # Get deployment count
        try:
            deployments = apigw.get_deployments(restApiId=api["id"])["items"]
            dep_count = len(deployments)
        except Exception:
            dep_count = 0

        resources.append({
            "name": api["name"],
            "id": api["id"],
            "type": f"REST API — {dep_count} deployment{'s' if dep_count != 1 else ''}",
            "state": "active",
            "cost": 0.0,
        })

    return {
        "id": "apigateway",
        "iconKey": "apigateway",
        "name": "API Gateway",
        "desc": f"REST APIs — {len(apis)} API{'s' if len(apis) != 1 else ''}",
        "count": len(apis),
        "region": region,
        "status": "free" if apis else "idle",
        "cost": 0.0,
        "about": "API Gateway creates and manages your HTTP APIs. Free tier: 1M API calls/month for first 12 months.",
        "resources": resources,
    }


def collect_kms(session, region):
    kms = session.client("kms", region_name=region)
    paginator = kms.get_paginator("list_keys")
    keys = []

    for page in paginator.paginate():
        for k in page["Keys"]:
            try:
                meta = kms.describe_key(KeyId=k["KeyId"])["KeyMetadata"]
                if meta["KeyManager"] == "CUSTOMER" and meta["KeyState"] == "Enabled":
                    keys.append({
                        "name": meta.get("Description") or k["KeyId"][:8] + "...",
                        "id": k["KeyId"],
                        "type": f"{meta['KeyUsage']} — {meta['KeySpec']}",
                        "state": meta["KeyState"].lower(),
                        "cost": 1.0,  # $1/month per CMK
                    })
            except Exception:
                continue

    total_cost = round(len(keys) * 1.0, 2)

    return {
        "id": "kms",
        "iconKey": "kms",
        "name": "KMS",
        "desc": f"Encryption keys — {len(keys)} customer managed key{'s' if len(keys) != 1 else ''}",
        "count": len(keys),
        "region": region,
        "status": "running" if keys else "free",
        "cost": total_cost,
        "about": "KMS manages encryption keys. Customer managed keys (CMKs) cost $1/month each. AWS managed keys are free.",
        "resources": keys,
    }


def collect_aws_resources():
    """
    Main entry point. Collects resources from all supported AWS services.
    Returns a list of service objects the frontend can render directly.
    """
    session = get_session()
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    services = []

    # Each collector is wrapped in safe_collect so one failure does not
    # stop the others from running
    services.append(safe_collect("EC2",         lambda: collect_ec2(session, region)))
    services.append(safe_collect("S3",          lambda: collect_s3(session)))
    services.append(safe_collect("Lambda",      lambda: collect_lambda(session, region)))
    services.append(safe_collect("VPC",         lambda: collect_vpc(session, region)))
    services.append(safe_collect("Route 53",    lambda: collect_route53(session)))
    services.append(safe_collect("CloudWatch",  lambda: collect_cloudwatch(session, region)))
    services.append(safe_collect("API Gateway", lambda: collect_apigateway(session, region)))
    services.append(safe_collect("KMS",         lambda: collect_kms(session, region)))

    # Remove services with zero resources to keep the UI clean
    services = [s for s in services if s.get("count", 0) > 0 or s.get("error")]

    return {
        "provider": "aws",
        "region": region,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "services": services,
        "summary": {
            "total_resources": sum(s.get("count", 0) for s in services),
            "total_cost": round(sum(s.get("cost", 0) for s in services), 2),
            "paid_services": len([s for s in services if s.get("cost", 0) > 0]),
            "free_services": len([s for s in services if s.get("cost", 0) == 0]),
        }
    }
