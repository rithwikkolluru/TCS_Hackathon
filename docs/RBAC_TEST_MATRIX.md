# RBAC Test Matrix

## Role Capabilities

| Endpoint | Manager | Employee | Regional Ops |
|----------|---------|----------|--------------|
| GET /api/dashboard/summary | ✅ Own branch | ✅ Own branch | ✅ All |
| GET /api/dashboard/bottlenecks | ✅ Own branch | ✅ Own branch | ✅ All |
| GET /api/dashboard/service-load | ✅ Own branch | ✅ Own branch | ✅ All |
| POST /api/predictions/footfall | ✅ Own branch | ✅ Own branch | ✅ All |
| POST /api/predictions/wait-time | ✅ Own branch | ✅ Own branch | ✅ All |
| POST /api/predictions/staff-requirement | ✅ Own branch | ✅ Own branch | ✅ All |
| GET /api/recommendations | ✅ Own branch | VIEW only | ✅ All |
| POST /api/recommendations/generate | ✅ Own branch | ❌ 403 | ❌ 403 |
| POST /api/recommendations/:id/accept | ✅ Own branch | ❌ 403 | ❌ 403 |
| POST /api/recommendations/:id/reject | ✅ Own branch | ❌ 403 | ❌ 403 |
| GET /api/feedback/summary | ✅ Own branch | ✅ Own branch | ✅ All |
| GET /api/regional/branches | ❌ 403 | ❌ 403 | ✅ |
| GET /api/regional/load | ❌ 403 | ❌ 403 | ✅ |
| GET /api/regional/staffing | ❌ 403 | ❌ 403 | ✅ |
| GET /api/audit | LIMITED | ❌ | ✅ |
| WS /ws/alerts | ✅ Branch alerts | ✅ Branch alerts | ✅ All alerts |

## Branch Isolation
- Manager with branch_id=BR001 cannot access BR002 data
- Employee can only view their assigned branch
- Regional Ops can see all branches (no branch restriction)

## Verified via Test Script
All RBAC rules verified in `scripts/full_system_test.py` — tests 9/RBAC section.
