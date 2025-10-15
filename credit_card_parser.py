import streamlit as st
import PyPDF2
import re
from io import BytesIO

# --- Configuration ---
TARGET_DATA_POINTS = [
    "Card Last 4 Digits",
    "Statement Date",
    "Payment Due Date",
    "Total Balance Due",
    "Total Transactions Count"
]

PARSING_PATTERNS = {
    'AMEX (American Express)': {
        'keywords': ['AMERICAN EXPRESS', 'AMEX', 'Membership Rewards'],
        'Card Last 4 Digits': r'Account number\s*([X\*]+\s*)?(\d{4})',
        'Statement Date': r'Statement Date:\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Payment Due Date': r'Minimum Payment Due Date\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Total Balance Due': r'New Balance\s*\$([\d,]+\.\d{2})',
    },
    'CHASE (JPMorgan Chase)': {
        'keywords': ['JPMORGAN CHASE', 'CHASE BANK', 'Sapphire'],
        'Card Last 4 Digits': r'Card ending in\s*(\d{4})',
        'Statement Date': r'Billing Cycle Ending Date\s*(\d{2}/\d{2}/\d{4})',
        'Payment Due Date': r'Payment Due By:\s*(\d{2}/\d{2}/\d{4})',
        'Total Balance Due': r'Total New Balance\s*\$([\d,]+\.\d{2})',
    },
    'CITI (Citibank)': {
        'keywords': ['CITIBANK', 'CITI CARD', 'THANKYOU POINTS'],
        'Card Last 4 Digits': r'Account Number:\s*[\dX]+\s+(\d{4})',
        'Statement Date': r'CLOSING DATE\s*(\d{2}/\d{2}/\d{4})',
        'Payment Due Date': r'Payment Due Date\s*(\d{2}/\d{2}/\d{4})',
        'Total Balance Due': r'NEW BALANCE\s*\$([\d,]+\.\d{2})',
    },
    'DISCOVER': {
        'keywords': ['DISCOVER', 'CASHBACK BONUS'],
        'Card Last 4 Digits': r'Card Number:\s*\*\*\*\*(\d{4})',
        'Statement Date': r'Billing Period End\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Payment Due Date': r'Due Date\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Total Balance Due': r'Current Balance\s*\$([\d,]+\.\d{2})',
    },
    'CAPITAL ONE': {
        'keywords': ['CAPITAL ONE', 'QUICKSILVER', 'VENTURE'],
        'Card Last 4 Digits': r'Last four digits\s*of card\s*(\d{4})',
        'Statement Date': r'Statement Period\s*ending\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Payment Due Date': r'Minimum Payment Due Date\s*(\w+\s+\d{1,2},\s+\d{4})',
        'Total Balance Due': r'Total Amount Due\s*\$([\d,]+\.\d{2})',
    }
}

class CreditCardParser:
    def __init__(self, patterns=PARSING_PATTERNS):
        self.patterns = patterns

    def extract_text_from_pdf(self, uploaded_file):
        try:
            pdf_file = BytesIO(uploaded_file.read())
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return ' '.join(text.split()).upper()
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
            return None

    def identify_issuer(self, text):
        for issuer, config in self.patterns.items():
            for keyword in config['keywords']:
                if keyword in text:
                    return issuer
        return "UNKNOWN"

    def count_transactions(self, text):
        transaction_pattern = r'\d{2}/\d{2}\s+[\w\s,.-]+?\s+\$?\d{1,3}(?:,?\d{3})*\.\d{2}'
        raw_text = text.replace(" ", "\n")
        matches = re.findall(transaction_pattern, raw_text)
        return len(matches)

    def parse_statement(self, text, issuer):
        if issuer == "UNKNOWN":
            return {"Error": "Could not identify the credit card issuer from the document."}
        config = self.patterns.get(issuer)
        results = {"Issuer": issuer}
        for data_point, regex_pattern in config.items():
            if data_point in TARGET_DATA_POINTS:
                match = re.search(regex_pattern, text, re.IGNORECASE)
                value = match.group(2).strip() if match and match.lastindex == 2 else (match.group(1).strip() if match else "N/A")
                if "Balance" in data_point and value != "N/A":
                    value = f"${value}"
                results[data_point] = value
        results['Total Transactions Count'] = self.count_transactions(text)
        return results


# --- Streamlit UI ---
def main():
    st.set_page_config(layout="centered", page_title="Credit Card Statement Parser", page_icon="💳")

    # --- Enhanced UI Styling ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Poppins:wght@300;400;600&display=swap');

        .stApp {
            background: radial-gradient(circle at top left, #001f3f, #000000);
            font-family: 'Poppins', sans-serif;
            color: #E0F7FA;
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            color: #00FFFF;
            text-shadow: 0 0 20px #00FFFF;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.8rem;
            letter-spacing: 1.5px;
        }

        .main .block-container {
            background: rgba(20, 20, 30, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0,255,255,0.3);
            border-radius: 20px;
            padding: 45px;
            box-shadow: 0 0 25px rgba(0,255,255,0.15);
        }

        /* Uploader */
        .stFileUploader > div {
            border: 2px dashed #00FFFF;
            border-radius: 10px;
            padding: 10px;
            background-color: rgba(0,255,255,0.05);
            transition: all 0.3s ease-in-out;
        }
        .stFileUploader > div:hover {
            background-color: rgba(0,255,255,0.1);
            transform: scale(1.01);
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(0,255,255,0.2), rgba(0,255,255,0.05));
            border: 1px solid rgba(0,255,255,0.3);
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0,255,255,0.1);
            transition: 0.3s;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 0 25px rgba(0,255,255,0.4);
            transform: translateY(-3px);
        }

        div[data-testid="stMetricValue"] {
            color: #00FFFF !important;
            font-weight: bold;
            font-size: 2rem;
        }
        div[data-testid="stMetricLabel"] {
            color: #E0F7FA !important;
            font-weight: 600;
        }

        .custom-data-card {
            background: rgba(0, 60, 90, 0.6);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            box-shadow: inset 0 0 10px rgba(0,255,255,0.15);
        }
        .custom-data-card:hover {
            background: rgba(0,80,100,0.8);
            transform: scale(1.02);
            transition: 0.2s;
        }

        /* Buttons */
        button[kind="primary"] {
            background: linear-gradient(90deg, #00FFFF, #00BFFF);
            color: black !important;
            font-weight: bold;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💳 Smart Credit Card Statement Parser")

    st.markdown("""
        <p style='text-align:center; color:#B0E0E6; font-size:1.1em;'>
        Upload your credit card PDF statement and instantly extract <b>key insights</b> — 
        all with a futuristic neon dashboard interface. 🔮
        </p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Upload Statement (PDF Only)", type="pdf")

    if uploaded_file:
        parser = CreditCardParser()
        with st.spinner("⚡ Analyzing your statement..."):
            full_text = parser.extract_text_from_pdf(uploaded_file)
            if full_text:
                issuer = parser.identify_issuer(full_text)
                st.info(f"**Issuer Identified:** {issuer}")

                if issuer == "UNKNOWN":
                    st.error("❌ Unsupported issuer or invalid file format.")
                else:
                    parsed = parser.parse_statement(full_text, issuer)

                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.subheader("✨ Extracted Data Overview")

                    col1, col2 = st.columns(2)
                    col1.metric("💰 Total Balance Due", parsed.get("Total Balance Due", "N/A"))
                    col2.metric("🧾 Transactions", parsed.get("Total Transactions Count", "N/A"))

                    col3, col4, col5 = st.columns(3)
                    with col3:
                        st.markdown(f"<div class='custom-data-card'><b>Statement Date</b><br><span style='color:#FDD835;'>{parsed.get('Statement Date','N/A')}</span></div>", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"<div class='custom-data-card'><b>Payment Due Date</b><br><span style='color:#FDD835;'>{parsed.get('Payment Due Date','N/A')}</span></div>", unsafe_allow_html=True)
                    with col5:
                        st.markdown(f"<div class='custom-data-card'><b>Card Last 4 Digits</b><br><span style='color:#00FFFF;'>•••• {parsed.get('Card Last 4 Digits','N/A')}</span></div>", unsafe_allow_html=True)

                    with st.expander("🧠 View Extracted Raw Text"):
                        st.code(full_text[:4000] + "...", language="text")

if __name__ == "__main__":
    main()
