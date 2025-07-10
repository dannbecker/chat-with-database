import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Configure the Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the language model
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=api_key,
    temperature=1,
)

# Define the prompt template for sentiment analysis
template = """
Você é um agente de inteligência artificial especializado em análise de sentimentos de clientes. Sua tarefa é analisar a avaliação abaixo e gerar três elementos:

1. Sentimento: positivo, neutro ou negativo.
2. Satisfação: percentual entre 0% e 100%, baseado no tom e nas palavras utilizadas pelo cliente.
3. Comentário da IA: uma breve análise em linguagem natural (de 2 a 3 frases), explicando a razão do sentimento identificado.

Regras:
- Sentimentos positivos: satisfação entre 70% e 100%.
- Sentimentos neutros: satisfação entre 40% e 69%.
- Sentimentos negativos: satisfação entre 0% e 39%.
- Seja direto, sem copiar o texto do cliente literalmente.
- Não invente informações.
- Sempre responda no formato:

Sentimento: <classificação>  
Satisfação: <percentual>%  
Comentário da IA: <texto da análise>

🧪 Exemplo:

Avaliação: "Achei o produto bom, chegou antes do prazo e o atendimento foi ótimo. Só achei o preço um pouco salgado."

Saída esperada:
Sentimento: Positivo  
Satisfação: 85%  
Comentário da IA: O cliente demonstrou satisfação com a entrega e o atendimento, o que são pontos fortes da experiência. Apesar de mencionar o preço elevado, o tom geral da avaliação é positivo e indica uma boa aceitação do produto.

🔍 Agora, avalie a seguinte avaliação:

Avaliação: {user_input}"
"""

prompt_template = PromptTemplate(
    template=template,
    input_variables=["user_input"]
)

# --- Streamlit App Layout ---

st.set_page_config(page_title="Análise de Sentimentos com IA", page_icon="🤖")

st.title("🤖 Análise de Sentimentos de Avaliações")
st.markdown("---")

st.markdown("""
Esta aplicação utiliza Inteligência Artificial para classificar o sentimento em avaliações de clientes.
Basta inserir o texto no campo abaixo e clicar em **Analisar**.
""")

# User input text area
user_review = st.text_area(
    "Insira a avaliação do cliente aqui:",
    height=150,
    placeholder="Ex: 'Adorei o produto, mas a entrega demorou um pouco.'"
)

# Analysis button
if st.button("Analisar"):
    if user_review and api_key:
        # Format the prompt with user input
        prompt = prompt_template.format(user_input=user_review)

            # Invoke the language model
        response = llm_gemini.invoke([HumanMessage(content=prompt)])

            # Display the result
        st.markdown("---")
        st.subheader("Resultado da Análise:")
        st.markdown(response.content)
    elif not api_key:
        st.error("A chave da API do Gemini não foi encontrada. Por favor, configure-a no arquivo .env.")
    else:
        st.warning("Por favor, insira uma avaliação para analisar.")

st.markdown("---")
st.markdown("Desenvolvido com [Streamlit](https.streamlit.io/) e [Google Gemini](https://ai.google/discover/gemini/).")
