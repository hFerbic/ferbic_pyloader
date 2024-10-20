# Usa uma imagem base com Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o conteúdo do diretório atual (código da aplicação) para o diretório de trabalho no contêiner
COPY . /app

# Instala as dependências do projeto a partir de um requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposição da porta 1007
EXPOSE 1007

# Comando para executar a aplicação Flask
CMD ["python", "ferbic_pyloader.py"]
