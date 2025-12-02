# Functional Annotation Guidelines

## CRITICAL FIRST STEP: Identify Functional Evidence

Before extracting, scan for functional experimental data:

**Look for in Results/Methods/Tables:**
- Enzyme activity measurements
- Cell-based expression studies  
- Patient samples measuring enzyme function (plasma metabolite ratios)
- In vitro/ex vivo functional assays

**Ignore in Introduction/Discussion:**
- Clinical guidelines ("recommended for testing")
- Literature review ("previous studies showed")
- Treatment recommendations
- Toxicity associations

**Key Test:** Does this describe HOW the variant affects protein function?
- YES → Extract as functional
- NO → Skip (belongs in clinical annotations)

## Terms for Extraction

### Variant/Haplotypes
- **Content**: The specific genetic variant studied
- **Manual Process**: Extract variant names, star alleles, SNP IDs, or protein constructs tested
- **Example**: CYP2C19*1, CYP2C19*17, rs72552763, CYP2B6*1, CYP2B6*6

### Gene
- **Content**: Gene symbol associated with the variant
- **Manual Process**: Identify the gene being studied functionally
- **Example**: CYP2C19, CYP2B6, SLC22A1

### Drug(s)
- **Content**: Substrate or compound used in the functional assay
- **Manual Process**: Extract the drug/substrate used to test enzyme activity or transport
- **Example**: normeperidine, bupropion, warfarin, voriconazole

### Phenotype Category
- **Content**: Type of functional outcome measured
- **Manual Process**: Categorize based on what was measured:
  - Metabolism/PK: Enzyme activity, clearance, transport, binding affinity
  - Efficacy: Functional response in cellular systems
  - Leave empty for basic biochemical studies
- **Example**: 
  - Metabolism/PK (for enzyme kinetics)
  - Efficacy (for cellular response)

### Significance
- **Content**: Statistical significance of functional differences
- **Manual Process**: Look for statistical comparisons:
  - yes: Significant differences in activity/function
  - no: No significant differences
  - not stated: No statistical testing reported
- **Example**: 
  - yes (for significant activity differences)
  - not stated (for descriptive studies)

### Notes
- **Content**: Key experimental details, methodology, quantitative results
- **Manual Process**: Extract relevant quotes showing experimental conditions, numerical results, or important technical details
- **Example**: "Clearance was 26.57% of wild-type. CYP2C19 variants expressed in Sf21 insect cells..."

### Standardized Sentence
- **Content**: Standardized description of the functional relationship
- **Manual Process**: Write in format: "[Variant] is associated with [increased/decreased] [functional outcome] [experimental context] as compared to [reference variant]"
- **Example**: "CYP2C19 *17/*17 is associated with increased formation of normeperidine as compared to CYP2C19 *1/*1 + *1/*17."

### Alleles
- **Content**: Specific allele or genotype tested
- **Manual Process**: Extract the exact variant designation
- **Example**: *17/*17, *1/*1, del, A

### Metabolizer Types
- **Content**: Phenotype classification if applicable
- **Manual Process**: Rarely used in functional studies; mainly for CYP phenotyping
- **Example**: Usually empty

### Comparison Allele(s) or Genotype(s)
- **Content**: Reference variant for comparison
- **Manual Process**: Find the control/wild-type variant used for comparison
- **Example**: *1/*1 + *1/*17, *1, GAT

### Comparison Metabolizer Types
- **Content**: Reference metabolizer status
- **Manual Process**: Usually empty for functional studies
- **Example**: Usually empty

### Assay Type
- **Content**: Laboratory method or experimental system used
- **Manual Process**: Extract the specific assay methodology:
  - in human liver microsomes: Microsomal enzyme assays
  - hydroxylation assay: Specific metabolic pathway assays
  - crystal structure prediction: Computational modeling
  - Leave empty if not specified
- **Example**: 
  - in human liver microsomes
  - hydroxylation assay
  - crystal structure prediction

### Cell Type
- **Content**: Cell line or tissue system used for the assay
- **Manual Process**: Extract the specific cellular context:
  - 293FT cells: Human embryonic kidney cells
  - COS-7 cells: Monkey kidney cells
  - Sf21 insect cells: Insect cells for baculovirus expression
  - in insect microsomes: Microsomal preparations
  - expressed in [cell type]: Heterologous expression systems
- **Example**: 
  - in 293FT cells
  - expressed in COS-7 cells

### Specialty Population
- **Content**: Age-specific populations (rarely applicable to functional studies)
- **Manual Process**: Usually leave empty for in vitro studies
- **Example**: Usually empty

### isPlural
- **Content**: Grammar helper for sentence construction
- **Manual Process**: Use Is for singular subjects, Are for plural
- **Example**: Is

### Is/Is Not Associated
- **Content**: Direction of functional association
- **Manual Process**: Determine association type:
  - Associated with: Functional difference observed
  - Not associated with: No functional difference
- **Example**: Associated with

### Direction of Effect
- **Content**: Whether the variant increases or decreases function
- **Manual Process**: Look for directional language:
  - increased: Higher activity, better function, enhanced capability
  - decreased: Lower activity, reduced function, impaired capability
- **Example**: 
  - increased (for enhanced activity)
  - decreased (for reduced activity)

### Functional Terms
- **Content**: Specific functional outcome measured
- **Manual Process**: Extract the precise functional parameter:
  - activity of: Enzyme activity measurements
  - clearance of: Drug clearance kinetics
  - formation of: Metabolite formation
  - transport of: Transporter function
  - affinity to: Binding affinity
  - catalytic activity of: Catalytic efficiency
- **Example**: 
  - formation of
  - activity of
  - clearance of

### Gene/Gene Product
- **Content**: Specific gene or protein being functionally assessed
- **Manual Process**: Extract the gene symbol when the functional term relates to gene product activity
- **Example**: CYP2C19, CYP2B6, CYP2C9

### When Treated With/Exposed To/When Assayed With
- **Content**: Experimental substrate context
- **Manual Process**: Use standard phrases for functional assays:
  - when assayed with: For enzyme activity assays
  - of: For direct metabolite measurements
  - Leave empty for non-substrate specific functions
- **Example**: 
  - when assayed with
  - of

### Multiple Drugs And/Or
- **Content**: Logical connector for multiple substrates
- **Manual Process**: If multiple substrates tested:
  - and: Combination substrate assays
  - or: Alternative substrate assays
  - Leave empty for single substrate
- **Example**: or (for alternative substrates)

## Manual Reading Strategy for Functional Annotations

1. **Identify Experimental System**: Look for cell lines, microsomes, expression systems, computational models
2. **Find Functional Readouts**: Search for enzyme activity, kinetic parameters, binding affinity, transport rates
3. **Extract Substrate Information**: Identify the drug/compound used to test function
4. **Locate Comparison Data**: Find reference variants (usually wild-type or *1 alleles) for comparison
5. **Quantify Functional Changes**: Look for fold-changes, percentages, kinetic parameters (Km, Vmax, clearance)
6. **Note Experimental Conditions**: Extract assay conditions, expression systems, substrate concentrations
7. **Standardize the Relationship**: Convert findings into standardized sentence format describing the functional difference

## 5 Critical Rules for Functional Extraction

**Rule 1: ONLY extract laboratory measurements of protein function**
- ✅ YES: Enzyme activity, kinetics, clearance, binding affinity
- ✅ YES: Patient-derived samples measuring enzyme activity (plasma metabolite ratios)
- ❌ NO: Clinical toxicity, treatment response, guidelines

**Rule 2: Distinguish assay systems**
- Functional: "in 293FT cells", "plasma dihydrouracil/uracil ratio", "in microsomes"
- NOT functional: "in patients with cancer", "clinical trial results", "toxicity in patients"

**Rule 3: Drug field usage**
- Use Drug field: Testing activity with specific substrate (e.g., "ticagrelor metabolism")
- Set to NULL: Measuring general enzyme activity (e.g., "DPYD activity by plasma metabolites")

**Rule 4: Extract variants WITH STATISTICAL EVIDENCE in Results**
- PRIMARY: Variants with statistical significance reported in Results/Tables (P-values, statistical tests)
- Look for: "significantly associated with", "P < 0.05", "showed association"
- NEVER: Variants only mentioned as "clinically relevant" or "recommended for testing"
- NEVER: Literature review in Introduction stating "previous studies showed"

**CRITICAL:** If multiple variant sets are in Results, extract the ones THIS STUDY tested for association with functional outcomes (enzyme activity, etc.), NOT variants cited from clinical guidelines.

**Rule 5: Avoid clinical-functional confusion**
- If text mentions "toxicity", "guidelines", "recommended for testing" → NOT functional
- If text shows enzyme kinetics, activity assays → IS functional

### Examples to Guide Extraction

**Example 1: Patient-derived enzyme assay (PMC10786722-style)**

Text: "rs56038477 significantly associated with low DPD activity measured by plasma [UH2]/[U] ratio (P < 0.05)"

- Variant: rs56038477
- Gene: DPYD
- Drug: null (no specific substrate, general enzyme activity)
- Assay type: plasma dihydrouracil/uracil  
- Functional terms: activity of
- Gene/gene product: DPYD
- ✅ IS functional - measuring enzyme activity with plasma biomarkers

**Example 2: Clinical mention to AVOID**

Text: "c.1905+1G>A recommended for pre-treatment testing to reduce fluoropyrimidine toxicity"

- ❌ NOT functional - clinical guideline for testing
- This belongs in var-pheno or var-drug (toxicity association)

**Example 3: Subset Selection (CRITICAL for PMC10786722-style articles)**

Text: "Among the seven genetic variants identified, three variants (c.1236G>A or rs56038477; c.496A>G or rs2297595; c.2194G>A or rs1801160) were significantly more frequent in patients with partial DPD deficiency."

- ✅ Extract ONLY the three explicitly named variants: rs56038477, rs2297595, rs1801160
- ❌ DO NOT extract the other four variants mentioned elsewhere
- ❌ DO NOT extract rare clinical variants from other parts of Results

**Pattern to recognize:** "Among X variants, Y specific variants were significantly associated"
→ Extract ONLY the Y variants explicitly named in that sentence.

**Purpose**: Functional annotations provide the mechanistic basis for understanding why certain variants affect drug response in patients - they show how genetic changes alter protein function at the molecular level.