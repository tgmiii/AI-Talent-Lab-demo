import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI実習：ビジネス判断をAIで整理する")

st.subheader("ケース")
st.write("""
駅前にカフェを出店するか検討しています。

・人通りが多い  
・競合が2店舗ある  
・近くに大学がある  
""")

st.subheader("AIエージェント（3ステップ）")

# 状況整理
if st.button("① 状況を整理する"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": "このカフェ出店ケースの特徴を簡単に整理してください。"
        }]
    )
    st.write(response.choices[0].message.content)

# 判断ポイント
if st.button("② 判断ポイントを出す"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": "カフェ出店を判断するために考えるべきポイントを3つ挙げてください。"
        }]
    )
    st.write(response.choices[0].message.content)

# 不足情報
if st.button("③ 足りない情報を出す"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": "この判断をするために不足している情報は何ですか？"
        }]
    )
    st.write(response.choices[0].message.content)

st.subheader("あなたの判断")
st.text_area("出店するべきか？理由も書いてください")