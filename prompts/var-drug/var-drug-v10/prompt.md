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

## Population Fields - When to Include vs Exclude

### INCLUDE Population Fields When:
- Study enrolls patients with specific diseases/conditions
- Examples: HIV patients, breast cancer patients, patients with atrial fibrillation

### Determine Population types:

| Study Population | Population types |
|-----------------|------------------|
| Women with breast cancer | `in women with` |
| Children with depression/anxiety | `in children with` |
| People with HIV/TB | `in people with` |
| Patients with heart conditions (AF, valve replacement) | `in people with` |
| Patients with various indications | `in people with` |

### Use NULL Population Fields ONLY When:
- Pure pharmacogenetic algorithm development study with NO disease context
- Study cohort described only as "warfarin patients" without specific conditions
- Example: PMC4706412 - algorithm for "Caribbean Hispanic patients" without disease specified in findings

---

## Variant/Haplotypes Field

### Priority Order:
1. **rsID** when available: `rs9923231`, `rs1057910`
2. **Star alleles with gene prefix for EACH allele**: `CYP2C9*1, CYP2C9*2, CYP2C9*3, CYP2C9*8`
3. **Metabolizer phenotype**: `CYP2C19 intermediate metabolizer`

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
| p ≥ 0.05, "not significant" | `no` | `Not associated with` |
| No statistics | `not stated` | Based on author conclusion |

**Include BOTH positive AND negative findings!**

---

## isPlural - Is vs Are

| Subject | isPlural |
|---------|----------|
| Single: `TT`, `*3`, `intermediate metabolizer` | `Is` |
| Multiple with +: `CT + TT`, `*2 + *3 + *8` | `Are` |

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

---

## Specialty Population

| Population | Value |
|-----------|-------|
| Children, pediatric, adolescents | `Pediatric` |
| Elderly, geriatric | `Geriatric` |
| Adults | `null` |

---

## Example 1: PMC4706412 (Dosing Algorithm - No Disease Context)

```json
{
  "Variant/Haplotypes": "CYP4F2*1, CYP4F2*3",
  "Alleles": "*3",
  "Comparison Allele(s) or Genotype(s)": "*1",
  "Population types": null,
  "Population Phenotypes or diseases": null
}
```

## Example 2: PMC5508045 (Patients with Specific Conditions)

```json
{
  "Variant/Haplotypes": "rs9923231",
  "Alleles": "CT + TT",
  "Comparison Allele(s) or Genotype(s)": "CC",
  "Population types": "in people with",
  "Population Phenotypes or diseases": "Disease:Atrial Fibrillation, Disease:Heart valve replacement, Disease:Pulmonary Hypertension, Disease:Pulmonary Embolism, Disease:Venous Thrombosis"
}
```

---

## Extraction Checklist

- [ ] Separate entries for different Phenotype Categories
- [ ] Phenotype Category in TITLE CASE
- [ ] Variant/Haplotypes: star alleles HAVE gene prefix
- [ ] Alleles: NO gene prefix
- [ ] Comparison: NO gene prefix
- [ ] Population fields: Include when patients have specific diseases
- [ ] Population fields: NULL only when no disease context
- [ ] isPlural matches subject plurality
- [ ] Included negative findings

Extract ALL variant-drug associations from the article.