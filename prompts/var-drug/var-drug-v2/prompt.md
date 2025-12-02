You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

## CRITICAL: Multiple Entries Per Association Type

**CREATE SEPARATE ENTRIES** for each distinct association type, even for the same variant:

### Different Phenotype Categories = Separate Entries
If a variant shows:
- Association with drug response (efficacy) → Entry 1
- Association with drug levels (metabolism/PK) → Entry 2
- No association with another outcome → Entry 3

**Example**: A study reports rs3745274 is:
1. NOT associated with CD4 response to efavirenz (efficacy) → Create entry with `"Significance": "no"`
2. Associated with increased efavirenz plasma levels (metabolism/PK) → Create separate entry with `"Significance": "yes"`

These are TWO separate annotations, not one.

## Variant/Haplotypes - STRICT PRIORITY ORDER

**CRITICAL**: Use the MOST SPECIFIC genetic identifier. NEVER use metabolizer descriptions when specific variants are available.

1. **rs numbers (rsID)** - ALWAYS prefer when available
   - Search article for "rs" followed by digits
   - Examples: rs4149056, rs1057910, rs9923231

2. **Star alleles** - For pharmacogene haplotypes
   - List ALL alleles tested in the study, comma-separated
   - Format: "CYP2C9*1, CYP2C9*2, CYP2C9*3" (include gene prefix)
   - Examples: "CYP4F2*1, CYP4F2*3", "SLCO1B1*1, SLCO1B1*5, SLCO1B1*15"

3. **HGVS notation** - Only if no rsID or star allele available
   - Examples: c.521T>C, G516T

4. **Metabolizer phenotype** - LAST RESORT ONLY
   - Use ONLY when the article does NOT mention specific alleles/genotypes
   - Use ONLY when the article explicitly groups by metabolizer status (IM, PM, EM, UM)
   - Format: "[Gene] [metabolizer type]"
   - Example: "CYP2C19 intermediate metabolizer"

**IMPORTANT**:
- If article mentions BOTH rsID and HGVS (e.g., "rs4149056 (c.521T>C)"), use rsID ONLY
- If article mentions star alleles (*1, *2, *3), use star alleles NOT "poor metabolizer"
- NEVER use "poor metabolizer" or "intermediate metabolizer" when specific alleles are listed

## Drug(s) - EXTRACT EXACT METABOLITES

**CRITICAL**: Extract the EXACT compound measured/studied, not just the parent drug.

| If article measures... | Extract as Drug(s) |
|------------------------|-------------------|
| Endoxifen levels | "endoxifen" (NOT tamoxifen) |
| Simvastatin acid concentrations | "simvastatin acid" |
| Active metabolite of clopidogrel | "clopidogrel active metabolite" |
| Parent drug tamoxifen | "tamoxifen" |

When multiple metabolites are measured individually, create separate entries.

## PD/PK Terms - USE EXACT TERMINOLOGY

**CRITICAL**: Match the exact terminology from the article:

| Article says... | Use PD/PK terms |
|-----------------|-----------------|
| "dose-normalized AUC" | "dose-normalized AUC of" |
| "dose-adjusted trough concentrations" | "dose-adjusted trough concentrations of" |
| "steady-state plasma levels" | "steady-state plasma levels of" |
| "clearance" | "clearance of" |
| "response to" | "response to" |
| "metabolism of" | "metabolism of" |
| Generic "concentrations" | "concentrations of" |

## Specialty Population - REQUIRED FOR CHILDREN

| Study population | Specialty Population value |
|-----------------|---------------------------|
| Children, pediatric, youth, adolescents | "Pediatric" |
| Elderly, geriatric, older adults | "Geriatric" |
| General adult population | null |

## Field Definitions

### Variant Annotation ID
- Unique integer, start from 1, increment for each entry

### Gene
- HGNC gene symbol (e.g., CYP2B6, CYP2C19, SLCO1B1)

### PMID
- PubMed identifier from article (REQUIRED)

### Phenotype Category (lowercase)
- `efficacy` - Treatment response, clinical outcomes
- `metabolism/PK` - Drug levels, pharmacokinetics, clearance, AUC
- `toxicity` - Adverse effects, side effects
- `dosage` - Dose requirements
- `other` - Other outcomes

### Significance
- `yes` - p < 0.05 or stated as significant
- `no` - p ≥ 0.05 or non-significant result
- `not stated` - No statistical test reported

### Notes
- Include p-values, effect sizes, concentration values
- Quote key findings with statistics

### Sentence
Format: "[Genotype/Metabolizer] is [associated with/not associated with] [increased/decreased] [PD/PK term] [drug] [population context] as compared to [comparison]."

Example: "Genotype TT is not associated with response to efavirenz in people with HIV Infections and Tuberculosis as compared to genotypes GG + GT."

### Alleles
- Exact alleles/genotypes: "TT", "*1/*28", "CC + CT"
- null if metabolizer phenotype is used

### Metabolizer types
- poor metabolizer, intermediate metabolizer, normal metabolizer, extensive metabolizer, ultrarapid metabolizer
- Use when study groups by metabolizer phenotype

### isPlural
- "Is" for singular, "Are" for plural

### Is/Is Not associated
- "Associated with" - Significant association found
- "Not associated with" - No significant association (include these entries!)

### Direction of effect
- "increased" or "decreased" (lowercase)
- null if no direction or not associated

### Multiple drugs And/or
- "and" for combination therapy studied together
- "or" for drugs studied individually
- null for single drug

### Population types
- "in people with", "in patients with", "in children with"

### Population Phenotypes or diseases
- Format with prefix: "Disease:HIV Infections", "Disease:Breast Neoplasms"
- Multiple: "Disease:HIV infectious disease, Disease:Tuberculosis"

### Multiple phenotypes or diseases And/or
- "and" or "or" for multiple conditions

### Comparison Allele(s) or Genotype(s)
- Reference genotype: "GG + GT", "*1/*1", "wild-type"
- REQUIRED when comparison is made

### Comparison Metabolizer types
- Reference metabolizer: "normal metabolizer", "extensive metabolizer"
- Use when comparing metabolizer phenotypes

## Extraction Strategy

1. **Find all rs numbers** in the article first
2. **Identify metabolizer-based studies** - look for IM, PM, EM, UM groupings
3. **Create separate entries** for each phenotype category (efficacy, metabolism/PK, etc.)
4. **Include negative findings** - "Not associated with" entries are important
5. **Match exact drug/metabolite** being measured
6. **Use precise PD/PK terminology** from the article
7. **Note pediatric/geriatric populations** in Specialty Population

## Quality Checklist

Before submitting, verify:
- [ ] Used rsID when available (not HGVS notation)
- [ ] Used star alleles (CYP2C9*1, CYP2C9*2) NOT metabolizer descriptions when alleles are mentioned
- [ ] Listed ALL star alleles tested in comma-separated format with gene prefix
- [ ] Only used metabolizer phenotype when NO specific alleles are mentioned in article
- [ ] Created separate entries for each phenotype category (efficacy vs metabolism/PK)
- [ ] Included "Not associated with" findings
- [ ] Used exact metabolite name (endoxifen, not tamoxifen)
- [ ] Used precise PD/PK terms from article
- [ ] Set Specialty Population to "Pediatric" for children studies
- [ ] Included PMID

Extract ALL variant-drug associations from the article following these guidelines.
