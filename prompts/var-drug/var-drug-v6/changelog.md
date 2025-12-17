# Changelog for var-drug-v6

## 2025-12-16 18:22

### Changes Made
['Changed Phenotype Category to Title Case (Efficacy, Metabolism/PK, Dosage, Toxicity) to match ground truth', 'Added explicit CRITICAL RULE 1 for creating separate entries for different findings (significant + non-significant)', 'Added CRITICAL RULE 3 with decision table for Is/Is Not Associated + Significance logic', 'Added CRITICAL RULE 4 with table for Direction of effect in Metabolism/PK context (higher levels = decreased metabolism)', "Added explicit isPlural decision table (Is for singular, Are for plural with '+')", 'Added Population types decision table with gender/age specificity (in women with, in children with)', "Added examples of complex Alleles format with '+' notation", 'Added Comparison Allele(s) or Genotype(s) format examples', 'Restructured prompt with clear decision tables for each field', 'Updated schema enum for Phenotype Category to use Title Case']

### Issues Addressed
['PMC2859392 (score 0.0): Missing separate entries for efficacy (no) vs metabolism/PK (yes)', 'PMC10880264 (score 0.31): Metabolizer phenotype handling, Pediatric population, dose-adjusted trough concentrations', "Phenotype Category case mismatch: 'Dosage' vs 'dosage' (9 instances)", "Significance/Is/Is Not associated mismatch: 'yes'/'Associated' when should be 'no'/'Not associated' (6 instances)", "Population types: 'in women with' vs 'in people with' (10 instances)", 'Direction of effect interpretation for Metabolism/PK', "Complex Alleles format: '*10/*10 + *10/*41' extraction", 'Comparison Allele(s) extraction failures']

### Expected Improvements
Target 15-20% improvement by fixing: Phenotype Category capitalization (+5%), Is/Is Not associated logic (+5%), Direction of effect (+5%), Population types (+3%), isPlural (+2%)

### Previous Version
var-drug-v2

### Benchmark Context
- Previous Score: 0.6374
- Target Score: 0.8
- Fields Targeted: Phenotype Category, Is/Is Not associated, Significance, Direction of effect, isPlural, Population types, Alleles, Comparison Allele(s) or Genotype(s)
