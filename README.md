# Ferbic Pyloader

![Docker Icon](https://i.imgur.com/1eu90Zp.png)

Ferbic Pyloader é uma ferramenta para gerenciar scripts Python, permitindo que você faça upload, execute e monitore scripts Python facilmente.

## Funcionalidades
- Upload de scripts Python.
- Execução contínua de scripts.
- Interface gráfica amigável.
- Sistema de login com senha para proteger o acesso.

## Como usar

### Usando Docker Compose
1. Clone este repositório ou baixe os arquivos necessários.
2. Certifique-se de ter o Docker e Docker Compose instalados.
3. Execute o seguinte comando no diretório do projeto:
    ```bash
    sudo docker-compose up --build
    ```
4. Acesse a aplicação no seu navegador através de `http://localhost:1007` (ou substitua pela porta configurada).

### Usando Docker Hub
Se preferir usar a imagem já publicada no Docker Hub:
1. Execute o comando:
    ```bash
    docker run -d -p 1007:1007 --name ferbic_pyloader ferbic/ferbic_pyloader
    ```
   (Esse comando usará a imagem já publicada no Docker Hub com o nome `ferbic/ferbic_pyloader`).

### Usando GitHub
Se preferir clonar o repositório diretamente do GitHub:
1. Acesse o repositório [hFerbic/ferbic_pyloader](https://github.com/hFerbic/ferbic_pyloader) para obter o código.

## Configurações
- A aplicação irá criar um arquivo `users.json` para gerenciar usuários e senhas.
- Scripts e ícones são armazenados no diretório `uploaded_scripts/` e `icons/` respectivamente.

Desenvolvido por: Hiatan Ferbic.
