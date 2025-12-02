# study-parameters-v2 Changelog

## Version: v2 (2025-12-01)

### Changes from `improved_v1`

1. **Characteristics Type Decision Tree**
   - Added explicit priority-based classification:
     1. Drug name present → `"drug"`
     2. Disease/condition present → `"disease"`
     3. Age group present → `"age group"`
     4. Gender present → `"gender"`
     5. Otherwise → `"Study Cohort"`
   - Prevents misclassification of drug-containing entries as "Study Cohort"

2. **P-Value Format Specification**
   - Emphasized exact format: `"= 0.025"` (operator + space + number)
   - Added format examples table

3. **Biogeographical Groups Mapping**
   - Added clear mapping table for population terms to standard values
   - Chinese/Japanese/Korean → "East Asian"
   - European/Caucasian/White → "European"

4. **Validation Checklist**
   - Added pre-submission verification steps
   - Format validation for P-value, confidence intervals
   - Consistency checks for statistical measures

### Benchmark Results

| Metric | Baseline (improved_v1) | v2 |
|--------|------------------------|-----|
| Score | 51.2% | **54.7%** |
| Improvement | - | **+3.5%** |

### Key Insights

- The Characteristics Type decision tree significantly improved classification accuracy
- P-value space formatting matched ground truth expectations
- This version performs better than v3 (which had lower scores)

### Recommended: YES (Best performing version)
