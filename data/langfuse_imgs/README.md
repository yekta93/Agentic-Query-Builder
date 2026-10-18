# Langfuse Traces (Screenshots)

Screenshots from Langfuse while tracing the multi-agent LangGraph pipeline.

| File | Description |
|------|-------------|
| `trace_overview.png` | Overview of traces in Langfuse UI |
| `trace_detail_1.png` | Detailed trace – node timeline |
| `trace_detail_2.png` | Detailed trace – LLM span |
| `trace_detail_3.png` | Detailed trace – generation step |
| `trace_detail_4.png` | Detailed trace – reflection / retry |
| `trace_detail_5.png` | Detailed trace – full run |

## How to materialize the PNG files

```bash
python scripts/extract_langfuse_imgs.py
git add data/langfuse_imgs/*.png
git commit -m "Add Langfuse screenshot PNGs"
git push
```

Requires that the source repository is reachable (or copy the files from your local `Generate-Query-Language/data/langfuse_imgs/` folder).

If the original repo is private, copy locally instead:

```bash
mkdir -p data/langfuse_imgs
cp /path/to/Generate-Query-Language/data/langfuse_imgs/image.png data/langfuse_imgs/trace_overview.png
cp "/path/to/Generate-Query-Language/data/langfuse_imgs/image (1).png" data/langfuse_imgs/trace_detail_1.png
cp "/path/to/Generate-Query-Language/data/langfuse_imgs/image (2).png" data/langfuse_imgs/trace_detail_2.png
cp "/path/to/Generate-Query-Language/data/langfuse_imgs/image (3).png" data/langfuse_imgs/trace_detail_3.png
cp "/path/to/Generate-Query-Language/data/langfuse_imgs/image (4).png" data/langfuse_imgs/trace_detail_4.png
cp "/path/to/Generate-Query-Language/data/langfuse_imgs/image (5).png" data/langfuse_imgs/trace_detail_5.png
```
