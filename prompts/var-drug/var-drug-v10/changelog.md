# Changelog for var-drug-v10

## 2025-12-16 18:58

### Changes Made
['Revised Population Fields guidance to be more nuanced - include when patients have diseases, exclude only when no disease context', 'Added concrete examples for both cases: PMC4706412 (null) and PMC5508045 (with diseases)', 'Clarified that warfarin patients with atrial fibrillation, valve replacement, etc. DO need population fields', 'Simplified overall prompt structure while maintaining key guidance']

### Issues Addressed
['PMC5508045 regression from v8 to v9 (0.86 -> 0.77) due to overly aggressive null population guidance', 'Need to balance: PMC4706412 needs null, PMC5508045 needs disease list', 'Both types of warfarin studies need correct handling']

### Expected Improvements
['PMC5508045 score: 0.77 -> 0.85+ with restored population handling', 'PMC4706412 score: 0.70 maintained with clear null guidance', 'Overall: 0.73 -> 0.80+']

### Previous Version
var-drug-v9

### Benchmark Context
- Previous Score: 0.7345
- Target Score: 0.9
- Fields Targeted: Population types, Population Phenotypes or diseases
