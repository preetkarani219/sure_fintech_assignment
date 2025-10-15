# Credit Card Statement Parser (Streamlit)

**A Streamlit app that extracts key data points from PDF credit card statements.**  
This project demonstrates a simple PDF-to-data parser that recognizes simulated issuers (AMEX, Chase, Citi, Discover, Capital One) using regex heuristics, and displays results in a polished dark/glass UI.

---

## Features

- Upload a credit card statement PDF and extract 5 key data points:
  - Card Last 4 Digits
  - Statement Date
  - Payment Due Date
  - Total Balance Due
  - Total Transactions Count (heuristic)
- Supports 5 simulated issuers with issuer-specific regex patterns.
- Modern neon/glass-inspired Streamlit frontend with hover effects and dashboard-style metrics.
- Includes sample PDF statements for quick testing (`/samples`):
  - `sample_amex_statement.pdf`
  - `sample_chase_statement.pdf`
  - `sample_citi_statement.pdf`
  - `sample_discover_statement.pdf`
  - `sample_capitalone_statement.pdf`
- Includes sample markdown files for each statement for documentation/testing.

---

## Repository Structure (suggested)

```
credit-card-parser/
├── app.py                   # Main Streamlit app (frontend + backend glue)
├── parser.py                # (Optional) Refactored parser class and helpers
├── requirements.txt         # Python dependencies
├── samples/                 # Pre-generated sample PDFs (for testing)
│   ├── sample_amex_statement.pdf
│   ├── sample_chase_statement.pdf
│   └── ...
├── docs/                    # Optional docs / .md sample statements
│   ├── amex_statement.md
│   └── ...
└── README.md
```

> **Note:** In the code snippets from this project the Streamlit app and parser are included in a single file. You can keep `app.py` as-is or split parsing logic into `parser.py` for a cleaner structure.

---

## Getting Started

### Prerequisites

- Python 3.9+ (3.10 recommended)
- `pip` package manager

### Recommended: Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate       # Windows PowerShell
```

### Install dependencies

Create a `requirements.txt` with the following contents (example):

```
streamlit
PyPDF2
reportlab
```

Then install:

```bash
pip install -r requirements.txt
```

### Run the app locally

If your main file is `app.py` (the Streamlit frontend + parser):

```bash
streamlit run app.py
```

This will open the UI in your default browser. Upload any of the sample PDF files from the `samples/` folder to test the parser.

---

## How it Works (high level)

1. **PDF extraction:** `PyPDF2` reads the uploaded PDF and extracts text with `page.extract_text()`.
2. **Normalization:** The text is normalized (uppercased and condensed whitespace) to make regex matching more reliable.
3. **Issuer identification:** The parser looks for issuer-specific keywords to determine which set of regex patterns to apply.
4. **Regex parsing:** For each target data point (card last 4, dates, balance), the corresponding regex pattern is used to extract values.
5. **Transaction counting:** A heuristic regex counts transaction-like lines (dates followed by a description and an amount) to estimate the number of transactions on the statement.
6. **UI display:** Extracted values are shown in a slick dashboard using `st.metric`, custom cards, and a raw-text expander for debugging.

---

## Testing with Sample Files

The repository includes 5 simple PDF samples in `samples/`. To test:
1. Run `streamlit run app.py`.
2. Click **Upload Statement (PDF Only)** in the app.
3. Select one of the sample PDFs (e.g., `sample_chase_statement.pdf`).
4. Confirm the issuer is detected and the fields are populated.

These sample PDFs are intentionally simplified. Real-world statements vary a lot — to improve accuracy you can:
- Add more regex patterns per issuer to cover edge cases.
- Use an ML-based layout/text classifier (e.g., layoutLM) for complex statements.
- Preprocess PDFs with OCR (Tesseract/pytesseract) for image-based PDFs.

---

## Customization Ideas / Next Steps

- Add a theme toggle (light/dark) that toggles CSS styles.
- Export parsed results as CSV / JSON for downstream processing.
- Add a "rules editor" UI so users can add or tweak regex patterns per issuer.
- Add unit tests for the parser (pytest) and sample-based integration tests.
- Improve transaction counting with better heuristics or NLP clustering.

---

## Contributing

Contributions are welcome! Steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make changes and add tests.
4. Open a PR describing the change.

Please avoid committing large binary files — keep sample PDFs in `samples/` but consider `.gitignore` for any generated output.

---

## License

This project is provided under the **MIT License** — see LICENSE for details (or add one if you want).

---

## Acknowledgements

- Built with Streamlit and PyPDF2.
- Sample PDFs were generated for demonstration/testing purposes.

---
