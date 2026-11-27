
import random
from datetime import datetime, timezone
from bson import ObjectId
from mongo_cursos.conexao import obter_banco
from pymongo.errors import WriteError


def criar_colecoes():
    banco = obter_banco()

    validador = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "titulo",
                "categoria",
                "preco",
                "vagas",
                "modulos"
            ],
            "properties": {
                "titulo": {
                    "bsonType": "string"
                },
                "categoria": {
                    "bsonType": "string"
                },
                "preco": {
                    "bsonType": ["double", "int", "long"],
                    "minimum": 0
                },
                "vagas": {
                    "bsonType": ["int", "long"],
                    "minimum": 0
                },
                "modulos": {
                    "bsonType": "array"
                }
            }
        }
    }

    colecoes = banco.list_collection_names()
    if "cursos" not in colecoes:
        banco.create_collection(
            "cursos",
            validator=validador
        )
    elif banco.cursos.options().get("validator") != validador:
        banco.command("collMod", "cursos", validator=validador)

    if "alunos" not in colecoes:
        banco.create_collection("alunos")

    if "matriculas" not in colecoes:
        banco.create_collection("matriculas")

    print("Coleções configuradas com sucesso!")


def testar_validacao():
    banco = obter_banco()

    curso_invalido = {
        "titulo": "Curso de Teste",
        "categoria": "Programação",
        "preco": -50.00,
        "vagas": 10,
        "modulos": []
    }

    try:
        resultado = banco.cursos.insert_one(curso_invalido)

        banco.cursos.delete_one({
            "_id": resultado.inserted_id
        })

    except WriteError as erro:
        if erro.code == 121:
            print("Sucesso: curso com preço negativo rejeitado!")
        else:
            raise
    else:
        raise RuntimeError("O curso com preço negativo foi aceito pelo banco.")


def criar_indices():
    banco = obter_banco()

    banco.alunos.create_index(
        "email",
        unique=True
    )

    banco.matriculas.create_index(
        [("aluno_id", 1), ("curso_id", 1)],
        unique=True
    )

    print("Índices criados com sucesso!")


def inserir_cursos():
    banco = obter_banco()

    categorias = {
        "Programação": [
            "Java", "Python", "C#", "C++",
            "JavaScript", "Ruby"
        ],
        "Dados": [
            "SQL", "MongoDB", "Power BI",
            "Excel", "Pandas", "Big Data"
        ],
        "Design": [
            "Figma", "Canva", "UX Design",
            "UI Design", "Photoshop", "Pixel Art"
        ],
        "Gestão": [
            "Scrum", "Kanban", "Liderança",
            "Finanças", "Marketing", "Projetos"
        ],
        "Infraestrutura": [
            "Redes", "Linux", "Docker",
            "Cloud", "Segurança", "Git"
        ]
    }

    cursos = []

    for categoria, temas in categorias.items():
        for tema in temas:
            curso = {
                "titulo": f"Introdução a {tema}",
                "categoria": categoria,
                "carga_horaria": random.choice(
                    [20, 30, 40, 60, 80]
                ),
                "preco": round(
                    random.uniform(50, 300), 2
                ),
                "vagas": random.randint(20, 50),
                "tags": [
                    tema.lower(),
                    "iniciante"
                ],
                "instrutor": {
                    "nome": "Professor " + tema,
                    "email": tema.lower().replace(
                        " ", ""
                    ) + "@aprendamais.com"
                },
                "modulos": [
                    {
                        "ordem": 1,
                        "titulo": "Fundamentos",
                        "aulas": [
                            "Introdução",
                            "Conceitos básicos"
                        ]
                    },
                    {
                        "ordem": 2,
                        "titulo": "Prática",
                        "aulas": [
                            "Exercícios",
                            "Projeto final"
                        ]
                    }
                ]
            }

            if not banco.cursos.find_one({
                "titulo": curso["titulo"]
            }):
                cursos.append(curso)

    if cursos:
        banco.cursos.insert_many(cursos)

    print("Cursos cadastrados:", len(cursos))


def inserir_alunos():
    banco = obter_banco()

    nomes = [
        "Ana Silva",
        "João Santos",
        "Maria Oliveira",
        "Pedro Souza",
        "Lucas Costa",
        "Julia Lima",
        "Marcos Alves",
        "Laura Pereira",
        "Gabriel Rocha",
        "Beatriz Gomes"
    ]

    alunos = []

    for nome in nomes:
        email = nome.lower().replace(
            " ", "."
        ) + "@email.com"

        if not banco.alunos.find_one({
            "email": email
        }):
            aluno = {
                "nome": nome,
                "email": email,
                "data_cadastro": datetime.now(
                    timezone.utc
                )
            }

            alunos.append(aluno)

    if alunos:
        banco.alunos.insert_many(alunos)

    print("Alunos cadastrados:", len(alunos))


def inserir_matriculas():
    banco = obter_banco()

    alunos = list(banco.alunos.find())
    cursos = list(banco.cursos.find())

    quantidade = banco.matriculas.count_documents({})

    faltam = 30 - quantidade

    if faltam <= 0:
        print("Carga de matrículas já realizada!")
        return

    matriculas = []
    pares = set()

    while len(matriculas) < faltam:
        aluno = random.choice(alunos)

        disponiveis = [
            curso for curso in cursos
            if curso["vagas"] > 0
            and (aluno["_id"], curso["_id"]) not in pares
            and not banco.matriculas.find_one({
                "aluno_id": aluno["_id"],
                "curso_id": curso["_id"]
            })
        ]

        if not disponiveis:
            if not any(
                curso["vagas"] > 0
                and (a["_id"], curso["_id"]) not in pares
                and not banco.matriculas.find_one({
                    "aluno_id": a["_id"],
                    "curso_id": curso["_id"]
                })
                for a in alunos
                for curso in cursos
            ):
                raise ValueError("Não há matrículas disponíveis.")
            continue

        curso = random.choice(disponiveis)

        progresso = random.choice(
            [0, 25, 50, 75, 100]
        )

        matricula = {
            "_id": ObjectId(),
            "aluno_id": aluno["_id"],
            "curso_id": curso["_id"],
            "data": datetime.now(timezone.utc),
            "progresso": progresso,
            "concluida": progresso == 100
        }

        if progresso == 100:
            matricula["nota"] = random.randint(1, 5)

        matriculas.append(matricula)

        pares.add((aluno["_id"], curso["_id"]))
        curso["vagas"] -= 1

    with banco.client.start_session() as sessao:
        with sessao.start_transaction():

            for matricula in matriculas:
                resultado = banco.cursos.update_one(
                    {
                        "_id": matricula["curso_id"],
                        "vagas": {"$gt": 0}
                    },
                    {"$inc": {"vagas": -1}},
                    session=sessao
                )

                if resultado.modified_count == 0:
                    raise ValueError("Curso sem vagas!")

            banco.matriculas.insert_many(
                matriculas,
                session=sessao
            )

    print("Matrículas cadastradas:", len(matriculas))


if __name__ == "__main__":
    criar_colecoes()
    criar_indices()
    testar_validacao()

    inserir_cursos()
    inserir_alunos()
    inserir_matriculas()
