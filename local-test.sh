#!/bin/bash

# Local testing script for credential rotator
set -e

echo "🚀 Starting local credential rotator test..."

# Create a test secret file in the current directory
echo "📁 Creating test secret for Kubernetes..."
kubectl create secret generic test-credentials \
    --from-literal=username=olduser \
    --from-literal=password=oldpass123 \
    --dry-run=client -o yaml > test-secret.yaml

# Apply the test secret to default namespace
kubectl apply -f test-secret.yaml

echo "✅ Test secret created"

# Set environment variables for the test
export API_URL="https://jsonplaceholder.typicode.com/users/1"
export NAMESPACE="default"
export SECRET_NAME="test-credentials"

echo "🔧 Environment variables set:"
echo "  API_URL: $API_URL"
echo "  NAMESPACE: $NAMESPACE"
echo "  SECRET_NAME: $SECRET_NAME"

# Test local connection first
echo "🔍 Testing local connection to OpenShift..."
kubectl cluster-info
kubectl get pods --all-namespaces | head -5

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t credential-rotator:local .

# Run the container with debug info
echo "🏃 Running credential rotator container..."
docker run --rm \
    --network host \
    -v ~/.kube:/root/.kube:ro \
    -e API_URL="$API_URL" \
    -e NAMESPACE="$NAMESPACE" \
    -e SECRET_NAME="$SECRET_NAME" \
    credential-rotator:local

# Check the updated secret
echo "🔍 Checking updated secret..."
kubectl get secret test-credentials -o yaml

# Cleanup
#echo "🧹 Cleaning up test resources..."
#kubectl delete secret test-credentials
#rm -f test-secret.yaml

echo "✅ Local test completed!"

    # -e KUBECONFIG=/root/.kube/config \