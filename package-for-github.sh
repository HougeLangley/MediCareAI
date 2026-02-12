#!/bin/bash
#==============================================================================
# MediCare_AI GitHub Release Packaging Script
# Version: 2.0.0
# Date: 2026-02-09
#==============================================================================

set -o pipefail
set -o errexit

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="MediCare_AI"
VERSION="v2.0.0"
OUTPUT_FILE="${PROJECT_NAME}-${VERSION}.tar.gz"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}MediCare_AI GitHub Release Packager${NC}          ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                    ${YELLOW}Version ${VERSION}${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo

# Check if we're in the right directory
if [[ ! -f "docker-compose.yml" ]] || [[ ! -f "install.sh" ]]; then
    echo -e "${RED}Error: Please run this script from the MediCare_AI project root${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1:${NC} Cleaning up temporary files..."
# Clean up any existing archives
rm -f "${OUTPUT_FILE}"
rm -f "${PROJECT_NAME}"-*.tar.gz
echo -e "${GREEN}✓${NC} Cleanup complete"
echo

echo -e "${BLUE}Step 2:${NC} Verifying required files exist..."
required_files=(
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "install.sh"
    "docker-compose.yml"
    ".env.example"
    "docs/RELEASE_v2.0.0.mdx"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $file"
done
echo

echo -e "${BLUE}Step 3:${NC} Checking .gitignore exclusions..."
if ! grep -q "^\.env$" .gitignore; then
    echo -e "${YELLOW}! Warning: .env not found in .gitignore${NC}"
fi
if ! grep -q "^logs/" .gitignore; then
    echo -e "${YELLOW}! Warning: logs/ not found in .gitignore${NC}"
fi
echo -e "${GREEN}✓${NC} .gitignore check complete"
echo

echo -e "${BLUE}Step 4:${NC} Creating release archive..."
echo -e "${YELLOW}This will exclude:${NC}"
echo "  - .env files (sensitive configuration)"
echo "  - .git directory (version control)"
echo "  - logs/ directory (runtime logs)"
echo "  - backups/ directory (backup files)"
echo "  - uploads/ directory (user uploads)"
echo "  - node_modules/ (npm packages - will be installed during deployment)"
echo "  - __pycache__/ and *.pyc (Python cache)"
echo "  - .tar.gz files (existing packages)"
echo "  - COMMIT_MESSAGE*.md (internal commit messages)"
echo

# Create the archive with exclusions
tar czvf "${OUTPUT_FILE}" \
    --exclude='.env' \
    --exclude='backend/.env' \
    --exclude='.git' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='uploads' \
    --exclude='data/uploads/*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.vscode' \
    --exclude='.idea' \
    --exclude='*.swp' \
    --exclude='.DS_Store' \
    --exclude='test_*.py' \
    --exclude='**/node_modules' \
    --exclude='frontend/node_modules' \
    --exclude='*.tar.gz' \
    --exclude='MediCare_AI-*.tar.gz' \
    --exclude='COMMIT_MESSAGE*.md' \
    --exclude='package-for-github.sh' \
    .

echo

# Check if archive was created
if [[ -f "${OUTPUT_FILE}" ]]; then
    FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}              ${GREEN}✓ Release Package Created!${NC}                ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}File:${NC} ${YELLOW}${OUTPUT_FILE}${NC}"
    echo -e "${BLUE}Size:${NC} ${YELLOW}${FILE_SIZE}${NC}"
    echo -e "${BLUE}Location:${NC} ${YELLOW}$(pwd)/${OUTPUT_FILE}${NC}"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Upload ${OUTPUT_FILE} to GitHub Releases"
    echo "2. Tag the release: git tag ${VERSION}"
    echo "3. Push the tag: git push origin ${VERSION}"
    echo
    echo -e "${BLUE}Verification:${NC}"
    echo "  tar tzf ${OUTPUT_FILE} | head -20"
else
    echo -e "${RED}✗ Failed to create release archive${NC}"
    exit 1
fi
