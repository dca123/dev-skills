---
name: error-message-review
description: Use when writing or revising form validation, warnings, or application failure messages.
---

# Write error messages

Write for someone who knows the workflow but has hit an unfamiliar state. Tell them what interrupted the action and what they can do next.

Trace the action, its outcome, what the user can see or change, and which recovery works. Check shared copy everywhere it appears. A field message can rely on a label that a summary must name. Flag unverified recovery for review instead of putting it in the message.

## Validation and warnings

State the requirement or mismatch. Let the visible label and value supply context. If the fix is apparent, explaining the rule is enough. Beside two editable dates, "End can't be before Start" identifies the problem without guessing which date is wrong.

Inline warnings can supply just the missing threshold when the value is visible. In a confirmation, name the value, the threshold, and what proceeding does if there is a consequence. A warning should not sound like a block.

## Application failures

Anchor the message in what the user tried, either in the heading or at the start of the message. If their work may be at risk or its status is unclear, say what you can confirm. Distinguish work that didn't save, work that saved but isn't visible yet, and a save the app couldn't confirm. Then state what blocked or interrupted the action; don't make the user infer it from the fix. Finish with the fix or when and where they can safely resume. Use this order as a starting point, not a sentence template.

## Recovery

Start from where the user is. Skip instructions for controls whose purpose is already clear on this screen. In the order the user will need them, give the details they must remember beyond this screen: any required preparation, the destination where recovery works, and the status or condition that makes the next action safe. Link to the destination if a direct link is available.

Use the terms the user knows from the workflow. Describe the state they need rather than how the app gets there: "once the updated settings are available in the app." Keep technical details that change what the user needs to do. Use the exact label for anything they need to recognize, and set it apart in plain text. If the user still needs to check the status, say "only if the status is 'Not received'" rather than writing as though the app confirmed it. Use the app's conventions; the message doesn't prescribe a component or style.

Reread the message in place. Cut anything the user doesn't need to understand what happened or take the next safe step.
