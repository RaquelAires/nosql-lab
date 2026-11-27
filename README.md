# Aprenda+ — Catálogo de Cursos

## Sobre o projeto

Projeto desenvolvido para a disciplina de Banco de Dados do curso de Engenharia de Software da Ulbra Palmas.

O objetivo é implementar um catálogo de cursos utilizando um banco de dados não relacional, permitindo o gerenciamento de cursos, alunos e matrículas.

## Tecnologias utilizadas

- Python
- MongoDB Atlas
- PyMongo
- Python-dotenv
- Visual Studio Code

## Estrutura do projeto

```text
nosql-lab/
├── mongo_cursos/
│   ├── __init__.py
│   ├── conexao.py
│   ├── seed.py
│   ├── repositorio.py
│   └── main.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Como executar

1. Clone o repositório e abra a pasta do projeto. Use Python 3.10 ou mais recente.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` na raiz do projeto e configure as variáveis com sua própria conexão:

```env
MONGO_URI=sua_string_de_conexao
MONGO_DB=aprenda_mais
```

Use um banco de testes no MongoDB Atlas ou em um replica set que suporte transações. No Atlas, inclua seu IP em **Network Access** e use um usuário de banco com permissão `readWrite` para criar e popular um banco novo. Se for corrigir o validador de uma coleção já existente, o usuário também precisa da permissão `collMod`. Guarde a URI com a senha apenas no seu `.env` local.

4. Teste a conexão:

```bash
python -m mongo_cursos.conexao
```

5. Execute a carga inicial:

```bash
python -m mongo_cursos.seed
```

Em um banco vazio, o script deve exibir `Sucesso: curso com preço negativo rejeitado!` e cadastrar 30 cursos, 10 alunos e 30 matrículas. Rode o mesmo comando de novo para conferir que a carga inicial não insere novos registros.

6. Execute o sistema:

```bash
python -m mongo_cursos.main
```

## Modelagem do banco de dados

O banco de dados é composto por três coleções: cursos, alunos e matriculas.

### Coleção cursos — Embedding

Os módulos e o instrutor são armazenados dentro do próprio documento do curso, pois essas informações normalmente são consultadas em conjunto. Essa abordagem reduz a necessidade de consultas adicionais e facilita a recuperação dos dados, respeitando o limite de 16 MB por documento do MongoDB.

### Coleção alunos

Os alunos são armazenados em uma coleção independente, pois um mesmo aluno pode estar matriculado em diferentes cursos. Dessa forma, evita-se a duplicação de informações pessoais.

### Coleção matriculas — Linking

As matrículas são armazenadas em uma coleção própria, utilizando os campos aluno_id e curso_id como referências. Essa escolha permite consultar e atualizar as matrículas individualmente, além de evitar o crescimento excessivo dos documentos dos cursos.

## Validação dos dados

A coleção cursos utiliza o operador `$jsonSchema` para garantir a obrigatoriedade dos campos titulo, categoria, preco, vagas e modulos.

O preço e a quantidade de vagas não podem ser negativos, e os módulos devem ser armazenados em um array.

Também foram utilizados índices únicos para impedir a duplicação de e-mails e matrículas.

## Carga inicial e idempotência

A carga inicial utiliza a biblioteca random e o método insert_many() para cadastrar:

- 30 cursos;
- 5 categorias;
- 10 alunos;
- 30 matrículas.

O script é idempotente, permitindo sua execução repetida, sem duplicar os registros da carga inicial.

## Funcionalidades

- Buscar cursos por categoria, preço máximo e tag;
- Adicionar módulos utilizando `$push`;
- Atualizar o progresso utilizando `$set`;
- Realizar matrículas;
- Avaliar cursos concluídos;
- Listar alunos e matrículas;
- Remover alunos e suas matrículas;
- Exibir relatórios.

## Relatórios

O sistema apresenta três relatórios utilizando o framework de agregação do MongoDB:

1. Quantidade de cursos por categoria;
2. Quantidade de matrículas e progresso médio por curso;
3. Média das avaliações por curso.

## Mecanismos de recuperação

As operações de matrícula e exclusão de alunos utilizam transações para garantir a atomicidade e preservar a consistência do banco de dados.

Caso ocorra uma falha durante essas operações, as alterações da transação são desfeitas, evitando inconsistências.

## Pergunta teórica

**Em que situação embutir as matrículas dentro do documento do curso seria um erro de modelagem?**

Embutir as matrículas dentro do documento do curso seria um erro quando a quantidade de matrículas crescesse constantemente ou quando fosse necessário consultá-las e atualizá-las individualmente. Isso poderia fazer com que o documento atingisse o limite de 16 MB do MongoDB, além de dificultar a manutenção dos dados.

Nesse caso, utilizar uma coleção independente para as matrículas, com referências aos alunos e aos cursos, é mais adequado, pois permite maior flexibilidade e evita o crescimento excessivo dos documentos.

## Referências

- Material da disciplina de Banco de Dados — Bancos de Dados NoSQL, 2026/2.
- Material da disciplina de Banco de Dados — Mecanismos de Recuperação, 2026/2.
- MongoDB — Documentação oficial do PyMongo.
- SADALAGE, Pramod J.; FOWLER, Martin. NoSQL Essencial. Novatec, 2013.
