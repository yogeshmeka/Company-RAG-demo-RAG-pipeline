from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()

persistent_directory = "db/chroma_db"

# Load embeddings and vector store
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}  
)

# Search for relevant documents
query = "How many days of annual leave do employees get at TechMeka?"

# retriever = db.as_retriever(search_kwargs={"k": 5})

retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.3  # Only return chunks with cosine similarity ≥ 0.3
    }
)

relevant_docs = retriever.invoke(query)

print(f"User Query: {query}")
# Display results
print("--- Context ---")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")

# Combine the query and the relevant document contents
combined_input = f"""Based on the following documents, please answer this question: {query}

Documents:
{chr(10).join([f"- {doc.page_content}" for doc in relevant_docs])}

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
"""

# Create a ChatOllama model
model = ChatOllama(model="hermes3")

# Define the messages for the model
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content=combined_input),
]

# Invoke the model with the combined input
result = model.invoke(messages)

# Display the full result and content only
print("\n--- Generated Response ---")
# print("Full result:")
# print(result)
print("Content only:")
print(result.content)


# Synthetic Questions: 


# HR Policy:
# 1. "How many days of annual leave do employees get at TechMeka?"
# 2. "What happens after 3 late arrivals in a month?"
# 3. "What is the notice period during probation?"
# 4. "What are the steps in the grievance process?"

# Payroll:
# 5. "What is the salary band for a Senior level employee?"
# 6. "What is the overtime rate on public holidays?"
# 7. "How much is the referral bonus?"
# 8. "When are annual performance bonuses paid?"

# IT Security:
# 9. "What are the password requirements at TechMeka?"
# 10. "How long must passwords be?"
# 11. "What should an employee do if they lose their laptop?"
# 12. "What cloud services are approved at TechMeka?"

# Benefits:
# 13. "How much does the company contribute to the 401k?"
# 14. "What is the annual learning budget for employees?"
# 15. "How many therapy sessions are covered per year?"
# 16. "What is the gym reimbursement amount per month?"

# Onboarding:
# 17. "What happens during the first day at TechMeka?"
# 18. "How long is the probation period?"
# 19. "What is the mentor bonus amount?"
# 20. "What mandatory training must be completed in the first 2 weeks?"