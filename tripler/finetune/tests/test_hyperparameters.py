import subprocess
import unittest
from pathlib import Path


FINETUNE_DIR = Path(__file__).resolve().parents[1]
EXPERIMENTS_SCRIPT = FINETUNE_DIR / "experiments.sh"
SCRIPTS_DIR = FINETUNE_DIR / "scripts"
TRAIN_SCRIPT = FINETUNE_DIR / "train_qlora.py"


EXPECTED = {
    "baseline": {
        "TRAIN_EPOCHS": "3",
        "TRAIN_LR": "1e-4",
        "TRAIN_WARMUP_RATIO": "0.03",
        "TRAIN_LORA_R": "16",
        "TRAIN_LORA_ALPHA": "32",
        "TRAIN_LORA_DROPOUT": "0.05",
        "TRAIN_WEIGHT_DECAY": "0.0",
    },
    "low_lr": {
        "TRAIN_EPOCHS": "5",
        "TRAIN_LR": "3e-5",
        "TRAIN_WARMUP_RATIO": "0.05",
        "TRAIN_LORA_R": "16",
        "TRAIN_LORA_ALPHA": "32",
        "TRAIN_LORA_DROPOUT": "0.05",
        "TRAIN_WEIGHT_DECAY": "0.01",
    },
    "higher_capacity": {
        "TRAIN_EPOCHS": "3",
        "TRAIN_LR": "5e-5",
        "TRAIN_WARMUP_RATIO": "0.05",
        "TRAIN_LORA_R": "32",
        "TRAIN_LORA_ALPHA": "64",
        "TRAIN_LORA_DROPOUT": "0.05",
        "TRAIN_WEIGHT_DECAY": "0.01",
    },
    "regularized_capacity": {
        "TRAIN_EPOCHS": "5",
        "TRAIN_LR": "3e-5",
        "TRAIN_WARMUP_RATIO": "0.10",
        "TRAIN_LORA_R": "32",
        "TRAIN_LORA_ALPHA": "64",
        "TRAIN_LORA_DROPOUT": "0.10",
        "TRAIN_WEIGHT_DECAY": "0.01",
    },
}


class HyperparameterTests(unittest.TestCase):
    def _load_experiment(self, name):
        keys = list(EXPECTED["baseline"])
        command = (
            f'source "{EXPERIMENTS_SCRIPT}"; '
            f'configure_experiment "{name}"; '
            + " ".join(f'printf "%s=%s\\n" {key} "${key}";' for key in keys)
        )
        result = subprocess.run(["bash", "-c", command], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return dict(line.split("=", 1) for line in result.stdout.splitlines())

    def test_experiment_values(self):
        for name, expected in EXPECTED.items():
            with self.subTest(experiment=name):
                self.assertEqual(self._load_experiment(name), expected)

    def test_experiment_values_are_valid(self):
        for name, values in EXPECTED.items():
            with self.subTest(experiment=name):
                self.assertGreater(float(values["TRAIN_EPOCHS"]), 0)
                self.assertGreater(float(values["TRAIN_LR"]), 0)
                self.assertGreaterEqual(float(values["TRAIN_WARMUP_RATIO"]), 0)
                self.assertLess(float(values["TRAIN_WARMUP_RATIO"]), 1)
                self.assertGreater(int(values["TRAIN_LORA_R"]), 0)
                self.assertGreater(int(values["TRAIN_LORA_ALPHA"]), 0)
                self.assertGreaterEqual(float(values["TRAIN_LORA_DROPOUT"]), 0)
                self.assertLess(float(values["TRAIN_LORA_DROPOUT"]), 1)
                self.assertGreaterEqual(float(values["TRAIN_WEIGHT_DECAY"]), 0)

    def test_unknown_experiment_fails(self):
        result = subprocess.run(
            ["bash", "-c", f'source "{EXPERIMENTS_SCRIPT}"; configure_experiment invalid'],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_all_domain_batches_use_shared_experiments(self):
        for kind in ("finetune", "eval"):
            for domain in ("gsmarena", "openweather", "owid", "wikidata"):
                path = SCRIPTS_DIR / f"batch_{kind}_{domain}.sh"
                content = path.read_text(encoding="utf-8")
                with self.subTest(kind=kind, domain=domain):
                    self.assertIn('EXPERIMENT="${EXPERIMENT:-baseline}"', content)
                    self.assertIn('source "$D2TPATH/tripler/finetune/experiments.sh"', content)
                    if kind == "finetune":
                        self.assertIn('--weight-decay "$TRAIN_WEIGHT_DECAY"', content)
                        self.assertIn('checkpoint-100', content)
                        self.assertIn('checkpoint-150', content)
                    else:
                        self.assertIn('--model checkpoint-100', content)
                        self.assertIn('--model checkpoint-150', content)

    def test_all_domain_launcher_covers_every_variant(self):
        content = (FINETUNE_DIR / "run_hyperparameter_experiments.sh").read_text(encoding="utf-8")
        for experiment in EXPECTED:
            if experiment != "baseline":
                self.assertIn(experiment, content)
        for domain in ("gsmarena", "openweather", "owid", "wikidata"):
            self.assertIn("batch_finetune_${domain}.sh", content)
            self.assertIn("batch_eval_${domain}.sh", content)

    def test_training_script_accepts_weight_decay_and_retains_checkpoints(self):
        content = TRAIN_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--weight-decay", type=float, default=0.0)', content)
        self.assertIn("weight_decay=args.weight_decay", content)
        self.assertIn("save_total_limit=5", content)


if __name__ == "__main__":
    unittest.main()
