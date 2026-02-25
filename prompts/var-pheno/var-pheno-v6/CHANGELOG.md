# var-pheno-v6 Changelog

## Version: v6 (2025-12-02)

### Major Addition: Task Selection Guidance

**Problem**: Analysis of PMC5561238 showed critical task mis-classification:
- Ground truth: 43 var_pheno entries, 0 var_drug entries
- LLM output: 13 var_pheno entries, 42 var_drug entries (after expansion)
- 23 of 30 missing var_pheno variants were incorrectly placed in var_drug

**Root Cause**: Neither prompt explained when to use var_pheno vs var_drug.

**Fix**: Added prominent "CRITICAL: var_pheno vs var_drug Task Selection" section at the top of the prompt with:

1. **Clear task definitions:**
   - var_pheno = variants associated with PHENOTYPES (side effects, adverse reactions)
   - var_drug = variants affecting DRUG METABOLISM/RESPONSE (PK, clearance, levels)

2. **Decision examples table:**
   | Scenario | Correct Task | Reason |
   |----------|--------------|--------|
   | HLA-B*57:01 + abacavir → hypersensitivity | var_pheno | Phenotype = hypersensitivity |
   | HLA-B*15:02 + carbamazepine → SJS/TEN | var_pheno | Phenotype = SJS |
   | CYP2D6*4 + codeine → reduced metabolism | var_drug | Drug metabolism affected |

3. **Rule of thumb**: "If the association involves HLA alleles and a clinical syndrome (hypersensitivity, SJS, DRESS), it belongs in var_pheno."

### Changes from v5

1. **Added task distinction section** (lines 5-35)
   - Explains what belongs in var_pheno vs var_drug
   - Provides concrete examples
   - Rule of thumb for quick decisions

2. **Updated validation checklist** to include:
   - [ ] HLA + drug + adverse reaction → var_pheno (this task)
   - [ ] CYP/transporter + drug + metabolism/PK → var_drug (different task)

3. **Added to common mistakes table:**
   - "Putting HLA+hypersensitivity in var_drug → Use var_pheno for phenotype associations"

4. **Updated "Now Extract" section** with reminder:
   - "This task is for PHENOTYPE associations (side effects, adverse reactions, hypersensitivity). Drug metabolism/PK associations belong in var_drug."

### Expected Impact

This should significantly improve recall for studies like PMC5561238 where HLA alleles are associated with drug-induced adverse reactions, which should be captured in var_pheno, not var_drug.
