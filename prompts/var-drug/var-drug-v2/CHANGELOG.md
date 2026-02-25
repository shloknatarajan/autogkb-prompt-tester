# var-drug-v2 Changelog

## Version: v2.1 (2025-12-02)

### Fix: Variant Format Priority Order

**Problem**: LLM was outputting "CYP2C9 poor metabolizer" instead of star alleles like "CYP2C9*1, CYP2C9*2, CYP2C9*3"

**Root Cause**: Previous prompt had "Metabolizer phenotype" as priority #2, but GT analysis showed:
- rsID: 19 entries (79%)
- Star alleles: 4 entries (17%)
- Metabolizer phenotype: 1 entry (4%)

**Fix**: Changed priority order to:
1. rsID (always prefer)
2. Star alleles (list ALL tested, comma-separated with gene prefix)
3. HGVS notation
4. Metabolizer phenotype (LAST RESORT - only when no specific alleles mentioned)

Added explicit warnings:
- "NEVER use metabolizer descriptions when specific variants are available"
- "If article mentions star alleles (*1, *2, *3), use star alleles NOT 'poor metabolizer'"

---

## Version: v2 (2025-12-02)

### Changes from `improved_v1`

1. **Multiple Entries Per Phenotype Category**
   - Added explicit guidance: same variant with different phenotype categories = separate entries
   - Example: efficacy (no association) vs metabolism/PK (association) = 2 entries

2. **Metabolizer Phenotype Format** (Note: Deprioritized in v2.1)
   - New format: "[Gene] [metabolizer type]" in Variant/Haplotypes field
   - Examples: "CYP2C19 intermediate metabolizer", "CYP2D6 poor metabolizer"
   - Use when study groups by metabolizer status, not specific genotypes

3. **Exact Metabolite Extraction**
   - Guidance to extract measured compound, not parent drug
   - "endoxifen" not "tamoxifen" when measuring endoxifen levels

4. **Precise PD/PK Terms**
   - Match exact terminology from article
   - "dose-adjusted trough concentrations of" not generic "concentrations of"

5. **Specialty Population**
   - Explicit guidance: "Pediatric" for children/youth/adolescents
   - "Geriatric" for elderly populations

6. **Include Negative Findings**
   - Emphasized creating entries for "Not associated with" results

### Single File Test Results

| PMCID | improved_v1 | var-drug-v2 | Change |
|-------|-------------|-------------|--------|
| PMC10880264 | ~20% | **83%** | +63% |
| PMC2859392 | 0% | 0% | No change* |
| PMC3584248 | ~20% | 0% | -20%** |

*PMC2859392: Article lacks rsID (uses G516T notation only), alignment fails regardless of prompt
**PMC3584248: Ground truth uses very specific star allele listing convention that differs from metabolizer phenotype approach

### Key Improvements

- **Metabolizer-based studies**: Now correctly extracts "CYP2C19 intermediate metabolizer" format
- **Pediatric populations**: Now correctly sets Specialty Population = "Pediatric"
- **Multiple entries**: Creates separate entries for different phenotype categories

### Known Limitations

1. **rsID mapping**: Cannot map HGVS notation (G516T) to rsID when article doesn't contain rsID
2. **Star allele conventions**: Ground truth sometimes expects specific star allele listings that differ from metabolizer phenotype descriptions

### Files Changed

- `prompt.md` - Complete rewrite with new guidance sections
