Phenotype Association Annotation Guidelines

Article: \n\n{article_text}\n\n


## Terms for Extraction

### Variant/Haplotypes
- **Content**: The specific genetic variant studied
- **Manual Process**: Extract SNP IDs (rs numbers), HLA alleles, star alleles, or genotype combinations
- **Example**: HLA-B*35:08, rs1801272, UGT1A1*1, UGT1A1*28

### Gene
- **Content**: Gene symbol associated with the variant
- **Manual Process**: Find the gene name near the variant mention
- **Example**: HLA-B, CYP2A6, UGT1A1

### Drug(s)
- **Content**: Drug(s) that caused or were involved in the phenotype
- **Manual Process**: 
  - Extract drug names that triggered the adverse event or phenotype
  - Leave empty for disease susceptibility studies without drug involvement
- **Example**: lamotrigine, sacituzumab govitecan, empty for disease predisposition

### Phenotype Category
- **Content**: Type of phenotype or outcome studied
- **Manual Process**: Categorize based on primary outcome:
  - Toxicity: Adverse drug reactions, side effects, drug-induced toxicity
  - Efficacy: Treatment response, therapeutic outcomes
  - Metabolism/PK: Pharmacokinetic parameters, drug levels
  - Dosage: Dose requirements, dose-response relationships
  - Other: Disease susceptibility, traits not directly drug-related
- **Example**: 
  - Toxicity (for Stevens-Johnson Syndrome)
  - Other (for alcoholism risk)

### Significance
- **Content**: Statistical significance of the association
- **Manual Process**: Look for p-values and statistical tests:
  - yes: p < 0.05 or stated as significant
  - no: p ≥ 0.05 or explicitly non-significant
  - not stated: No statistical testing reported
- **Example**: no (for non-significant HLA associations)

### Notes
- **Content**: Key study details, statistics, methodology
- **Manual Process**: Extract relevant quotes showing statistical results, case descriptions, or important context
- **Example**: "The allele was not significant when comparing allele frequency in cases..."

### Standardized Sentence
- **Content**: Standardized description of the genetic-phenotype association
- **Manual Process**: Write in format: "[Variant] is [associated with/not associated with] [increased/decreased] [phenotype outcome] [drug context] [population context]"
- **Example**: "HLA-B *35:08 is not associated with likelihood of Maculopapular Exanthema, severe cutaneous adverse reactions or Stevens-Johnson Syndrome when treated with lamotrigine in people with Epilepsy."

### Alleles
- **Content**: Specific allele or genotype if different from main variant field
- **Manual Process**: Extract the exact genotype mentioned
- **Example**: *35:08, AA + AT, *1/*28 + *28/*28

### Specialty Population
- **Content**: Age-specific populations
- **Manual Process**: Identify if study focused on specific age groups:
  - Pediatric: Children/adolescents
  - Geriatric: Elderly patients
  - Leave empty for general adult populations
- **Example**: Pediatric (for children with Fanconi Anemia)

### Metabolizer Types
- **Content**: CYP enzyme phenotype when applicable
- **Manual Process**: Look for metabolizer classifications in CYP studies:
  - poor metabolizer
  - intermediate metabolizer
  - extensive metabolizer
  - ultrarapid metabolizer
  - deficiency
- **Example**: ultrarapid metabolizer, intermediate activity

### isPlural
- **Content**: Grammar helper for sentence construction
- **Manual Process**: Use Is for singular subjects, Are for plural
- **Example**: Is (for single allele), Are (for combined genotypes)

### Is/Is Not Associated
- **Content**: Direction of statistical association
- **Manual Process**: Determine association type:
  - Associated with: Positive association found
  - Not associated with: No association found
- **Example**: Not associated with, Associated with

### Direction of Effect
- **Content**: Whether the variant increases or decreases the phenotype
- **Manual Process**: Look for directional language:
  - increased: Higher risk, more severe, greater likelihood
  - decreased: Lower risk, less severe, reduced likelihood
  - Leave empty if no clear direction
- **Example**: 
  - increased (for higher toxicity risk)
  - decreased (for lower disease risk)

### Side Effect/Efficacy/Other
- **Content**: Specific phenotype outcome with standardized prefix
- **Manual Process**: Categorize the phenotype and add appropriate prefix:
  - Side Effect: for adverse drug reactions
  - Efficacy: for therapeutic outcomes
  - Disease: for disease conditions
  - Other: for other traits/conditions
  - PK: for pharmacokinetic measures
- **Example**: 
  - Side Effect:Stevens-Johnson Syndrome
  - Disease:Alcohol abuse
  - Other:Medication adherence

### When Treated With/Exposed To/When Assayed With
- **Content**: Drug administration context
- **Manual Process**: Use standard phrases:
  - when treated with: For therapeutic drug administration
  - when exposed to: For environmental or non-therapeutic exposure
  - due to: For substance-related disorders
  - Leave empty for non-drug phenotypes
- **Example**: when treated with, due to (for substance abuse)

### Multiple Drugs And/Or
- **Content**: Logical connector for multiple drugs
- **Manual Process**: If multiple drugs involved:
  - and: Combination therapy
  - or: Any of the drugs
  - Leave empty for single drug
- **Example**: or (for any of several drugs)

### Population Types
- **Content**: Description of study population
- **Manual Process**: Look for population descriptors:
  - in people with: General population with condition
  - in children with: Pediatric population
  - in women with: Gender-specific population
- **Example**: in people with, in children with

### Population Phenotypes or Diseases
- **Content**: Disease/condition context with prefix
- **Manual Process**: Find the medical condition and add prefix:
  - Disease: for established diseases
  - Other: for conditions/traits
- **Example**: 
  - Disease:Epilepsy
  - Other:Diabetes Mellitus, Type 2

### Multiple Phenotypes or Diseases And/Or
- **Content**: Logical connector for multiple conditions
- **Manual Process**: Use and/or for multiple disease contexts
- **Example**: and (for multiple comorbidities)

### Comparison Allele(s) or Genotype(s)
- **Content**: Reference genotype for comparison
- **Manual Process**: Find what the variant was compared against
- **Example**: TT (wild-type), *1/*1 (normal function allele)

### Comparison Metabolizer Types
- **Content**: Reference metabolizer phenotype
- **Manual Process**: Extract comparison metabolizer status
- **Example**: normal metabolizer

## General Strategy Recommendations

1. **Identify Phenotype Outcomes**: Look for adverse events, toxicities, disease conditions, clinical traits
2. **Find Genetic Associations**: Search for variants linked to the phenotype (may or may not involve drugs)
3. **Determine Drug Involvement**: Check if phenotype is drug-induced or related to disease susceptibility
4. **Extract Statistical Evidence**: Look for odds ratios, p-values, case reports, frequency differences
5. **Categorize Phenotype Type**: Classify as toxicity, efficacy, disease susceptibility, or other trait
6. **Note Population Context**: Identify specific patient populations, age groups, disease conditions
7. **Standardize the Relationship**: Convert findings into standardized sentence format describing the genetic-phenotype association

**Note**: If there is no extractable functional annotations, please return an empty array. 