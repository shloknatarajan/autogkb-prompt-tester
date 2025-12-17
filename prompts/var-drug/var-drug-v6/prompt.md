# Variant-Drug Association Extraction

You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

---

## CRITICAL RULE 1: Create Separate Entries for Different Findings

**ALWAYS create separate annotation entries** when a study reports:
- Association with one outcome (e.g., plasma levels) AND no association with another (e.g., clinical response)
- Different phenotype categories (Efficacy, Metabolism/PK, Dosage, Toxicity)
- Significant AND non-significant findings for the same variant

### Example: rs3745274 and efavirenz
If a study reports:
1. **No association** with CD4 response (efficacy) → Entry 1: `Significance: "no"`, `Is/Is Not associated: "Not associated with"`
2. **Association** with plasma levels (metabolism/PK) → Entry 2: `Significance: "yes"`, `Is/Is Not associated: "Associated with"`

**These are TWO separate entries, not one.**

---

## CRITICAL RULE 2: Phenotype Category (TITLE CASE)

**Use exact Title Case values:**

| Category | When to use |
|----------|-------------|
| `Efficacy` | Treatment response, clinical outcomes, CD4 counts, viral load, tumor response |
| `Metabolism/PK` | Drug levels, plasma concentrations, AUC, clearance, half-life, Cmax, Ctrough |
| `Dosage` | Dose requirements, dose adjustments, dosing algorithms |
| `Toxicity` | Adverse effects, side effects, toxicity |
| `Other` | Outcomes not fitting above |

---

## CRITICAL RULE 3: Is/Is Not Associated + Significance Logic

**Decision Table:**

| Finding in article | Significance | Is/Is Not associated |
|-------------------|--------------|---------------------|
| p < 0.05, "significant", "associated with" | `yes` | `Associated with` |
| p ≥ 0.05, "no significant difference", "not associated" | `no` | `Not associated with` |
| No p-value or stats reported | `not stated` | Based on author's conclusion |

**WARNING**: Do NOT skip negative findings! Articles often report both significant AND non-significant results. Extract BOTH.

---

## CRITICAL RULE 4: Direction of Effect for Metabolism/PK

**For Metabolism/PK phenotype category:**

| Article describes | Direction of effect |
|-------------------|---------------------|
| Increased plasma levels/concentrations | `decreased` (slower metabolism → higher levels) |
| Decreased plasma levels/concentrations | `increased` (faster metabolism → lower levels) |
| Increased AUC, Cmax, half-life | `decreased` (metabolism) |
| Decreased clearance | `decreased` (metabolism) |
| Increased clearance | `increased` (metabolism) |

**Example**: "TT genotype had significantly higher plasma efavirenz levels" → `Direction of effect: "decreased"` (decreased metabolism leads to higher levels)

---

## Variant/Haplotypes - PRIORITY ORDER

1. **rsID** - ALWAYS prefer when available (e.g., rs3745274, rs9923231)
2. **Star alleles with gene prefix** - List ALL alleles tested
   - Format: `"CYP2D6*1, CYP2D6*2, CYP2D6*5, CYP2D6*10, CYP2D6*41"`
   - Include gene prefix for each allele
3. **Metabolizer phenotype** - ONLY when article does NOT specify alleles
   - Format: `"CYP2C19 intermediate metabolizer"`
   - Use when study groups patients by metabolizer status without specific genotypes

---

## Alleles Field - Genotype Combinations

**Format**: Use "+" to combine multiple genotypes being tested together

| Ground truth example | Meaning |
|---------------------|---------|
| `TT` | Single genotype |
| `CT + TT` | Two genotypes grouped together |
| `*10/*10 + *10/*41 + *1/*5 + *2/*5 + *5/*10` | Multiple diplotypes grouped |
| `*2 + *3 + *8` | Multiple alleles grouped |
| `null` | When using Metabolizer types instead |

---

## Comparison Allele(s) or Genotype(s)

**REQUIRED** when study compares to a reference group:

| Study compares to | Comparison Allele(s) or Genotype(s) |
|------------------|-------------------------------------|
| Wild-type GG genotype | `GG` |
| GG and GT combined | `GG + GT` |
| CYP2D6 *1/*1 reference | `*1/*1` |
| Multiple reference genotypes | `*1/*1 + *1/*2 + *2/*2` |
| Normal metabolizer | Use `Comparison Metabolizer types` instead |

---

## isPlural - Is vs Are

| Alleles/Metabolizer types | isPlural |
|--------------------------|----------|
| Single: `TT`, `*3`, `intermediate metabolizer` | `Is` |
| Multiple with "+": `CT + TT`, `*2 + *3 + *8` | `Are` |
| Diplotypes with "+": `*10/*10 + *10/*41` | `Are` |

---

## Population Types - Gender/Age Specificity

**Match the study population exactly:**

| Study population | Population types |
|-----------------|------------------|
| Women only (breast cancer, pregnancy) | `in women with` |
| Men only | `in men with` |
| Children, pediatric, youth, adolescents (≤17 years) | `in children with` |
| General/mixed adult population | `in people with` |
| Clinical patient population | `in patients with` |
| No specific disease context | `null` |

---

## Specialty Population

| Study population | Specialty Population |
|-----------------|---------------------|
| Children, pediatric, youth, adolescents | `Pediatric` |
| Elderly, geriatric, older adults | `Geriatric` |
| General adult population | `null` |

---

## Drug(s) - Exact Compound

Extract the EXACT compound measured:

| Article measures | Drug(s) value |
|-----------------|---------------|
| Endoxifen levels (tamoxifen metabolite) | `endoxifen` |
| Plasma efavirenz concentration | `efavirenz` |
| Escitalopram pharmacokinetics | `escitalopram` |
| Multiple metabolites separately | Create separate entries |

---

## PD/PK Terms - Match Article Terminology

| Article says | PD/PK terms |
|--------------|-------------|
| "dose", "dose requirement", "required dose" | `dose of` |
| "concentrations", "plasma concentrations" | `concentrations of` |
| "dose-adjusted trough concentrations" | `dose-adjusted trough concentrations of` |
| "dose-normalized AUC" | `dose-normalized AUC of` |
| "response to", "clinical response" | `response to` |
| "metabolism", "metabolized" | `metabolism of` |
| "clearance" | `clearance of` |

---

## Complete Field Reference

### Required Fields:
- **Variant Annotation ID**: Unique integer, starting from 1
- **Variant/Haplotypes**: rsID, star alleles with gene prefix, or metabolizer phenotype
- **Gene**: HGNC symbol (CYP2B6, CYP2C19, CYP2D6, VKORC1, etc.)
- **Drug(s)**: Exact drug or metabolite name
- **PMID**: PubMed ID from article
- **Phenotype Category**: `Efficacy`, `Metabolism/PK`, `Dosage`, `Toxicity`, `Other` (Title Case!)
- **Significance**: `yes`, `no`, `not stated`
- **Sentence**: Standardized summary sentence

### Conditional Fields:
- **Alleles**: Genotypes when NOT using metabolizer phenotype
- **Metabolizer types**: `poor metabolizer`, `intermediate metabolizer`, `normal metabolizer`, `extensive metabolizer`, `ultrarapid metabolizer`
- **Comparison Allele(s) or Genotype(s)**: Reference genotype for comparison
- **Comparison Metabolizer types**: Reference metabolizer status

### Sentence Construction:
- **isPlural**: `Is` (singular) or `Are` (plural)
- **Is/Is Not associated**: `Associated with` or `Not associated with`
- **Direction of effect**: `increased` or `decreased` (lowercase) or `null`
- **PD/PK terms**: Exact terminology from article
- **Multiple drugs And/or**: `and` or `or` or `null`
- **Population types**: `in people with`, `in women with`, `in children with`, etc.
- **Population Phenotypes or diseases**: `Disease:HIV Infections`, `Other:Depression`, etc.
- **Multiple phenotypes or diseases And/or**: `and` or `or` or `null`

### Optional:
- **Notes**: P-values, effect sizes, key statistics
- **Specialty Population**: `Pediatric`, `Geriatric`, or `null`

---

## Extraction Checklist

Before submitting, verify:
- [ ] Created SEPARATE entries for significant AND non-significant findings
- [ ] Phenotype Category uses Title Case: `Efficacy`, `Metabolism/PK`, `Dosage`, `Toxicity`
- [ ] Is/Is Not associated matches Significance (no → Not associated with)
- [ ] Direction of effect correct for Metabolism/PK (higher levels = decreased metabolism)
- [ ] Used rsID when available in article
- [ ] Star alleles include gene prefix: `CYP2D6*1, CYP2D6*2`
- [ ] Alleles use "+" for combinations: `CT + TT`
- [ ] isPlural correct: "Is" for singular, "Are" for plural
- [ ] Population types matches study population (women/children/people)
- [ ] Specialty Population set to "Pediatric" for youth studies
- [ ] Comparison Allele(s) or Genotype(s) included when applicable
- [ ] PMID included

Extract ALL variant-drug associations from the article following these guidelines.
