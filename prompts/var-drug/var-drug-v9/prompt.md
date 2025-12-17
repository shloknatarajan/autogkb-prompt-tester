# Variant-Drug Association Extraction

You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

---

## CRITICAL: Create SEPARATE Entries for Different Phenotypes

When a variant has findings for multiple outcomes, create separate entries:

| If article reports | Create entry with |
|-------------------|-------------------|
| Association with plasma levels | Phenotype Category: "Metabolism/PK", Significance: "yes" |
| No association with treatment response | Phenotype Category: "Efficacy", Significance: "no" |
| Association with dose requirements | Phenotype Category: "Dosage", Significance: "yes" |

---

## Phenotype Category - TITLE CASE REQUIRED

| Value | Use when |
|-------|----------|
| `Efficacy` | Clinical response, treatment outcomes, CD4 counts, viral suppression |
| `Metabolism/PK` | Drug concentrations, AUC, clearance, plasma levels, half-life |
| `Dosage` | Dose requirements, dosing algorithms, dose predictions |
| `Toxicity` | Adverse events, side effects |
| `Other` | Other outcomes |

---

## CRITICAL: Population Fields Decision Tree

### Step 1: Is this a dosing algorithm/prediction study?
Dosing algorithm studies (developing warfarin dose prediction models, dose refinement algorithms, etc.) do NOT have disease-specific populations.

**If YES (dosing algorithm study)**:
- `Population types`: `null`
- `Population Phenotypes or diseases`: `null`

**If NO (disease treatment study)**:
- Proceed to Step 2

### Step 2: What population is studied?

| Study Population | Population types | Population Phenotypes or diseases |
|-----------------|------------------|-----------------------------------|
| Women with breast cancer | `in women with` | `Disease:Breast Neoplasms` |
| Children with depression/anxiety | `in children with` | `Other:Depression, Other:Anxiety Disorders` |
| People with HIV/TB | `in people with` | `Disease:HIV infectious disease, Disease:Tuberculosis` |
| Patients with atrial fibrillation | `in people with` | `Disease:Atrial Fibrillation` |
| General population, no specific disease | `null` | `null` |

### Examples:
- **PMC4706412**: Warfarin dosing algorithm study → `Population types: null`, `Population Phenotypes or diseases: null`
- **PMC3584248**: Endoxifen in breast cancer patients → `Population types: "in women with"`, `Population Phenotypes or diseases: "Disease:Breast Neoplasms"`

---

## Variant/Haplotypes Field

### Priority Order:
1. **rsID** when available: `rs9923231`, `rs1057910`
2. **Star alleles with gene prefix for EACH allele**: `CYP2C9*1, CYP2C9*2, CYP2C9*3, CYP2C9*8`
3. **Metabolizer phenotype**: `CYP2C19 intermediate metabolizer`

### Star Allele Format in Variant/Haplotypes:
- **Include gene prefix for EACH allele**
- Comma-separated
- Example: `"CYP4F2*1, CYP4F2*3"` NOT `"*1, *3"`

---

## Alleles Field - NO Gene Prefix

**The Alleles field contains BARE genotypes/alleles WITHOUT gene prefix.**

| What's tested | Alleles value |
|--------------|---------------|
| TT genotype | `TT` |
| CT and TT combined | `CT + TT` |
| CYP4F2*3 allele | `*3` (NOT "CYP4F2*3") |
| Multiple variant alleles | `*2 + *3 + *8` |
| Multiple diplotypes | `*10/*10 + *10/*41 + *1/*5` |
| Metabolizer phenotype | `null` (use Metabolizer types instead) |

---

## Comparison Allele(s) or Genotype(s) - NO Gene Prefix

**Comparison also uses BARE genotypes/alleles WITHOUT gene prefix.**

| Reference group | Comparison value |
|----------------|------------------|
| Wild-type *1 | `*1` (NOT "CYP2C9*1") |
| CC genotype | `CC` |
| Multiple reference genotypes | `*1/*1 + *1/*2 + *2/*2` |
| GG and GT combined | `GG + GT` |

---

## Significance and Association Logic

| Article finding | Significance | Is/Is Not associated |
|----------------|--------------|---------------------|
| p < 0.05, "significant" | `yes` | `Associated with` |
| p ≥ 0.05, "not significant", "NS" | `no` | `Not associated with` |
| No statistics | `not stated` | Based on author conclusion |

**Include BOTH positive AND negative findings!**

---

## isPlural - Is vs Are

| Subject | isPlural |
|---------|----------|
| Single: `TT`, `*3`, `intermediate metabolizer` | `Is` |
| Multiple with +: `CT + TT`, `*2 + *3 + *8` | `Are` |
| Multiple diplotypes: `*10/*10 + *10/*41` | `Are` |

---

## Direction of Effect

| Phenotype Category | Article finding | Direction |
|-------------------|-----------------|-----------|
| Metabolism/PK | Higher plasma levels/AUC | `decreased` (metabolism) |
| Metabolism/PK | Lower plasma levels/AUC | `increased` (metabolism) |
| Dosage | Higher dose required | `increased` |
| Dosage | Lower dose required | `decreased` |

---

## PD/PK Terms - Exact Phrases

| Correct | Incorrect |
|---------|-----------|
| `dose of` | "dose requirements of" |
| `concentrations of` | "plasma concentrations of" |
| `metabolism of` | "metabolic rate of" |

---

## Drug(s) - Exact Compound

Use the exact compound measured/studied:
- `endoxifen` (not tamoxifen, when endoxifen is measured)
- `warfarin`
- `escitalopram`

---

## Specialty Population

| Population | Value |
|-----------|-------|
| Children, pediatric, adolescents | `Pediatric` |
| Elderly, geriatric | `Geriatric` |
| Adults | `null` |

---

## Complete Example: PMC4706412 (Warfarin Dosing Algorithm)

```json
{
  "Variant/Haplotypes": "CYP4F2*1, CYP4F2*3",
  "Gene": "CYP4F2",
  "Drug(s)": "warfarin",
  "Phenotype Category": "Dosage",
  "Significance": "yes",
  "Alleles": "*3",
  "isPlural": "Is",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "increased",
  "PD/PK terms": "dose of",
  "Population types": null,
  "Population Phenotypes or diseases": null,
  "Comparison Allele(s) or Genotype(s)": "*1"
}
```

---

## Extraction Checklist

- [ ] Separate entries for different Phenotype Categories
- [ ] Phenotype Category in TITLE CASE
- [ ] Variant/Haplotypes: star alleles HAVE gene prefix (`CYP2C9*1, CYP2C9*2`)
- [ ] Alleles: NO gene prefix (`*2 + *3 + *8`)
- [ ] Comparison: NO gene prefix (`*1`)
- [ ] Population fields NULL for dosing algorithm studies
- [ ] isPlural matches subject (Is for single, Are for multiple)
- [ ] PD/PK terms exact (`dose of` not `dose requirements of`)
- [ ] Included negative findings

Extract ALL variant-drug associations from the article.