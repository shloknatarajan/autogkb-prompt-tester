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

**Example**: rs3745274 in efavirenz study with BOTH:
- No significant effect on CD4 response → Entry 1: Efficacy, Significance "no", Is/Is Not "Not associated with"
- Significantly higher plasma levels → Entry 2: Metabolism/PK, Significance "yes", Is/Is Not "Associated with"

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

## Significance and Association Logic

| Article finding | Significance | Is/Is Not associated |
|----------------|--------------|---------------------|
| p < 0.05, "significant", "correlated" | `yes` | `Associated with` |
| p ≥ 0.05, "no significant", "not correlated", "NS" | `no` | `Not associated with` |
| No statistics reported | `not stated` | Based on author conclusion |

**Extract BOTH positive AND negative findings!**

---

## Variant/Haplotypes Field

### Priority Order:
1. **rsID** when available: `rs9923231`, `rs1057910`, `rs2108622`
2. **Star alleles with gene prefix**: `CYP2C9*1, CYP2C9*2, CYP2C9*3, CYP2C9*8` or `CYP4F2*1, CYP4F2*3`
3. **Metabolizer phenotype** ONLY when study groups by phenotype: `CYP2C19 intermediate metabolizer`

### Star Allele Format:
- Include gene prefix for EACH allele
- Comma-separated list of ALL alleles studied
- Example: `"CYP2C9*1, CYP2C9*2, CYP2C9*3, CYP2C9*8"` (not just `"*1, *2, *3, *8"`)

---

## Alleles Field - Genotype/Allele Being Tested

Format depends on what's being compared:

| Study compares | Alleles value |
|---------------|---------------|
| TT genotype vs others | `TT` |
| CT and TT combined vs CC | `CT + TT` |
| Star allele diplotypes combined | `*10/*10 + *10/*41 + *1/*5 + *2/*5 + *5/*10` |
| Individual star alleles (not diplotypes) | `*2 + *3 + *8` |
| Metabolizer phenotype used | `null` (use Metabolizer types field instead) |

---

## Comparison Allele(s) or Genotype(s) - REQUIRED

| Study reference group | Comparison value |
|----------------------|------------------|
| CC genotype | `CC` |
| GG and GT combined | `GG + GT` |
| Wild-type *1 allele | `*1` |
| Multiple reference diplotypes | `*1/*1 + *1/*2 + *2/*2` |

---

## isPlural - Is vs Are

| Subject | isPlural |
|---------|----------|
| Single genotype: `TT`, `AA` | `Is` |
| Single metabolizer: `intermediate metabolizer` | `Is` |
| Single star allele: `*3` | `Is` |
| Multiple with +: `CT + TT`, `*2 + *3 + *8` | `Are` |
| Multiple diplotypes: `*10/*10 + *10/*41` | `Are` |

---

## Population Types - Match Study Context

| Study population | Population types |
|-----------------|------------------|
| Women only (breast cancer) | `in women with` |
| Men only | `in men with` |
| Children/adolescents/youth | `in children with` |
| Mixed/general with disease | `in people with` |
| No specific disease context | `null` |

**Important**: If article is a dosing algorithm study without specific patient disease mentioned, use `null`.

---

## Direction of Effect for Metabolism/PK

| Article describes | Direction of effect | Explanation |
|------------------|---------------------|-------------|
| Higher plasma levels, increased AUC | `decreased` | Decreased metabolism → higher levels |
| Lower plasma levels, decreased AUC | `increased` | Increased metabolism → lower levels |
| Higher dose required | `increased` | In Dosage category |
| Lower dose required | `decreased` | In Dosage category |

---

## PD/PK Terms - Exact Phrases

| Use this | NOT this |
|----------|----------|
| `dose of` | "dose requirements of", "required dose of" |
| `concentrations of` | "plasma concentrations of" |
| `metabolism of` | "metabolic rate of" |
| `response to` | "clinical response to" |

---

## Specialty Population

| Study population | Specialty Population |
|-----------------|---------------------|
| Children, pediatric, youth, adolescents | `Pediatric` |
| Elderly, geriatric | `Geriatric` |
| Adults, general | `null` |

---

## Drug(s) - Exact Compound Measured

| Article measures | Drug(s) |
|-----------------|---------|
| Endoxifen concentrations | `endoxifen` |
| Tamoxifen parent drug | `tamoxifen` |
| Escitalopram PK | `escitalopram` |
| Warfarin dosing | `warfarin` |

---

## Field Reference

### Required:
- **Variant Annotation ID**: Integer starting from 1
- **Variant/Haplotypes**: rsID, star alleles (with gene prefix), or metabolizer phenotype
- **Gene**: HGNC symbol (CYP2C9, VKORC1, CYP4F2, etc.)
- **Drug(s)**: Exact drug/metabolite name
- **PMID**: PubMed ID
- **Phenotype Category**: `Efficacy`, `Metabolism/PK`, `Dosage`, `Toxicity`, `Other` (TITLE CASE)
- **Significance**: `yes`, `no`, `not stated`
- **Sentence**: Standardized summary

### Conditional:
- **Alleles**: Genotypes when not using metabolizer phenotype
- **Metabolizer types**: `poor metabolizer`, `intermediate metabolizer`, etc.
- **Comparison Allele(s) or Genotype(s)**: Reference genotype
- **Comparison Metabolizer types**: Reference metabolizer

### Sentence Parts:
- **isPlural**: `Is` or `Are`
- **Is/Is Not associated**: `Associated with` or `Not associated with`
- **Direction of effect**: `increased`, `decreased`, or `null`
- **PD/PK terms**: Exact phrase
- **Population types**: `in people with`, `in women with`, `in children with`, or `null`
- **Population Phenotypes or diseases**: `Disease:...`, or `null`

---

## Extraction Checklist

Before submitting:
- [ ] Separate entries for different Phenotype Categories
- [ ] Included negative findings (Significance: "no")
- [ ] Phenotype Category in TITLE CASE
- [ ] Star alleles include gene prefix for EACH allele
- [ ] Alleles field uses + separator for combinations
- [ ] Comparison field populated when comparison exists
- [ ] isPlural matches subject plurality
- [ ] Population types null when no disease context
- [ ] PD/PK terms are exact phrases ("dose of" not "dose requirements of")

Extract ALL variant-drug associations from the article.