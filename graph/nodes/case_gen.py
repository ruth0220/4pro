# graph/nodes/case_gen.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "あなたは推理小説の事件生成AIです。"
     "与えられた仕様（ジャンル/作風/時間/場所/容疑者数/証拠数/証拠タイプ）を尊重し、"
     "事件の概要、主要人物（容疑者{suspects}名＋被害者/関係者）、"
     "重要な手掛かり（{clues}件、タイプ指定を優先）を箇条書きで簡潔に作成してください。"
     "手掛かりはIDをC1..CNで付与してください。"),
    ("human",
     "仕様:\n"
     "- テーマ: {request}\n"
     "- ジャンル: {genre}\n- 作風: {style}\n- 時間: {time}\n- 場所: {place}\n"
     "- 容疑者数: {suspects}\n- 証拠数: {clues}\n- 証拠タイプ: {clue_types_text}\n"
     "出力は『概要／登場人物／手掛かり』の3セクションに分けてください。")
])

def _clues_text(state):
    ct = state.get("clue_types", [])
    return ", ".join(ct) if ct else "(指定なし)"

def node_case_gen(state):
    payload = {
        "request": state.get("request", "大学で起きた盗難事件"),
        "genre": state.get("genre", "密室殺人"),
        "style": state.get("style", "アガサクリスティ風"),
        "time": state.get("time", "冬の夜"),
        "place": state.get("place", "音楽ホール"),
        "suspects": state.get("suspects", 3),
        "clues": state.get("clues", 3),
        "clue_types_text": _clues_text(state),
    }
    text = (prompt | llm).invoke(payload).content
    return {
        "history": state.get("history", []) + [{"role": "casegen", "text": text}],
        "round": 1
    }
