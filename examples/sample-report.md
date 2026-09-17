# OpsPulse Incident Analysis

- **Source:** `examples/sample-production.log`
- **Generated:** 2026-09-17 10:52 UTC
- **Status:** **CRITICAL**
- **Health score:** **15/100**

## Executive summary

Analyzed **20 events**. Detected **7 errors**, **1 critical events**, and **3 warnings**.

## Severity distribution

| Level | Count |
|---|---:|
| DEBUG | 0 |
| INFO | 9 |
| WARNING | 3 |
| ERROR | 7 |
| CRITICAL | 1 |

## Spike detection

- Window: 5 minutes
- Peak window start: 2026-09-17T02:01:08Z
- Errors in peak window: 8
- Spike detected: Yes

## Top error signatures

| Count | Services | Normalized signature |
|---:|---|---|
| 4 | payment-api | `payment gateway timeout transaction_id=<id> upstream=<ip>` |
| 2 | order-service | `failed to confirm payment transaction_id=<id>` |
| 1 | payment-api | `circuit breaker opened after repeated upstream failures` |
| 1 | notification-service | `retry queue depth exceeded threshold request_id=<id>` |

## Recommended next actions

1. Correlate the peak window with deployments, infrastructure changes, and dependency alerts.
2. Review the repeated signature "payment gateway timeout transaction_id=<id> upstream=<ip>" in service(s): payment-api.
3. Escalate critical events and verify customer-facing impact, failover, and recovery status.
4. Check upstream dependencies, resource saturation, recent releases, and network connectivity.
5. Track warnings for capacity or degradation signals before closing the incident.

---
Generated locally by OpsPulse. Review for sensitive data before sharing.
