# API Contract — All Production Endpoints

Base URL: `http://localhost:8000`
Auth: `Authorization: Bearer <JWT_TOKEN>` on all protected routes

## Authentication
| Method | Path | Auth | Body | Response |
|--------|------|------|------|----------|
| POST | /api/auth/login | None | {email, password} | {access_token, refresh_token, user} |
| POST | /api/auth/register | None | {name, email, password, role, branch_id} | UserOut |
| GET | /api/auth/me | Bearer | — | UserOut |
| POST | /api/auth/refresh | Bearer | — | {access_token} |
| POST | /api/auth/logout | Bearer | — | {success} |

## Dashboard (All roles, own branch)
| Method | Path | Params | Response |
|--------|------|--------|----------|
| GET | /api/dashboard/summary | branch_id | DashboardSummary |
| GET | /api/dashboard/bottlenecks | branch_id | List[BottleneckItem] |
| GET | /api/dashboard/service-load | branch_id | List[ServiceLoadItem] |

## Predictions (All roles, own branch)
| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | /api/predictions/footfall | {branch_id, date, start_time, end_time} | FootfallResponse |
| POST | /api/predictions/wait-time | {branch_id, service_category, queue_length, staff_available} | WaitTimeResponse |
| POST | /api/predictions/staff-requirement | {branch_id, date, start_time, end_time, expected_customers, service_category} | StaffRequirementResponse |

## Recommendations (Manager only for write)
| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | /api/recommendations | Bearer | List[RecommendationOut] |
| POST | /api/recommendations/generate | Manager | List[RecommendationOut] |
| POST | /api/recommendations/{id}/accept | Manager | {success, action} |
| POST | /api/recommendations/{id}/reject | Manager | {success, action} |
| GET | /api/recommendations/digital-redirection | Bearer | DigitalRedirectionResponse |

## Feedback
| Method | Path | Response |
|--------|------|----------|
| GET | /api/feedback/summary | FeedbackSummary (avg_rating, positive_%, top_topics, service_sentiment) |
| POST | /api/feedback/recommendation-outcome | RecommendationOutcome |
| POST | /api/feedback/analyze-comment?comment=&rating= | {sentiment, topics, score} |

## Live Events
| Method | Path | Response |
|--------|------|----------|
| POST | /api/live/events | {queue_length, prediction, websocket_broadcast} |
| GET | /api/live/events | List[LiveEventOut] |
| POST | /api/live/simulate-surge | SurgeResult with ML prediction |

## Regional Operations (Regional role only)
| Method | Path | Response |
|--------|------|----------|
| GET | /api/regional/branches | List[BranchOverview] |
| GET | /api/regional/load | List[BranchLoad] |
| GET | /api/regional/bottlenecks | List[BranchBottleneck] |
| GET | /api/regional/staffing | List[BranchStaffing] |

## Hybrid AI (Privacy-first)
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/hybrid-ai/health | Ollama + Gemini status |
| POST | /api/hybrid-ai/branch/full-analysis | Full 2-stage pipeline |
| POST | /api/hybrid-ai/branch/quick-risk | Local Ollama only |
| POST | /api/hybrid-ai/feedback/sentiment | Sentiment + Gemini insights |

## WebSocket
| Path | Auth | Events |
|------|------|--------|
| WS /ws/alerts?token=JWT | JWT in query | CONNECTED, SURGE_ALERT, BOTTLENECK_ALERT, STAFF_ALERT |

## Response Envelope
All responses: `{"success": bool, "data": <T>, "explanation": "str", "timestamp": "str"}`
