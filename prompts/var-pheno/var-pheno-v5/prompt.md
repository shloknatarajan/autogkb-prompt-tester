# Phenotype Association Annotation Guidelines

Article: \n\n{article_text}\n\n

## Output Format

Extract data according to this JSON structure:
```json
{
  "var_pheno_ann": [
    {
      "Variant Annotation ID": 1,
      "Variant/Haplotypes": "",
      "Gene": "",
      "Drug(s)": "",
      "PMID": "",
      "Phenotype Category": "",
      "Significance": "",
      "Notes": null,
      "Sentence": "",
      "Alleles": null,
      "Specialty Population": null,
      "Metabolizer types": null,
      "isPlural": null,
      "Is/Is Not associated": null,
      "Direction of effect": null,
      "Side effect/efficacy/other": null,
      "Phenotype": null,
      "Multiple phenotypes And/or": null,
      "When treated with/exposed to/when assayed with": null,
      "Multiple drugs And/or": null,
      "Population types": null,
      "Population Phenotypes or diseases": null,
      "Multiple phenotypes or diseases And/or": null,
      "Comparison Allele(s) or Genotype(s)": null,
      "Comparison Metabolizer types": null
    }
  ]
}
```

## CRITICAL: Annotation Granularity

**ONE ANNOTATION PER VARIANT/HAPLOTYPE**

When a table or text lists multiple variants/alleles with the same association, create a **SEPARATE annotation for EACH variant**.

### Example - Table Extraction

If the article contains a table like:

| HLA Allele | OR [95% CI] | P-value |
|------------|-------------|---------|
| HLA-B*35:05 | 2.32 [1.42-3.79] | 0.001 |
| HLA-B*51:01 | 2.32 [1.42-3.79] | 0.001 |
| HLA-B*67:01 | 2.32 [1.42-3.79] | 0.001 |

**WRONG** - Single consolidated annotation:
```json
{
  "Variant/Haplotypes": "HLA-B*35:05, HLA-B*51:01, HLA-B*67:01",
  "Gene": "HLA-B",
  ...
}
```

**CORRECT** - Three separate annotations:
```json
[
  {"Variant Annotation ID": 1, "Variant/Haplotypes": "HLA-B*35:05", "Gene": "HLA-B", ...},
  {"Variant Annotation ID": 2, "Variant/Haplotypes": "HLA-B*51:01", "Gene": "HLA-B", ...},
  {"Variant Annotation ID": 3, "Variant/Haplotypes": "HLA-B*67:01", "Gene": "HLA-B", ...}
]
```

### Table Extraction Strategy

1. **Scan all tables** in the article for variant/allele data
2. **Extract each row** as a separate annotation
3. **Do not consolidate** multiple variants into one entry
4. **Preserve the exact allele format** from the table (e.g., HLA-B*35:05, not just *35:05)

### CRITICAL: Expand Grouped Allele Notation

Tables often group alleles using parentheses notation. **EXPAND these into separate annotations.**

| Grouped Notation | Expand To |
|-----------------|-----------|
| HLA-B*51:(01/02) | HLA-B*51:01 AND HLA-B*51:02 (2 entries) |
| HLA-B*15:(01/12/24/25/27/32/35) | 7 separate entries: HLA-B*15:01, HLA-B*15:12, HLA-B*15:24, etc. |
| HLA-B*55:(01/02) | HLA-B*55:01 AND HLA-B*55:02 (2 entries) |
| HLA-C*04:(01/03/06/07) | 4 entries: HLA-C*04:01, HLA-C*04:03, HLA-C*04:06, HLA-C*04:07 |

**Example from table row:**
```
| Risk B07 alleles HLA-B*35:05, -B*39:10, -B*51:(01/02), -B*54:01 | 2.32 | 0.001 |
```
This becomes **5 separate annotations**:
1. HLA-B*35:05
2. HLA-B*39:10
3. HLA-B*51:01 (expanded from -B*51:(01/02))
4. HLA-B*51:02 (expanded from -B*51:(01/02))
5. HLA-B*54:01

### Common Table Patterns to Extract

- HLA allele association tables (expand grouped notation!)
- SNP/rsID association results tables
- Star allele (*1, *2, etc.) frequency tables
- Genotype distribution tables

## Critical Field Alignment Rules

**IMPORTANT**: Several fields must be aligned with each other for consistency.

### Phenotype Category ↔ Phenotype Prefix Alignment

| Phenotype Category | Phenotype Prefix | Example |
|-------------------|------------------|---------|
| `toxicity` | `Side Effect:` | `Side Effect:Stevens-Johnson Syndrome` |
| `efficacy` | `Efficacy:` | `Efficacy:Overall survival` |
| `metabolism/PK` | `PK:` | `PK:Drug clearance` |
| `other` | `Disease:` or `Other:` | `Disease:Drug Hypersensitivity` |
| `dosage` | `Other:` | `Other:Dose requirement` |
| `PD` | `Other:` | `Other:Response` |

### Drug(s) ↔ When treated with Alignment

| Drug(s) Value | When treated with Value |
|--------------|-------------------------|
| Has drug name(s) | **MUST have value** (default: `when treated with`) |
| Empty | Can be null |

## Field Definitions

### Variant/Haplotypes - STRICT FORMAT

**Use specific genetic identifiers ONLY. NEVER use metabolizer descriptions.**

**Priority order:**
1. **rs numbers (rsID)** - Always prefer: rs1801272, rs4149056
2. **Star alleles** - With gene prefix: CYP2D6*1, CYP2D6*2, UGT1A1*28
3. **HLA alleles** - Full format: HLA-B*35:08, HLA-A*31:01
4. **Genotype combinations** - Specific alleles: *1/*28, CC, TT

**NEVER use:**
- "poor metabolizer", "intermediate metabolizer", "extensive metabolizer"
- "slow metabolizers", "fast metabolizers"
- Generic descriptions like "variant carriers"

**If article groups by metabolizer status but lists specific alleles tested, use the star alleles:**
- WRONG: "poor or intermediate metabolizers"
- CORRECT: "CYP2D6*3, CYP2D6*4, CYP2D6*5, CYP2D6*6"

- **Extract EACH variant separately from tables**

### Gene
- HGNC gene symbol: HLA-B, CYP2A6, UGT1A1

### Drug(s)
- Drug names involved in the phenotype
- Empty for disease susceptibility studies without drug

### PMID
- PubMed identifier from the article

### Phenotype Category (LOWERCASE)
- **Valid values (exact, lowercase)**:
  - `toxicity` - Adverse drug reactions, side effects
  - `efficacy` - Treatment response, therapeutic outcomes
  - `metabolism/PK` - Pharmacokinetic parameters
  - `dosage` - Dose requirements
  - `PD` - Pharmacodynamics
  - `other` - Disease susceptibility, other traits

### Significance
- **Valid values**: `yes`, `no`, `not stated`

### Notes
- Key study details, statistics, quotes

### Sentence
- Standardized description of the association
- Format: "[Variant] is [associated with/not associated with] [direction] [phenotype] [drug context] [population]"

### Alleles
- Specific allele/genotype: *35:08, AA + AT, *1/*28

### Specialty Population
- Valid values: `Pediatric`, `Geriatric`, or null

### Metabolizer types
- Values: poor metabolizer, intermediate metabolizer, extensive metabolizer, ultrarapid metabolizer

### isPlural
- **Valid values (exact case)**: `Is`, `Are`, or null

### Is/Is Not associated - EXACT VALUES REQUIRED
- **Valid values (exact match)**:
  - `Associated with` - Positive association found
  - `Not associated with` - No association found
  - null - If unclear

### Direction of effect - LOWERCASE REQUIRED
- **Valid values (lowercase only)**:
  - `increased` - Higher risk, more severe
  - `decreased` - Lower risk, less severe
  - null - If no clear direction

**WRONG**: "Increased", "INCREASED"
**CORRECT**: "increased"

### Side effect/efficacy/other
- **Valid values**:
  - `likelihood of`
  - `risk of`
  - `severity of`
  - `age at onset of`
  - null

### Phenotype - MANDATORY PREFIX FORMAT

**CRITICAL**: Every phenotype MUST have a category prefix separated by colon.

**Format**: `[Category]:[Phenotype Name]`

**Prefixes:**
- `Side Effect:` - Adverse reactions, toxicity, side effects
- `Efficacy:` - Treatment response, survival outcomes
- `Disease:` - Disease conditions, susceptibility
- `Other:` - Other traits/conditions
- `PK:` - Pharmacokinetic measures

**Examples:**
| Raw Phenotype | Correct Format |
|--------------|----------------|
| Stevens-Johnson Syndrome | `Side Effect:Stevens-Johnson Syndrome` |
| Overall survival | `Efficacy:Overall survival` |
| Drug Hypersensitivity | `Disease:Drug Hypersensitivity` |
| Maculopapular Exanthema | `Side Effect:Maculopapular Exanthema` |
| Neutropenia | `Side Effect:Neutropenia` |
| Discontinuation | `Side Effect:Discontinuation` or `Efficacy:Discontinuation` |

**Multiple phenotypes** - Each with its own prefix:
- `Side Effect:Stevens-Johnson Syndrome, Side Effect:Toxic Epidermal Necrolysis`
- `Efficacy:Overall survival, Efficacy:Progression-free survival`

### Multiple phenotypes And/or
- `and` - All phenotypes together
- `or` - Any phenotype individually
- null - Single phenotype

### When treated with/exposed to/when assayed with - REQUIRED WHEN DRUG PRESENT
- **Valid values**:
  - `when treated with` - Drug therapy (DEFAULT)
  - `when exposed to` - Environmental exposure
  - `when assayed with` - Lab assay context
  - `due to` - Substance-related disorders
  - null - Only if Drug(s) is empty

**Rule**: If Drug(s) has ANY value → this field MUST have value (default: `when treated with`)

### Multiple drugs And/or
- `and` - Combination therapy
- `or` - Any of the drugs
- null - Single drug

### Population types
- Values: "in people with", "in children with", "in women with"

### Population Phenotypes or diseases - WITH PREFIX
- **Format**: `[Category]:[Condition]`
- Examples:
  - `Disease:Epilepsy`
  - `Disease:Diabetes Mellitus, Type 2`
  - `Other:Lung Transplantation`

### Multiple phenotypes or diseases And/or
- `and`, `or`, or null

### Comparison Allele(s) or Genotype(s)
- Reference genotype: TT, *1/*1, non-carriers

### Comparison Metabolizer types
- Reference metabolizer: normal metabolizer, extensive metabolizer

## Complete Extraction Example

**From article:**
"HLA-A*31:01 carriers showed significantly increased risk of carbamazepine-induced maculopapular exanthema (OR=5.2, P<0.001) compared to non-carriers in Japanese patients with epilepsy."

**Correct extraction:**
```json
{
  "Variant Annotation ID": 1,
  "Variant/Haplotypes": "HLA-A*31:01",
  "Gene": "HLA-A",
  "Drug(s)": "carbamazepine",
  "PMID": "12345678",
  "Phenotype Category": "toxicity",
  "Significance": "yes",
  "Notes": "OR=5.2, P<0.001. Carriers showed increased risk compared to non-carriers.",
  "Sentence": "HLA-A*31:01 is associated with increased risk of Maculopapular Exanthema when treated with carbamazepine in people with Epilepsy.",
  "Alleles": "*31:01",
  "Specialty Population": null,
  "Metabolizer types": null,
  "isPlural": "Is",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "increased",
  "Side effect/efficacy/other": "risk of",
  "Phenotype": "Side Effect:Maculopapular Exanthema",
  "Multiple phenotypes And/or": null,
  "When treated with/exposed to/when assayed with": "when treated with",
  "Multiple drugs And/or": null,
  "Population types": "in people with",
  "Population Phenotypes or diseases": "Disease:Epilepsy",
  "Multiple phenotypes or diseases And/or": null,
  "Comparison Allele(s) or Genotype(s)": "non-carriers",
  "Comparison Metabolizer types": null
}
```

## Validation Checklist

Before submitting, verify:

**Annotation Granularity:**
- [ ] Each variant from tables has its own annotation (NOT consolidated)
- [ ] All variants listed in association tables are extracted

**Field Alignment:**
- [ ] Phenotype Category `toxicity` → Phenotype prefix `Side Effect:`
- [ ] Phenotype Category `efficacy` → Phenotype prefix `Efficacy:`
- [ ] Drug(s) has value → "When treated with" has value

**Exact Values:**
- [ ] Direction of effect: `increased` or `decreased` (lowercase)
- [ ] Is/Is Not associated: `Associated with` or `Not associated with` (exact)
- [ ] Phenotype Category: `toxicity`, `efficacy`, etc. (lowercase)

**Prefixes:**
- [ ] Phenotype has prefix: `Side Effect:...`, `Efficacy:...`, etc.
- [ ] Population Phenotypes has prefix: `Disease:...`, `Other:...`

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Consolidating table variants into one annotation | Create separate annotation for each variant |
| `"Stevens-Johnson Syndrome"` | `"Side Effect:Stevens-Johnson Syndrome"` |
| `"Increased"` | `"increased"` |
| `"associated with"` | `"Associated with"` |
| Drug present but "When treated with" empty | Add `"when treated with"` |
| `Phenotype Category: "Toxicity"` | `"toxicity"` |

## Now Extract

Read the provided PubMed article carefully. **Scan all tables** for variant associations and extract **each variant as a separate annotation**. Follow the above guidelines and return only the JSON output with all extracted entries.
