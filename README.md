# Documents Insights - LLM Chatbot

## Índice

- [Documents Insights - LLM Chatbot](#documents-insights---llm-chatbot)
  - [Índice](#índice)
  - [Sobre](#sobre)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Uso](#uso)
  - [Futuras Implementações](#futuras-implementações)
  - [Contato](#contato)

## Sobre

Este repositório contém o código fonte do chatbot LLM, desenvolvido para o estudo de extração de informações de documentos de diversos formatos utilizando a API da openAI.

## Pré-requisitos

É necessário ter instalado:

- Python 3.6 ou superior
- Pip

```bash
python --version
pip --version
```

## Instalação

- Clone o repositório

- Instale as dependências

  ```bash
  pip install -r requirements.txt
  ```

- Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis de ambiente:

```text
OPENAI_API_KEY=your_openai_api_key
```

## Uso

Execute o script `oracle.py`, com o streamlit, para iniciar o chatbot.

```bash
streamlit run oracle.py
```

## Futuras Implementações

- [ ] Implementar a extração de informações de documentos de novos vários formatos
- [ ] Implementar o vector database para armazenar as informações extraídas, removendo a necessidade de reprocessar os documentos a cada nova consulta
- [ ] Implementar a extração de informações de documentos de áudio e vídeo
- [ ] (**_Verificar se já não funciona_**) Implementar a extração de informações de documentos de imagens
- [ ] Implementar a extração de informações de documentos de redes sociais
- [ ] Implementar a disponibilização do chatbot em uma API REST
- [ ] Implementar a disponibilização automática de insights em um dashboard

## Contato

Em caso de dúvidas, críticas ou sugestões, sinta-se à vontade para entrar em contato.

Mauricio Souza Menezes

```text
Email: mauriciosm95@gmail.com
Tel.: +55 71 9 9241-4527
```
