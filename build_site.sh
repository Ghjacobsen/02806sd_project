#!/usr/bin/env bash
# Build script: run notebook → copy artifacts to site/
set -e

cd "$(dirname "$0")/.."
ROOT=$(pwd)

echo "=== Activating virtualenv ==="
source .venv/bin/activate 2>/dev/null || true

echo "=== Running notebook ==="
cd notebooks
jupyter nbconvert --to notebook --execute Assignment2_Final.ipynb \
    --output Assignment2_Final_executed.ipynb \
    --ExecutePreprocessor.timeout=600

echo "=== Copying artifacts to site/ ==="
cd "$ROOT"
# Static image
cp reports/figures/viz1_civil_sidewalks.png site/images/
cp reports/figures/viz1_civil_sidewalks.svg site/images/ 2>/dev/null || true

# Interactive visualizations
cp reports/figures/viz2_dualmap.html site/visualizations/
cp reports/figures/viz3_interactive_trends.html site/visualizations/

echo "=== Build complete ==="
echo "Site files:"
find site/ -type f | sort
echo ""
echo "Preview locally: cd site && python -m http.server 8000"
echo "Then open: http://localhost:8000"
