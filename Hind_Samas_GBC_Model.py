import streamlit as st
import pandas as pd
import re
import joblib
import time
import streamlit.components.v1 as components

# मॉडल लोड करने का फ़ंक्शन जिसमें त्रुटि को हैंडल किया जाएगा
def load_model(model_path):
    try:
        return joblib.load(model_path)  # मॉडल लोड करने का प्रयास
    except ModuleNotFoundError as e:
        if "_loss" in str(e):
            pass  # चेतावनी को इग्नोर करें
        return None  # मॉडल लोड नहीं हुआ
    except Exception:
        return None  # मॉडल लोड नहीं हुआ

# मॉडल लोड करें
model_path = "gbc_best_model_hindi.pkl"
model_data = load_model(model_path)

# Dataset लोड करें
file_path = "samas_hindi_dataset.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# समास के लिए मैपिंग
samas_mapping = {
    "D": "द्वंद्व समास",
    "T": "तत्पुरुष समास",
    "M": "मध्यपदलोपी समास",
    "U": "उपपद समास",
    "K": "कर्मधारय समास",
    "B": "बहुव्रीहि समास",
    "DV": "द्विगु समास"
}

# समास पहचानने के लिए फ़ंक्शन
def find_compound_words(text):
    words = re.findall(r'\b[^\s]+\b', text)
    return [word for word in words if word in df["Word"].values]

# समास बदलने का फ़ंक्शन
def replace_compound_words(text):
    compound_words = find_compound_words(text)
    replaced_text = text
    
    for word in compound_words:
        row = df[df["Word"] == word]
        if not row.empty:
            meaning = f"{row['sangna1'].values[0]} {row['Middle'].values[0]} {row['sangna2'].values[0]}"
            replaced_text = replaced_text.replace(word, meaning)
    
    return replaced_text, compound_words

# समास के प्रकार सूचीबद्ध करने का फ़ंक्शन
def list_compound_words_with_types(compound_words):
    compound_info = []
    for word in compound_words:
        row = df[df["Word"] == word]
        if not row.empty:
            label = row["Label"].values[0]
            full_samas_name = samas_mapping.get(label, label)
            compound_info.append(f"{word}: {full_samas_name}")
    return "\n".join(compound_info)

# UI डिज़ाइन
st.markdown(
     """
    <style>
        body {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            font-family: Arial, sans-serif;
        }
        .stApp {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            animation: gradientAnimation 10s infinite alternate;
        }
        @keyframes gradientAnimation {
            0% { background: linear-gradient(135deg, #ff9a9e, #fad0c4); }
            100% { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }
        }
        .stTextArea textarea {
            background: white !important;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton button {
            background: #4CAF50;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton button:hover {
            background: #45a049;
            transform: scale(1.05);
        }
        .stMarkdown h1 {
            color: #333366;
            text-align: center;
            font-size: 32px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .marquee {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            animation: marquee 10s linear infinite;
            font-size: 32px;
            font-weight: bold;
            color: #333366;
            text-align: center;
        }
        @keyframes marquee {
            from { transform: translateX(100%); }
            to { transform: translateX(-100%); }
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <div class='marquee'>🚀 हिंदी समास पहचान और व्याख्या🚀</div>
    """, unsafe_allow_html=True)


input_text = st.text_area("हिंदी पाठ दर्ज करें:")

if st.button("पाठ संसाधित करें"):
    start_time = time.time()
    if input_text.strip():
        replaced_text, compound_words = replace_compound_words(input_text)
        compound_list = list_compound_words_with_types(compound_words)
        end_time = time.time()
        response_time = round(end_time - start_time, 4)
        
        st.subheader("संशोधित पाठ:")
        st.markdown(f"<div class='output-box'>{replaced_text.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        
        st.subheader("पहचाने गए समास और उनके प्रकार:")
        st.markdown(f"<div class='output-box'>{compound_list.replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        
        st.subheader("प्रतिक्रिया समय:")
        st.write(f"{response_time} सेकंड")
    else:
        st.warning("कृपया कुछ पाठ दर्ज करें।")
