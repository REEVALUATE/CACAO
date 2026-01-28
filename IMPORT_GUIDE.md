# CACAO Ontology: CRM 7.1.3 Full Import & PROV-O Integration Guide

## What Has Been Done

### 1. Full CIDOC CRM 7.1.3 Import
**Updated file:** [src/ontology/imports/crm_terms.txt](src/ontology/imports/crm_terms.txt)

- **Before:** 65 selected CRM terms
- **After:** 241 complete terms (81 classes + 160 properties)
- **Notable additions:**
  - `E13_Attribute_Assignment` - For tracking opinions vs facts
  - `E14_Condition_Assessment` - For assessment events
  - `E89_Propositional_Object` - For opinions and propositions
  - All temporal/spatial reasoning properties
  - Full measurement and classification framework

### 2. PROV-O Integration Added
**New files:**
- [src/ontology/imports/prov_terms.txt](src/ontology/imports/prov_terms.txt) - 105 PROV-O terms
- Updated [src/ontology/cacao-odk.yaml](src/ontology/cacao-odk.yaml) with PROV-O import

**PROV-O concepts imported:**
- Core classes: `Entity`, `Activity`, `Agent`
- Agent types: `Person`, `Organization`, `SoftwareAgent`
- Provenance properties: `wasAttributedTo`, `wasGeneratedBy`, `wasDerivedFrom`
- Temporal tracking: `startedAtTime`, `endedAtTime`, `generatedAtTime`
- Qualified relations for detailed provenance chains

---

## Step-by-Step: Running the Import

### Option A: Using Docker (Recommended)

```bash
cd src/ontology

# On Windows Git Bash or WSL:
bash run.sh make refresh-imports

# On Windows PowerShell:
docker run -v ${PWD}/../..:/work -w /work/src/ontology obolibrary/odkfull:v1.5.4 make refresh-imports

# On Linux/Mac:
./run.sh make refresh-imports
```

**If you encounter TTY errors on Windows:**
```bash
winpty bash run.sh make refresh-imports
```

### Option B: Manual ROBOT Execution

If Docker isn't available, install ROBOT locally:
```bash
# Download ROBOT from https://github.com/ontodev/robot/releases
# Then run:
cd src/ontology
robot extract --input imports/crm.owl --term-file imports/crm_terms.txt --output imports/crm_import.owl
robot extract --input imports/prov.owl --term-file imports/prov_terms.txt --output imports/prov_import.owl
```

### Verify Import Success

```bash
# Check that import files were created/updated:
ls -lh imports/*_import.owl

# Expected new/updated files:
# - crm_import.owl (should be larger now - ~1-2MB)
# - prov_import.owl (new file - ~200-400KB)
```

---

## Mapping PROV-O to CACAO for Opinion Tracking

### Use Case: Distinguishing Facts from Opinions

PROV-O combined with CIDOC CRM provides powerful provenance tracking for cultural heritage assertions.

### Recommended Mapping Pattern

#### 1. **Facts (Objective Assertions)**
Use standard CRM properties directly:
```turtle
:Artwork_Mona_Lisa a cacao:Artwork ;
    crm:P14_carried_out_by :Leonardo_da_Vinci ;  # Factual attribution
    crm:P108_has_produced :Physical_Object_123 ;
    crm:P94_has_created :Artwork_Mona_Lisa .
```

#### 2. **Opinions (Subjective Assertions)**
Use CRM's `E13_Attribute_Assignment` with PROV-O provenance:

```turtle
# The opinion/interpretation activity
:Attribution_Opinion_456 a crm:E13_Attribute_Assignment ;
    crm:P140_assigned_attribute_to :Artwork_Disputed_Painting ;
    crm:P141_assigned :Artist_X ;
    crm:P177_assigned_property_of_type crm:P14_carried_out_by ;
    prov:wasAttributedTo :Expert_Curator_Smith ;
    prov:generatedAtTime "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    prov:hadPrimarySource :Archival_Document_789 ;
    crm:P3_has_note "Attribution based on stylistic analysis" .

# The expert who made the attribution
:Expert_Curator_Smith a prov:Person , crm:E21_Person ;
    rdfs:label "Dr. Jane Smith" ;
    cacao:hasDomain :Art_History_Domain ;
    prov:actedOnBehalfOf :Museum_Organization .

# The source document
:Archival_Document_789 a prov:Entity , crm:E31_Document ;
    rdfs:label "Stylistic Analysis Report 2025" ;
    prov:wasGeneratedBy :Research_Activity_2024 .
```

#### 3. **Competing Opinions**
Track multiple interpretations with provenance chains:

```turtle
# Opinion 1
:Attribution_Opinion_A a crm:E13_Attribute_Assignment ;
    crm:P140_assigned_attribute_to :Painting_X ;
    crm:P141_assigned :Artist_Rembrandt ;
    prov:wasAttributedTo :Expert_A ;
    prov:generatedAtTime "2020-03-15T09:00:00Z"^^xsd:dateTime ;
    crm:P3_has_note "Attributed to Rembrandt based on brushwork analysis" .

# Opinion 2 (contradicts Opinion 1)
:Attribution_Opinion_B a crm:E13_Attribute_Assignment ;
    crm:P140_assigned_attribute_to :Painting_X ;
    crm:P141_assigned :Artist_Rembrandt_School ;  # Different attribution
    prov:wasAttributedTo :Expert_B ;
    prov:generatedAtTime "2023-11-20T14:30:00Z"^^xsd:dateTime ;
    prov:wasDerivedFrom :Attribution_Opinion_A ;  # References previous opinion
    prov:hadPrimarySource :Scientific_Analysis_Report_2023 ;
    crm:P3_has_note "Revised attribution based on pigment analysis - likely workshop of Rembrandt" .

# Link opinions as alternative interpretations
:Attribution_Opinion_A prov:alternateOf :Attribution_Opinion_B .
```

#### 4. **Opinion Revisions**
Track how interpretations evolve over time:

```turtle
# Original interpretation
:Interpretation_v1 a crm:E13_Attribute_Assignment ;
    crm:P140_assigned_attribute_to :Artifact_Medieval_Coin ;
    crm:P141_assigned :Date_1200_AD ;
    prov:wasAttributedTo :Archaeologist_Jones ;
    prov:generatedAtTime "2018-06-10T11:00:00Z"^^xsd:dateTime .

# Revised interpretation
:Interpretation_v2 a crm:E13_Attribute_Assignment ;
    crm:P140_assigned_attribute_to :Artifact_Medieval_Coin ;
    crm:P141_assigned :Date_1150_AD ;  # Revised date
    prov:wasAttributedTo :Archaeologist_Jones ;
    prov:generatedAtTime "2024-09-05T16:45:00Z"^^xsd:dateTime ;
    prov:wasRevisionOf :Interpretation_v1 ;  # Links to previous interpretation
    prov:hadPrimarySource :Carbon_Dating_Report_2024 ;
    crm:P3_has_note "Date revised based on new carbon-14 analysis" .
```

### Suggested CACAO Extensions

Add these new classes to [src/ontology/cacao-edit.owl](src/ontology/cacao-edit.owl):

```turtle
###############################################
# CACAO Provenance Extension Classes
###############################################

### Opinion
cacao:Opinion a owl:Class ;
    rdfs:subClassOf crm:E13_Attribute_Assignment ,
                    prov:Entity ;
    rdfs:label "Opinion"@en ;
    rdfs:comment "A subjective interpretation or attribution made by an expert or authority, tracked with full provenance."@en .

### Fact
cacao:Fact a owl:Class ;
    rdfs:subClassOf prov:Entity ;
    rdfs:label "Fact"@en ;
    rdfs:comment "An objective, verifiable statement about a cultural artifact or entity, distinguished from opinions."@en .

### Interpretation
cacao:Interpretation a owl:Class ;
    rdfs:subClassOf cacao:Opinion ,
                    crm:E89_Propositional_Object ;
    rdfs:label "Interpretation"@en ;
    rdfs:comment "A reasoned analysis or explanation of cultural artifacts, events, or phenomena."@en .

### Attribution
cacao:Attribution a owl:Class ;
    rdfs:subClassOf cacao:Opinion ;
    rdfs:label "Attribution"@en ;
    rdfs:comment "An opinion about the creator, origin, or authorship of an artifact."@en .

### Assessment
cacao:Assessment a owl:Class ;
    rdfs:subClassOf crm:E14_Condition_Assessment ,
                    cacao:Opinion ;
    rdfs:label "Assessment"@en ;
    rdfs:comment "An expert evaluation of condition, authenticity, or value."@en .

###############################################
# CACAO Provenance Properties
###############################################

### hasInterpretation
cacao:hasInterpretation a owl:ObjectProperty ;
    rdfs:domain crm:E1_CRM_Entity ;
    rdfs:range cacao:Interpretation ;
    rdfs:subPropertyOf prov:wasGeneratedBy ;
    rdfs:label "has interpretation"@en ;
    rdfs:comment "Links an entity to scholarly interpretations about it."@en .

### hasAttribution
cacao:hasAttribution a owl:ObjectProperty ;
    rdfs:domain cacao:Physical_Artefact ;
    rdfs:range cacao:Attribution ;
    rdfs:subPropertyOf prov:wasAttributedTo ;
    rdfs:label "has attribution"@en ;
    rdfs:comment "Links an artifact to attribution opinions about its creator or origin."@en .

### basedOnEvidence
cacao:basedOnEvidence a owl:ObjectProperty ;
    rdfs:domain cacao:Opinion ;
    rdfs:range prov:Entity ;
    rdfs:subPropertyOf prov:hadPrimarySource ;
    rdfs:label "based on evidence"@en ;
    rdfs:comment "Links an opinion to the evidence or sources supporting it."@en .

### contradictsOpinion
cacao:contradictsOpinion a owl:ObjectProperty ;
    rdfs:domain cacao:Opinion ;
    rdfs:range cacao:Opinion ;
    rdfs:subPropertyOf prov:alternateOf ;
    rdfs:label "contradicts opinion"@en ;
    rdfs:comment "Indicates that two opinions present conflicting interpretations."@en .

### confidence (Data Property)
cacao:confidence a owl:DatatypeProperty ;
    rdfs:domain cacao:Opinion ;
    rdfs:range xsd:decimal ;
    rdfs:label "confidence"@en ;
    rdfs:comment "Confidence level of an opinion (0.0 to 1.0)."@en .
```

---

## Query Examples

### Find all opinions about an artifact:
```sparql
PREFIX cacao: <http://w3id.org/cacao/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>

SELECT ?opinion ?expert ?timestamp ?note
WHERE {
    ?opinion a cacao:Opinion ;
        crm:P140_assigned_attribute_to :Artifact_X ;
        prov:wasAttributedTo ?expert ;
        prov:generatedAtTime ?timestamp ;
        crm:P3_has_note ?note .
}
ORDER BY DESC(?timestamp)
```

### Find competing attributions:
```sparql
SELECT ?painting ?opinion1 ?artist1 ?opinion2 ?artist2
WHERE {
    ?opinion1 a cacao:Attribution ;
        crm:P140_assigned_attribute_to ?painting ;
        crm:P141_assigned ?artist1 .

    ?opinion2 a cacao:Attribution ;
        crm:P140_assigned_attribute_to ?painting ;
        crm:P141_assigned ?artist2 ;
        prov:alternateOf ?opinion1 .

    FILTER(?artist1 != ?artist2)
}
```

### Track provenance chain of a revised opinion:
```sparql
SELECT ?interpretation ?timestamp ?source
WHERE {
    :Latest_Interpretation (prov:wasRevisionOf|prov:wasDerivedFrom)* ?interpretation .
    ?interpretation prov:generatedAtTime ?timestamp ;
                    prov:hadPrimarySource ?source .
}
ORDER BY ?timestamp
```

---

## Next Steps

1. **Run the import refresh** (see commands above)
2. **Edit cacao-edit.owl** to add the new Opinion/Interpretation classes
3. **Create example instances** showing fact vs opinion patterns
4. **Update SHACL shapes** to validate provenance chains:
   ```bash
   cd src/ontology
   bash run.sh make update-shapes
   ```
5. **Build and release**:
   ```bash
   bash run.sh make all
   bash run.sh make prepare_release
   ```

---

## Benefits of This Approach

### For Facts:
- Standard CRM properties provide well-established semantics
- Direct relationships are clearer and simpler
- Queries are straightforward

### For Opinions:
- Full provenance tracking via PROV-O
- Track who said what, when, and based on what evidence
- Support for competing interpretations
- Revision history for evolving scholarly consensus
- Confidence levels for uncertain attributions
- Clear distinction from established facts

### Combined:
- SPARQL queries can filter facts vs opinions
- Temporal reasoning about how interpretations changed
- Attribution of responsibility for subjective claims
- Support for scholarly debate and discourse
- Clear evidence chains for all assertions

---

## CRM + PROV-O Mapping Summary

| Use Case | CRM Class | PROV-O Integration | CACAO Extension |
|----------|-----------|-------------------|-----------------|
| Opinion/Attribution | E13_Attribute_Assignment | prov:Entity + prov:wasAttributedTo | cacao:Opinion |
| Interpretation | E89_Propositional_Object | prov:Entity + prov:wasGeneratedBy | cacao:Interpretation |
| Assessment | E14_Condition_Assessment | prov:Activity + prov:used | cacao:Assessment |
| Expert/Scholar | E21_Person | prov:Person + prov:Agent | (inherit both) |
| Evidence/Source | E31_Document | prov:Entity + prov:hadPrimarySource | (inherit both) |
| Research Activity | E7_Activity | prov:Activity + prov:wasInformedBy | (inherit both) |

---

## Alignment with E13_Attribute_Assignment

CIDOC CRM's `E13_Attribute_Assignment` is specifically designed for tracking **subjective assignments**, making it the perfect partner for PROV-O:

**E13 Properties:**
- `P140_assigned_attribute_to` - what is being interpreted
- `P141_assigned` - the assigned value/interpretation
- `P177_assigned_property_of_type` - which property is being assigned
- `P14_carried_out_by` - who made the assignment (maps to `prov:wasAttributedTo`)
- `P4_has_time-span` - when (maps to `prov:generatedAtTime`)

**PROV-O enriches E13 with:**
- Detailed agent roles (expert, curator, researcher)
- Evidence chains (`prov:hadPrimarySource`, `prov:wasDerivedFrom`)
- Revision tracking (`prov:wasRevisionOf`)
- Alternative interpretations (`prov:alternateOf`)
- Qualified relations for complex provenance

---

## References

- **CIDOC CRM 7.1.3**: [https://www.cidoc-crm.org/](https://www.cidoc-crm.org/)
- **PROV-O**: [https://www.w3.org/TR/prov-o/](https://www.w3.org/TR/prov-o/)
- **ODK Documentation**: [https://github.com/INCATools/ontology-development-kit](https://github.com/INCATools/ontology-development-kit)
- **ROBOT Tool**: [http://robot.obolibrary.org/](http://robot.obolibrary.org/)

---

**Document created:** 2026-01-28
**CACAO version:** Current development branch
**Status:** Ready for import refresh
