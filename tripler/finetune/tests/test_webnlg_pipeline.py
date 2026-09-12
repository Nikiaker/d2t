import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree.ElementTree import parse

_TRIPLER = Path(__file__).resolve().parents[2]
_FINETUNE = _TRIPLER / "finetune"
sys.path.insert(0, str(_TRIPLER))
sys.path.insert(0, str(_FINETUNE))

from generate_webnlg import build_batch_jsonl, parse_batch_output  # noqa: E402
from merge_webnlg_test_xml import merge_test_xml  # noqa: E402
from prepare_webnlg_xml import package_json  # noqa: E402


class WebNlgPipelineTests(unittest.TestCase):
    def test_batch_requests_keep_instance_ids_and_joint_schema(self):
        lines = build_batch_jsonl(
            "served-model",
            [{"instance_id": 4, "data": {"name": "Example"}}],
            2048,
        ).splitlines()
        request = json.loads(lines[0])
        self.assertEqual(request["custom_id"], "instance-4")
        self.assertEqual(request["body"]["model"], "served-model")
        self.assertEqual(request["body"]["response_format"]["json_schema"]["name"], "instance_text_and_triples")
        self.assertIn('instance_context={"instance_id": 4, "data": {"name": "Example"}}',
                      request["body"]["messages"][1]["content"])

    def test_batch_parser_separates_success_and_error(self):
        success = {
            "custom_id": "instance-0",
            "response": {
                "body": {
                    "choices": [
                        {"message": {"content": '{"text":"A sentence.","triples":[{"subject":"A","predicate":"p","object":"B"}]}'}},
                    ]
                }
            },
        }
        failure = {"custom_id": "instance-1", "error": {"type": "upstream", "message": "failed"}}
        predictions, errors = parse_batch_output(
            json.dumps(success) + "\n" + json.dumps(failure) + "\n"
        )
        self.assertEqual(predictions[0]["text"], "A sentence.")
        self.assertEqual(predictions[0]["triples"][0]["predicate"], "p")
        self.assertIn(1, errors)

    def test_xml_packager_groups_supported_sizes_and_reports_skips(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "owid_dev_2994.json"
            source.write_text(
                json.dumps(
                    {
                        "triples_by_instance": [
                            {"instance_id": 0, "triples": [{"subject": "A", "predicate": "p", "object": "B"}]},
                            {"instance_id": 1, "triples": []},
                            {"instance_id": 2, "triples": [{"subject": "A", "predicate": "p", "object": "B"}] * 8},
                        ],
                        "generated_text_by_instance": [
                            {"instance_id": 0, "text": "A relates to B."},
                            {"instance_id": 1, "text": "No facts."},
                            {"instance_id": 2, "text": "A relates to B."},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_root = temp / "en"
            report = package_json(source, output_root, "Owid", "dev")
            xml_path = output_root / "dev" / "1triples" / "Owid.xml"
            self.assertTrue(xml_path.is_file())
            self.assertEqual(len(parse(xml_path).findall(".//entry")), 1)
            self.assertEqual(report["accepted_instances"], 1)
            reasons = {item["reason"] for item in report["skipped"]}
            self.assertEqual(reasons, {"no_triples", "unsupported_triple_count"})

            package_json(source, output_root, "Owid", "test")
            merged = temp / "test" / "rdf-to-text-generation-test-data-with-refs-seed-2994.xml"
            self.assertEqual(merge_test_xml(None, output_root, merged), 1)
            self.assertEqual(len(parse(merged).findall(".//entry")), 1)


if __name__ == "__main__":
    unittest.main()
