from rdflib import Graph, Namespace, URIRef, BNode
from rdflib.namespace import RDF, SH
import re
import hashlib

def sanitize_uri(uri):
    return re.split(r'[/#]', str(uri))[-1]

def create_property_shape_uri(path_uri,base_ns):
    path_fragment = sanitize_uri(path_uri)
    return URIRef(f"{base_ns}{path_fragment}")

def create_node_shape_uri(target_classes, base_ns):
    class_names = [sanitize_uri(cls) for cls in sorted(target_classes, key=lambda x: str(x))]
    name = "_".join(class_names)
    return URIRef(f"{base_ns}{name}")

def update_shape_identifiers(input_file, output_file, base_ns_uri):
    base_ns = Namespace(base_ns_uri)
    g = Graph()
    g.parse(input_file, format="turtle")

    g.bind("", base_ns)

    replacement_map = {}

    # Rename NodeShapes
    for s in g.subjects(RDF.type, SH.NodeShape):
        target_classes = list(g.objects(s, SH.targetClass))
        if target_classes:
            new_uri = create_node_shape_uri(target_classes, base_ns)
            replacement_map[s] = new_uri

    # Rename PropertyShapes
    for shape in g.subjects(RDF.type, SH.PropertyShape):
        path = next(g.objects(shape, SH.path), None)
        if path and isinstance(path, URIRef):
            # Try to find the parent NodeShape that links to this property shape
            # for parent in g.subjects(SH.property, shape):
            #     if parent in replacement_map:
            #         parent_shape = replacement_map[parent]
            #     else:
            #         parent_shape = parent
            new_prop_uri = create_property_shape_uri(path, base_ns)
            replacement_map[shape] = new_prop_uri
                # break

    # Rebuild graph with updated URIs
    new_graph = Graph()
    for s, p, o in g:
        new_s = replacement_map.get(s, s)
        new_o = replacement_map.get(o, o) if isinstance(o, (URIRef, BNode)) else o
        new_graph.add((new_s, p, new_o))

    new_graph.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    input_file = "shapes/cacao-owl2shacl.ttl"  # Replace with actual input path
    output_file = "shapes/cacao-shacl.ttl"
    base_ns_uri = "http://w3id.org/cacao/shapes/"
    update_shape_identifiers(input_file, output_file, base_ns_uri)
