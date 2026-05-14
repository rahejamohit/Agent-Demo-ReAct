# VS Code Setup Guide for Python Development

## 🚀 Quick Setup (2 minutes)

### Step 1: Run the Extension Installer

**On macOS/Linux:**
```bash
bash install-extensions.sh
```

**On Windows:**
```bash
install-extensions.bat
```

This will automatically install all 11 recommended extensions.

---

## ✅ What Gets Installed

| Extension | Purpose | ID |
|-----------|---------|-----|
| Python | Core Python support | `ms-python.python` |
| Pylance | Advanced IntelliSense | `ms-python.vscode-pylance` |
| Python Debugger | Debug Python apps | `ms-python.debugpy` |
| Pylint | Code linting | `ms-python.pylint` |
| Black Formatter | Auto-format code | `ms-python.black-formatter` |
| REST Client | Test APIs in VS Code | `humao.rest-client` |
| Error Lens | Show errors inline | `usernamehw.errorlens` |
| Better Comments | Color-coded comments | `aaron-bond.better-comments` |
| Trailing Spaces | Highlight whitespace | `shardulm94.trailing-spaces` |
| JSON Support | JSON file handling | `ms-json.json-language-features` |
| FastAPI Snippets | FastAPI code snippets | `DRMWNM.fastapi-snippets` |

---

## 📝 Step 2: Configure Python Interpreter

After installing extensions:

1. **Open VS Code** in your project folder:
   ```bash
   code .
   ```

2. **Select Python Interpreter**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type: `Python: Select Interpreter`
   - Choose: The one with `./venv/bin/python` or `venv\Scripts\python.exe`

3. **Verify Selection**:
   - Check bottom right of VS Code
   - Should show Python version (e.g., "3.11.x ('venv')")

---

## 🎯 Pre-Configured Settings

The project includes `.vscode/settings.json` with:
- ✅ **Auto-format on save** (Black formatting)
- ✅ **Type checking** (Pylance)
- ✅ **Linting** (Pylint)
- ✅ **Code organization** (Import sorting)
- ✅ **Editor rulers** (80, 100, 120 character markers)
- ✅ **Hidden cache files** (`__pycache__`, `.pyc`)

No additional configuration needed!

---

## 🐛 Debugging Configuration

The project includes `.vscode/launch.json` with pre-configured debug profiles:

### Debug Current Python File
1. Open any `.py` file
2. Press `F5` or click "Run" → "Start Debugging"
3. Choose: `Python: Current File`

### Debug FastAPI App
1. Press `F5`
2. Choose: `FastAPI: Main App`
3. API starts on `http://localhost:8080`
4. Set breakpoints and step through code

### Debug Example Usage
1. Press `F5`
2. Choose: `Python: Example Usage`
3. Runs the example client

### Debug Tests
1. Press `F5`
2. Choose: `Python: Debug Tests`
3. Runs pytest in debug mode

---

## 💡 Pro Tips

### 1. **IntelliSense & Auto-Completion**
- Type `from models import` and press `Ctrl+Space`
- See all available imports with documentation
- Pylance shows type hints in real-time

### 2. **Format Code**
- Press `Shift+Alt+F` (Windows/Linux) or `Shift+Option+F` (Mac)
- Automatically formats to Black style
- Or save file (auto-format on save enabled)

### 3. **Quick Error Fix**
- Hover over red squiggle
- Click "Quick Fix" or press `Ctrl+.`
- Auto-corrects common issues

### 4. **Run Tests**
- Click "Testing" icon in sidebar
- Auto-discovers test files
- Run individual tests with one click

### 5. **Terminal Integration**
- Press `` Ctrl+` `` to open integrated terminal
- Terminal automatically uses project's Python environment
- Ready to run commands

### 6. **REST Client - Test APIs**
Create file `test-api.http`:
```http
@baseUrl = http://localhost:8080

### Health Check
GET {{baseUrl}}/health

### Search Flights
POST {{baseUrl}}/api/v1/flights/search
Content-Type: application/json

{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1,
  "cabin_class": "economy"
}
```

Click "Send Request" above each request!

---

## 🔍 Verify Everything Works

### Test 1: Syntax Highlighting
1. Open `main.py`
2. Should see color-coded syntax (blue for keywords, etc.)

### Test 2: IntelliSense
1. Type `flight_service.` 
2. Should see dropdown with available methods
3. Hover over method to see documentation

### Test 3: Format on Save
1. Open `main.py`
2. Press `Ctrl+Z` to mess up formatting
3. Save file (`Ctrl+S`)
4. Should auto-format back to Black style

### Test 4: Linting
1. Add a typo or unused import
2. Should see red squiggle with error message
3. Hover to see details

---

## ❌ Troubleshooting

### Extensions not installing?
- Ensure you have `code` command in PATH
- In VS Code: `Cmd+Shift+P` → "Shell Command: Install code command in PATH"
- Restart terminal and try again

### IntelliSense not working?
- Check Python interpreter is selected (bottom right)
- Click reload (bottom right)
- Wait 10 seconds for Pylance to analyze

### Format not working on save?
- Check settings file exists: `.vscode/settings.json`
- Verify Black is installed: `pip list | grep black`
- Try manual format: `Shift+Alt+F`

### Debugger not starting?
- Ensure Python extension is installed
- Check Python interpreter is selected
- Try `F5` and select the debug configuration

---

## 📚 Keyboard Shortcuts Cheat Sheet

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Format Code | `Shift+Alt+F` | `Shift+Option+F` |
| Quick Fix | `Ctrl+.` | `Cmd+.` |
| Go to Definition | `F12` | `F12` |
| Find All References | `Ctrl+Shift+H` | `Cmd+Shift+H` |
| Rename Symbol | `F2` | `F2` |
| Toggle Terminal | `` Ctrl+` `` | `` Cmd+` `` |
| Start Debugging | `F5` | `F5` |
| Step Over | `F10` | `F10` |
| Step Into | `F11` | `F11` |
| Step Out | `Shift+F11` | `Shift+F11` |

---

## 🎓 Next: Start Coding!

1. **Setup complete** ✅
2. **Open project**: `code .`
3. **Create new file**: `test.py`
4. **Write Python**: Let IntelliSense help you
5. **Run file**: `F5` → `Python: Current File`
6. **Debug**: Set breakpoints and step through

**Happy coding! 🚀**
