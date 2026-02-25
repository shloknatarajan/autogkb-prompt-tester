# Variant-Drug Association Extraction

You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

---

## CRITICAL RULES

### 1. Create SEPARATE Entries for Different Phenotype Categories

**ALWAYS create multiple entries** when a variant shows associations with different outcomes:

| Outcome Type | Phenotype Category | Example |
|-------------|-------------------|---------|
| CD4 response, viral load, treatment success | Efficacy | No association with CD4 response |
| Drug plasma levels, AUC, clearance | Metabolism/PK | Association with increased plasma levels |
| Dose requirements | Dosage | Association with decreased dose |
| Side effects, adverse reactions | Toxicity | Association with rash |

**Example from PMC2859392**: rs3745274 has TWO entries:
1. `Phenotype Category: "Efficacy"`, `Significance: "no"`, `Is/Is Not associated: "Not associated with"` (for CD4 response)
2. `Phenotype Category: "Metabolism/PK"`, `Significance: "yes"`, `Is/Is Not associated: "Associated with"` (for plasma levels)

### 2. Include NEGATIVE Findings (Significance: "no")

**Non-significant results are REQUIRED annotations**. Look for:
- p ≥ 0.05
- "no significant difference"
- "not associated"
- "no correlation"

These become entries with:
- `"Significance": "no"`
- `"Is/Is Not associated": "Not associated with"`
- `"Direction of effect": null`

---

## Phenotype Category - USE TITLE CASE

| Category | Use for | Examples |
|----------|---------|----------|
| **Efficacy** | Treatment response, clinical outcomes | CD4 response, viral suppression, tumor response |
| **Metabolism/PK** | Drug levels, pharmacokinetics | Plasma concentration, AUC, clearance, Cmax, Ctrough |
| **Dosage** | Dose requirements | Dose needed for INR, daily dose |
| **Toxicity** | Adverse effects | Rash, hepatotoxicity, CNS effects |
| **Other** | Other outcomes | |

---

## Variant/Haplotypes - SELECTION RULES

### Priority Order:
1. **rsID** → Use when article mentions rs numbers: `"rs3745274"`, `"rs9923231"`
2. **Star alleles** → List ALL tested with gene prefix: `"CYP2C9*1, CYP2C9*2, CYP2C9*3, CYP2C9*8"`
3. **Metabolizer phenotype** → ONLY when study groups by phenotype, NOT genotype: `"CYP2C19 intermediate metabolizer"`

### When to Use Metabolizer Phenotype:
Use `"[Gene] [metabolizer] metabolizer"` format ONLY when:
- Article explicitly groups results by IM, PM, NM, RM, UM status
- No individual genotype comparisons are made
- Example: "CYP2C19 metabolizer phenotype had a significant effect on AUC" → Use `"CYP2C19 intermediate metabolizer"`

---

## Alleles Field - EXACT GENOTYPE FORMAT

### Format for Genotype Combinations:
Use `+` to combine multiple genotypes:

| Ground Truth Example | Description |
|---------------------|-------------|
| `"TT"` | Single genotype |
| `"CT + TT"` | Two genotypes combined |
| `"*10/*10 + *10/*41 + *1/*5 + *2/*5 + *5/*10"` | Multiple star allele genotypes |
| `"AC + CC"` | Two genotypes for rs number |
| `"*2 + *3 + *8"` | Star alleles without genotype notation |

### When Alleles is null:
- Set to `null` when using Metabolizer types instead

---

## Comparison Allele(s) or Genotype(s) - REQUIRED

**Always include the reference/comparison group**:

| Study Says | Comparison Field |
|-----------|------------------|
| "compared to wild-type" | `"*1/*1"` or `"*1"` |
| "compared to GG genotype" | `"GG"` |
| "compared to TT or GT" | `"TT + GT"` or `"GG + GT"` |
| "compared to normal metabolizers" | Use `Comparison Metabolizer types: "normal metabolizer"` |
| "compared to *1/*1, *1/*2, *2/*2" | `"*1/*1 + *1/*2 + *2/*2"` |

---

## Population Types - GENDER-SPECIFIC

| Study Population | Population types |
|-----------------|------------------|
| Women only (breast cancer studies) | `"in women with"` |
| Men only | `"in men with"` |
| Children/adolescents/pediatric | `"in children with"` |
| General/mixed population | `"in people with"` |
| Patient population | `"in patients with"` |

**Check for gender-specific conditions:**
- Breast cancer → `"in women with"`
- Prostate cancer → `"in men with"`

---

## isPlural - Is vs Are

| Alleles/Variant Format | isPlural |
|-----------------------|----------|
| Single genotype: `"TT"`, `"*1/*1"` | `"Is"` |
| Single metabolizer: `"intermediate metabolizer"` | `"Is"` |
| Multiple combined: `"CT + TT"`, `"*2 + *3"` | `"Are"` |
| Multiple genotypes: `"*10/*10 + *10/*41 + *1/*5"` | `"Are"` |

---

## PD/PK Terms - EXACT PHRASES

| Article Language | PD/PK terms |
|-----------------|-------------|
| "dose of", "warfarin dose" | `"dose of"` |
| "plasma concentration", "drug levels" | `"concentrations of"` |
| "AUC", "area under curve" | `"AUC of"` |
| "dose-normalized AUC" | `"dose-normalized AUC of"` |
| "dose-adjusted trough concentrations" | `"dose-adjusted trough concentrations of"` |
| "clearance" | `"clearance of"` |
| "response to treatment" | `"response to"` |
| "metabolism" | `"metabolism of"` |

**DO NOT ADD EXTRA WORDS**: Use `"dose of"` NOT `"dose requirements of"`

---

## Drug(s) - Extract EXACT Compound

| Article Measures | Drug(s) Value |
|-----------------|---------------|
| Endoxifen levels (tamoxifen metabolite) | `"endoxifen"` |
| Parent drug tamoxifen | `"tamoxifen"` |
| Escitalopram pharmacokinetics | `"escitalopram"` |
| 4-hydroxytamoxifen | `"4-hydroxytamoxifen"` |

---

## Specialty Population

| Study Population | Specialty Population |
|-----------------|---------------------|
| Children, pediatric, adolescents, youth (ages 0-17) | `"Pediatric"` |
| Elderly, geriatric (65+) | `"Geriatric"` |
| Adults, general | `null` |

---

## Complete Field Reference

| Field | Type | Required | Values |
|-------|------|----------|--------|
| Variant Annotation ID | integer | Yes | Sequential from 1 |
| Variant/Haplotypes | string | Yes | rsID, star alleles with gene prefix, or metabolizer phenotype |
| Gene | string | Yes | HGNC symbol: CYP2B6, CYP2C19, VKORC1, etc. |
| Drug(s) | string | Yes | Exact drug/metabolite name |
| PMID | integer | Yes | PubMed ID from article |
| Phenotype Category | string | Yes | `"Efficacy"`, `"Metabolism/PK"`, `"Dosage"`, `"Toxicity"`, `"Other"` |
| Significance | string | Yes | `"yes"`, `"no"`, `"not stated"` |
| Notes | string | No | P-values, statistics, key findings |
| Sentence | string | Yes | Standardized sentence format |
| Alleles | string | No | Exact genotypes with + separator |
| Specialty Population | string | No | `"Pediatric"`, `"Geriatric"`, or null |
| Metabolizer types | string | No | `"intermediate metabolizer"`, `"poor metabolizer"`, etc. |
| isPlural | string | No | `"Is"` or `"Are"` |
| Is/Is Not associated | string | No | `"Associated with"` or `"Not associated with"` |
| Direction of effect | string | No | `"increased"`, `"decreased"`, or null |
| PD/PK terms | string | No | Exact phrase from list above |
| Multiple drugs And/or | string | No | `"and"`, `"or"`, or null |
| Population types | string | No | `"in people with"`, `"in women with"`, `"in children with"` |
| Population Phenotypes or diseases | string | No | `"Disease:Breast Neoplasms"`, `"Disease:HIV Infections"` |
| Multiple phenotypes or diseases And/or | string | No | `"and"`, `"or"`, or null |
| Comparison Allele(s) or Genotype(s) | string | No | Reference genotype |
| Comparison Metabolizer types | string | No | Reference metabolizer type |

---

## Sentence Format

Template:
`"[Variant/Genotype/Metabolizer] [is/are] [associated with/not associated with] [increased/decreased] [PD/PK term] [drug] [population context] as compared to [comparison]."`

Examples:
- `"Genotype TT is not associated with response to efavirenz in people with HIV Infections and Tuberculosis as compared to genotypes GG + GT."`
- `"CYP2C19 intermediate metabolizer is associated with increased dose-adjusted trough concentrations of escitalopram in children with Depression or Anxiety Disorders as compared to CYP2C19 normal metabolizer."`
- `"CYP2D6 *10/*10 + *10/*41 + *1/*5 + *2/*5 + *5/*10 are associated with decreased concentrations of endoxifen in women with Breast Neoplasms as compared to CYP2D6 *1/*1 + *1/*2 + *2/*2."`

---

## Extraction Checklist

Before submitting, verify:
- [ ] Created SEPARATE entries for different Phenotype Categories (Efficacy vs Metabolism/PK vs Dosage)
- [ ] Included all NEGATIVE findings (`Significance: "no"`, `Is/Is Not associated: "Not associated with"`)
- [ ] Phenotype Category uses TITLE CASE: `"Efficacy"`, `"Metabolism/PK"`, `"Dosage"`, `"Toxicity"`
- [ ] Used correct Population types (`"in women with"` for breast cancer, `"in children with"` for pediatric)
- [ ] isPlural matches allele format (`"Is"` for single, `"Are"` for multiple)
- [ ] Alleles format uses `+` separator: `"CT + TT"`, `"*10/*10 + *10/*41"`
- [ ] Comparison Allele(s) or Genotype(s) is populated when comparison exists
- [ ] Used exact PD/PK terms (`"dose of"` not `"dose requirements of"`)
- [ ] Drug(s) is exact compound measured (endoxifen, not tamoxifen when endoxifen is measured)
- [ ] Specialty Population is `"Pediatric"` for children/adolescent studies
- [ ] PMID is included

Extract ALL variant-drug associations from the article following these guidelines.