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

## 2026-03-01 - Destructive Action Safety
**Learning:** Reusing generic async button handlers for multi-step confirmations (like "Are you sure?") requires careful state management to prevent data loss (original label/text) and accessibility issues (stale aria-labels).
**Action:** Enhance generic handlers to support optional `restoreContent` and `restoreLabel` parameters, allowing complex interactions to piggyback on standard loading/error states without rewriting the wheel.

## 2026-03-02 - Smart Auto-Scrolling for Logs
**Learning:** Forcing auto-scroll on log containers interrupts users who are reading history to debug issues.
**Action:** Implement "Smart Auto-Scroll" that only scrolls to the bottom if the user was already at the bottom (within a small tolerance).

## 2026-03-03 - D3 SVG Accessibility
**Learning:** Complex D3 visualizations (like the CAN bus analyzer) generate many internal `<g>`, `<text>`, and `<path>` elements that create confusing noise for screen readers.
**Action:** Treat complex SVG charts as single accessible images by adding `role="img"` and a descriptive `aria-label` to the root `<svg>` element to suppress internal DOM noise.

## 2026-03-07 - Interactive SVG Keyboard Accessibility
**Learning:** Even with `role="img"` and `aria-label`, interactive or content-rich SVGs are completely invisible to keyboard-only users who navigate via the Tab key because SVGs are not focusable by default.
**Action:** Always add `tabindex="0"` to the root `<svg>` element of visualizations so keyboard users can navigate to them, and provide explicit `:focus-visible` CSS styles (e.g., an outline) so sighted keyboard users know when the SVG has focus.

## 2026-03-03 - [Dark Theme Contrast & Async Polling Feedback]
**Learning:** Secondary text colors like `#666` often fail WCAG AA contrast requirements (4.5:1) on very dark backgrounds (`#0b0c10`), achieving only ~3.4:1 contrast. Additionally, static "Waiting..." text during background polling operations can leave users uncertain if the system is still active or frozen.
**Action:** Always verify secondary "muted" text colors against their background. Use at least `#888` or `#999` on deep black/gray backgrounds to maintain accessibility while achieving visual hierarchy. For async polling states, add a subtle CSS opacity pulse animation to reassure users the system is actively listening.

## 2026-03-04 - Stale Attributes in Temporary States
**Learning:** Leaving `aria-busy="true"` and loading `title` attributes on buttons during temporary success/error feedback states (like "Done!") confuses screen readers and mouse users. Also, overriding `.className` in JS often accidentally strips crucial utility classes like `.pulse-text`.
**Action:** Always clean up `aria-busy` and loading tooltips *immediately* when an operation resolves, before showing the temporary success/error text. Use `classList.add()` instead of `className` assignments to preserve existing animations. Added a global CSS rule for `button[aria-busy="true"]` to ensure consistent visual loading feedback.

## 2026-03-05 - Contextual Tooltips in Data Displays
**Learning:** Complex raw data displays (like hex dumps or binary payloads) can be intimidating and hard to parse. However, adding visible labels inline clutters the interface and disrupts the density of the visualization.
**Action:** Use native `title` tooltips on individual data fragments (e.g., specific bytes in a hex dump) to provide contextual, on-demand explanations of what the data represents without compromising the clean, dense layout of technical data displays.

## 2026-03-05 - Multi-Step Confirmation for Destructive Actions
**Learning:** Destructive actions (like "Freeze OBC" or "Reboot") risk accidental triggering if they only require a single click. Relying on browser `confirm()` popups creates a disjointed user experience and breaks immersion. Furthermore, writing custom multi-step confirmations inline for each button duplicates complex logic (managing timeouts, saving/restoring DOM state, handling ARIA labels).
**Action:** Implement and use a reusable `setupConfirmAction(btnId, apiUrl, kbdShortcut, ariaLabel)` helper. This pattern provides in-place visual feedback (changing to a yellow "Confirm?" state with a keyboard hint) and gracefully restores the original DOM state and ARIA labels if the user doesn't confirm within the timeout, preventing accidental disruptions safely and accessibly.

## 2026-03-06 - Accessible Color Coding
**Learning:** Relying solely on hover `title` tooltips to explain color-coded data visualizations (like the hex dump) makes the meaning inaccessible to touch (mobile) and keyboard users, failing WCAG "Use of Color" criteria.
**Action:** Always provide a visible, static legend for color-coded data displays so that all users can understand the meaning without relying on precise pointer hover interactions.
