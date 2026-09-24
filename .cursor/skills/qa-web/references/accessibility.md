# Focused accessibility checks

Use for changed interactive UI or an agreed accessibility slice. Identify the
app state, browser/OS, input method and assistive technology actually available.
Apply the team's conformance target when supplied; do not infer a complete audit
scope from a request to test one form.

1. Navigate the real journey with the keyboard. Record focus order and visible
   focus, operation with the control's native keys, and whether focus is lost or
   trapped after dialogs, route changes or validation. Test escape/return behavior
   against the component's intended interaction pattern.
2. Inspect each changed control's accessible name, role and state in the runtime
   tree. Check labels, required/error relationships and whether errors identify
   how to recover. A source attribute alone does not prove the computed name.
3. Trigger loading, validation, failure and success states. Verify visible status
   and programmatic exposure. Inspecting a live-region attribute is structural
   evidence; actual announcements need a supported screen-reader session.
4. Where layout is affected, inspect the selected viewport and zoom/reflow state
   for clipped controls/content. For contrast, measure the actual foreground and
   background combination against the applicable requirement; screenshots alone
   are not a contrast measurement.
5. If an automated scanner is available, run it on the relevant states and retain
   the raw findings/version. Confirm reported issues and keep manual observations
   alongside them; zero findings applies only to the scanned rules and states.

In the parcel lab, verify keyboard reach and operation of Quantity and Place
order, visible focus, the exposed input label, and the success status/Receipt
after submission. Record browser evidence and any screen-reader capability gap.
This limited exercise does not establish WCAG conformance.

[W3C's evaluation overview](https://www.w3.org/WAI/test-evaluate/) explains the
need to combine tools with knowledgeable human evaluation. Preserve untested
assistive-technology and state coverage in the ticket instead of turning a clean
scan into a conformance claim.
