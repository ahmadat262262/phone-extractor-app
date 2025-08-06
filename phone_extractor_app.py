import fitz  # PyMuPDF
import re
import streamlit as st
from io import StringIO

def clean_phone(raw):
    raw = raw.strip()
    match = re.search(r'[\d\(\)\-\s]+', raw)
    return match.group().strip() if match else None

def extract_phone_numbers(pdf_file):
    phone_numbers = []
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text = page.get_text()
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip().lower()

            if "phone:" in line and "fax" not in line:
                parts = line.split("phone:")
                first_part = parts[1].strip() if len(parts) > 1 else ""

                if "n/a" in first_part:
                    i += 1
                    continue

                if first_part and len(first_part) >= 7 and not first_part.endswith('-'):
                    cleaned = clean_phone(first_part)
                    if cleaned:
                        phone_numbers.append(cleaned)

                elif first_part.endswith('-') or len(first_part) <= 6:
                    if i + 1 < len(lines):
                        second_part = lines[i + 1].strip()
                        if "fax" not in second_part.lower() and "n/a" not in second_part.lower():
                            combined = first_part + second_part
                            cleaned = clean_phone(combined)
                            if cleaned:
                                phone_numbers.append(cleaned)
                        i += 1

                elif not first_part:
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if "fax" not in next_line.lower() and "n/a" not in next_line.lower():
                            if i + 2 < len(lines):
                                third_line = lines[i + 2].strip()
                                if '-' in third_line or len(third_line) >= 7:
                                    combined = next_line + " " + third_line
                                    cleaned = clean_phone(combined)
                                    if cleaned:
                                        phone_numbers.append(cleaned)
                                    i += 2
                                    continue
                            cleaned = clean_phone(next_line)
                            if cleaned:
                                phone_numbers.append(cleaned)
                            i += 1
            i += 1
    doc.close()
    return phone_numbers

# Streamlit UI
st.set_page_config(page_title="Phone Number Extractor", layout="centered")
st.title("Phone Number Extractor from PDF")

uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_pdf:
    with st.spinner("Extracting phone numbers..."):
        phone_numbers = extract_phone_numbers(uploaded_pdf)

        if phone_numbers:
            # Show only the count
            st.success(f"✅ Extracted {len(phone_numbers)} phone numbers.")

            # Create downloadable .txt file
            output = StringIO()
            for i in range(0, len(phone_numbers), 10):
                group = phone_numbers[i:i+10]
                output.write(', '.join(group) + '\n\n\n')  # 3-line gap

            # Download button only
            st.download_button(
                label="📥 Download Phone Numbers as TXT",
                data=output.getvalue(),
                file_name="extracted_phone_numbers.txt",
                mime="text/plain"
            )
        else:
            st.warning("No phone numbers found.")

# Developer credit in bottom-right corner
st.markdown(
    """
    <style>
    .developer-credit {
        position: fixed;
        bottom: 10px;
        right: 15px;
        font-size: 13px;
        color: grey;
        opacity: 0.7;
    }
    </style>
    <div class="developer-credit">
        Developed by Ahmad Tariq · <a href="mailto:ahmadtariqllc@gmail.com" style="color: grey; text-decoration: none;">ahmadtariqllc@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True
)






