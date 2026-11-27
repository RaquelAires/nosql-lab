from mongo_cursos.conexao import obter_banco
from bson import ObjectId
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError


def buscar_cursos(categoria=None, preco_max=None, tag=None):
    banco = obter_banco()

    filtros = {}

    if categoria is not None:
        filtros["categoria"] = categoria

    if preco_max is not None:
        filtros["preco"] = {"$lte": preco_max}

    if tag is not None:
        filtros["tags"] = tag

    cursos = banco.cursos.find(
        filtros,
        {"modulos": 0}
    )

    return list(cursos)

def adicionar_modulo(curso_id, modulo):
    banco = obter_banco()

    resultado = banco.cursos.update_one(
        {"_id": ObjectId(curso_id)},
        {"$push": {"modulos": {"$each": [modulo], "$sort": {"ordem": 1}}}}
    )

    return resultado.modified_count > 0


def atualizar_progresso(matricula_id, progresso):
    banco = obter_banco()

    if not 0 <= progresso <= 100:
        raise ValueError(
            "O progresso deve estar entre 0 e 100."
        )

    atualizacao = {
        "$set": {
            "progresso": progresso,
            "concluida": progresso == 100
        }
    }

    if progresso < 100:
        atualizacao["$unset"] = {"nota": ""}

    resultado = banco.matriculas.update_one(
        {"_id": ObjectId(matricula_id)},
        atualizacao
    )

    return resultado.matched_count > 0


def remover_aluno(aluno_id):
    banco = obter_banco()
    aluno_id = ObjectId(aluno_id)

    with banco.client.start_session() as sessao:
        with sessao.start_transaction():

            matriculas = list(
                banco.matriculas.find(
                    {"aluno_id": aluno_id},
                    session=sessao
                )
            )

            for matricula in matriculas:
                banco.cursos.update_one(
                    {"_id": matricula["curso_id"]},
                    {"$inc": {"vagas": 1}},
                    session=sessao
                )

            banco.matriculas.delete_many(
                {"aluno_id": aluno_id},
                session=sessao
            )

            resultado = banco.alunos.delete_one(
                {"_id": aluno_id},
                session=sessao
            )

    return resultado.deleted_count > 0


def matricular_aluno(aluno_id, curso_id):
    banco = obter_banco()

    aluno_id = ObjectId(aluno_id)
    curso_id = ObjectId(curso_id)

    try:
        with banco.client.start_session() as sessao:
            with sessao.start_transaction():

                aluno = banco.alunos.find_one(
                    {"_id": aluno_id},
                    session=sessao
                )

                if not aluno:
                    raise ValueError("Aluno não encontrado!")

                resultado = banco.cursos.update_one(
                    {
                        "_id": curso_id,
                        "vagas": {"$gt": 0}
                    },
                    {"$inc": {"vagas": -1}},
                    session=sessao
                )

                if resultado.modified_count == 0:
                    raise ValueError(
                        "Curso inexistente ou sem vagas!"
                    )

                banco.matriculas.insert_one(
                    {
                        "aluno_id": aluno_id,
                        "curso_id": curso_id,
                        "data": datetime.now(timezone.utc),
                        "progresso": 0,
                        "concluida": False
                    },
                    session=sessao
                )

        return True

    except DuplicateKeyError:
        raise ValueError(
            "Aluno já matriculado nesse curso!"
        )


def avaliar_curso(matricula_id, nota):
    banco = obter_banco()

    if not 1 <= nota <= 5:
        raise ValueError(
            "A nota deve estar entre 1 e 5."
        )

    resultado = banco.matriculas.update_one(
        {
            "_id": ObjectId(matricula_id),
            "concluida": True
        },
        {
            "$set": {"nota": nota}
        }
    )

    if resultado.matched_count == 0:
        raise ValueError(
            "Matrícula inexistente ou curso não concluído!"
        )

    return True


def relatorio_cursos_categoria():
    banco = obter_banco()

    return list(banco.cursos.aggregate([
        {
            "$group": {
                "_id": "$categoria",
                "total_cursos": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_cursos": -1}
        }
    ]))


def relatorio_matriculas():
    banco = obter_banco()

    return list(banco.matriculas.aggregate([
        {
            "$group": {
                "_id": "$curso_id",
                "total_matriculas": {"$sum": 1},
                "progresso_medio": {
                    "$avg": "$progresso"
                }
            }
        },
        {
            "$lookup": {
                "from": "cursos",
                "localField": "_id",
                "foreignField": "_id",
                "as": "curso"
            }
        },
        {"$unwind": "$curso"},
        {
            "$project": {
                "_id": 0,
                "titulo": "$curso.titulo",
                "total_matriculas": 1,
                "progresso_medio": 1
            }
        },
        {
            "$sort": {"total_matriculas": -1}
        }
    ]))


def relatorio_avaliacoes():
    banco = obter_banco()

    return list(banco.matriculas.aggregate([
        {
            "$match": {
                "concluida": True,
                "nota": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": "$curso_id",
                "media_avaliacoes": {
                    "$avg": "$nota"
                },
                "total_avaliacoes": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "cursos",
                "localField": "_id",
                "foreignField": "_id",
                "as": "curso"
            }
        },
        {"$unwind": "$curso"},
        {
            "$project": {
                "_id": 0,
                "titulo": "$curso.titulo",
                "media_avaliacoes": 1,
                "total_avaliacoes": 1
            }
        },
        {
            "$sort": {"media_avaliacoes": -1}
        }
    ]))

def listar_alunos():
    banco = obter_banco()
    return list(banco.alunos.find())


def listar_matriculas():
    banco = obter_banco()
    return list(banco.matriculas.find())
