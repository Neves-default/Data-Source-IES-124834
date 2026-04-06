# 1. Usamos uma imagem leve do Python
FROM python:3.10-slim

# 2. Define a pasta de trabalho dentro do contentor
WORKDIR /app

# 3. Copia o ficheiro de requisitos primeiro (otimiza a cache do Docker)
COPY requirements.txt .

# 4. Instala as dependências (aqui não precisas de venv, o Docker já é isolado!)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo o teu código para dentro do contentor
COPY . .

# 6. Comando para iniciar a tua DataSource
CMD ["python", "main.py"]