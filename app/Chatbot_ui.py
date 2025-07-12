import gradio as gr
import requests
import pandas as pd
from rag_pipeline import RAGPipeline
from utils.stock_utils import load_stock_data, get_stat, compare_months
from utils.date_parser import extract_month_years

pipeline = RAGPipeline()
pipeline.load_existing_index()

stock_df = load_stock_data("data/BFS_Share_Price.csv")

def query_llm(prompt):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    hf_token = os.environ.get("HF_TOKEN")  # Set this in your Space's secrets
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        return response.json()[0]["generated_text"]
    except Exception as e:
        return f"⚠️ LLM error: {e}"
    
    
def detect_stock_intent(q):
    q_lower = q.lower()
    # Define sets of keywords for each intent
    high_words = {"high", "highest", "max", "maximum", "peak", "top"}
    low_words = {"low", "lowest", "min", "minimum", "bottom"}
    avg_words = {"average", "mean", "median", "typical"}
    compare_words = {"compare", "difference", "vs", "versus", "between", "trend", "change"}
    price_words = {"price", "close", "closing", "stock", "value", "rate"}

    # Tokenize the question
    tokens = set(q_lower.replace("-", " ").replace("/", " ").split())

    # Detect intent
    if tokens & compare_words and len(extract_month_years(q)) >= 2:
        return "compare"
    if tokens & high_words and tokens & price_words:
        return "high"
    if tokens & low_words and tokens & price_words:
        return "low"
    if tokens & avg_words and tokens & price_words:
        return "avg"
    # Fallback: if price words and month present, assume average
    if tokens & price_words and extract_month_years(q):
        return "avg"
    return None

def answer_question(q):
    months = extract_month_years(q)
    intent = detect_stock_intent(q)

    if intent and months:
        if intent == "high":
            return f"📈 Highest closing price for {months[0]} was ₹{get_stat(stock_df, months[0], 'high')}"
        elif intent == "low":
            return f"📉 Lowest closing price for {months[0]} was ₹{get_stat(stock_df, months[0], 'low')}"
        elif intent == "avg":
            return f"📊 Average closing price for {months[0]} was ₹{get_stat(stock_df, months[0], 'avg')}"
        elif intent == "compare" and len(months) >= 2:
            df = compare_months(stock_df, months[0], months[1])
            return f"📊 Comparison of closing prices between {months[0]} and {months[1]}:\n\n{df.to_string(index=False)}"

    # Else fallback to LLM using RAG
    retrieved_chunks = pipeline.query(q, top_k=10)
    context = "\n".join(retrieved_chunks)
    answer = query_llm(f"Answer the question using this context:\n\n{context}\n\nQuestion: {q}")
    highlighted_chunks = pipeline.highlight_answer(answer, retrieved_chunks)
    return f"**Answer:**\n{answer}\n\n**Relevant Chunks:**\n" + "\n\n".join(highlighted_chunks)


gr.Interface(
    fn=answer_question,
    inputs="text",
    outputs="text",
    title="📊 Bajaj Finserv Chatbot",
    description="Ask about stock data or business insights from transcripts."
).launch()