#!/bin/bash

echo "=== 获取浏览器页面内容 ==="

# AppleScript to get page text content
osascript << 'EOF'
tell application "Google Chrome"
    if (count of windows) > 0 then
        set theTab to active tab of window 1
        set pageContent to execute theTab javascript "document.body.textContent"
        return pageContent
    else
        return "No Chrome window found"
    end if
end tell
EOF
