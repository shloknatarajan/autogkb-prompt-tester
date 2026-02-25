# var-pheno-v5 Changelog

## Version: v5 (2025-12-02)

### Changes from `var-pheno-v4`

1. **CRITICAL: Annotation Granularity Section**
   - Added explicit "ONE ANNOTATION PER VARIANT/HAPLOTYPE" rule
   - Added "WRONG vs CORRECT" example showing consolidated vs separate annotations
   - Added "Table Extraction Strategy" with 4-step process:
     1. Scan all tables for variant/allele data
     2. Extract each row as separate annotation
     3. Do not consolidate multiple variants
     4. Preserve exact allele format from table

2. **Table Pattern Examples**
   - Added explicit table showing HLA alleles with OR/CI/P-value
   - Listed common table patterns to extract:
     - HLA allele association tables
     - SNP/rsID association results tables
     - Star allele frequency tables
     - Genotype distribution tables

3. **Enhanced Validation Checklist**
   - Added "Annotation Granularity" section to checklist:
     - Each variant from tables has its own annotation
     - All variants listed in association tables are extracted

4. **Updated Common Mistakes**
   - Added: "Consolidating table variants into one annotation → Create separate annotation for each variant"

5. **Updated Final Instruction**
   - Now explicitly says: "Scan all tables for variant associations and extract each variant as a separate annotation"

### Motivation

Analysis of PMC5561238 revealed that ground truth has 43 separate annotations (one per HLA allele from Table 2), while LLM output had only 4 consolidated annotations. The data IS in the article markdown, but the model was consolidating variants instead of creating separate entries.

### Expected Impact

This change should significantly improve scores on articles with association tables that list multiple variants, like:
- PMC5561238 (43 HLA alleles in Table 2)
- Other HLA association studies
- Large SNP association tables

### Benchmark Results

| Metric | v4 | v5 |
|--------|-----|-----|
| Score | 54.7% | **64.4%** |
| Change | - | **+9.7%** |

### Key Insights

- The annotation granularity guidance had a major impact (+9.7%)
- Clear "WRONG vs CORRECT" examples helped the model understand the expected output format
- Table extraction instructions improved capture of HLA allele association data
- This is the best-performing var-pheno prompt version

### Files Changed

- `prompt.md` - Added annotation granularity section, table extraction strategy, updated validation checklist

### Recommended: YES (Best performing version)
