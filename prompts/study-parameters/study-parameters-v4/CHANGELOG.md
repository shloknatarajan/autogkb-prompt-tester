# study-parameters-v4 Changelog

## Version: v4 (2025-12-02)

### Changes from `study-parameters-v2`

1. **Added Entry Granularity Section**
   - "ONE ENTRY PER VARIANT/ALLELE FROM TABLES" guidance
   - Table extraction strategy (scan all tables, extract each row)
   - Example patterns for when to create multiple entries

2. **Simplified Field Definitions**
   - Condensed some sections for clarity
   - Kept core decision tree for Characteristics Type

3. **Updated Validation Checklist**
   - Added granularity check

### Single File Test Results (PMC554812)

| Metric | v2 | v4 |
|--------|-----|-----|
| Entries Generated | 2 | 2 |
| Score | 8.8% | **10.7%** |
| Change | - | +1.9% |

### Why v4 Didn't Significantly Improve

The study-parameters granularity problem is **fundamentally different** from var-pheno:

**var-pheno granularity** (solved by v5):
- One entry per variant from association tables
- Clear pattern: Table row → Entry

**study-parameters granularity** (harder problem):
- Multiple entries from different control group comparisons
- Multiple entries from different analysis types (main vs sensitivity)
- Multiple entries from different haplotype definitions
- Requires understanding study design, not just extracting rows

For PMC554812, ground truth has 14 entries because:
1. Two control groups: "tolerant to allopurinol" vs "general population"
2. Multiple HLA haplotypes tested (B*5801, extended haplotype, etc.)
3. Different statistical comparisons within the same study

The model would need to understand that the same variant can have multiple study-parameters entries for different comparisons - this is study design comprehension, not table extraction.

### Recommendation

**NOT RECOMMENDED** - v2 performs better on full benchmark (54.7% vs TBD)

The granularity approach that worked for var-pheno doesn't directly transfer to study-parameters. A different approach would be needed:
- Explicit guidance about multiple control groups → multiple entries
- Examples showing same-variant-different-comparison patterns
- This may require more complex prompt engineering or model capability

### Files Changed

- `prompt.md` - Added granularity section from var-pheno-v5 approach
