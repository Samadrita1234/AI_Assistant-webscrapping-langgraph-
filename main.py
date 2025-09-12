import streamlit as st
import json
import os
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langgraph.graph import StateGraph, END

VECTORSTORE_PATH = "faiss_index"
USER_FILE = "user_data.json"
CHAT_FILE = "chat_history.json"


embeddings = OllamaEmbeddings(model="mistral")
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever()

llm = OllamaLLM(model="mistral")

class State(dict):
    question: str
    context: str
    answer: str

def mask_pii(text):
    masked = text
    if "user_info" in st.session_state:
        info = st.session_state.user_info
        masked = masked.replace(info.get("name", ""), "[NAME]")
        masked = masked.replace(info.get("email", ""), "[EMAIL]")
        masked = masked.replace(info.get("phone", ""), "[PHONE]")
    return masked

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def load_chat(user_email):
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            all_history = json.load(f)
        return all_history.get(user_email, [])
    return []

def save_chat(user_email, history):
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            all_history = json.load(f)
    else:
        all_history = {}
    all_history[user_email] = history
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_history, f, indent=2)

def router_node(state: State):
    state["route"] = "RETRIEVAL"
    return state

def retrieval_node(state: State):
    question_masked = mask_pii(state["question"])
    docs = retriever.invoke(question_masked)
    
    if not docs:
        state["context"] = None
    else:
        state["context"] = "\n".join([d.page_content for d in docs])
    return state

def output_node(state: State):
      
    
    try:
        prompt = f"""
        You are an AI Assistantrepresenting Occams Advisory.
        Using the following context, provide a clear, structured answer to the user.
        When answering, speak in first-person as the company ("we", "our").
        Be friendly, professional, and concise.
        Rules:
           -If the user greets with (eg. "hi","hello","hey"), reply with a warm greeting and suggest 
            what they can ask about (services, careers, contact info).
           -If the user greets + asks a real question (e.g., "Hi, I want to know about your company"), 
            combine both: start with a greeting and then answer their question.
           -If the user asks something unrelated to the knowledge base, reply: 
            "❌ Sorry, I don’t know the answer based on our data."
           - Do NOT say "based on the provided context" or similar phrases.
           - Just answer directly like a human from the company would.
           - Do not include any generic signatures, disclaimers, or placeholders like [Your Name] 
             or [Your Position]

Context:
{state['context']}

Question:
{state['question']}

Format: bullet points if applicable.
"""
        masked_prompt = mask_pii(prompt)
        state["answer"] = llm.invoke(masked_prompt)
    except Exception:
        state["answer"] = (
            "⚠️ Our AI assistant is temporarily unavailable.\n\n"
            "But here’s some quick info:\n"
            "- 📌 **Who we are:** Occams Advisory, redefining advisory services for businesses.\n"
            "- 💼 **Services:** Business services, growth strategy, capital advisory, tax & audit.\n"
            "- 📞 **Contact:** info@occamsadvisory.com | +1-646-494-9720\n"
            "- 🌐 More: [occamsadvisory.com](https://www.occamsadvisory.com/)\n\n"
            "Please try again later for AI-powered assistance."
        )

    if "user_info" in st.session_state:
        state["answer"] = state["answer"].replace("[NAME]", st.session_state.user_info["name"])
    return state

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("output", output_node)
graph.set_entry_point("router")
graph.add_edge("router", "retrieval")
graph.add_edge("retrieval", "output")
graph.add_edge("output", END)
app = graph.compile()


col1, col2 = st.columns([1, 5])
with col1:
    st.image("company_logo.png", width=300)
with col2:
    st.markdown(
        "<h1 style='margin-bottom:5; color:#1E3A8A;'>Occams Advisory</h1>"
        "<p style='margin-top:0; font-size:16px; color:#4B5563;'>Redefining Advisory Services for Business</p>",
        unsafe_allow_html=True
    )


if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "form_id" not in st.session_state:
    st.session_state.form_id = 0


if not st.session_state.onboarding_complete:
    st.subheader("Complete Onboarding")
    with st.form(f"onboarding_form_{st.session_state.form_id}"):
        name = st.text_input("👤 Name", key=f"name_{st.session_state.form_id}")
        email = st.text_input("📧 Email", key=f"email_{st.session_state.form_id}")
        phone = st.text_input("📞 Phone", key=f"phone_{st.session_state.form_id}")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not name or not email or not phone:
                st.error("All fields are required.")
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email.")
            elif not phone.isdigit() or len(phone) < 7:
                st.error("Please enter a valid phone number.")
            else:
                users = load_users()
                new_user = {"name": name, "email": email, "phone": phone}

                already_signed_up = any(
                    u["name"] == new_user["name"] and 
                    u["email"] == new_user["email"] and 
                    u["phone"] == new_user["phone"]
                    for u in users
                )
                
                if already_signed_up:
                    st.warning("⚠️ You have already signed up.")
                else:
                    users.append(new_user)
                    save_users(users)
                    st.success("✅ Onboarding completed! You can now chat with the assistant.")

                st.session_state.onboarding_complete = True
                st.session_state.user_info = new_user
                # st.session_state.chat_history = load_chat(email)
                st.session_state.chat_history = [] 

if st.session_state.onboarding_complete:
    user_info = st.session_state.user_info
    if st.button("🚪 Logout"):
        save_chat(user_info["email"], st.session_state.chat_history)
        st.session_state.onboarding_complete = False
        st.session_state.user_info = {}
        st.session_state.chat_history = []
        st.session_state.form_id += 1
        st.rerun()

if st.session_state.onboarding_complete:
    user_input = st.text_input("Ask a question:")
    if user_input:
        state = {"question": user_input}
        result = app.invoke(state)
        st.session_state.chat_history.append({"user": user_input, "ai": result["answer"]})
        save_chat(user_info["email"], st.session_state.chat_history)

if st.session_state.chat_history:
    st.subheader("Chat History")
    for chat in st.session_state.chat_history:
        st.markdown(f"**👤 User:** {chat['user']}")
        st.markdown(f"**🤖 AI Bot:** {chat['ai']}")
