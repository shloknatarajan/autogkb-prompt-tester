# Functional Annotation Guidelines

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

## Key Differences from Clinical Annotations

- **Laboratory-based**: In vitro studies rather than patient studies
- **Mechanistic Focus**: How variants affect protein function rather than clinical outcomes
- **Quantitative Measures**: Enzyme kinetics, binding constants, activity percentages
- **Controlled Conditions**: Defined experimental systems rather than clinical populations
- **Substrate-specific**: Effects measured with specific drugs/compounds as substrates

**Purpose**: Functional annotations provide the mechanistic basis for understanding why certain variants affect drug response in patients - they show how genetic changes alter protein function at the molecular level.

**Note**: If there are no extractable functional annotations, please return an empty array. 