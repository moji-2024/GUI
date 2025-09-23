# qPCR Project (Tkinter GUI)

A graphical user interface for analyzing **qPCR (quantitative PCR) data**.  
This tool helps researchers process qPCR results with reference genes, calculate fold changes, and generate publication-ready plots.

---

## ✨ Features
- Load and process qPCR datasets
- Normalize data using reference/control samples
- Calculate fold-change values
- Generate bar plots for fold-change graphs
- Export results for further analysis

---
## 🚀 How to Run
1. Install dependencies:
   ```bash
   cd tkinter/qPCR_project
   pip install -r requirements.txt
   pyinstaller --onedir --windowed qPCR_GUI.py

