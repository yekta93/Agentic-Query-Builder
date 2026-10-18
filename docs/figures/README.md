# Evaluation figures

Add the chart images here (from the experimental study):

| File | Description |
|------|-------------|
| `accuracy_by_model.jpg` | Configuration comparison — Accuracy |
| `cost_by_model.jpg` | Configuration comparison — Cost |

Copy from your local attachments or the original experiment export:

```bash
mkdir -p docs/figures
cp /path/to/acc.jpg  docs/figures/accuracy_by_model.jpg
cp /path/to/cost.jpg docs/figures/cost_by_model.jpg
git add docs/figures/*.jpg
git commit -m "Add evaluation charts"
git push
```
