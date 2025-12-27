# Upgrading Python with asdf

This guide explains how to upgrade Python using asdf without affecting your system Python installation.

## ✅ Safety Guarantees

1. **asdf Python supports venv**: asdf installs a complete Python distribution, including the `venv` module
2. **No system conflicts**: asdf installs Python in `~/.asdf/installs/python/`, completely separate from system Python
3. **System Python untouched**: Your system Python (`/usr/bin/python3`) and Xcode Python remain unchanged
4. **Project-specific**: Using `asdf local` only affects this project directory

## 📋 Step-by-Step Instructions

### 1. Install asdf Python Plugin (if not already installed)

```bash
asdf plugin add python
```

### 2. Install Latest Python Version

Install the latest stable Python (3.14.x):

```bash
asdf install python latest
```

Or install a specific version:

```bash
asdf install python 3.14.2
```

### 3. Set Python Version for This Project

Set it locally (only affects this project):

```bash
cd /Users/lds/Documents/Workspace/Projects/cv-mailer
asdf local python latest
# or
asdf local python 3.14.2
```

This creates a `.tool-versions` file in your project root.

### 4. Verify the New Python Version

```bash
python3 --version
which python3
```

You should see the asdf-managed Python path: `~/.asdf/installs/python/...`

### 5. Remove Old Virtual Environment

```bash
rm -rf venv
```

### 6. Recreate Virtual Environment with New Python

```bash
python3 -m venv venv
```

### 7. Activate and Reinstall Dependencies

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -e ".[api,dev]"
```

### 8. Verify Everything Works

```bash
python3 --version  # Should show new version
cv-mailer --help   # Should work
cv-mailer-api --help  # Should work
```

## 🔍 Verification Commands

Check which Python is being used:

```bash
which python3
python3 --version
asdf current python
```

Check venv is using asdf Python:

```bash
readlink -f venv/bin/python3
# Should point to ~/.asdf/installs/python/...
```

## 📝 Notes

- The `.tool-versions` file will be created in your project root
- You can commit this file to ensure team members use the same Python version
- System Python remains at `/usr/bin/python3` and is unaffected
- Other projects can continue using their own Python versions

## 🚨 Troubleshooting

If `python3` still points to system Python after setting asdf local:

1. Make sure asdf is initialized in your shell:

   ```bash
   # Add to ~/.zshrc if not already there:
   . "$HOME/.asdf/asdf.sh"
   ```

2. Restart your terminal or reload shell:

   ```bash
   source ~/.zshrc
   ```

3. Verify asdf shims are in PATH:

   ```bash
   echo $PATH | grep asdf
   ```
