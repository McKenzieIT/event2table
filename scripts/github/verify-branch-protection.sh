#!/bin/bash
# 验证分支保护配置

echo "🔍 验证GitHub分支保护配置..."
echo ""

# 检查分支保护状态
gh api repos/McKenzieIT/event2table/branches/main/protection 2>&1 | \
  jq '{
    branch_protection: true,
    requires_pr: (.required_pull_request_reviews != null),
    required_approvals: .required_pull_request_reviews.required_approving_review_count,
    dismiss_stale: .required_pull_request_reviews.dismiss_stale_reviews,
    enforce_admins: .enforce_admins,
    allow_force_push: .allow_force_pushes,
    allow_deletions: .allow_deletions
  }' 2>/dev/null || echo "⚠️  分支可能未受保护"

echo ""
echo "✅ 如果以上显示了配置信息，说明分支保护已生效"
echo "🔗 访问查看：https://github.com/McKenzieIT/event2table/settings/branches"
