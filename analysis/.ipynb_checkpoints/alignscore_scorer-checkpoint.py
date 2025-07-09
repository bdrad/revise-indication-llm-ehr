import torch
import torch.nn as nn
from alignscore import AlignScore
import argparse
import pandas as pd

class AlignScorer(nn.Module):
    def __init__(self):
        super(AlignScorer, self).__init__()
        self.align_scorer = AlignScore(
            model='roberta-base', 
            device='cuda:0',
            batch_size=32, 
            ckpt_path='AlignScore-base.ckpt', 
            evaluation_mode='nli_sp')

    def forward(self, refs, hyps):
        f = self.align_scorer.score(
            contexts=refs,
            claims=hyps,
        )
        return f

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate using AlignScore")
    parser.add_argument("--csv_path", required=True, help="Input CSV path with 'reference' and 'generated' columns")
    parser.add_argument("--output_path", required=True, help="Output CSV path to save scores")
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path)

    align_scorer = AlignScorer()
    scores = align_scorer(
        refs=data['reference'].fillna("None").tolist(),
        hyps=data['generated'].fillna("None").tolist()
    )
    data['align_score'] = scores
    data.to_csv(args.output_path, index=False)