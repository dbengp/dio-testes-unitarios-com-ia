import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# --- Configuração do Azure OpenAI ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME]):
    raise ValueError(
        "Por favor, defina as variáveis de ambiente AZURE_OPENAI_API_KEY, "
        "AZURE_OPENAI_ENDPOINT e AZURE_OPENAI_DEPLOYMENT_NAME."
    )

# Inicializa o modelo GPT do Azure OpenAI via LangChain
llm = AzureChatOpenAI(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    temperature=0.7, # Um pouco de criatividade pode ser útil para testes, mas evite alucinações.
    max_tokens=1500, # Aumentado para acomodar testes mais complexos
)

# --- Função para Gerar Testes Dinamicamente ---
def generate_unit_tests_dynamically(user_prompt: str, code_to_test: str) -> str:
    """
    Gera testes unitários para um dado código Python usando LangChain e Azure OpenAI,
    permitindo um prompt personalizado.

    Args:
        user_prompt (str): O prompt personalizado para o modelo, descrevendo como gerar os testes.
        code_to_test (str): O código Python para o qual os testes unitários serão gerados.

    Returns:
        str: O código Python dos testes unitários gerados.
    """
    # Combina o prompt do sistema com o prompt fornecido pelo usuário e o código a ser testado
    full_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "Você é um expert em desenvolvimento de software e testes unitários em Python. Sua tarefa é gerar testes unitários completos e eficazes para o código fornecido. Siga rigorosamente as instruções do usuário."),
            ("human", f"{user_prompt}\n\nO código Python para o qual os testes devem ser gerados é:\n```python\n{code_to_test}\n```\n\nPor favor, forneça apenas o código Python dos testes."),
        ]
    )

    # Cria a cadeia de processamento: prompt -> LLM -> parser de string
    chain = full_prompt_template | llm | StrOutputParser()

    print("Gerando testes unitários com prompt personalizado... isso pode levar um momento.")
    try:
        response = chain.invoke({"user_prompt": user_prompt, "code_to_test": code_to_test})
        return response
    except Exception as e:
        return f"Ocorreu um erro ao gerar testes: {e}"

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # 1. Código Python que queremos testar
    example_code = """
def factorial(n):
    \"\"\"Calculates the factorial of a non-negative integer.\"\"\"
    if not isinstance(n, int):
        raise TypeError("Input must be an integer.")
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def is_prime(number):
    \"\"\"Checks if a number is prime.\"\"\"
    if not isinstance(number, int):
        raise TypeError("Input must be an integer.")
    if number < 2:
        return False
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            return False
    return True
"""

    print("--- Código Original ---")
    print(example_code)

    # 2. Prompt Dinâmico fornecido pelo usuário
    user_defined_prompt = input(
        "\nDigite seu prompt para a geração de testes (ex: 'Gere testes pytest para o código acima, cobrindo casos de sucesso, zero, negativos e tipos inválidos. Use mocks onde apropriado.'):\n"
    )

    # Gera os testes unitários
    generated_tests = generate_unit_tests_dynamically(user_defined_prompt, example_code)

    print("\n--- Testes Unitários Gerados ---")
    print(generated_tests)

    # Opcional: Salvar os testes em um arquivo
    file_name = "test_generated_dynamic_code.py"
    with open(file_name, "w") as f:
        f.write(generated_tests)
    print(f"\nTestes salvos em '{file_name}'")

    print("\nLembre-se de revisar os testes gerados e executá-los em seu ambiente de desenvolvimento.")
    print(f"Para executar, salve o código original (seção '--- Código Original ---' acima) em um arquivo como 'my_math_module.py' e execute 'pytest {file_name}'.")