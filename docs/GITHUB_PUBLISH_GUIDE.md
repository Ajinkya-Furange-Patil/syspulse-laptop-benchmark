# Complete Guide: Publishing SysPulse to GitHub (Public Repository)

This guide walks you through publishing this repository to GitHub step-by-step. It is designed for students and developers who want to share their work publicly with the global developer community.

---

## 🚀 Fast Track: 1-Command Push via GitHub CLI (Recommended)

Since your system already has **GitHub CLI (`gh`)** authenticated as **`Ajinkya-Furange-Patil`**, you can create the public repository and push all code directly from your terminal in seconds!

### Step 1: Initialize Git and Commit Files
Open PowerShell in this project folder (`d:\College Work\Personal Work\stress test`) and run:

```powershell
# 1. Initialize local Git repository
git init

# 2. Add all files (respecting .gitignore)
git add .

# 3. Create your initial commit
git commit -m "feat: initial release of SysPulse all-in-one laptop benchmark & 34-point buyer audit suite"

# 4. Set default branch to main
git branch -M main
```

### Step 2: Create Public GitHub Repository and Push
Run this single command:

```powershell
gh repo create syspulse-laptop-benchmark --public --source=. --remote=origin --push --description "All-in-one C++20 and CUDA hardware benchmark, thermal stress test, and 34-point laptop buying inspection suite with interactive HTML reports."
```

*(You can replace `syspulse-laptop-benchmark` with whatever repository name you prefer!)*

That's it! Your repository will immediately be live on GitHub at:
`https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark`

---

## 🌐 Alternative: Standard Git & Browser Method

If you prefer using the GitHub web interface:

### 1. Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Set **Repository name**: e.g. `syspulse-laptop-benchmark` or `pc-stress-benchmark`.
3. Set Visibility to **Public**.
4. **DO NOT** check "Add a README file", ".gitignore", or "Choose a license" (we already have these prepared for you!).
5. Click **Create repository**.

### 2. Connect and Push Local Repo
In your PowerShell window:

```powershell
# Initialize git if not done
git init
git add .
git commit -m "feat: initial release of SysPulse PC Benchmark & Laptop Buyer Audit suite"
git branch -M main

# Link to your new GitHub repository (replace with your repo URL)
git remote add origin https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark.git

# Push to GitHub
git push -u origin main
```

---

## 🏷️ Recommended GitHub Repository Settings

To help students, gamers, and developers discover your tool on GitHub:

### 1. Topics / Tags
Go to your repository homepage on GitHub, click the gear icon ⚙️ next to "About", and add these topics:
- `benchmark`
- `hardware-audit`
- `cpp20`
- `cuda`
- `laptop-buying-guide`
- `stress-test`
- `openmp`
- `hardware-inspection`
- `thermal-throttling`
- `performance-analysis`

### 2. About Description & Website
- **Description**: *All-in-one C++20 and CUDA hardware benchmark, thermal stress test, and 34-point laptop buying inspection suite with interactive HTML reports.*
- **Website URL**: You can host the generated sample HTML report via **GitHub Pages**!

---

## 📦 Precompiled Standalone Releases (Live on GitHub)

Release **v1.0.0** is already published on GitHub with the standalone portable ZIP attached:
👉 **[View SysPulse v1.0.0 Release](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/tag/v1.0.0)**

To generate new portable releases at any time:
1. Run `package_portable.bat` in the project root.
2. It automatically bundles `laptop_benchmark.exe`, `vcomp140.dll`, and `run_portable.bat` into `SysPulse_Portable.zip`.
3. Create a new release via GitHub CLI:
   ```powershell
   gh release create v1.0.1 SysPulse_Portable.zip --title "SysPulse v1.0.1" --notes "Release notes here..."
   ```

Students can now test any laptop in under 60 seconds without installing compilers!

