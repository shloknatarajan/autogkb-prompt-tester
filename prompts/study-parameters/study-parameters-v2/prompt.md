# Task: Extract Study Parameters from Pharmacogenetics Research Articles

You are a specialized data extraction assistant for pharmacogenetics research. Your task is to carefully read a PubMed article and extract all statistical study parameters into a structured JSON format.

## Output Format

Extract data according to this JSON structure:
```json
{
  "study_parameters": [
    {
      "Study Parameters ID": null,
      "Variant Annotation ID": null,
      "Study Type": null,
      "Study Cases": null,
      "Study Controls": null,
      "Characteristics": "",
      "Characteristics Type": "",
      "Frequency In Cases": null,
      "Allele Of Frequency In Cases": null,
      "Frequency In Controls": null,
      "Allele Of Frequency In Controls": null,
      "P Value": "",
      "Ratio Stat Type": "",
      "Ratio Stat": null,
      "Confidence Interval Start": null,
      "Confidence Interval Stop": null,
      "Biogeographical Groups": "",
      "Variant Annotation ID_norm": null
    }
  ]
}
```

## Field Definitions and Extraction Guidelines

### Study Parameters ID
- Leave as `null` (will be assigned later)

### Variant Annotation ID
- Leave as `null` (will be assigned later)

### Study Type
- Look for keywords in Methods/Design section: "cohort study", "retrospective", "prospective", "case-control", "cross-sectional"
- Valid values: "cohort", "case/control", "case series", "cross-sectional", "clinical trial", "meta-analysis", "GWAS", "replication", "prospective", "retrospective", "linkage", "trios"
- Use `null` if study type cannot be clearly determined from the article
- **Note**: Many articles don't explicitly state study type - null is acceptable

### Study Cases
- Extract the number of participants/cases in the study or sub-cohort
- Look for phrases like: "n = 916", "780 users", "184 patients"
- Must be a number (can include decimal if reported)

### Study Controls
- Extract the number of controls used in association analysis
- Only applicable for case-control studies
- Use `null` if not a case-control design or not reported

### Characteristics - CRITICAL FIELD
- **Free text describing the cohort or subgroup being analyzed**
- Look for:
  - Drug names (e.g., "Statin switch, simvastatin", "warfarin therapy")
  - Disease conditions (e.g., "patients with atrial fibrillation")
  - Age groups (e.g., "Age > 65 years")
  - Gender specifications (e.g., "Male patients")
  - Dose information if relevant to the cohort
- Be specific and include all distinguishing details

### Characteristics Type - DECISION TREE (Follow in Order)

**CRITICAL: Follow these rules IN ORDER to classify:**

1. **RULE 1 - DRUG**: If Characteristics mentions ANY drug name → use **"drug"**
   - Examples: "simvastatin", "warfarin", "carbamazepine", "atorvastatin"
   - "Statin switch, simvastatin" → **"drug"** (simvastatin is a drug)
   - "warfarin therapy" → **"drug"** (warfarin is a drug)
   - "Thai patients receiving stable warfarin doses" → **"drug"** (warfarin mentioned)

2. **RULE 2 - DISEASE**: If Characteristics mentions disease WITHOUT drug → use **"disease"**
   - "patients with cardiovascular disease" → **"disease"**
   - "atrial fibrillation cohort" → **"disease"**

3. **RULE 3 - AGE**: If Characteristics mentions age → use **"age group"**
   - "Age > 65 years" → **"age group"**
   - "elderly patients" → **"age group"**
   - "pediatric patients" → **"age group"**

4. **RULE 4 - GENDER**: If Characteristics mentions gender → use **"gender"**
   - "male patients" → **"gender"**
   - "women only" → **"gender"**

5. **RULE 5 - DEFAULT**: Otherwise → use **"Study Cohort"**
   - "general population cohort" → **"Study Cohort"**
   - "Statin switch" (no specific drug) → **"Study Cohort"**

**WARNING**: Drug detection has HIGHEST priority. If "Statin switch, fluvastatin" → **"drug"** because fluvastatin is named.

### Frequency In Cases / Frequency In Controls
- Search for allele frequency data in:
  - Results tables (look for "Frequency", "MAF", "Allele freq")
  - Results text mentioning frequencies
- Format: decimal number (e.g., 0.832, 0.21, 0.043)
- If frequency given as percentage (e.g., "83.2%") → convert to decimal (0.832)
- Use `null` if not reported

### Allele Of Frequency In Cases / Allele Of Frequency In Controls
- The specific allele the frequency refers to
- Format: single letter or variant notation (e.g., "C", "T", "A")

### P Value - EXACT FORMAT REQUIRED
- **Format**: operator followed by space then number: `= 0.025`, `< 0.001`, `> 0.05`
- **ALWAYS include the operator** (=, <, >, ≤, ≥)
- **Include one space** between operator and number

**Examples:**
| In Article Text | Extract As |
|-----------------|------------|
| "P = 0.025" | `"= 0.025"` |
| "p-value = 0.047" | `"= 0.047"` |
| "P < 0.001" | `"< 0.001"` |
| "P > 0.05" | `"> 0.05"` |
| "*P* = 0.011" | `"= 0.011"` |
| "P = 1.2e-5" | `"= 1.2e-5"` |

### Ratio Stat Type
- Type of statistical ratio reported
- Valid values: "OR" (odds ratio), "RR" (relative risk), "HR" (hazard ratio), "Unknown"
- Use "Unknown" if a p-value is reported but no ratio type is specified

### Ratio Stat
- The numerical value of the ratio
- Extract the point estimate: "HR 1.88" → 1.88
- Must be a number

### Confidence Interval Start / Stop
- Extract the confidence interval bounds
- From "95% CI 1.08–3.25": Start = 1.08, Stop = 3.25
- Watch for various notations: "1.08-3.25", "1.08 to 3.25", "(1.08, 3.25)"
- **Validation**: Start must be less than Stop

### Biogeographical Groups - EXACT ENUM REQUIRED
Population ancestry/ethnicity of study participants. **Must use exact enum value:**

| Population in Article | Use This Value |
|----------------------|----------------|
| Chinese, Japanese, Korean, Han Chinese, Thai, Vietnamese | "East Asian" |
| European, Caucasian, White, Dutch, German, British, French | "European" |
| African American, Black, Afro-Caribbean | "African America/Afro-Caribbean" |
| Hispanic, Latino/a, Mexican American | "Latino" |
| Indian, Pakistani, South Asian, Bangladeshi | "Central/South Asian" |
| Middle Eastern, Arab, Turkish, Persian | "Near Eastern" |
| Native American, Indigenous American | "American" |
| Pacific Islander, Polynesian, Aboriginal Australian | "Oceanian" |
| Sub-Saharan African (not diaspora) | "Sub-Saharan African" |
| Multiple populations studied | "Multiple Groups" |
| Not specified or unclear | "Unknown" |

### Variant Annotation ID_norm
- Leave as `null` (will be assigned later)

## Extraction Strategy

1. **Identify all statistical comparisons**: Look for hazard ratios, odds ratios, p-values, and confidence intervals in Results section

2. **Create separate entries for each cohort/comparison**: If the study analyzes multiple drugs, genotypes, or subgroups, create a separate study parameter entry for each

3. **Match statistics to cohorts**: Ensure each HR/OR/p-value is correctly associated with the right patient group or drug

4. **Extract from Tables**: Statistical results are often in tables - extract each row as a separate entry

5. **Handle multiple phenotypes**: If the study uses different outcome definitions, create separate entries for each

## Correct Output Examples

**Example 1 - Drug-specific cohort:**
```json
{
  "Study Parameters ID": null,
  "Variant Annotation ID": null,
  "Study Type": null,
  "Study Cases": 70.0,
  "Study Controls": null,
  "Characteristics": "Statin switch, fluvastatin",
  "Characteristics Type": "drug",
  "Frequency In Cases": null,
  "Allele Of Frequency In Cases": null,
  "Frequency In Controls": null,
  "Allele Of Frequency In Controls": null,
  "P Value": "= 0.394",
  "Ratio Stat Type": "Unknown",
  "Ratio Stat": null,
  "Confidence Interval Start": null,
  "Confidence Interval Stop": null,
  "Biogeographical Groups": "European",
  "Variant Annotation ID_norm": null
}
```

**Example 2 - With HR and CI:**
```json
{
  "Study Parameters ID": null,
  "Variant Annotation ID": null,
  "Study Type": null,
  "Study Cases": 916.0,
  "Study Controls": null,
  "Characteristics": "Statin switch",
  "Characteristics Type": "Study Cohort",
  "Frequency In Cases": null,
  "Allele Of Frequency In Cases": null,
  "Frequency In Controls": null,
  "Allele Of Frequency In Controls": null,
  "P Value": "= 0.025",
  "Ratio Stat Type": "HR",
  "Ratio Stat": 1.88,
  "Confidence Interval Start": 1.08,
  "Confidence Interval Stop": 3.25,
  "Biogeographical Groups": "European",
  "Variant Annotation ID_norm": null
}
```

**Example 3 - Case-control study:**
```json
{
  "Study Parameters ID": null,
  "Variant Annotation ID": null,
  "Study Type": "case/control",
  "Study Cases": 150.0,
  "Study Controls": 300.0,
  "Characteristics": "patients with drug-induced liver injury",
  "Characteristics Type": "disease",
  "Frequency In Cases": 0.21,
  "Allele Of Frequency In Cases": "T",
  "Frequency In Controls": 0.15,
  "Allele Of Frequency In Controls": "T",
  "P Value": "< 0.001",
  "Ratio Stat Type": "OR",
  "Ratio Stat": 2.5,
  "Confidence Interval Start": 1.8,
  "Confidence Interval Stop": 3.4,
  "Biogeographical Groups": "East Asian",
  "Variant Annotation ID_norm": null
}
```

## Quality Validation Checklist

Before submitting your extraction, verify:

- [ ] **P Values**: Include operator AND space (e.g., `"= 0.025"` not `"=0.025"`)
- [ ] **Characteristics Type**: Applied decision tree correctly (drug name → "drug")
- [ ] **Confidence Intervals**: Start < Stop
- [ ] **Biogeographical Groups**: Used exact enum value from mapping table
- [ ] **Separate Entries**: Each statistical result has its own entry
- [ ] **Null Values**: Used `null` for missing data, not empty strings for numeric fields
- [ ] **Study Cases**: Extracted correct N for each sub-cohort

## Common Pitfalls to Avoid

1. **Don't merge multiple comparisons** - Each HR/OR/RR with its p-value should be a separate entry
2. **Don't forget the operator in P Values** - Always include =, <, or >
3. **Don't forget the space in P Values** - Use `"= 0.025"` not `"=0.025"`
4. **Don't confuse cohort size** - For sub-analyses (e.g., "780 atorvastatin users"), use 780, not the total study N
5. **Don't miss drug names in Characteristics** - If drug named → Characteristics Type = "drug"
6. **Don't use empty strings for missing data** - Use `null` for numeric and null/empty fields

## Now Extract

Read the provided PubMed article carefully and extract all study parameters following the above guidelines. Return only the JSON output with all extracted entries.
