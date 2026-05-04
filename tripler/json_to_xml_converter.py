#!/usr/bin/env python3
"""
Convert JSON triples and generated text to WebNLG XML format.

Usage:
    python json_to_xml_converter.py <json_input_file> <category> [--output <output_file>]

Example:
    python json_to_xml_converter.py tripler/outputs/test8/wikidata/extracted_triples_text_predicate_catalog.json "Wikidata" --output output.xml
"""

import json
import sys
import argparse
from xml.etree.ElementTree import Element, SubElement, ElementTree
from pathlib import Path
from typing import Dict, Any


def load_json_data(json_file: str) -> Dict[str, Any]:
    """Load JSON data from file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_triple_string(triple: Dict[str, str]) -> str:
    """Create a triple string from subject, predicate, object."""
    subject = triple.get('subject', '')
    predicate = triple.get('predicate', '')
    obj = triple.get('object', '')
    return f"{subject} | {predicate} | {obj}"


def create_xml_tree(data: Dict[str, Any], category: str) -> Element:
    """Create XML tree structure matching WebNLG format."""
    
    # Root element
    benchmark = Element('benchmark')
    entries_elem = SubElement(benchmark, 'entries')
    
    # Get the triples and texts
    triples_by_instance = data.get('triples_by_instance', [])
    generated_texts = data.get('generated_text_by_instance', [])
    
    # Create mapping of instance_id to texts for quick lookup
    texts_map = {item['instance_id']: item['text'] for item in generated_texts}
    
    # Process each instance
    for triples_item in triples_by_instance:
        instance_id = triples_item.get('instance_id', 0)
        triples_list = triples_item.get('triples', [])
        shape = triples_item.get('shape', '')
        shape_type = triples_item.get('shape_type', '')
        
        if not triples_list:
            continue
        
        # Get the generated text for this instance
        generated_text = texts_map.get(instance_id, '')
        
        # Create entry element
        entry_id = f"Id{instance_id + 1}"
        entry = SubElement(entries_elem, 'entry')
        entry.set('category', category)
        entry.set('eid', entry_id)
        entry.set('shape', shape)
        entry.set('shape_type', shape_type)
        entry.set('size', str(len(triples_list)))
        
        # Create original tripleset
        orig_tripleset = SubElement(entry, 'originaltripleset')
        for triple in triples_list:
            triple_str = create_triple_string(triple)
            otriple = SubElement(orig_tripleset, 'otriple')
            otriple.text = triple_str
        
        # Create modified tripleset (same as original for simplicity)
        mod_tripleset = SubElement(entry, 'modifiedtripleset')
        for triple in triples_list:
            triple_str = create_triple_string(triple)
            mtriple = SubElement(mod_tripleset, 'mtriple')
            mtriple.text = triple_str
        
        # Create lex element with generated text
        if generated_text:
            lex = SubElement(entry, 'lex')
            lex.set('comment', 'auto-generated')
            lex.set('lid', f"{entry_id}_1")
            lex.text = generated_text
    
    return benchmark


def prettify_xml(elem: Element, level: int = 0) -> str:
    """Return a pretty-printed XML string."""
    indent = "\n" + level * "  "
    
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        
        for child in elem:
            prettify_xml(child, level + 1)
        
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def write_xml_file(root: Element, output_file: str) -> None:
    """Write XML tree to file."""
    prettify_xml(root)
    tree = ElementTree(root)
    
    # Write with XML declaration
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<?xml version='1.0' encoding='utf-8'?>\n")
        tree.write(f, encoding='unicode', xml_declaration=False)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON triples to WebNLG XML format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tripler/outputs/test8/wikidata/extracted_triples_text_predicate_catalog.json "Wikidata"
  %(prog)s data.json "Airport" --output output.xml
        """
    )
    
    parser.add_argument('json_file', help='Path to input JSON file')
    parser.add_argument('category', help='Category name to use in XML entries')
    parser.add_argument('--output', '-o', 
                        help='Output XML file (default: output.xml)',
                        default='output.xml')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.json_file).exists():
        print(f"Error: Input file '{args.json_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load JSON data
        print(f"Loading JSON from '{args.json_file}'...")
        data = load_json_data(args.json_file)
        
        # Create XML tree
        print(f"Converting to XML with category '{args.category}'...")
        root = create_xml_tree(data, args.category)
        
        # Write to file
        print(f"Writing XML to '{args.output}'...")
        write_xml_file(root, args.output)
        
        # Count entries
        entries_count = len(root.findall('.//entry'))
        print(f"✓ Successfully created XML with {entries_count} entries")
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
