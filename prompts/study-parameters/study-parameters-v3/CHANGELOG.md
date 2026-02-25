# study-parameters-v3 Changelog

## Version: v3 (2025-12-02)

### Changes from `study-parameters-v2`

1. **Priority Extraction Table**
   - Added structured decision flow for field extraction
   - Three-step process: Initial scan → Statistical extraction → Classification

2. **Enhanced Biogeographical Groups Mapping**
   - Expanded mapping table with more population terms
   - Added sub-categories for each group

3. **Step-by-Step Extraction Strategy**
   - More detailed guidance for finding statistical values
   - Emphasis on table extraction

### Benchmark Results

| Metric | v2 | v3 |
|--------|-----|-----|
| Score | 54.7% | 52.4% |
| Change | - | **-2.3%** |

### Analysis: Why v3 Underperformed

The additional complexity in v3 may have:
1. **Over-constrained** the model with too many detailed steps
2. **Increased confusion** with competing guidance
3. **Reduced flexibility** in handling edge cases

The simpler v2 approach with clear decision trees was more effective.

### Lesson Learned

More detailed instructions don't always lead to better results. Sometimes a cleaner, more focused prompt outperforms a comprehensive one.

### Recommended: NO (v2 performs better)
