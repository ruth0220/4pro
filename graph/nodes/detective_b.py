from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

base = ChatPromptTemplate.from_messages([
    ("system", "{role_desc}。これまでの履歴を読み、1つの仮説を述べ、その根拠を1-2文で示してください。既出の繰り返しは避け、新しい視点を加えてください。"),
    ("human", "履歴:\n{history_text}")
])

def _h(state):
    return "\n".join(f"[{m['role']}] {m['text']}" for m in state.get("history", []))

def node_detective_b(state):
    prompt = base.partial(role_desc="あなたは論理重視の探偵A")
    text = (prompt | llm).invoke({"history_text": _h(state)}).content
    return {"history": state["history"] + [{"role": "detectiveA", "text": text}]}
