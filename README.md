# LLM Rewrite Pipeline (HKUST RA Project)

This repository contains a lightweight, multi-threaded pipeline for rewriting large-scale text datasets using LLMs. The system supports GPT-based models, Doubao, and DeepSeek, with safe placeholder configuration for all API endpoints.

## Features
- Multi-threaded processing (up to 64 workers)
- Supports multiple LLM providers (configurable)
- Robust retry mechanism for failed requests
- JSONL input / output for easy dataset handling
- Post-processing: filtering, deduplication, sentence splitting
- All sensitive configuration removed (safe for open-source)

## How It Works
1. Load a JSONL dataset where each line contains:
   - Title
   - Conclusion text
   - Source / organization info
2. Construct a rewriting prompt while preserving meaning, style, and length.
3. Send requests to the selected LLM provider.
4. Save outputs into a new JSONL file.
5. Optionally generate a flat corpus file (`kuochong_data.txt`).

## File
- `rewrite_pipeline.py` — main pipeline script

## Usage
1. Fill in your API server URLs and keys at the top of the script:
YOUR_SERVER_URL = "..."
YOUR_API_KEY = "..."
YOUR_ACCESS_KEY = "..."
YOUR_MODEL_ENDPOINT = "..."
GPT_SERVER_URL = "..."
2. Run:
python rewrite_pipeline.py

## Notes
- This repo contains no API keys or private endpoints.
- All placeholders must be replaced locally before running.
- Intended for research and dataset generation.

