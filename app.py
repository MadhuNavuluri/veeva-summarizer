import streamlit as st
import pandas as pd
import openai

# ✅ Initialize OpenAI client using latest syntax
openai.api_key = st.secrets["OPENAI_API_KEY"]

# UI Setup
st.set_page_config(page_title="Veeva Call Note Summarizer", page_icon="🧠")
st.title("🧠 Veeva Call Note Summarizer")
st.caption("Upload a CSV with call notes to generate AI-powered summaries")

uploaded_file = st.file_uploader("📄 Upload your Call Notes CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df)

    if st.button("🔍 Summarize Call Notes"):
        if 'Notes' not in df.columns:
            st.error("❌ Your CSV must contain a 'Notes' column.")
        else:
            summaries = []

            for note in df['Notes']:
                prompt = f"""
Summarize the following Veeva call note in 2-3 lines.
Extract key keywords and the overall sentiment (positive/neutral/negative).

Call Note: {note}
"""

                try:
                    # ✅ New OpenAI API (chat.completions.create)
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.4,
                        max_tokens=150
                    )

                    summary = response.choices[0].message.content.strip()
                    summaries.append(summary)

                except Exception as e:
                    summaries.append(f"Error: {e}")

            df['Summary'] = summaries
            st.success("🧠 Summarized Call Notes:")
            st.dataframe(df)

            st.download_button(
                "⬇️ Download as CSV",
                data=df.to_csv(index=False),
                file_name="summarized_call_notes.csv",
                mime="text/csv"
            )
