import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,
    temperature=1,
)

while True:
    pergunta = input("Usuário: ")

    if pergunta.lower() == "sair":
        print("Encerrando o chat!")
        break
        
    resposta = llm_gemini.invoke([HumanMessage(content=pergunta)])

    print(f"Assistente: {resposta.content}\n")

