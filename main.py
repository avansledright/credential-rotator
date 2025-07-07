#!/usr/bin/env python3
"""
OpenShift Credential Rotator
Fetches new credentials from an API and updates an existing OpenShift secret.
"""

import os
import base64
import requests
from kubernetes import client, config


def main():
    # Get environment variables
    api_url = os.getenv('API_URL')
    namespace = os.getenv('NAMESPACE')
    secret_name = os.getenv('SECRET_NAME')
    
    # Fetch new credentials from API
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        credentials = response.json()
    except Exception as e:
        print(f"❌ Error fetching credentials: {e}")
        return
    
    # Load Kubernetes config
    try:
        config.load_incluster_config()
        print("Using in-cluster configuration")
    except:
        # Check for explicit token-based auth (for containers)
        k8s_host = os.environ.get('KUBERNETES_SERVICE_HOST')
        k8s_port = os.environ.get('KUBERNETES_SERVICE_PORT')
        k8s_token = os.environ.get('KUBERNETES_TOKEN')
        print(f"HOST: {k8s_host}")
        print(f"PORT: {k8s_port}")
        print(f"TOKEN: {k8s_token}")
        if k8s_host and k8s_port and k8s_token:
            print(f"Using token-based auth to {k8s_host}:{k8s_port}")
            configuration = client.Configuration()
            configuration.host = f"https://{k8s_host}:{k8s_port}"
            configuration.api_key = {"authorization": f"Bearer {k8s_token}"}
            configuration.verify_ssl = False  # For CRC self-signed certs
            client.Configuration.set_default(configuration)
        else:
            try:
                config.load_kube_config()
                print("Using kubeconfig file")
            except Exception as e:
                print(f"Failed to load Kubernetes config: {e}")
                print("Make sure you're logged into OpenShift with 'oc login' or set KUBERNETES_* env vars")
                raise
    
    # Prepare secret data (base64 encode values)
    secret_data = {}
    for key, value in credentials.items():
        secret_data[key] = base64.b64encode(str(value).encode()).decode()
    
    # Update the secret
    try:
        print("Attempting to update secret")
        v1 = client.CoreV1Api()
        existing_secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)
        existing_secret.data = secret_data
        v1.patch_namespaced_secret(name=secret_name, namespace=namespace, body=existing_secret)
        print("✅ Secret updated successfully!")
    except Exception as e:
        print(f"❌ Error updating secret: {e}")


if __name__ == '__main__':
    main()