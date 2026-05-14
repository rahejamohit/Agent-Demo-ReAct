#!/bin/bash

# VS Code Python Development Extensions Installer
# This script installs all recommended Python extensions

echo "🚀 Installing VS Code Python Extensions"
echo "=========================================="
echo ""

# Check if code command is available
if ! command -v code &> /dev/null; then
    echo "❌ VS Code 'code' command not found"
    echo "   Please ensure VS Code is installed and in your PATH"
    echo ""
    echo "   To add VS Code to PATH:"
    echo "   1. Open VS Code"
    echo "   2. Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)"
    echo "   3. Type 'Shell Command: Install code command in PATH'"
    exit 1
fi

echo "✅ VS Code found"
echo ""

# Essential Extensions
echo "📦 Installing ESSENTIAL extensions..."
echo ""

extensions=(
    # Essential
    "ms-python.python"
    "ms-python.vscode-pylance"
    "ms-python.debugpy"

    # Linting & Formatting
    "ms-python.pylint"
    "ms-python.black-formatter"

    # API Testing
    "humao.rest-client"

    # Code Quality
    "usernamehw.errorlens"
    "aaron-bond.better-comments"
    "shardulm94.trailing-spaces"

    # JSON Support
    "ms-json.json-language-features"

    # FastAPI Snippets
    "DRMWNM.fastapi-snippets"
)

# Install each extension
for extension in "${extensions[@]}"; do
    echo "⏳ Installing: $extension"
    code --install-extension "$extension" 2>&1 | grep -E "(Install|already|Successfully)" || true
done

echo ""
echo "=========================================="
echo "✅ Extension installation complete!"
echo ""
echo "🔄 Next steps:"
echo "   1. Reload VS Code (Ctrl+R or Cmd+R)"
echo "   2. Select your Python interpreter:"
echo "      - Press Ctrl+Shift+P (Cmd+Shift+P on Mac)"
echo "      - Type 'Python: Select Interpreter'"
echo "      - Choose the venv in your project folder"
echo ""
echo "📚 Verify setup:"
echo "   - Create a test Python file"
echo "   - You should see syntax highlighting & IntelliSense"
echo ""
