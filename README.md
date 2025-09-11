# Occams Advisory AI Assistant

A lightweight, offline-friendly AI assistant that provides answers about Occams Advisory using a local knowledge base. The system scrapes official website content, processes it into a vectorstore, and uses a local LLM for intelligent responses. Designed with privacy, clarity, and minimal stack in mind.

---

## **1. Architecture Overview**

```text
          ┌───────────────────────────────┐
          │   occamsadvisory.com website   │
          └───────────────┬───────────────┘
                          │  (scraper.py)
                          ▼
            ┌────────────────────────────┐
            │   knowledge.json (raw)     │
            └───────────────┬────────────┘
                            │ (chunks.py)
                            ▼
            ┌────────────────────────────┐
            │     chunks.json (clean)    │
            └───────────────┬────────────┘
                            │ (build_embeddings.py)
                            ▼
            ┌────────────────────────────┐
            │   FAISS vectorstore index  │
            └───────────────┬────────────┘
                            │
                            ▼
          ┌────────────────────────────────────────┐
          │         Streamlit Frontend (main.py)   │
          │                                        │
          │  - User Onboarding (PII masked)        │
          │  - Chat Input                          │
          │  - LangGraph Pipeline:                 │
          │      Router → Retriever → Output Node  │
          │  - LLM Response + Fallback             │
          └────────────────────────────────────────┘
---

## **1. Architecture Overview**

```text
---

## **2. Key Design Choices **

**Minimal Stack:**  
The system uses small, focused libraries: **BeautifulSoup** for scraping, **FAISS** for offline vector search, **Ollama** for local LLM inference, and **Streamlit** for the frontend. This makes it lightweight, portable, and easy to maintain. The trade-off is fewer out-of-the-box features but greater clarity and simplicity.

**Fallback Logic for Offline-Friendliness:**  
When the LLM/API is unavailable, pre-defined helpful responses are served to ensure continuity. This reduces richness of answers but guarantees usability even offline.

**Dynamic Prompt Handling:**  
Instead of hardcoding replies for greetings or unknown queries, the LLM generates answers based on context and defined rules. This is flexible but requires careful prompt design to prevent hallucinations.

---

## **3. Threat Model**

**PII Flow:**  
- User data (name, email, phone) is collected during onboarding.  
- Stored locally in `user_data.json` and session state during runtime.  
- Masked before sending prompts to the LLM, so sensitive info never leaves the system.

**Mitigation:**  
- No unmasked PII is transmitted externally.  
- Session-based masking ensures safe interaction with the LLM.  
- Local storage minimizes third-party exposure.

---

## **4. Scraping Approach**

- Used **Selenium + BeautifulSoup** to extract unstructured content from occamsadvisory.com.  
- Targeted headings, paragraphs, and main text blocks; filtered out boilerplate and duplicates.  
- Saved raw data in `knowledge.json`, processed into clean chunks in `chunks.json`.  
- Generated vector embeddings with **Ollama + FAISS** for efficient retrieval during chat.

---

## **5. Failure Modes & Graceful Degradation**

**Potential Failures:**  
- LLM/API unavailable → serves fallback text with key company info.  
- No relevant context found → returns safe “❌ Sorry, I don’t know the answer based on our data.”  
- Invalid user inputs → form validation prevents onboarding until corrected.

**Graceful Handling:**  
- Predefined responses keep the app functional without AI.  
- Masking prevents PII leaks.  
- Local chat history persists to maintain session continuity.

---

## **6. Minimal Tests Implemented**

- **Email & phone validation:** Ensures correct format and prevents invalid onboarding.  
- **Unknown question handling:** Returns safe fallback without hallucinating.  
- **Chat nudges:** Gently guides users to ask questions about services, careers, or contact info.

---

## **7. Usage**

1. Install dependencies:  
```bash
pip install -r requirements.txt
2.Installing Ollama for Local LLM:

Visit Ollama Official Site
Go to https://ollama.com/download
 to download the installer for your operating system (macOS, Windows, or Linux).

Install Ollama

macOS: Open the downloaded .dmg and drag Ollama to Applications.

Windows: Run the .exe installer and follow the prompts.

Linux: Follow the instructions on the website (usually involves a .tar or package manager installation).

Verify Installation
Open your terminal or command prompt and run:

ollama list


You should see available models, e.g., mistral.

Download the Model
If the model you want isn’t installed yet, run:

ollama pull mistral


This downloads the model locally so that the LLM works offline.

3.Scrape Website Data: Generates knowledge.json with raw content from the website.
python scraper.py

4. Process Data into Chunks: Generates chunks.json, which is structured for embedding.
python chunks.py

7. Build FAISS Vectorstore: Creates faiss_index for efficient offline retrieval.
python build_embeddings.py

8. Run the Streamlit App
streamlit run main.py
