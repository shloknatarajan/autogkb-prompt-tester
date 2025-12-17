# Variant-Drug Association Extraction

You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

---

## RULE 1: Create SEPARATE Entries for Different Phenotypes

**CRITICAL**: Same variant can have MULTIPLE entries if it has findings for different outcomes.

### Example: rs3745274 (CYP2B6) with efavirenz

**Finding 1**: "No significant difference in CD4 T cell counts" (p > 0.05)
```json
{
  "Variant/Haplotypes": "rs3745274",
  "Phenotype Category": "Efficacy",
  "Significance": "no",
  "Is/Is Not associated": "Not associated with",
  "Direction of effect": null,
  "PD/PK terms": "response to"
}
```

**Finding 2**: "Significantly higher plasma efavirenz concentrations" (p < 0.0001)
```json
{
  "Variant/Haplotypes": "rs3745274",
  "Phenotype Category": "Metabolism/PK",
  "Significance": "yes",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "decreased",
  "PD/PK terms": "metabolism of"
}
```

---

## RULE 2: Phenotype Category - TITLE CASE

| Value | Use when |
|-------|----------|
| `Efficacy` | Clinical response, CD4 counts, viral suppression, tumor response |
| `Metabolism/PK` | Drug concentrations, AUC, clearance, plasma levels |
| `Dosage` | Dose requirements, dosing algorithms |
| `Toxicity` | Adverse events, side effects |
| `Other` | Other outcomes |

---

## RULE 3: Significance and Is/Is Not Associated Must Match

| Article says | Significance | Is/Is Not associated | Direction |
|-------------|--------------|---------------------|-----------|
| p < 0.05, "significant" | `yes` | `Associated with` | `increased` or `decreased` |
| p ≥ 0.05, "not significant", "NS" | `no` | `Not associated with` | `null` |
| No p-value given | `not stated` | Based on text | Based on text |

**INCLUDE NEGATIVE FINDINGS** - they are just as important as positive findings!

---

## RULE 4: Population Fields Decision

### Use Population Fields When:
- Study mentions specific patient diseases (HIV, cancer, atrial fibrillation, etc.)
- Example: "patients with atrial fibrillation" → `Population types: "in people with"`, `Population Phenotypes or diseases: "Disease:Atrial Fibrillation"`

### Set Population Fields to NULL When:
- Pure pharmacogenetic/dosing algorithm study
- Cohort described generically without specific disease in findings
- Example: "Caribbean Hispanic patients" in a dose algorithm study → `Population types: null`

---

## RULE 5: Variant/Haplotypes vs Alleles Field Format

### Variant/Haplotypes (INCLUDE gene prefix):
- rsID: `rs9923231`
- Star alleles: `CYP2C9*1, CYP2C9*2, CYP2C9*3` or `CYP4F2*1, CYP4F2*3`
- Metabolizer: `CYP2C19 intermediate metabolizer`

### Alleles Field (NO gene prefix):
- Genotypes: `TT`, `CT + TT`, `CC`
- Star alleles: `*3`, `*2 + *3 + *8`
- Diplotypes: `*10/*10 + *10/*41 + *1/*5`
- If using metabolizer phenotype: `null`

### Comparison (NO gene prefix):
- `*1`, `CC`, `GG + GT`, `*1/*1 + *1/*2`

---

## RULE 6: isPlural

| Subject | isPlural |
|---------|----------|
| Single genotype: `TT`, `*3` | `Is` |
| Single metabolizer | `Is` |
| Multiple with +: `CT + TT`, `*2 + *3` | `Are` |

---

## RULE 7: Direction of Effect Logic

### For Metabolism/PK:
- **Higher plasma levels** = `decreased` metabolism (drug stays in body longer)
- **Lower plasma levels** = `increased` metabolism (drug cleared faster)

### For Dosage:
- **Higher dose needed** = `increased`
- **Lower dose needed** = `decreased`

---

## RULE 8: PD/PK Terms

| Use | NOT |
|-----|-----|
| `dose of` | "dose requirements of" |
| `concentrations of` | "plasma concentrations of" |
| `metabolism of` | "metabolic rate of" |
| `response to` | "clinical response to" |

---

## RULE 9: Specialty Population

- Children/adolescents/youth: `Pediatric`
- Elderly/geriatric: `Geriatric`
- General adults: `null`

---

## Complete Examples

### Example A: Warfarin dosing with patients having specific diseases

```json
{
  "Variant Annotation ID": 1,
  "Variant/Haplotypes": "rs9923231",
  "Gene": "VKORC1",
  "Drug(s)": "warfarin",
  "Phenotype Category": "Dosage",
  "Significance": "yes",
  "Alleles": "CT + TT",
  "isPlural": "Are",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "decreased",
  "PD/PK terms": "dose of",
  "Population types": "in people with",
  "Population Phenotypes or diseases": "Disease:Atrial Fibrillation, Disease:Heart valve replacement",
  "Comparison Allele(s) or Genotype(s)": "CC"
}
```

### Example B: Warfarin dosing algorithm (no disease context)

```json
{
  "Variant Annotation ID": 1,
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

### Example C: Metabolism/PK study with pediatric population

```json
{
  "Variant Annotation ID": 1,
  "Variant/Haplotypes": "CYP2C19 intermediate metabolizer",
  "Gene": "CYP2C19",
  "Drug(s)": "escitalopram",
  "Phenotype Category": "Metabolism/PK",
  "Significance": "yes",
  "Alleles": null,
  "Metabolizer types": "intermediate metabolizer",
  "isPlural": "Is",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "increased",
  "PD/PK terms": "dose-adjusted trough concentrations of",
  "Specialty Population": "Pediatric",
  "Population types": "in children with",
  "Population Phenotypes or diseases": "Other:Depression, Other:Anxiety Disorders",
  "Comparison Metabolizer types": "normal metabolizer"
}
```

---

## Extraction Checklist

- [ ] Created SEPARATE entries for different Phenotype Categories (Efficacy vs Metabolism/PK vs Dosage)
- [ ] Included NEGATIVE findings (Significance: "no", Is/Is Not: "Not associated with")
- [ ] Phenotype Category is TITLE CASE
- [ ] Variant/Haplotypes has gene prefix for star alleles
- [ ] Alleles has NO gene prefix
- [ ] Comparison has NO gene prefix
- [ ] Population fields null ONLY when no disease context
- [ ] isPlural matches (Is for single, Are for multiple)
- [ ] Direction of effect correct for Metabolism/PK (higher levels = decreased metabolism)

Extract ALL variant-drug associations from the article.