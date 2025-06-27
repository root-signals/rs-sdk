#!/bin/bash

# OpenAPI Generation Script for Root Signals TypeScript SDK
# Based on the frontend's openapi-typescript-generator.sh

set -e

url="https://api.app.rootsignals.ai/docs/download/"

if [ -n "$1" ]; then
    url="$1"
fi

echo "🔄 Downloading OpenAPI schema from $url"
curl -o ./src/generated/schema.yaml "$url"

echo "🔧 Generating TypeScript types and client..."
npx openapi-typescript ./src/generated/schema.yaml -o ./src/generated/types.ts

echo "✅ OpenAPI generation complete!"
echo "📁 Generated files:"
echo "   - ./src/generated/types.ts"
echo "   - ./src/generated/schema.yaml"

# Clean up
rm ./src/generated/schema.yaml