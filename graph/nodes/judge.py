from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "あなたは厳密な審判です。直近ラウンドの探偵発言を、"
     "論理性・根拠・新規性の観点で短く評価し、"
     "最後に総合スコア(0~1)と最有力仮説を1行で出力してください。"),
    ("human", "履歴:\n{history_text}")
])

def _h(state):
    return "\n".join(f"[{m['role']}] {m['text']}" for m in state.get("history", []))

def node_judge(state):
    text = (prompt | llm).invoke({"history_text": _h(state)}).content
    # デモ用の簡易スコア（本番はJSON構造化に）
    score = 0.86 if any(k in text for k in ("根拠", "一貫", "新規")) else 0.72
    return {
        "history": state["history"] + [{"role": "judge", "text": text}],
        "overall_score": score,
        "round": state.get("round", 1) + 1
    }
