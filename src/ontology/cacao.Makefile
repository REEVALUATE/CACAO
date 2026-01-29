## Customize Makefile settings for cacao
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

# WIDOCO configuration
WIDOCO_VERSION ?= v1.4.25
WIDOCO_CONFIG = ../../widoco-config
WIDOCO_OUTPUT = ../../docs/ontology

documentation:
  documentation_system: mkdocs

# Generate WIDOCO HTML documentation from the ontology using Docker
.PHONY: widoco
widoco: $(ONT)-full.owl
	@echo "Generating WIDOCO documentation using Docker..."
	mkdir -p $(WIDOCO_OUTPUT)
	docker run --rm \
		-v $(shell cd ../..; pwd):/work \
		-w /work/src/ontology \
		dgarijo/widoco:$(WIDOCO_VERSION) \
		-ontFile cacao-full.owl \
		-outFolder /work/docs/ontology \
		-confFile /work/widoco-config \
		-webVowl \
		-rewriteAll
	@echo "WIDOCO documentation generated in $(WIDOCO_OUTPUT)"
	@echo "Open $(WIDOCO_OUTPUT)/index.html in your browser to view"

# Clean WIDOCO artifacts
.PHONY: clean-widoco
clean-widoco:
	rm -rf $(WIDOCO_OUTPUT)
	@echo "WIDOCO documentation cleaned"