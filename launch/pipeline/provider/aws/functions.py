import logging
import json
import subprocess

logger = logging.getLogger(__name__)

def assume_role(role_arn, profile='qa', region="us-east-2"):
    logger.info("Assuming the IAM deployment role")
    try:
        sts_credentials = json.loads(subprocess.check_output(["aws", "sts", "assume-role", "--role-arn", role_arn, "--role-session-name", "caf-build-agent"]))
    except Exception as e:
        raise RuntimeError(f"Failed aws sts assume-role: {str(e)}") from e

    access_key = sts_credentials["Credentials"]["AccessKeyId"]
    secret_access_key = sts_credentials["Credentials"]["SecretAccessKey"]
    session_token = sts_credentials["Credentials"]["SessionToken"]
        
    try:
        subprocess.run(["aws", "configure", "set", f"profile.{profile}.aws_access_key_id", access_key])
        subprocess.run(["aws", "configure", "set", f"profile.{profile}.aws_secret_access_key", secret_access_key])
        subprocess.run(["aws", "configure", "set", f"profile.{profile}.aws_session_token", session_token])
        subprocess.run(["aws", "configure", "set", f"profile.{profile}.region", region])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed set aws configure: {str(e)}")