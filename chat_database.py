import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from schema import schema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import json

load_dotenv()

DATABASE_URL = f"mysql+pymysql://root:root@localhost:3306/test_schema"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def executar_sql(query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            # Converter o resultado do banco para dicionário
            formated_result = []
            for row in rows:
                row_dict = {}
                for i in range(len(columns)):
                    nome_coluna = columns[i]
                    valor = row[i]
                    row_dict[nome_coluna] = valor
                formated_result.append(row_dict)
            # lista = [dict(zip(columns, row)) for row in rows]
            return formated_result
    except SQLAlchemyError as error:
        print("Erro ao executar o comando SQL: ", error)
        print(query)
        return {"erro": error}

api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,
    temperature=1,
)

template = """
## OBJETIVO DO AGENTE:
Você é um agente especialista em construção de queries SQL (MySQL) para um sistema de gestão de empréstimos de uma biblioteca. Seu papel é ler a estrutura (schema) do banco de dados e, com base em uma pergunta feita por um usuário, gerar apenas a consulta SQL correta e completa que atenda precisamente à solicitação.

Você deve considerar:
- As tabelas, campos e relacionamentos descritos no schema.
- A pergunta do usuário, que pode vir em linguagem natural.
- O contexto de uma biblioteca: livros, empréstimos, devoluções, usuários, datas, etc.

Seu único output será o Json com a consulta SQL correspondente. Nada mais.

---

## BOAS PRÁTICAS (GUARDRAILS):
- Nunca adicione explicações ou comentários no output. Apenas a SQL dentro de um Json.
- Evite SELECT *: sempre especifique os campos necessários.
- Sempre utilize aliases (ex: `u.nome AS nome_usuario`) para melhorar legibilidade, quando necessário.
- Respeite as chaves estrangeiras e relacione corretamente as tabelas via JOINs.
- Trate filtros com clareza (ex: `WHERE`, `LIKE`, `BETWEEN`, etc.).
- Use funções agregadoras (`COUNT`, `AVG`, etc.) apenas quando fizerem sentido na pergunta.
- Sempre termine a query com `;`.

---

## OUTPUT ESPERADO:

O output esperado do modelo é um objeto JSON e somente isso, no formato: "query": "consulta_sql_aqui"

---


Agora, com base no schema abaixo e na pergunta do usuário, gere apenas a consulta SQL correspondente:

schema:
{schema}

pergunta:
{pergunta}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["pergunta", "schema"]
)

while True:

    pergunta = input("Digite a pergunta: ")

    if pergunta.lower() == "sair":
        quit()

    prompt_format = prompt.format(pergunta=pergunta, schema=schema)
    resposta = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    resposta = resposta.content.strip("```json").strip("```").strip()

    #print(f"Assistente: {resposta}\n")

    try:
        resposta_json = json.loads(resposta)
    except json.JSONDecodeError as e:
        print("Erro ao tentar converter a String para JSON: ", e)
        quit()

    # print("Consulta SQL:", resposta_json['query'])

    resultado = executar_sql(resposta_json['query'])
    print(resultado)

    #resultado_sql = executar_sql(resposta)
    #print(resultado_sql)