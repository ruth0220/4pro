from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Cは人物関係・動機・機会(MMO)を重視
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

base = ChatPromptTemplate.from_messages([
    ("system",
     "{role_desc}。履歴を踏まえ、"
     "被害者/容疑者の関係・動機・機会の観点から1つの仮説を述べ、"
     "根拠を1-2文で示してください。既出の内容の言い換えは避けてください。"),
    ("human", "履歴:\n{history_text}")
])

def _h(state):
    return "\n".join(f"[{m['role']}] {m['text']}" for m in state.get("history", []))

def node_detective_c(state):
    prompt = base.partial(role_desc="あなたは動機・人物心理を重視する探偵C")
    text = (prompt | llm).invoke({"history_text": _h(state)}).content
    return {"history": state["history"] + [{"role": "detectiveC", "text": text}]}
