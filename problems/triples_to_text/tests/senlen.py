class Senlen:
    def compute(self, predictions: list[str], references: list[list[str]]) -> dict:
        prediction = predictions[0]
        reference_sentences = references[0]

        ref_lens = [len(ref.split(".")) for ref in reference_sentences]
        avg_ref_len = sum(ref_lens) / len(ref_lens) if ref_lens else 0.0

        pred_len = len(prediction.split("."))

        score = pred_len / avg_ref_len if avg_ref_len >= pred_len else avg_ref_len / pred_len

        return {"senlen": score}