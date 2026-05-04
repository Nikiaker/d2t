# JSON to XML Converter for WebNLG Format

A Python utility to convert triples and generated text from JSON format into WebNLG XML format, similar to the Airport.xml structure.

## Features

- Converts `triples_by_instance` and `generated_text_by_instance` from JSON to XML
- Generates proper WebNLG XML structure with entries, triples, and lexicalizations
- Customizable category attribute via command-line argument
- Pretty-printed XML output for readability
- Emits `shape` and `shape_type` attributes for every entry, defaulting to empty strings when the JSON does not provide them

## Installation

No external dependencies required beyond Python 3.6+. The program uses only standard library modules (`json`, `xml.etree.ElementTree`, `argparse`, `pathlib`).

## Usage

```bash
python3 json_to_xml_converter.py <json_input_file> <category> [--output <output_file>]
```

### Arguments

- `json_input_file` (required): Path to the input JSON file containing `triples_by_instance` and `generated_text_by_instance` keys
- `category` (required): Category name to use for all entries in the XML (e.g., "Wikidata", "Airport", "Film")
- `--output`, `-o` (optional): Output XML file path (default: `output.xml`)

### Examples

```bash
# Convert with default output filename
python3 json_to_xml_converter.py tripler/outputs/test8/wikidata/extracted_triples_text_predicate_catalog.json "Wikidata"

# Convert with custom output filename
python3 json_to_xml_converter.py data.json "Airport" --output results.xml

# Using short option for output
python3 json_to_xml_converter.py data.json "Film" -o film_output.xml
```

## JSON Input Format

Expected structure:
```json
{
  "triples_by_instance": [
    {
      "instance_id": 0,
      "triples": [
        {
          "subject": "Entity",
          "predicate": "relation",
          "object": "Target"
        },
        ...
      ]
    },
    ...
  ],
  "generated_text_by_instance": [
    {
      "instance_id": 0,
      "text": "Generated text description"
    },
    ...
  ]
}
```

## XML Output Format

Generates XML matching WebNLG structure:
```xml
<?xml version='1.0' encoding='utf-8'?>
<benchmark>
  <entries>
    <entry category="YourCategory" eid="Id1" size="5">
      <originaltripleset>
        <otriple>Subject | predicate | Object</otriple>
        ...
      </originaltripleset>
      <modifiedtripleset>
        <mtriple>Subject | predicate | Object</mtriple>
        ...
      </modifiedtripleset>
      <lex comment="auto-generated" lid="Id1_1">Generated text here</lex>
    </entry>
    ...
  </entries>
</benchmark>
```

### Key Features of Output

- Each instance becomes an `<entry>` with unique `eid` (Id1, Id2, etc.)
- `category` attribute is set from command-line argument
- `size` attribute indicates the number of triples
- Both `originaltripleset` and `modifiedtripleset` contain the same triples (for simplicity)
- Generated text is placed in `lex` elements with auto-generated comment
- Triples are formatted as: `Subject | predicate | Object`

## Error Handling

The program includes error handling for:
- Missing input file
- Invalid JSON format
- Missing required JSON fields

## Performance

- Processes 100 instances with multiple triples efficiently
- Example: ~100 instances with 375 total triples converts in < 1 second

## Notes

- The program includes `shape` and `shape_type` attributes on every entry
- Those attributes are empty when the source JSON does not provide values
- Applied triples are identical in both `originaltripleset` and `modifiedtripleset`
- Each lex element has a comment of "auto-generated" for clarity
