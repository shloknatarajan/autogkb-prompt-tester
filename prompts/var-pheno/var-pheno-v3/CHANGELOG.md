# var-pheno-v3 Changelog

## Version: v3 (2025-12-01)

### Changes from `improved-v2`

1. **MANDATORY Phenotype Prefix Format**
   - **Critical fix**: Added requirement for category prefix on all phenotypes
   - Format: `[Category]:[Phenotype Name]`
   - Categories: `Side Effect:`, `Efficacy:`, `Disease:`, `Other:`, `PK:`
   - Examples:
     - `Stevens-Johnson Syndrome` → `Side Effect:Stevens-Johnson Syndrome`
     - `Overall survival` → `Efficacy:Overall survival`

2. **"When treated with" Field Requirement**
   - Made field REQUIRED when Drug(s) is populated
   - Default value: `"when treated with"`
   - Other valid values: `"when exposed to"`, `"when assayed with"`, `"due to"`

3. **Complete Worked Example**
   - Added full JSON extraction example with all fields
   - Demonstrates correct prefix usage and field population

4. **Direction of Effect Standardization**
   - Emphasized lowercase requirement: `"increased"` or `"decreased"`
   - Added explicit "WRONG" vs "CORRECT" examples

### Benchmark Results

| Metric | Baseline (improved-v2) | v3 |
|--------|------------------------|-----|
| Score | 47.9% | **49.5%** |
| Improvement | - | **+1.6%** |

### Key Insights

- Phenotype prefix was the highest-impact fix
- Ground truth consistently uses prefixes like "Side Effect:", "Efficacy:"
- The "When treated with" field alignment improved sentence consistency

### Superseded by: var-pheno-v4 (better performance)
