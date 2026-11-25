---
name: principle-separate-before-serializing-shared-state
description: "Apply when concurrent actors or synced replicas might write the same file, branch, key, record, or state object. Eliminate the sharing first; coordinate only the writes that must stay shared."
---

# Separate Before Serializing Shared State

When concurrent actors might write the same file, branch, key, or object, first ask whether they need one shared object or are publishing independent facts. Default to giving each actor its own file, key, branch, or state directory, and merge only where the state is read. Two workers writing their own field into one `state.json` is still shared mutation.

Only when one shared write target is a real invariant, serialize access structurally (a lockfile, a single writer, sequential phases, compare-and-swap). Instructions are not concurrency control, and "we need a lock" is a smell to check first.

A synced record can hold facts with different owners; keep those writes separate, and keep fields that must change together in one write. When replicas must edit the same fields, send each change with the value or revision it was based on, and accept it where the authoritative copy lives only if that base still matches. A check on the device alone misses an edit made elsewhere before the upload. On a conflict, keep the pending edit and tell the editor.
