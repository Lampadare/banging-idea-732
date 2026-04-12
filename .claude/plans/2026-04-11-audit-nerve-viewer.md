<!-- audit-meta
commit: db617df
scope: blog/js/nerve-viewer.js
date: 2026-04-11
files: 1
-->

# Audit: nerve-viewer.js State Management

## Findings

### HIGH

1. **Material leak in updateElectrodeVisuals()** (line 413-426) — creates new MeshPhysicalMaterial every call via factory, never disposes old. Each onUpdate() leaks 8+ materials.
2. **Slider pipeline drift** (line 573-580) — slider handler has inline calls instead of onUpdate(), will silently drift.
3. **Custom mode retains old electrodes** (line 464-470) — switching to custom keeps preset electrodes, confusing UX.

### MEDIUM

4. **Reset doesn't clear electrodeMode** (line 599-607) — anode mode persists after reset.
5. **Reset re-applies current preset** (line 599-607) — should return to bipolar default.
6. **Hover mutates baseMat** (line 663-669) — emissive set directly on shared material in render loop.
7. **isDragging fires without pointer down** (line 624-629) — pointermove sets isDragging even when just hovering, causing click failures.
8. **Overlay CSS-only hide** (line 529-533) — no JS fallback if CSS class doesn't apply pointer-events.

### LOW

9. Glow sprite material mutated in place — not a bug currently.
10. Streamline disposal — clean, correct.

## Fix Plan

- [x] #1 Cache electrode materials instead of factory per call
- [x] #2 Replace slider inline pipeline with onUpdate()
- [x] #3 Clear activeElectrodes when entering custom mode
- [x] #4 Reset electrodeMode and mode button in reset handler
- [x] #5 Reset to bipolar instead of currentPreset
- [x] #6 Use separate hover emissive tracking instead of mutating baseMat
- [x] #7 Gate isDragging on isPointerDown flag
- [x] #8 Set overlay display:none in JS after transition
