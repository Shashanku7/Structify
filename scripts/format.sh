#!/bin/bash
# format.sh - Format and sort imports for the Structify project

echo "🛠 Running code formatting and import sorting..."

# Format Python code
echo "📦 Running black..."
black src/ tests/ || { echo "❌ Black formatting failed"; exit 1; }

# Sort imports
echo "🔀 Running isort..."
isort src/ tests/ || { echo "❌ isort failed"; exit 1; }

echo "✅ Formatting completed successfully!"