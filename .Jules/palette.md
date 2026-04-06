## 2026-04-01 - Inline Validation Feedback for Dynamically Injected Inputs
**Learning:** When DOM elements like API key prompts are dynamically injected (e.g., during a 401 Unauthorized state), native HTML5 validation (`required`) often fails to trigger browser tooltips because the form is rarely wrapped in a standard `<form>` element or submitted synchronously. Failing silently when a user submits an empty input causes confusion and poor usability.
**Action:** Always implement explicit, inline validation feedback for dynamically injected inputs. Temporarily apply visual cues (like `.status-err`) and semantic states (`aria-invalid="true"`) to the input, provide an actionable error message (e.g., via the placeholder attribute), and immediately `focus()` the input so the user can correct the error without searching for it.

## 2024-03-04 - Semantic Acronym Tags for Complex Domains
**Learning:** Using semantic `<abbr title="...">` tags is a highly effective, low-effort way to improve both accessibility and usability in domain-specific interfaces (like aerospace). It provides built-in tooltips for new users and expands cryptic abbreviations for screen readers, reducing the cognitive load.
**Action:** Always check if industry-specific terms or acronyms can be wrapped in `<abbr>` tags, and provide a subtle visual cue (like a dotted underline) to hint that they are interactive.

## 2024-04-05 - Pausing aria-live When Injecting Form Inputs
**Learning:** When dynamically injecting interactive form inputs (like an API key prompt) into a container that has `aria-live` and `aria-atomic` attributes, screen readers will repeatedly read out the entire container's contents on every keystroke. This causes severe screen reader spam and a poor user experience.
**Action:** Always temporarily remove `aria-live` and `aria-atomic` attributes from a live region before injecting an inline input field, and restore them when returning to a static message.
