#!/bin/bash
# GitHub分支保护配置脚本
# 使用gh CLI配置main分支的保护规则

set -e

echo "🔒 配置GitHub分支保护规则..."

# 1. 配置main分支的保护规则
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  repos/McKenzieIT/event2table/branches/main/protection \
  -f < <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [],
    "checks": [
      {
        "context": "pre-commit"
      }
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "✅ 分支保护规则配置完成！"
echo ""
echo "📋 已配置的保护规则："
echo "  - 需要PR才能合并"
echo "  - 至少1个审查批准"
echo "  - 自动驳回过期的审查"
echo "  - 管理员也必须遵守规则"
echo "  - 禁止强制推送"
echo "  - 禁止删除分支"
echo ""
echo "🔗 查看配置："
echo "https://github.com/McKenzieIT/event2table/settings/branches"
