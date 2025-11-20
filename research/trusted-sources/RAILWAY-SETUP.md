# Railway Deployment Setup Guide

This guide explains how to deploy the Trusted Sources project to Railway as two separate services.

## Services Overview

- **Backend Service**: FastAPI application (Python)
- **Frontend Service**: Next.js application (Node.js)

## Backend Service Setup

### 1. Create Backend Service
1. Connect your GitHub repository to Railway
2. Set the root directory to: `research/trusted-sources/backend`
3. Railway will automatically detect it's a Python application

### 2. Environment Variables
Set these environment variables in the Railway dashboard:

```
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
PYTHONPATH=/app
```

### 3. Domain Configuration
- Railway will provide a domain like: `https://backend-service.railway.app`
- Note this URL for frontend configuration

## Frontend Service Setup

### 1. Create Frontend Service
1. Connect the same GitHub repository to Railway
2. Set the root directory to: `research/trusted-sources/frontend`
3. Railway will automatically detect it's a Node.js application

### 2. Environment Variables
Set these environment variables in the Railway dashboard:

```
NEXT_PUBLIC_API_URL=https://your-backend-service.railway.app
NODE_ENV=production
PORT=3000
```

**Important**: Replace `your-backend-service.railway.app` with your actual backend service URL from step 3 above.

### 3. Build Configuration
Railway will automatically:
- Run `npm install`
- Run `npm run build`
- Start with `npm run start`

## Branch Deployment Strategy

### Research Branches
- Any branch starting with `research/` will automatically deploy to temporary environments
- Perfect for testing experimental features
- Automatically cleaned up when branch is deleted

### Main Branch
- Deploys to stable development environment
- Use for integration testing

## Common Issues

### CORS Errors
If you see CORS errors, make sure:
1. Your backend's Railway URL is added to the frontend's NEXT_PUBLIC_API_URL
2. The backend CORS configuration includes your frontend's Railway URL

### Environment Variables Not Working
- Make sure environment variables are set in Railway dashboard, not just in .env files
- .env files are for local development only
- Use the exact variable names shown above

## Testing Your Deployment

1. Open your frontend Railway URL
2. Try the chat functionality
3. Check Railway logs for any errors
4. Verify the backend health endpoint at: `https://your-backend-service.railway.app/health`

## Local Development

For local development, use the existing setup:
- Backend: `cd backend && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm run dev`