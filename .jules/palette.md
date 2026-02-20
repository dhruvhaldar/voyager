## 2024-05-23 - System Status & Focus
**Learning:** Users can't distinguish between "no data changes" and "connection lost" in real-time dashboards without explicit status indicators.
**Action:** Always include a heartbeat/connection status indicator for websocket or polling-based interfaces.

**Learning:** Custom dark themes often strip default browser focus rings, leaving keyboard users lost.
**Action:** Always add `:focus-visible` styles when overriding button styles in custom themes.

## 2026-02-17 - Live FDIR Logs Accessibility
**Learning:** `role="log"` provides implicit `aria-live="polite"` and is semantic for scrolling log containers. Coupled with `tabindex="0"`, it ensures keyboard users can scroll through history.
**Action:** Use this pattern for all future scrolling status/log panels in the dashboard.

## 2026-02-18 - Micro-UX: Status Change Feedback
**Learning:** Static values updating in a dashboard are often missed by users (both sighted and blind). Combining `aria-live="polite"` with a subtle CSS flash animation ensures critical state changes (like Mode or Reboots) are noticed without being intrusive.
**Action:** Use a reusable `updateStatusValue()` helper that diffs values and applies a temporary `.status-changed` class for visual feedback, while `aria-live` handles the screen reader announcement.
