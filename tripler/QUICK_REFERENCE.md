# Quick Reference: JSON to XML Converter

## Installation
```bash
# Make executable (optional)
chmod +x json_to_xml_converter.py
```

## Quick Start
```bash
# Most basic usage (outputs to output.xml)
python3 json_to_xml_converter.py input.json "YourCategory"

# With custom output file
python3 json_to_xml_converter.py input.json "YourCategory" -o result.xml
```

## Common Use Cases

### Convert Wikidata
```bash
python3 json_to_xml_converter.py tripler/outputs/test8/wikidata/extracted_triples_text_predicate_catalog.json "Wikidata"
```

### Convert to different categories
```bash
# Airport data
python3 json_to_xml_converter.py data.json "Airport" -o airports.xml

# Film/Movie data
python3 json_to_xml_converter.py data.json "Film" -o films.xml

# Person data
python3 json_to_xml_converter.py data.json "Person" -o people.xml

# Custom category
python3 json_to_xml_converter.py data.json "MySpecialCategory" -o output.xml
```

## Command Options

| Option | Short | Purpose | Default |
|--------|-------|---------|---------|
| `--output` | `-o` | Output file path | `output.xml` |
| `--help` | `-h` | Show help message | - |

## Example Output Structure

**Input JSON:**
- Instance with 5 triples about "Vanuatu"
- Generated text: "Vanuatu is a UNESCO member..."

**Output XML Entry:**
```xml
<entry category="Wikidata" eid="Id1" size="5">
  <originaltripleset>
    <otriple>Vanuatu | is_member_of | UNESCO</otriple>
    ...
  </originaltripleset>
  <modifiedtripleset>
    <mtriple>Vanuatu | is_member_of | UNESCO</mtriple>
    ...
  </modifiedtripleset>
  <lex comment="auto-generated" lid="Id1_1">
    Vanuatu is a UNESCO member...
  </lex>
</entry>
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "File not found" | Check JSON file path is correct |
| "Invalid JSON" | Validate JSON format with `python3 -m json.tool file.json` |
| Permission denied | Run `chmod +x json_to_xml_converter.py` |
| Wrong output file | Use `-o` or `--output` option to specify path |

## Notes

- **Category argument is required** - specifies the category for all entries
- **Output file defaults to `output.xml`** in current directory
- **UTF-8 encoding** - supports special characters
- **Pretty-printed** - readable indented XML format
- **Size attribute** - automatically set to number of triples per entry
- **Auto-generated IDs** - entries labeled Id1, Id2, Id3, etc.

## Validation

Check generated XML:
```bash
# Count entries
grep -c "<entry" output.xml

# View first entry
head -50 output.xml

# Validate XML
python3 -m xml.etree.ElementTree output.xml
```
