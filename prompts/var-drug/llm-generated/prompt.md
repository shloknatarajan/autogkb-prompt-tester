# Variant/Drug Annotation Extraction Prompt

## Task
Extract variant/drug annotations from the provided scientific article and format them according to the specified schema. Focus on identifying genetic associations with drug dosing, efficacy, toxicity, and pharmacokinetic/pharmacodynamic parameters.

## Output Format
Generate a JSON object with a "var_drug_ann" array containing annotation objects. Each annotation should capture a specific variant-drug association reported in the article.

## Schema Field Definitions

### Core Identification Fields:
- **Variant Annotation ID**: Generate a unique integer ID for each annotation
- **Variant/Haplotypes**: The dbSNP rsID (e.g., rs9923231) or haplotype involved in the association
- **Gene**: HGNC gene symbol (e.g., VKORC1, CYP2C9, CYP4F2, UGT1A1)
- **Drug(s)**: Generic drug name(s) involved in the association
- **PMID**: PubMed ID from the article
- **Phenotype Category**: Choose from: "Dosage", "Efficacy", "Toxicity", "Metabolism/PK", "PD", "Other"
- **Significance**: Based on author's findings - "yes" (significant), "no" (not significant), or "not stated"

### Detailed Annotation Fields:
- **Notes**: Any relevant curator notes (e.g., "alleles complemented to + strand")
- **Sentence**: A structured sentence describing the association (see template below)
- **Alleles**: The specific alleles/genotypes being compared (e.g., "CT + TT", "AC + CC")
- **Specialty Population**: Special populations if mentioned (e.g., "pediatric")

### Sentence Component Fields:
- **Metabolizer types**: Gene phenotype group if applicable (e.g., "poor metabolizer")
- **isPlural**: "Is" or "Are" based on grammatical number
- **Is/Is Not associated**: "Associated with" or "Not associated with"
- **Direction of effect**: "increased" or "decreased" (null if not significant)
- **PD/PK terms**: Pharmacological measure (e.g., "dose of", "concentration of", "metabolism of")
- **Multiple drugs And/or**: "and" or "or" if multiple drugs listed
- **Population types**: Study population descriptor (e.g., "in people with", "in healthy individuals")
- **Population Phenotypes or diseases**: Specific conditions prefixed with "Disease:" (comma-separated)
- **Multiple phenotypes or diseases And/or**: "and" or "or" for multiple conditions
- **Comparison Allele(s) or Genotype(s)**: Reference genotype/allele for comparison
- **Comparison Metabolizer types**: Reference metabolizer phenotype if applicable

## Sentence Template Pattern
The sentence should follow this structure:
`[Alleles/Genotypes] [isPlural] [Is/Is Not associated] [Direction of effect] [PD/PK terms] [Drug(s)] [Population types] [Population Phenotypes or diseases] as compared to [Comparison Allele(s) or Genotype(s)].`

Example: "Genotypes CT + TT are associated with decreased dose of warfarin in people with Atrial Fibrillation, heart valve replacement, Pulmonary Hypertension, Pulmonary Embolism or Venous Thrombosis as compared to genotype CC."

## Extraction Guidelines

1. **Identify Key Findings**: Look for statements about genetic polymorphisms affecting drug response, particularly:
   - Dose requirements
   - Treatment efficacy
   - Adverse effects/toxicity
   - Drug metabolism rates

2. **Statistical Significance**: 
   - Mark "yes" if p-value < 0.05 or authors state significance
   - Mark "no" if explicitly stated as non-significant
   - Use "not stated" if unclear

3. **Direction of Effect**:
   - "increased" = higher dose needed, increased risk, enhanced effect
   - "decreased" = lower dose needed, reduced risk, diminished effect
   - Leave null if no association found

4. **Population Details**:
   - Extract all mentioned conditions/diseases
   - Use "Disease:" prefix for each condition
   - Separate multiple conditions with commas
   - Use "and"/"or" based on study design

5. **Genotype Notation**:
   - For SNPs: Use standard notation (e.g., CC, CT, TT)
   - For star alleles: Use CYP notation (e.g., *1/*3)
   - Combine multiple genotypes with "+"

6. **Special Considerations**:
   - If complemented to plus strand, note in "Notes" field
   - Include all indications for drug use mentioned
   - Preserve author's terminology for metabolizer phenotypes

## Example Input/Output

### Input Article Excerpt:
"The patients with variant genotypes of VKORC1 −1639G>A required significantly lower warfarin stable weekly doses than those with wild-type genotype (p < 0.001). Patients with AA and GA genotypes required 49.7% and 27.7% significantly lower averages of warfarin doses compared with those with wild-type GG genotype."

### Output Annotation:
```json
{
  "Variant Annotation ID": 1448624157,
  "Variant/Haplotypes": "rs9923231",
  "Gene": "VKORC1",
  "Drug(s)": "warfarin",
  "PMID": 28550460,
  "Phenotype Category": "Dosage",
  "Significance": "yes",
  "Notes": "Please note: alleles have been complemented to the + strand.",
  "Sentence": "Genotypes CT + TT are associated with decreased dose of warfarin in people with Atrial Fibrillation, heart valve replacement, Pulmonary Hypertension, Pulmonary Embolism or Venous Thrombosis as compared to genotype CC.",
  "Alleles": "CT + TT",
  "Metabolizer types": null,
  "isPlural": "Are",
  "Is/Is Not associated": "Associated with",
  "Direction of effect": "decreased",
  "PD/PK terms": "dose of",
  "Population types": "in people with",
  "Population Phenotypes or diseases": "Disease:Atrial Fibrillation, Disease:Heart valve replacement, Disease:Pulmonary Hypertension, Disease:Pulmonary Embolism, Disease:Venous Thrombosis",
  "Multiple phenotypes or diseases And/or": "or",
  "Comparison Allele(s) or Genotype(s)": "CC",
  "Comparison Metabolizer types": null
}
```

## Processing Instructions

1. Read the entire article first to understand the study design and population
2. Identify all variant-drug associations reported
3. Create one annotation entry per unique variant-drug-outcome combination
4. If a variant affects multiple aspects (e.g., both efficacy and dosage), create separate annotations
5. Include both significant and non-significant findings if explicitly reported
6. Maintain consistency in terminology within the annotation set
7. Generate normalized fields (PMID_norm, Variant Annotation ID_norm) as string versions

Extract all variant/drug associations from the provided article and return them in the specified JSON format.