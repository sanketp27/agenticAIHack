#!/bin/bash

# Manual deployment script for Travel Planner to Google Cloud Run
# Use this if you prefer manual deployment over Cloud Build

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="travel-planner"
GOOGLE_API_KEY="your-google-api-key-here"

echo "🚀 Manually deploying Travel Planner to Google Cloud Run..."

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com

# Build the container image locally
echo "Building container image..."
docker build -t gcr.io/$PROJECT_ID/travel-planner:latest .

# Push to Container Registry
echo "Pushing to Container Registry..."
docker push gcr.io/$PROJECT_ID/travel-planner:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/travel-planner:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY",GEMINI_MODEL="gemini-1.5-pro" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300

echo "✅ Deployment completed!"
echo "🌐 Your service is available at:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'

echo ""
echo "📝 Test your deployment with:"
echo "SERVICE_URL=\$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')"
echo "curl -X POST \$SERVICE_URL/plan-trip \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"user_input\": \"I want to visit Paris for 5 days with a budget of $2000\"}'"