# Generating WIDOCO Documentation

This guide explains how to generate the ontology reference documentation using WIDOCO.

## What is WIDOCO?

WIDOCO (WIzard for DOCumenting Ontologies) automatically generates HTML documentation from your OWL ontology file. It creates a comprehensive reference showing:

- All classes and their hierarchies
- All properties with domains and ranges
- Visual diagrams
- Cross-references and relationships
- Import information

## Prerequisites

- Java 8 or higher installed
- Built ontology file (`cacao-full.owl`)

## Generating Documentation

### Using the Makefile (Recommended)

```bash
cd src/ontology

# On Windows (Git Bash or WSL):
bash run.sh make widoco

# On Linux/Mac:
./run.sh make widoco

# Or directly without Docker:
make widoco
```

This will:
1. Download WIDOCO if needed (stored in `src/ontology/tmp/`)
2. Generate HTML documentation to `docs/ontology/`
3. Include WebVOWL visualizations

### Manual Generation

If you prefer to run WIDOCO manually:

```bash
cd src/ontology

# Download WIDOCO (if not already present)
curl -L https://github.com/dgarijo/Widoco/releases/download/v1.4.25/widoco-1.4.25-jar-with-dependencies.jar -o tmp/widoco.jar

# Generate documentation
java -jar tmp/widoco.jar \
  -ontFile cacao-full.owl \
  -outFolder ../../docs/ontology \
  -confFile ../../widoco-config \
  -webVowl \
  -rewriteAll
```

## Output

The generated documentation will be in `docs/ontology/`:
- `index.html` - Main documentation page
- `sections/` - Individual sections (introduction, overview, etc.)
- `webvowl/` - Interactive visualization

## Configuration

Edit [`widoco-config`](../../widoco-config) in the root directory to customize:
- Abstract and description
- Authors and contributors
- License information
- Version details
- Related resources

## Cleaning Up

To remove generated WIDOCO documentation:

```bash
cd src/ontology
make clean-widoco
```

## Including in MkDocs

The WIDOCO documentation is standalone HTML. To link it from the MkDocs site, we've added a link in the main [index.md](index.md).

## Troubleshooting

### Java Not Found
Ensure Java is installed and in your PATH:
```bash
java -version
```

### Out of Memory
If WIDOCO runs out of memory with large ontologies:
```bash
java -Xmx4G -jar tmp/widoco.jar ...
```

### File Not Found
Make sure you've built the ontology first:
```bash
cd src/ontology
./run.sh make all
```
