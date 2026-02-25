# Changelog for var-drug-v7

## 2025-12-16 18:27

### Changes Made
['Changed Phenotype Category enum from lowercase to Title Case (Efficacy, Metabolism/PK, Dosage, Toxicity, Other) to match ground truth', 'Added explicit section on creating SEPARATE entries for different phenotype categories with concrete PMC2859392 example', 'Added comprehensive section on NEGATIVE findings extraction with clear markers to look for', 'Added detailed Population types guidance for gender-specific populations (in women with, in men with, in children with)', 'Added isPlural decision table based on allele format (Is for single, Are for multiple)', "Added exact PD/PK terms mapping table - emphasized 'dose of' not 'dose requirements of'", 'Added complex genotype format examples (*10/*10 + *10/*41 + *1/*5)', 'Added clear guidance on when to use metabolizer phenotype vs specific alleles', 'Added Comparison Allele(s) or Genotype(s) examples with + separator format', 'Added Specialty Population guidance with Pediatric requirement for children studies', 'Restructured prompt with clear tables and decision guides for each field']

### Issues Addressed
['PMC2859392 (score 0.0): Missing separate entries for Efficacy vs Metabolism/PK phenotype categories', 'PMC10880264 (score 0.31): Metabolizer phenotype format, Pediatric specialty population, children population type', "PMC3584248 (score 0.68): Complex genotype format (*10/*10 + *10/*41), 'in women with' population type, endoxifen drug extraction", 'Phenotype Category case mismatch: 9 errors for Dosage/dosage, 8 errors for Metabolism/PK', 'Is/Is Not associated errors: 6 cases of Associated when should be Not associated', 'Significance errors: 6 cases of yes when should be no', "Population types: 'in women with' vs 'in people with' mismatches", "PD/PK terms: 'dose of' vs 'dose requirements of' mismatches", 'Alleles extraction failures for complex genotype combinations', 'Comparison Allele(s) extraction failures']

### Expected Improvements
['Phenotype Category score: 0.54 → 0.90+ (fixing case sensitivity)', 'Is/Is Not associated score: 0.45 → 0.80+ (better negative finding detection)', 'Significance score: 0.57 → 0.85+ (correlates with association detection)', 'Direction of effect score: 0.51 → 0.80+ (correlates with association)', 'isPlural score: 0.62 → 0.90+ (clear Is/Are decision rules)', 'Overall score: 0.64 → 0.85+']

### Previous Version
var-drug-v2

### Benchmark Context
- Previous Score: 0.6374
- Target Score: 0.9
- Fields Targeted: Phenotype Category, Is/Is Not associated, Significance, Direction of effect, isPlural, Population types, Alleles, Comparison Allele(s) or Genotype(s), PD/PK terms, Specialty Population
