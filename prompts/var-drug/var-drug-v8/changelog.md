# Changelog for var-drug-v8

## 2025-12-16 18:48

### Changes Made
['Simplified prompt structure with cleaner tables', 'Added explicit guidance for null Population types when no disease context', 'Clarified star allele format - gene prefix required for EACH allele', 'Simplified Direction of effect table with clear explanation', "Added explicit 'NOT this' column for PD/PK terms to prevent common errors", 'Streamlined isPlural table with more examples', 'Added clearer Alleles field guidance for star allele combinations vs diplotypes', 'Removed verbose explanations in favor of concise tables']

### Issues Addressed
['PMC4706412 (score 0.43): Warfarin dosing algorithm with no specific disease population - Population types should be null', 'PMC5508045: Similar warfarin dosing study issues', 'Star allele format inconsistencies', 'Population types being added when not needed', 'PD/PK terms mismatches (dose of vs dose requirements of)']

### Expected Improvements
['Population types accuracy for algorithm studies', 'Better star allele formatting with gene prefixes', 'Cleaner PD/PK term extraction', 'Overall score: 0.62 → 0.75+']

### Previous Version
var-drug-v7

### Benchmark Context
- Previous Score: 0.62
- Target Score: 0.9
- Fields Targeted: Population types, Alleles, Variant/Haplotypes, PD/PK terms, Direction of effect
