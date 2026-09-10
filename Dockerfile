# Usa uma imagem oficial e leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o tempo de build)
COPY requirements.txt .

# Instala as bibliotecas necessárias, incluindo o pytest para o Test Harness
RUN pip install --no-cache-dir -r requirements.txt pytest

# Copia o resto do código do PhishGuard para dentro do container
COPY . .

# Comando padrão ao ligar o container
CMD ["python", "-m", "pytest", "-v"]