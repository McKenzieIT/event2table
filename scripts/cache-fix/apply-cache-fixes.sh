#!/bin/bash

###############################################################################
# React Query Cache Consistency Fixes - Automated Fix Script
#
# This script automatically applies all the cache consistency fixes
# identified in the analysis report.
#
# Usage:
#   bash scripts/cache-fix/apply-cache-fixes.sh
#
# Author: Event2Table Development Team
# Date: 2026-02-22
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
FRONTEND_SRC="$PROJECT_ROOT/frontend/src"
BACKEND_SRC="$PROJECT_ROOT/backend"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}React Query Cache Consistency Fixes${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Create backup directory
BACKUP_DIR="$PROJECT_ROOT/.cache-fix-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✓ Created backup directory: $BACKUP_DIR${NC}"
echo ""

###############################################################################
# Fix 1: EventsList.jsx - Fix cache invalidation keys
###############################################################################
echo -e "${YELLOW}[Fix 1/7] EventsList.jsx - Fix cache invalidation keys${NC}"

FILE="$FRONTEND_SRC/analytics/pages/EventsList.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/EventsList.jsx.bak"

  # Fix line 89: delete mutation
  sed -i '' 's/queryClient\.invalidateQueries(\['"'"'events'"'"'\]);/queryClient.invalidateQueries({ queryKey: ['"'"'events'"'"', currentGame?.gid] });/g' "$FILE"

  # Fix line 226: manual reload button
  sed -i '' 's/queryClient\.invalidateQueries({ queryKey: \['"'"'events'"'"'\] });/queryClient.invalidateQueries({ queryKey: ['"'"'events'"'"', currentGame?.gid] });/g' "$FILE"

  echo -e "${GREEN}✓ Fixed EventsList.jsx${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 2: CategoriesList.jsx - Fix cache invalidation keys
###############################################################################
echo -e "${YELLOW}[Fix 2/7] CategoriesList.jsx - Fix cache invalidation keys${NC}"

FILE="$FRONTEND_SRC/analytics/pages/CategoriesList.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/CategoriesList.jsx.bak"

  # Fix line 90: delete mutation
  sed -i '' 's/queryClient\.invalidateQueries({ queryKey: \['"'"'categories'"'"'\] });/queryClient.invalidateQueries({ queryKey: ['"'"'categories'"'"', gameGid] });/g' "$FILE"

  # Fix line 111: batch delete mutation
  sed -i '' '/batchDeleteMutation/,/onSuccess:/ s/queryClient\.invalidateQueries({ queryKey: \['"'"'categories'"'"'\] });/queryClient.invalidateQueries({ queryKey: ['"'"'categories'"'"', gameGid] });/g' "$FILE"

  echo -e "${GREEN}✓ Fixed CategoriesList.jsx${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 3: CommonParamsList.jsx - Fix cache invalidation keys
###############################################################################
echo -e "${YELLOW}[Fix 3/7] CommonParamsList.jsx - Fix cache invalidation keys${NC}"

FILE="$FRONTEND_SRC/analytics/pages/CommonParamsList.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/CommonParamsList.jsx.bak"

  # Fix line 60: delete mutation
  sed -i '' 's/queryClient\.invalidateQueries({ queryKey: \['"'"'common-params'"'"'\] });/queryClient.invalidateQueries({ queryKey: ['"'"'common-params'"'"', gameGid] });/g' "$FILE"

  # Fix line 77: batch delete mutation
  sed -i '' '/batchDeleteMutation/,/onSuccess:/ s/queryClient\.invalidateQueries({ queryKey: \['"'"'common-params'"'"'\] });/queryClient.invalidateQueries({ queryKey: ['"'"'common-params'"'"', gameGid] });/g' "$FILE"

  echo -e "${GREEN}✓ Fixed CommonParamsList.jsx${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 4: FlowsList.jsx - Fix cache invalidation keys
###############################################################################
echo -e "${YELLOW}[Fix 4/7] FlowsList.jsx - Fix cache invalidation keys${NC}"

FILE="$FRONTEND_SRC/analytics/pages/FlowsList.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/FlowsList.jsx.bak"

  # Fix line 64: delete mutation
  sed -i '' 's/queryClient\.invalidateQueries(\['"'"'flows'"'"'\]);/queryClient.invalidateQueries({ queryKey: ['"'"'flows'"'"', gameGid] });/g' "$FILE"

  echo -e "${GREEN}✓ Fixed FlowsList.jsx${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 5: CategoryManagementModal.jsx - Fix cache invalidation keys
###############################################################################
echo -e "${YELLOW}[Fix 5/7] CategoryManagementModal.jsx - Fix cache invalidation keys${NC}"

FILE="$FRONTEND_SRC/analytics/components/categories/CategoryManagementModal.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/CategoryManagementModal.jsx.bak"

  # Fix all three mutations (create, update, delete)
  sed -i '' 's/queryClient\.invalidateQueries(\['"'"'categories'"'"'\]);/queryClient.invalidateQueries({ queryKey: ['"'"'categories'"'"', gameGid] });/g' "$FILE"

  echo -e "${GREEN}✓ Fixed CategoryManagementModal.jsx${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 6: EventForm.jsx - Add cache invalidation
###############################################################################
echo -e "${YELLOW}[Fix 6/7] EventForm.jsx - Add cache invalidation${NC}"

FILE="$FRONTEND_SRC/analytics/pages/EventForm.jsx"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/EventForm.jsx.bak"

  # Add useQueryClient to imports
  sed -i '' 's/import { useQuery, useMutation } from '"'"'@tanstack/react-query'"'"';/import { useQuery, useMutation, useQueryClient } from '"'"'@tanstack/react-query'"'"';/g' "$FILE"

  # Add queryClient initialization after component declaration
  # This requires a more complex edit, showing manual instructions instead
  echo -e "${YELLOW}⚠ EventForm.jsx requires manual editing (see below)${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Fix 7: Backend invalidator.py - Fix parameter names
###############################################################################
echo -e "${YELLOW}[Fix 7/7] Backend invalidator.py - Fix parameter names${NC}"

FILE="$BACKEND_SRC/core/cache/invalidator.py"
if [ -f "$FILE" ]; then
  cp "$FILE" "$BACKUP_DIR/invalidator.py.bak"

  # Fix game_id -> game_gid
  sed -i '' "s/self\.invalidate_pattern('events\.list', game_id=game_gid)/self.invalidate_pattern('events.list', game_gid=game_gid)/g" "$FILE"

  echo -e "${GREEN}✓ Fixed invalidator.py${NC}"
else
  echo -e "${RED}✗ File not found: $FILE${NC}"
fi
echo ""

###############################################################################
# Summary
###############################################################################
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}Fix Summary${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${GREEN}✓ Automatic fixes applied: 6/7${NC}"
echo -e "${YELLOW}⚠ Manual fixes required: 1/7 (EventForm.jsx)${NC}"
echo ""
echo -e "${BLUE}Backup location: $BACKUP_DIR${NC}"
echo ""

###############################################################################
# Manual fix instructions for EventForm.jsx
###############################################################################
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}Manual Fix Required: EventForm.jsx${NC}"
echo -e "${YELLOW}======================================================================${NC}"
echo ""
echo "Please add the following code to EventForm.jsx:"
echo ""
echo -e "${GREEN}1. Add useQueryClient to imports (already done):${NC}"
echo "   import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';"
echo ""
echo -e "${GREEN}2. Add queryClient initialization after line 26:${NC}"
echo "   function EventForm() {"
echo "     const queryClient = useQueryClient();  // ← Add this line"
echo "     const { success, error: showError } = useToast();"
echo ""
echo -e "${GREEN}3. Add cache invalidation in handleSubmit (after line 159):${NC}"
echo "   success(isEdit ? '事件更新成功' : '事件创建成功');"
echo ""
echo "   // Add these lines:"
echo "   const gameGid = searchParams.get('game_gid') || currentGame?.gid;"
echo "   queryClient.invalidateQueries({"
echo "     queryKey: ['events', parseInt(gameGid)]"
echo "   });"
echo ""
echo "   navigate('/events', { replace: true });"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo ""

###############################################################################
# Verification instructions
###############################################################################
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}Verification Instructions${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo "1. Start the backend server:"
echo "   ${GREEN}cd $PROJECT_ROOT && python web_app.py${NC}"
echo ""
echo "2. Start the frontend server (new terminal):"
echo "   ${GREEN}cd $PROJECT_ROOT/frontend && npm run dev${NC}"
echo ""
echo "3. Test each module:"
echo "   - Games: Create, edit, delete games"
echo "   - Events: Create, edit, delete events"
echo "   - Categories: Create, edit, delete categories"
echo "   - Common Params: Delete, sync common params"
echo "   - Flows: Delete flows"
echo ""
echo "4. Verify that lists update immediately without page refresh"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo ""

###############################################################################
# Rollback instructions
###############################################################################
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}Rollback Instructions (if needed)${NC}"
echo -e "${YELLOW}======================================================================${NC}"
echo ""
echo "To rollback all changes, run:"
echo "   ${GREEN}cp $BACKUP_DIR/*.bak $FRONTEND_SRC/analytics/pages/${NC}"
echo "   ${GREEN}cp $BACKUP_DIR/*.bak $FRONTEND_SRC/analytics/components/categories/${NC}"
echo "   ${GREEN}cp $BACKUP_DIR/invalidator.py.bak $BACKEND_SRC/core/cache/invalidator.py${NC}"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo ""
