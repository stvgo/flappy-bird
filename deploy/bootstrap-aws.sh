#!/usr/bin/env bash
set -euo pipefail

# One-time setup: crea bucket S3 privado, OAC y distribución CloudFront.
# Ejecutar una sola vez. Después usar deploy-s3.sh para deploys.
#
# Requiere env: AWS_REGION, BUCKET_NAME

: "${AWS_REGION:?required}"
: "${BUCKET_NAME:?required}"

ACCT="$(aws sts get-caller-identity --query Account --output text)"
echo "==> Cuenta: $ACCT  Region: $AWS_REGION  Bucket: $BUCKET_NAME"

echo "==> Creando bucket S3 privado"
if [[ "$AWS_REGION" == "us-east-1" ]]; then
    aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" || true
else
    aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" \
        --create-bucket-configuration LocationConstraint="$AWS_REGION" || true
fi

aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "==> Creando Origin Access Control"
OAC_ID=$(aws cloudfront create-origin-access-control --origin-access-control-config \
    "Name=${BUCKET_NAME}-oac,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3" \
    --query 'OriginAccessControl.Id' --output text)
echo "OAC creado: $OAC_ID"

echo "==> Creando distribución CloudFront"
DIST_CONFIG=$(cat <<EOF
{
  "CallerReference": "flappy-bird-$(date +%s)",
  "Comment": "Flappy Bird (pygbag/WASM)",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "s3-${BUCKET_NAME}",
      "DomainName": "${BUCKET_NAME}.s3.${AWS_REGION}.amazonaws.com",
      "S3OriginConfig": { "OriginAccessIdentity": "" },
      "OriginAccessControlId": "${OAC_ID}"
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "s3-${BUCKET_NAME}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": { "Quantity": 2, "Items": ["GET","HEAD"], "CachedMethods": { "Quantity": 2, "Items": ["GET","HEAD"] } },
    "Compress": true,
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
  },
  "PriceClass": "PriceClass_100"
}
EOF
)

DIST_RESULT=$(aws cloudfront create-distribution --distribution-config "$DIST_CONFIG")
DIST_ID=$(echo "$DIST_RESULT" | python -c "import sys,json; print(json.load(sys.stdin)['Distribution']['Id'])")
DIST_DOMAIN=$(echo "$DIST_RESULT" | python -c "import sys,json; print(json.load(sys.stdin)['Distribution']['DomainName'])")

echo "Distribución: $DIST_ID  ($DIST_DOMAIN)"

echo "==> Aplicando bucket policy (CloudFront → S3 via OAC)"
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontServicePrincipal",
    "Effect": "Allow",
    "Principal": { "Service": "cloudfront.amazonaws.com" },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::${BUCKET_NAME}/*",
    "Condition": { "StringEquals": { "AWS:SourceArn": "arn:aws:cloudfront::${ACCT}:distribution/${DIST_ID}" } }
  }]
}
EOF
aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy file:///tmp/bucket-policy.json
rm -f /tmp/bucket-policy.json

echo ""
echo "==================================================="
echo "Listo. Guardá estos valores para deploy-s3.sh:"
echo "  export BUCKET_NAME=$BUCKET_NAME"
echo "  export DIST_ID=$DIST_ID"
echo ""
echo "URL pública (tarda ~5min en estar 'Deployed'):"
echo "  https://$DIST_DOMAIN"
echo "==================================================="
