#!/usr/bin/env bash
set -euo pipefail

# Build con pygbag, sync a S3, invalidar CloudFront.
# Requiere env: BUCKET_NAME, DIST_ID

: "${BUCKET_NAME:?required}"
: "${DIST_ID:?required}"

cd "$(dirname "$0")/.."

echo "==> Build"
bash deploy/build.sh

echo "==> Sync a S3"
aws s3 sync build/web/ "s3://${BUCKET_NAME}/" --delete

echo "==> Invalidando CloudFront"
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "$DIST_ID" \
    --paths "/*" \
    --query 'Invalidation.Id' --output text)
echo "Invalidación: $INVALIDATION_ID"

echo "==> Listo. Cambios visibles en 1-2min."
