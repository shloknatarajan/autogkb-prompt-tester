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

## Field Definitions and Extraction Guidelines

### Variant/Haplotypes
- **Content**: The specific genetic variant studied
- **Extract**: SNP IDs (rs numbers), HLA alleles, star alleles, or genotype combinations
- **Examples**: HLA-B*35:08, rs1801272, UGT1A1*1, UGT1A1*28

### Gene
- **Content**: Gene symbol associated with the variant
- **Extract**: HGNC gene symbol
- **Examples**: HLA-B, CYP2A6, UGT1A1

### Drug(s)
- **Content**: Drug(s) that caused or were involved in the phenotype
- **Extract**: Drug names that triggered the adverse event or phenotype
- **Leave empty**: For disease susceptibility studies without drug involvement
- **Examples**: lamotrigine, sacituzumab govitecan, carbamazepine

### PMID
- **Content**: PubMed identifier for the article
- **Extract**: The PMID number from the article

### Phenotype Category
- **Content**: Type of phenotype or outcome studied
- **Valid values** (lowercase):
  - `toxicity` - Adverse drug reactions, side effects, drug-induced toxicity
  - `efficacy` - Treatment response, therapeutic outcomes
  - `metabolism/PK` - Pharmacokinetic parameters, drug levels
  - `dosage` - Dose requirements, dose-response relationships
  - `PD` - Pharmacodynamics
  - `other` - Disease susceptibility, traits not directly drug-related

### Significance
- **Content**: Statistical significance of the association
- **Valid values**:
  - `yes` - p < 0.05 or stated as significant
  - `no` - p >= 0.05 or explicitly non-significant
  - `not stated` - No statistical testing reported

### Notes
- **Content**: Key study details, statistics, methodology
- **Extract**: Relevant quotes showing statistical results or important context

### Sentence
- **Content**: Standardized description of the genetic-phenotype association
- **Format**: "[Variant] is [associated with/not associated with] [increased/decreased] [phenotype outcome] [drug context] [population context]"

### Alleles
- **Content**: Specific allele or genotype if different from main variant field
- **Examples**: *35:08, AA + AT, *1/*28 + *28/*28

### Specialty Population
- **Content**: Age-specific populations
- **Valid values**: Pediatric, Geriatric, or leave empty for general adult

### Metabolizer types
- **Content**: CYP enzyme phenotype when applicable
- **Valid values**: poor metabolizer, intermediate metabolizer, extensive metabolizer, ultrarapid metabolizer, deficiency

### isPlural
- **Content**: Grammar helper
- **Valid values**: "Is" (singular subjects), "Are" (plural)

### Is/Is Not associated
- **Content**: Direction of statistical association
- **Valid values** (exact match required):
  - `Associated with` - Positive association found
  - `Not associated with` - No association found

### Direction of effect
- **Content**: Whether the variant increases or decreases the phenotype
- **Valid values** (lowercase):
  - `increased` - Higher risk, more severe, greater likelihood
  - `decreased` - Lower risk, less severe, reduced likelihood
  - Leave null if no clear direction

### Side effect/efficacy/other
- **Content**: Modifier describing the type of effect
- **Valid values**:
  - `likelihood of` - Probability of outcome
  - `risk of` - Risk of adverse outcome
  - `severity of` - Severity of outcome
  - `age at onset of` - Age when outcome occurs

### Phenotype - CRITICAL FIELD WITH MANDATORY PREFIX

**CRITICAL**: Every phenotype MUST have a category prefix separated by colon.

**Format**: `[Category]:[Phenotype Name]`

**Category Prefixes (use exactly as shown):**
- `Side Effect:` - For adverse drug reactions, toxicity, side effects
- `Efficacy:` - For treatment response, survival outcomes
- `Disease:` - For disease conditions, susceptibility
- `Other:` - For other traits/conditions
- `PK:` - For pharmacokinetic measures

**Examples of CORRECT format:**
| Phenotype in Article | Correct Phenotype Field Value |
|---------------------|-------------------------------|
| Stevens-Johnson Syndrome | `Side Effect:Stevens-Johnson Syndrome` |
| Maculopapular Exanthema | `Side Effect:Maculopapular Exanthema` |
| Overall survival | `Efficacy:Overall survival` |
| Drug Hypersensitivity | `Disease:Drug Hypersensitivity` |
| Discontinuation (due to side effects) | `Side Effect:Discontinuation` |
| Neutropenia | `Side Effect:Neutropenia` |

**Multiple phenotypes** - Comma-separated, EACH with its own prefix:
- `Side Effect:Stevens-Johnson Syndrome, Side Effect:Toxic Epidermal Necrolysis`
- `Efficacy:Overall survival, Efficacy:Progression-free survival`
- `Side Effect:Neutropenia, Side Effect:Leukopenia, Side Effect:Diarrhea`

**Match Phenotype Category to Prefix:**
| Phenotype Category | Phenotype Prefix |
|-------------------|------------------|
| toxicity | Side Effect: |
| efficacy | Efficacy: |
| metabolism/PK | PK: |
| other | Disease: or Other: |
| dosage | Other: |

### Multiple phenotypes And/or
- **Content**: Logical connector for multiple phenotypes
- **Valid values**: "and", "or", or null
- Use "or" if any phenotype individually applies
- Use "and" if all phenotypes required together

### When treated with/exposed to/when assayed with - REQUIRED FOR DRUG STUDIES

**CRITICAL**: If Drug(s) field is populated, this field MUST be populated.

- **Valid values**:
  - `when treated with` - For therapeutic drug administration (DEFAULT)
  - `when exposed to` - For environmental or non-therapeutic exposure
  - `when assayed with` - For laboratory assay context
  - `due to` - For substance-related disorders

**Rule**: If Drug(s) is NOT empty → default to `when treated with`

Only leave null if Drug(s) field is also empty (non-drug phenotypes).

### Multiple drugs And/or
- **Content**: Logical connector for multiple drugs
- **Valid values**: "and" (combination therapy), "or" (any of the drugs), or null

### Population types
- **Content**: Description of study population
- **Valid values**: "in people with", "in children with", "in women with", etc.

### Population Phenotypes or diseases - WITH PREFIX
- **Content**: Disease/condition context with prefix
- **Format**: `[Category]:[Condition]`
- **Examples**:
  - `Disease:Epilepsy`
  - `Disease:Diabetes Mellitus, Type 2`
  - `Other:Lung Transplantation`

### Multiple phenotypes or diseases And/or
- **Content**: Logical connector for multiple population conditions
- **Valid values**: "and", "or", or null

### Comparison Allele(s) or Genotype(s)
- **Content**: Reference genotype for comparison
- **Examples**: TT (wild-type), *1/*1 (normal function allele)

### Comparison Metabolizer types
- **Content**: Reference metabolizer phenotype
- **Examples**: normal metabolizer, extensive metabolizer

## Complete Extraction Example

**From article text:**
"HLA-A*31:01 was significantly associated with carbamazepine-induced maculopapular exanthema (OR=5.2, P<0.001) in Japanese patients with epilepsy. Carriers showed increased risk compared to non-carriers."

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
  "Sentence": "HLA-A*31:01 is associated with increased likelihood of Maculopapular Exanthema when treated with carbamazepine in people with Epilepsy.",
  "Alleles": "*31:01",
  "Specialty Population": null,
  "Metabolizer types": null,
  "isPlural": "Is",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "increased",
  "Side effect/efficacy/other": "likelihood of",
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

## General Extraction Strategy

1. **Identify Phenotype Outcomes**: Look for adverse events, toxicities, disease conditions, clinical traits
2. **Find Genetic Associations**: Search for variants linked to the phenotype (may or may not involve drugs)
3. **Determine Drug Involvement**: Check if phenotype is drug-induced or related to disease susceptibility
4. **Extract Statistical Evidence**: Look for odds ratios, p-values, case reports, frequency differences
5. **Categorize Phenotype Type**: Classify as toxicity, efficacy, disease susceptibility, or other trait
6. **Apply Phenotype Prefix**: Match prefix to category (toxicity → Side Effect:)
7. **Note Population Context**: Identify specific patient populations, age groups, disease conditions

## Quality Validation Checklist

Before submitting your extraction, verify:

- [ ] **Phenotype has prefix**: Every phenotype has `Side Effect:`, `Efficacy:`, `Disease:`, etc.
- [ ] **Phenotype Category matches prefix**: toxicity → Side Effect:, efficacy → Efficacy:
- [ ] **When treated with populated**: If Drug(s) has value, this field has value
- [ ] **Direction of effect lowercase**: "increased" or "decreased", not capitalized
- [ ] **Is/Is Not exact match**: "Associated with" or "Not associated with" exactly
- [ ] **Multiple phenotypes have individual prefixes**: Each comma-separated phenotype has its own prefix
- [ ] **Population diseases have prefix**: "Disease:Epilepsy" not just "Epilepsy"

## Common Pitfalls to Avoid

1. **Don't forget phenotype prefix** - "Stevens-Johnson Syndrome" is WRONG, use "Side Effect:Stevens-Johnson Syndrome"
2. **Don't leave When treated with empty** - If Drug(s) is populated, default to "when treated with"
3. **Don't capitalize direction** - Use "increased" not "Increased"
4. **Don't mix prefixes** - Phenotype Category "toxicity" should have prefix "Side Effect:", not "Disease:"
5. **Don't omit prefix for multiple phenotypes** - Each phenotype in a comma-separated list needs its own prefix

## Now Extract

Read the provided PubMed article carefully and extract all phenotype annotations following the above guidelines. Return only the JSON output with all extracted entries.
