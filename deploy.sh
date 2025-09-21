#!/bin/bash

# Deploy Travel Planner to Google Cloud Run
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="travel-planner"
GOOGLE_API_KEY="your-google-api-key-here"

echo "🚀 Deploying Travel Planner to Google Cloud Run..."

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secret for Google API Key
echo "Creating secret for Google API Key..."
echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key --data-file=-

# Grant Cloud Run access to the secret
echo "Granting Cloud Run access to secret..."
gcloud secrets add-iam-policy-binding google-api-key \
    --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Build and deploy using Cloud Build
echo "Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml

echo "✅ Deployment completed!"
echo "🌐 Your service will be available at:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'

echo ""
echo "📝 Test your deployment with:"
echo "curl -X POST [YOUR_SERVICE_URL]/plan-trip \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"user_input\": \"I want to visit Paris for 5 days with a budget of $2000\"}'"