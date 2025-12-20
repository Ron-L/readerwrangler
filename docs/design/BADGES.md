# Badge System Design

**Feature**: Visual indicators on book covers
**Status**: In Development
**Created**: 2025-12-19

---

## Overview

Book covers display up to 3 badges showing key metadata at a glance:
- **Top-left**: Collections, Wishlist, or Selection status (mutually exclusive)
- **Top-right**: Rating
- **Bottom-right**: Read status checkmark

---

## Badge Specifications

### 1. Top-Left Corner (Mutually Exclusive)

**Priority order** (highest priority shown):
1. **Selection Checkmark** (when book is selected)
   - Blue circle with white checkmark
   - `className`: `absolute top-1 left-1 bg-blue-600 rounded-full w-6 h-6 flex items-center justify-center z-10`
   - Icon: SVG checkmark (white)

2. **Wishlist Badge** (when `book.isWishlist === true`)
   - Small badge with heart + plus icon (❤️+)
   - Background: Semi-transparent red/pink
   - `className`: `absolute top-1 left-1 bg-red-500 bg-opacity-80 rounded px-1.5 py-0.5 text-xs font-bold text-white`
   - Text: `❤+` (heart + plus sign overlaid)
   - Future: Gray out entire book cover when wishlist

3. **Collections Count** (when `book.collections.length > 0`)
   - Folder icon with count
   - `className`: `absolute top-1 left-1 bg-gray-700 bg-opacity-75 rounded px-1.5 py-0.5 text-xs font-bold text-white`
   - Text: `📁 ${count}` (e.g., "📁 3")

### 2. Top-Right Corner

**Rating Badge** (when `book.rating > 0`)
- Black background with yellow star and rating
- `className`: `absolute top-1 right-1 bg-black bg-opacity-75 rounded px-1.5 py-0.5 text-xs font-bold text-yellow-400`
- Text: `★ ${rating.toFixed(1)}` (e.g., "★ 4.5")
- **Status**: Already implemented

### 3. Bottom-Right Corner

**Read Status Checkmark** (when `book.readStatus === 'READ'`)
- Green circle with white checkmark
- `className`: `absolute bottom-1 right-1 bg-green-600 rounded-full w-6 h-6 flex items-center justify-center`
- Icon: SVG checkmark (white)
- **Replaces**: Previous diagonal "READ" ribbon

---

## Visual Layout

```
┌─────────────────┐
│ 📁3       ⭐4.5 │  ← Collections (owned) OR ❤+ (wishlist) OR ✓ (selected) | Rating
│                 │
│   Book Cover    │
│                 │
│              ✓  │  ← Read checkmark (green circle, white checkmark)
└─────────────────┘
```

---

## Badge States by Book Type

| Book Type | Top-Left | Top-Right | Bottom-Right |
|-----------|----------|-----------|--------------|
| Owned, unread, no collections | (none) | Rating (if >0) | (none) |
| Owned, read, no collections | (none) | Rating (if >0) | ✓ green |
| Owned, in collections | 📁 3 | Rating (if >0) | ✓ (if read) |
| Wishlist | ❤+ | Rating (if >0) | (none) |
| Selected (any type) | ✓ blue | Rating (if >0) | ✓ green (if read) |

---

## Implementation Notes

### Top-Left Priority Logic

```javascript
// Determine top-left badge
let topLeftBadge = null;

if (selectedBooks.has(book.id)) {
    topLeftBadge = 'selection'; // Blue checkmark
} else if (book.isWishlist) {
    topLeftBadge = 'wishlist'; // ❤+
} else if (book.collections && book.collections.length > 0) {
    topLeftBadge = 'collections'; // 📁 count
}
```

### Wishlist Icon Options

- **Chosen**: ❤+ (heart + plus sign, Option B)
- **Alternatives considered**:
  - A. ❤️🛒 (heart + cart) - too busy
  - C. ❤️✓ (heart + check) - confusing with "read"
  - D. 🛒 (just cart) - doesn't convey "wanted" feeling

### Read Status Badge

**Previous implementation**: Diagonal ribbon in SE corner with "READ" text
- CSS class: `.read-ribbon`
- Position: `bottom: 0; right: 0`

**New implementation**: Circular checkmark badge in SE corner
- Cleaner, less intrusive
- Consistent with selection checkmark style
- Easier to spot at a glance

---

## Future Enhancements

1. **Wishlist Gray-out Effect**: Full book cover opacity reduction when `isWishlist === true`
2. **Series Badge**: Potential badge for series position (e.g., "📚 2/5")
3. **New/Recent Badge**: For books acquired in last N days
4. **Custom Tags**: User-defined color-coded tags

---

## Related Files

- `readerwrangler.js` - Badge rendering logic (lines 2549-2596)
- `TODO.md` - Priority 1, #1 (Collections Integration UI)
- `TODO.md` - Priority 1, #3 (Wishlist Integration)
