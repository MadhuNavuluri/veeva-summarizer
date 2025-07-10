import streamlit as st
import pandas as pd
import openai

# Set OpenAI API Key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Veeva Call Note Summarizer + Keyword & Sentiment")

uploaded_file = st.file_uploader("📤 Upload your call notes CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check for necessary columns
    required_columns = ["HCP Name", "Notes"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"CSV must contain the columns: {', '.join(required_columns)}")
    else:
        if st.button("🔍 Summarize Call Notes"):
            summaries = []
            keywords_list = []
            sentiments = []

            for _, row in df.iterrows():
                note = row["Notes"]
                prompt = f"""
Given the following call note, provide:
- A brief summary (1-2 sentences)
- 3 keywords
- Sentiment (Positive, Neutral, or Negative)

Call Note:
{note}
                """
                
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful medical assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.5,
                        max_tokens=150
                    )
                    result = response.choices[0].message.content.strip()

                    # Try to parse the output into 3 parts
                    lines = result.split('\n')
                    summary = ""
                    keywords = ""
                    sentiment = ""
                    for line in lines:
                        if "summary" in line.lower():
                            summary = line.split(":", 1)[-1].strip()
                        elif "keyword" in line.lower():
                            keywords = line.split(":", 1)[-1].strip()
                        elif "sentiment" in line.lower():
                            sentiment = line.split(":", 1)[-1].strip()

                    summaries.append(summary)
                    keywords_list.append(keywords)
                    sentiments.append(sentiment)

                except Exception as e:
                    summaries.append("Error")
                    keywords_list.append("Error")
                    sentiments.append("Error")
                    st.error(f"OpenAI error: {e}")

            df["Summary"] = summaries
            df["Keywords"] = keywords_list
            df["Sentiment"] = sentiments

            st.success("✅ Summarization complete!")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv,
                file_name='veeva_summary_output.csv',
                mime='text/csv'
            )
