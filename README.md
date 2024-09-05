# Lux Test Summarizer and Clusterer

This project contains two Python scripts that work together to summarize and analyze Lux test files:

1. `summarize_lux_tests.py`: Extracts information from Lux test files and creates a summary.
2. `cluster_tests.py`: Clusters the summarized tests based on content similarity.

## summarize_lux_tests.py

This script processes Lux test files (.lux) and generates a summary of their contents.

### Features:

- Recursively searches for .lux files in a given directory
- Extracts comments, [doc] descriptions, [invoke log] entries, and [progress] information
- Generates a summary file (lux_tests_summary.txt) with organized test information

### Usage:

```bash
    make venv
    ./venv/bin/python categorize-lux-tests.py
    ./venv/bin/python group-tests.py
```

