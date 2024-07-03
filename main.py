import streamlit as st
from openai import OpenAI
import os

with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="chatbot_api_key", type="password"
    )

# openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

if "problem" not in st.session_state:
    st.session_state["problem"] = ""
if "answer" not in st.session_state:
    st.session_state["answer"] = ""


def get_problem(client, grade):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"あなたは最高の英語教師です。日本語の文章を英語に訳す練習をしたいです。{grade}レベルの問題を1問のみ出題してください。問題となる日本語の文章だけを返してください。「はい、わかりました」なども不要です。",
            },
        ],
    )

    answer = completion.choices[0].message
    return answer.content


def check_answer(client, jp, en):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"あなたは最高の英語教師です。私は{jp}という日本語の文章を{en}と訳しました。訳が正しいかどうか、解説を含めて教えてください。",
            },
        ],
    )

    answer = completion.choices[0].message
    return answer.content


st.title("英作文問題ジェネレーター")
grade = st.selectbox(
    "レベルを選択してください",
    ["初級", "中級", "上級"],
)
if st.button("問題を出してもらう"):
    if not openai_api_key:
        st.error("OpenAI API Keyが入力されていません。")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    with st.spinner("問題を生成中..."):
        problem = get_problem(client, grade)
        st.session_state["problem"] = problem
        st.session_state["answer"] = ""

if "problem" in st.session_state and st.session_state["problem"] != "":
    st.write("下の文章を英語に訳してください。")
    st.write(st.session_state["problem"])
    answer = st.text_area("英語の回答", height=200, value=st.session_state["answer"])
    st.session_state["answer"] = answer

    if st.button("回答をチェックする"):
        if not openai_api_key:
            st.error("OpenAI API Keyが入力されていません。")
            st.stop()

        client = OpenAI(api_key=openai_api_key)
        with st.spinner("回答をチェック中..."):
            check = check_answer(
                client, st.session_state["problem"], st.session_state["answer"]
            )
            st.write(check)
