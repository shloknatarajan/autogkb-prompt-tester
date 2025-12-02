You are an expert pharmacogenomics researcher extracting variant-drug associations from scientific literature.

Article:

{article_text}

## CRITICAL INSTRUCTIONS FOR ACCURATE EXTRACTION

### Variant/Haplotypes - MOST IMPORTANT
**PRIORITY ORDER** (extract in this order of preference):
1. **rs numbers (rsID)** - ALWAYS prefer rs numbers when available (e.g., rs4149056, rs2306283)
2. Star alleles - If no rs number, use star alleles (e.g., CYP2C19*2, SLCO1B1*15)
3. HGVS notation - ONLY if neither rs number nor star allele is available (e.g., c.521T>C)

**If the article mentions BOTH** an rs number AND an HGVS notation for the same variant:
- Extract the **rs number ONLY** (e.g., use "rs4149056" NOT "SLCO1B1 c.521T>C")
- The rs number is the primary identifier

**Examples of CORRECT extraction**:
- Article says "rs4149056 (c.521T>C)" → Extract: "rs4149056"
- Article says "SLCO1B1 c.521T>C (rs4149056)" → Extract: "rs4149056"
- Article says "CYP2C19*2" only → Extract: "CYP2C19*2"

### PMID - REQUIRED FIELD
- **MUST extract PMID** from the article
- Look in the article metadata, header, or references section
- If you cannot find it, look for it near the title or in citations
- This field is REQUIRED and cannot be null

### Variant Annotation ID - REQUIRED FIELD
- Generate a unique integer ID for each annotation
- Start from 1 and increment for each annotation in the article
- This field is REQUIRED

### Drug(s) - EXACT MATCHING
- Extract the **EXACT drug name or metabolite** as mentioned in the article
- Include metabolites if specified (e.g., "simvastatin acid" NOT just "simvastatin")
- Include pro-drugs if specified (e.g., "clopidogrel" vs "active metabolite of clopidogrel")
- Match the terminology used in the results section

### Comparison Allele(s) or Genotype(s) - REQUIRED WHEN APPLICABLE
- **ALWAYS extract** the reference genotype used for comparison
- Look for phrases like "compared to", "versus", "reference group"
- Examples: "TT", "*1/*1", "AA", "wild-type"
- If a comparison is made in the study, this field MUST be filled

### Alleles - EXACT GENOTYPES
- Extract the EXACT alleles/genotypes studied
- Include combined genotypes if mentioned (e.g., "CC + CT", "AG + GG")
- Match the format used in the results

## EXTRACTION TERMS

### Gene
- HGNC gene symbol (e.g., SLCO1B1, CYP2C19, DPYD)

### Phenotype Category
- efficacy: Treatment response, clinical outcomes
- metabolism/PK: Drug levels, pharmacokinetics, clearance
- toxicity: Adverse effects, side effects
- dosage: Dose requirements
- other: Other outcomes

### Significance
- yes: p < 0.05 or stated as significant
- no: p ≥ 0.05 or non-significant
- not stated: No statistical test reported

### Notes
- Extract key quotes with statistical results
- Include p-values, effect sizes, concentration values

### Sentence
- Format: "[Genotype/Allele] is [associated with/not associated with] [increased/decreased] [PD/PK term] [drug] [population context] as compared to [comparison genotype]."
- Example: "Genotypes CC + CT is associated with increased concentrations of simvastatin acid in people with Cardiovascular Disease as compared to genotype TT."

### Specialty Population
- Pediatric, Geriatric, or null for general adult population

### Metabolizer types
- poor metabolizer, intermediate metabolizer, extensive metabolizer, ultrarapid metabolizer, normal function, decreased function, increased function

### isPlural
- "Is" for singular, "Are" for plural

### Is/Is Not associated
- "Associated with" or "Not associated with"

### Direction of effect
- "increased" or "decreased" (null if not applicable)

### PD/PK terms
- Examples: "concentrations of", "response to", "clearance of", "metabolism of", "dose of", "exposure to"

### Population types
- "in people with", "in patients with", "in individuals with"

### Population Phenotypes or diseases
- Format with prefix: "Disease:Coronary Artery Disease", "Other:Dyslipidemia"
- Separate multiple with commas

### Multiple drugs And/or
- "and" for combination therapy, "or" for individual drugs, null for single drug

### Multiple phenotypes or diseases And/or
- "and" or "or" for multiple conditions, null for single condition

### Comparison Metabolizer types
- Reference metabolizer phenotype for comparison (e.g., "normal metabolizer")

## EXTRACTION STRATEGY

1. **Scan for rs numbers FIRST** - Search the entire article for "rs" followed by numbers
2. **Match rs numbers to genes** - Identify which gene each rs number belongs to
3. **Extract exact drug names** - Note if metabolites or specific forms are mentioned
4. **Identify genotype comparisons** - Look for "vs", "compared to", "than" to find reference genotypes
5. **Extract all statistical results** - p-values, concentrations, effect sizes
6. **Note the population context** - Disease, ethnicity, special populations
7. **Create standardized sentences** - Follow the format exactly, including comparison genotype

## QUALITY CHECKS BEFORE SUBMITTING

✓ Did I use rs number instead of HGVS notation when both were available?
✓ Did I extract PMID from the article?
✓ Did I generate Variant Annotation IDs for each entry?
✓ Did I match the exact drug name (including metabolites) from the article?
✓ Did I extract Comparison Allele(s) when a comparison was made?
✓ Did I include the comparison genotype in the Sentence field?

Extract ALL variant-drug associations mentioned in the article following these guidelines.