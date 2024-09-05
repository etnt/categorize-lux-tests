# Lux Test Summarizer and Clusterer

This project contains two Python scripts that work together to summarize and analyze Lux test files:

1. `categorize-lux-tests.py`: Extracts information from Lux test files and creates a summary.
2. `group-tests.py`: Clusters the summarized tests based on content similarity.

## categorize-lux-tests.py

This script processes Lux test files (.lux) and generates a summary of their contents.

### Features:

- Recursively searches for .lux files in a given directory
- Extracts comments, [doc] descriptions, [invoke log] entries, and [progress] information
- Generates a summary file (lux_tests_summary.txt) with organized test information

## group-tests.py

This script organizes Lux tests into groups based on their common attributes found in the test files.

### Features:

- Identifies common attributes or tags within test files
- Groups tests based on shared characteristics
- Generates a report of test groups with their common attributes


## Usage:

```bash
    make venv
    ./venv/bin/python categorize-lux-tests.py
    ./venv/bin/python group-tests.py [--num-clusters NUM_CLUSTERS]
```


