# Performance Monitoring Report

**Generated:** 2026-03-18 09:19:04
**Server:** macbookpro
**Version:** 912775e

## Executive Summary

### Cache Performance
[0;34m[2026-03-18 09:19:04][0m Monitoring cache performance...
[0;34m[2026-03-18 09:19:04][0m Cache API not available, checking logs...
[1;33m[WARN][0m Cache log file not found
Status: ✅ PASS

### API Response Times
[0;34m[2026-03-18 09:19:04][0m Monitoring API response times...
[0;34m[2026-03-18 09:19:04][0m Testing endpoint: http://127.0.0.1:5001/api/health
[0;34m[2026-03-18 09:19:04][0m Response time: 0
0ms
/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh: line 188: printf: 0
0: invalid number
[0;32m[OK][0m Response time is acceptable (0
0ms)
[0;34m[2026-03-18 09:19:04][0m Testing endpoint: http://127.0.0.1:5001/api/games
[0;34m[2026-03-18 09:19:04][0m Response time: 0
0ms
/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh: line 188: printf: 0
0: invalid number
[0;32m[OK][0m Response time is acceptable (0
0ms)
[0;34m[2026-03-18 09:19:04][0m Testing endpoint: http://127.0.0.1:5001/api/events
[0;34m[2026-03-18 09:19:04][0m Response time: 0
0ms
/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh: line 188: printf: 0
0: invalid number
[0;32m[OK][0m Response time is acceptable (0
0ms)
[0;34m[2026-03-18 09:19:04][0m Average response time: 0
0
0
0ms
/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh: line 204: printf: 0
0
0
0: invalid number
[0;32m[OK][0m Average response time is good (0
0
0
0ms)
Status: ✅ PASS

### Database Query Performance
[0;34m[2026-03-18 09:19:04][0m Monitoring database query performance...
[0;34m[2026-03-18 09:19:04][0m Database size:  12M
Count games: 2.18ms
Count events: Error - no such table: events
Fetch games: 0.05ms
Average query time: 0.74ms
[0;32m[OK][0m Database query performance is good
Status: ✅ PASS

### System Resources
[0;34m[2026-03-18 09:19:04][0m Monitoring system resources...
[0;34m[2026-03-18 09:19:05][0m CPU usage: 15.69%
[0;32m[OK][0m CPU usage is normal (15.69%)
[0;34m[2026-03-18 09:19:05][0m Disk usage: 59%
[0;32m[OK][0m Disk usage is normal (59%)

### Application Resources
[0;34m[2026-03-18 09:19:05][0m Monitoring application resource usage...
