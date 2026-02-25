# Changelog for var-drug-v9

## 2025-12-16 18:53

### Changes Made
["Added explicit 'Population Fields Decision Tree' section", "Added 'CRITICAL' label for dosing algorithm studies having null population fields", 'Emphasized NO gene prefix in Alleles and Comparison fields with explicit tables', 'Added complete JSON example from PMC4706412 showing correct null population handling', "Updated schema descriptions to clarify 'NO gene prefix' for Alleles and Comparison", 'Reordered sections to put critical population guidance earlier']

### Issues Addressed
['PMC4706412 (score 0.46): Model incorrectly adding population context to dosing algorithm study', "Alleles field incorrectly including gene prefix (should be '*3' not 'CYP4F2*3')", "Comparison field incorrectly including gene prefix (should be '*1' not 'CYP2C9*1')", 'Confusion between Variant/Haplotypes format (needs gene prefix) vs Alleles format (no gene prefix)']

### Expected Improvements
['PMC4706412 score: 0.46 -> 0.75+ with correct null population handling', 'Overall score: 0.66 -> 0.80+']

### Previous Version
var-drug-v8

### Benchmark Context
- Previous Score: 0.6581
- Target Score: 0.9
- Fields Targeted: Population types, Population Phenotypes or diseases, Alleles, Comparison Allele(s) or Genotype(s)
