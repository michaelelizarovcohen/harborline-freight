#!/usr/bin/env bash
# Render and apply the kustomize overlay for an environment.
# Usage: deploy/deploy.sh <staging|production> <image-tag>
set -euo pipefail

ENVIRONMENT="${1:-}"
TAG="${2:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERLAY="$REPO_ROOT/infra/k8s/overlays/$ENVIRONMENT"

die() { echo "deploy.sh: $*" >&2; exit 1; }

[[ -n "$ENVIRONMENT" && -n "$TAG" ]] || die "usage: $0 <staging|production> <image-tag>"
[[ -d "$OVERLAY" ]] || die "unknown environment '$ENVIRONMENT' (no $OVERLAY)"
command -v kubectl >/dev/null || die "kubectl not found"
command -v kustomize >/dev/null || die "kustomize not found"

case "$ENVIRONMENT" in
  staging)    EXPECTED_CONTEXT_SUFFIX="cluster/hbl-staging"; REGISTRY="123456789012.dkr.ecr.us-west-2.amazonaws.com" ;;
  production) EXPECTED_CONTEXT_SUFFIX="cluster/hbl-prod";    REGISTRY="210987654321.dkr.ecr.us-west-2.amazonaws.com" ;;
esac

CURRENT_CONTEXT="$(kubectl config current-context)"
if [[ "$CURRENT_CONTEXT" != *"$EXPECTED_CONTEXT_SUFFIX" ]]; then
  die "kubectl context is '$CURRENT_CONTEXT', expected *$EXPECTED_CONTEXT_SUFFIX — refusing to deploy"
fi

if [[ "$ENVIRONMENT" == "production" && "${HBL_CONFIRM_PROD:-}" != "yes" ]]; then
  die "production deploys require HBL_CONFIRM_PROD=yes (and a green staging deploy of the same tag)"
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
cp -r "$REPO_ROOT/infra/k8s" "$WORKDIR/"

pushd "$WORKDIR/k8s/overlays/$ENVIRONMENT" >/dev/null
kustomize edit set image \
  "harborline/api=$REGISTRY/harborline/api:$TAG" \
  "harborline/web=$REGISTRY/harborline/web:$TAG"
kustomize build . > "$WORKDIR/rendered.yaml"
popd >/dev/null

echo "==> Applying $(grep -c '^kind:' "$WORKDIR/rendered.yaml") objects to $ENVIRONMENT (tag $TAG)"
kubectl apply -f "$WORKDIR/rendered.yaml"

for deploy in harborline-api harborline-worker harborline-web; do
  kubectl -n harborline rollout status "deployment/$deploy" --timeout=180s
done

echo "==> $ENVIRONMENT is running $TAG"
