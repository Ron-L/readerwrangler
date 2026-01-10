# Responsive Filter Panel Design

**Status**: Design
**Created**: 2026-01-09
**Complexity**: LOW/LOW (2-4 hours)
**Problem**: Filter panel consumes ~200px of vertical space (nearly 20% of viewport on 1080p), reducing visible book area.

---

## Overview

Redesign the filter panel to use responsive grid layout with inline labels, reducing vertical footprint while maintaining full functionality.

---

## Current State

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🔍 Search                    📖 Read Status              ⭐ Rating      │  <- Labels row
│ [Title or author...    ]     [All Status         ▼]     [All Ratings ▼]│  <- Fields row
│ 📁 Collection                📚 Series                   ❤️ Wishlist    │  <- Labels row
│ [All Collections      ▼]     [All Series         ▼]     [All Books   ▼]│  <- Fields row
│ 🔑 Ownership                                                            │  <- Label row
│ [All Types            ▼]                                                │  <- Field row
│ 📅 Acquisition Date - From                 📅 Acquisition Date - To     │  <- Labels row
│ [mm/dd/yyyy                    📅]         [mm/dd/yyyy              📅] │  <- Fields row
│ Showing: 2349 of 2349 books  ☑️ Show Hidden                [Clear All] │  <- Status row
└─────────────────────────────────────────────────────────────────────────┘

Total: ~200px vertical height (8-9 rows of content)
```

### Problems

1. **Labels above fields** - Each label consumes its own row
2. **Fixed 3-column layout** - Doesn't utilize wide screens
3. **Date pickers span full width** - Could be smaller
4. **Ownership alone on its row** - Wasted space

---

## Proposed Design

### Visual Layout (Wide Screen, >1200px)

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ 🔍[Title or author] 📖[All Status▼] ⭐[All Ratings▼] 📁[All Collections▼] 📚[All Series▼] │
│ ❤️[All Books▼] 🔑[All Types▼] 📅[From date  📅] 📅[To date    📅]  [Clear All Filters] │
│ Showing: 2349 of 2349 books  ☑️ Show Hidden                                        │
└───────────────────────────────────────────────────────────────────────────────────┘

Total: ~80px vertical height (2 rows of fields + 1 status row)
```

### Visual Layout (Medium Screen, 800-1200px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍[Title or author    ] 📖[All Status    ▼] ⭐[All Ratings▼]        │
│ 📁[All Collections  ▼] 📚[All Series     ▼] ❤️[All Books  ▼]        │
│ 🔑[All Types        ▼] 📅[From      📅] 📅[To        📅]            │
│ Showing: 2349 of 2349 books  ☑️ Show Hidden        [Clear All Filters] │
└─────────────────────────────────────────────────────────────────────┘

Total: ~120px vertical height (3 rows of fields + 1 status row)
```

### Visual Layout (Narrow Screen, <800px)

```
┌─────────────────────────────────┐
│ 🔍[Title or author...        ] │
│ 📖[All Status              ▼] │
│ ⭐[All Ratings             ▼] │
│ 📁[All Collections         ▼] │
│ 📚[All Series              ▼] │
│ ❤️[All Books               ▼] │
│ 🔑[All Types               ▼] │
│ 📅[From date            📅]  │
│ 📅[To date              📅]  │
│ Showing: 2349  ☑️ Show Hidden  │
│              [Clear All Filters] │
└─────────────────────────────────┘

Stacked for mobile/narrow windows
```

---

## Key Changes

### 1. Inline Labels with Icons

Instead of:
```
📖 Read Status
[All Status ▼]
```

Use:
```
📖[All Status ▼]
```

- Icon serves as visual label
- Placeholder text shows default/current value
- Tooltip on hover shows full label name (accessibility)
- `aria-label` attribute for screen readers

### 2. Responsive CSS Grid

```css
.filter-panel {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 8px;
    padding: 8px;
}

.filter-field {
    min-width: 180px;
    max-width: 300px;
}

/* Search field can be wider */
.filter-field.search {
    min-width: 200px;
    max-width: 400px;
}

/* Date fields can be narrower */
.filter-field.date {
    min-width: 140px;
    max-width: 180px;
}
```

### 3. Compact Date Pickers

Current date pickers are full-width. Reduce to ~150px each:
- `📅[mm/dd/yyyy 📅]` format
- Side by side on medium+ screens

### 4. Status Row Consolidation

Keep status row at bottom but make it compact:
```
Showing: 2349 of 2349 books  ☑️ Show Hidden  [Clear All Filters]
```

---

## Accessibility Considerations

| Element | Accessibility Feature |
|---------|----------------------|
| Icons as labels | `aria-label` on each field with full label text |
| Placeholders | Not relied upon for labeling (use `aria-label`) |
| Keyboard nav | Tab order preserved left-to-right, top-to-bottom |
| Screen readers | "Read Status filter, All Status selected" |
| Tooltips | Show full label on hover/focus |

---

## Space Savings

| Screen Width | Current Height | Proposed Height | Savings |
|--------------|----------------|-----------------|---------|
| >1200px (wide) | ~200px | ~80px | **60%** |
| 800-1200px (medium) | ~200px | ~120px | **40%** |
| <800px (narrow) | ~300px (stacked) | ~280px | ~7% |

Primary benefit is on wide screens where vertical space is most valuable for seeing books.

---

## Implementation Steps

### Phase 1: CSS Grid Layout (1-2 hours)
1. Replace fixed 3-column flexbox with CSS Grid `auto-fit`
2. Set `minmax()` widths for each field type
3. Test at various viewport widths

### Phase 2: Inline Labels (1-2 hours)
1. Move labels into field containers (icon + field)
2. Add `aria-label` attributes
3. Add tooltip on hover showing full label
4. Remove separate label rows from JSX

### Phase 3: Polish (30 min)
1. Adjust spacing/padding
2. Test keyboard navigation
3. Test screen reader announcements

---

## Files to Modify

- `readerwrangler.js` - Filter panel JSX structure
- `readerwrangler.css` - Grid layout, field sizing

---

## Open Questions

1. **Icon-only vs Icon+Text**: Should we show "📖 Status" or just "📖" with tooltip?
   - Recommendation: Icon-only on wide screens, icon+text on narrow (via CSS)

2. **Collapse behavior**: Keep existing "Filters ▼" toggle?
   - Recommendation: Yes, for users who want maximum book space

3. **Filter chips for active filters**: Show active filters as dismissible chips below panel?
   - Recommendation: Future enhancement, not in initial scope

---

## Related Files

- `readerwrangler.js` - Lines ~800-950 (filter panel rendering)
- `readerwrangler.css` - Filter styling

---

## Mockup Reference

Before (current):
- 8 visual rows, ~200px height
- Labels consume 4 rows
- Fixed 3-column layout

After (proposed):
- 3 visual rows on wide screens, ~80px height
- Labels inline with fields
- Responsive 5-6 columns on wide screens
