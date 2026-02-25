# var-pheno-v4 Changelog

## Version: v4 (2025-12-02)

### Changes from `var-pheno-v3`

1. **Phenotype Category ↔ Phenotype Prefix Alignment Table**
   - Added explicit mapping table:
     | Phenotype Category | Phenotype Prefix |
     |-------------------|------------------|
     | `toxicity` | `Side Effect:` |
     | `efficacy` | `Efficacy:` |
     | `metabolism/PK` | `PK:` |
     | `other` | `Disease:` or `Other:` |
     | `dosage` | `Other:` |
     | `PD` | `Other:` |
   - Ensures consistency between category and prefix

2. **Drug(s) ↔ When treated with Alignment**
   - Clear rule: If Drug(s) has ANY value → "When treated with" MUST have value
   - Default: `"when treated with"`

3. **Exact Value Requirements**
   - Direction of effect: LOWERCASE (`"increased"`, `"decreased"`)
   - Is/Is Not associated: EXACT case (`"Associated with"`, `"Not associated with"`)
   - Added "WRONG" vs "CORRECT" examples for each

4. **Enhanced Validation Checklist**
   - Pre-submission verification for field alignment
   - Format validation for exact values

5. **Common Mistakes Section**
   - Added table of common errors and corrections
   - Helps prevent systematic mistakes

### Benchmark Results

| Metric | Baseline | v3 | v4 |
|--------|----------|-----|-----|
| Score | 47.9% | 49.5% | **54.7%** |
| vs Baseline | - | +1.6% | **+6.8%** |
| vs Previous | - | - | **+5.2%** |

### Key Insights

- Field alignment between Phenotype Category and Phenotype prefix was crucial
- The alignment tables provided clear guidance that improved consistency
- Combined with v3's prefix requirement, this produced the best results

### Recommended: YES (Best performing version)
