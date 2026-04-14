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

## 2026-03-08 - Accessible Tooltips for Keyboard Navigation
**Learning:** `<abbr>` tags and custom `.abbr-like` spans with `title` attributes act as tooltips, but by default, they are not accessible to keyboard users who navigate via the Tab key because they are not focusable.
**Action:** Always ensure you include `tabindex="0"` when wrapping acronyms or text in `<abbr>` or `.abbr-like` elements with `title` attributes. This enables keyboard-only users to focus the element and read the browser's native title tooltip, making the interface more accessible.

## 2026-03-14 - Visual Focus Indicators for Tooltips
**Learning:** Adding `tabindex="0"` to `<abbr>` tags and `.abbr-like` spans makes them focusable, but without a corresponding `:focus-visible` CSS style, keyboard-only users won't know which element has focus.
**Action:** Always provide clear `:focus-visible` styles (such as an outline) when adding `tabindex="0"` to text elements like `<abbr>` to ensure users can visually track their keyboard navigation.

## 2026-03-15 - Cleanup of Contextual Status Classes
**Learning:** Temporary feedback states (like success, warning, or error) applied via CSS classes (e.g., `.status-ok`, `.status-warn`) can remain "stuck" on reusable interactive elements if the reset logic only focuses on attributes and content. This leads to confusing UI where a button might show an error color even after returning to its default state.
**Action:** Always explicitly `classList.remove()` all contextual state classes when building a generic `resetButton()` or similar DOM restoration utility to guarantee a clean slate.

## 2026-03-16 - Confusing Hover States on Disabled Buttons
**Learning:** Disabled buttons (e.g., awaiting data) that still trigger CSS `:hover` states (like changing background color and glowing) provide conflicting UX signals, confusing users as the visual feedback implies interactivity while the cursor remains `not-allowed`.
**Action:** Always restrict active and hover states in CSS to `:not(:disabled)` (e.g., `button:hover:not(:disabled)`) so that disabled elements properly reflect their inactive status visually.

## 2026-03-20 - Actionable Error States
**Learning:** Generic error messages (like "Connection Lost") when an explicit user action is required (like entering an API key due to a 401 Unauthorized response) leave the user stranded without a clear path forward.
**Action:** Always provide specific, actionable feedback for known error states. If an authentication error occurs during background polling, provide an interactive, accessible button (with proper `aria-label`) right next to the error message to let the user immediately resolve the issue.

## 2026-03-21 - Keyboard Shortcut Tactile Feedback
**Learning:** When UI buttons are triggered programmatically via keyboard shortcuts (e.g., `btn.click()`), the browser does not natively apply the `:active` or `:hover` CSS pseudo-classes. This leaves keyboard power-users without the immediate tactile visual feedback that mouse users rely on.
**Action:** Always pair programmatic clicks from keyboard shortcuts with a temporary CSS class (e.g., `.keyboard-active`) that explicitly mirrors the `:active` and `:hover` button styling to ensure consistent, delightful tactile feedback across all input modalities.

## 2026-03-22 - Visual Discoverability of Tooltips
**Learning:** Data fragments with `title` attributes (like individual bytes in a hex dump) contain valuable contextual information but remain functionally invisible if they appear as static text. Users will not randomly hover over text unless there is a visual cue indicating interactivity.
**Action:** Always provide explicit visual cues (such as `cursor: help`, `transition`, and subtle `:hover` styling like a background change or outline) to text elements with `title` attributes so users know they can explore them for more details.

## 2026-03-23 - Keyboard Accessibility of Data Fragments Tooltips
**Learning:** Interactive data fragments with `title` attributes (like individual bytes in a hex dump) remain completely invisible to keyboard-only users who navigate via the Tab key because they are not focusable by default, even if visual hover cues exist.
**Action:** Always ensure you add `tabindex="0"` and explicitly share `:focus-visible` styles with the `:hover` pseudo-class for data fragments relying on native browser tooltips so keyboard users can navigate to them and visually track their focus.

## 2026-03-23 - Continuous Metrics and Screen Reader Spam
**Learning:** Placing rapidly updating continuous metrics (like a countdown timer or live voltage reading) inside `aria-live` regions causes continuous, overwhelming announcements, making the rest of the application unusable for screen reader users.
**Action:** Only use `aria-live` on status indicators that represent discrete state changes (like Mode, Comm Status, or Error events). For continuous, predictable metrics like a Watchdog Timer, rely on standard HTML semantic structures without live regions so users can consume the data on demand when navigating.

## 2026-03-24 - Blocking Prompts in Real-time Dashboards
**Learning:** Using blocking browser dialogs like `prompt()` for authentication (e.g., API Key entry) disrupts the user experience, especially in real-time dashboards with background polling. Furthermore, if an inline input replaces the prompt but isn't protected, the continuous polling loop will overwrite the DOM and steal focus while the user is typing.
**Action:** Always replace blocking `prompt()` dialogs with inline `<input>` elements. Crucially, when rendering inputs dynamically inside a polling loop, add a check (like `if (container.querySelector('input')) return;`) to ensure the input is not continuously overwritten, preserving user focus and input state.

## 2026-03-30 - Semantic Labels for Dynamic Inputs
**Learning:** When injecting dynamic inputs into the DOM (such as a fallback authentication prompt), appending loose text nodes beside the input creates orphaned form fields. Screen readers rely on explicit `<label>` associations to announce inputs correctly, and visual users benefit from an increased click target area.
**Action:** Always wrap text associated with dynamically generated inputs in a semantic `<label>` element with a matching `htmlFor` attribute. Do not use plain text nodes for input prompts.

## 2026-04-04 - aria-live Restraints with Interactive Elements
**Learning:** Injecting interactive elements (like a password input for an API key) directly into a container marked with `aria-live` causes a major accessibility issue. Every time the user types a character, the DOM updates, triggering the screen reader to repeatedly announce the entire contents of the live region, making it impossible to type securely or efficiently.
**Action:** Always dynamically remove `aria-live` and `aria-atomic` attributes from a container *before* injecting interactive inputs into it. Once the input resolves (e.g., returning to a static status message), restore the `aria-live` properties to ensure normal status updates continue to be announced.

## 2026-04-07 - Accessible Disabled Tooltips
**Learning:** Using the native HTML `disabled` attribute on an element completely removes it from the browser's accessibility tree and focus order. This means that if a disabled button has an important contextual `title` tooltip (e.g., explaining *why* it's disabled), screen reader and keyboard-only users will never be able to access that explanation.
**Action:** When a disabled interactive element contains an important tooltip, use `aria-disabled="true"` instead of the native `disabled` attribute. This allows the element to remain focusable so the tooltip can be read, while you manually enforce the disabled behavior via CSS (`cursor: not-allowed`, `pointer-events: none` or specific click handling) and JavaScript (returning early from click handlers).
## 2026-04-13 - Critical System Metrics Visual Warnings
**Learning:** Continuous metrics like a Watchdog Timer are often ignored until they fail if they remain a static color, defeating the purpose of a proactive dashboard.
**Action:** Always implement progressive visual warnings (e.g., adding a `.status-warn` class when approaching a critical threshold) for time-sensitive or critical system metrics to give users explicit, actionable time to react before a failure occurs.

## 2026-04-14 - Semantic Text Extraction for UI Logging
**Learning:** When dynamically extracting button text for UI logging (e.g. tracking what action the user performed), simply grabbing `Node.TEXT_NODE` elements will inadvertently drop semantic inline elements like `<abbr>`. Conversely, blindly using `element.textContent` will extract everything, including decorative, screen-reader-hidden hints (like a keyboard shortcut `.kbd` class). This leads to confusing UI logs for users (e.g., "Command 'Step +1s S' failed" or "Command 'Freeze ' sent").
**Action:** When extracting textual command names from composite UI elements, iterate over `childNodes` and explicitly filter: include `Node.TEXT_NODE` and standard `Node.ELEMENT_NODE`s, but exclude specific decorative element classes like `.kbd`. This ensures logs are clean, readable, and semantically complete.
