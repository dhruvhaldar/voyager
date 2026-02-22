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

## 2026-02-19 - Robust Button Feedback
**Learning:** Rapid interaction with feedback buttons often leads to race conditions (stuck state) if naive timeouts are used. Screen readers also miss visual text changes on buttons unless `aria-label` is updated.
**Action:** Always debounce state resets, use `data-*` attributes to store original state safely, and update `aria-label` temporarily to ensure accessible feedback.

## 2026-02-22 - CSS-First Design System
**Learning:** Injecting "glow" and status effects via JavaScript creates fragile code and violates strict CSPs.
**Action:** Migrated all visual feedback and SVG effects (like the CAN BUS glow) into a centralized CSS class system (`.bus-path`, `.val-highlight`). This ensures a premium aesthetic remains consistent and secure across all deployment environments.
