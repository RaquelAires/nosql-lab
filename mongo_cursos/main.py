
from mongo_cursos.repositorio import (
    buscar_cursos,
    adicionar_modulo,
    atualizar_progresso,
    remover_aluno,
    matricular_aluno,
    avaliar_curso,
    relatorio_cursos_categoria,
    relatorio_matriculas,
    relatorio_avaliacoes,
    listar_alunos,
    listar_matriculas
)

from bson.errors import InvalidId
from pymongo.errors import PyMongoError


def exibir_cursos(cursos):
    if not cursos:
        print("Nenhum curso encontrado.")
        return

    for curso in cursos:
        print("-" * 50)
        print("ID:", curso["_id"])
        print("Curso:", curso["titulo"])
        print("Categoria:", curso["categoria"])
        print("Carga horária:", curso["carga_horaria"], "horas")
        print(f"Preço: R$ {curso['preco']:.2f}")
        print("Vagas:", curso["vagas"])
        print("Tags:", ", ".join(curso["tags"]))
        print("Instrutor:", curso["instrutor"]["nome"])


def exibir_relatorios():
    print("\n=== CURSOS POR CATEGORIA ===")

    for item in relatorio_cursos_categoria():
        print(
            item["_id"],
            "- Total:", item["total_cursos"]
        )

    print("\n=== MATRÍCULAS POR CURSO ===")

    for item in relatorio_matriculas():
        print(
            f"{item['titulo']} | "
            f"Matrículas: {item['total_matriculas']} | "
            f"Progresso médio: {item['progresso_medio']:.2f}%"
        )

    print("\n=== AVALIAÇÕES DOS CURSOS ===")

    for item in relatorio_avaliacoes():
        print(
            f"{item['titulo']} | "
            f"Nota média: {item['media_avaliacoes']:.2f} | "
            f"Avaliações: {item['total_avaliacoes']}"
        )


def menu():
    while True:
        print("\n" + "=" * 50)
        print("          APRENDA+ | CATÁLOGO DE CURSOS")
        print("=" * 50)

        print("1 - Buscar cursos")
        print("2 - Matricular aluno")
        print("3 - Atualizar progresso")
        print("4 - Avaliar curso")
        print("5 - Exibir relatórios")
        print("6 - Listar alunos")
        print("7 - Listar matrículas")
        print("8 - Adicionar módulo")
        print("9 - Remover aluno")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ")

        try:
            if opcao == "1":
                categoria = input("Categoria: ").strip()
                preco = input("Preço máximo: ").strip()
                tag = input("Tag: ").strip()

                cursos = buscar_cursos(
                    categoria or None,
                    float(preco) if preco else None,
                    tag or None
                )

                exibir_cursos(cursos)

            elif opcao == "2":
                aluno_id = input("ID do aluno: ")
                curso_id = input("ID do curso: ")

                matricular_aluno(aluno_id, curso_id)
                print("Matrícula realizada com sucesso!")

            elif opcao == "3":
                matricula_id = input("ID da matrícula: ")
                progresso = int(input("Progresso (0-100): "))

                if atualizar_progresso(
                    matricula_id, progresso
                ):
                    print("Progresso atualizado!")
                else:
                    print("Matrícula não encontrada!")

            elif opcao == "4":
                matricula_id = input("ID da matrícula: ")
                nota = int(input("Nota (1-5): "))

                avaliar_curso(matricula_id, nota)
                print("Avaliação registrada!")

            elif opcao == "5":
                exibir_relatorios()

            elif opcao == "6":
                for aluno in listar_alunos():
                    print("-" * 50)
                    print("ID:", aluno["_id"])
                    print("Nome:", aluno["nome"])
                    print("E-mail:", aluno["email"])

            elif opcao == "7":
                for matricula in listar_matriculas():
                    print("-" * 50)
                    print("ID:", matricula["_id"])
                    print("Aluno:", matricula["aluno_id"])
                    print("Curso:", matricula["curso_id"])
                    print("Progresso:", matricula["progresso"])
                    print("Concluída:", matricula["concluida"])
                    print("Nota:", matricula.get("nota", "Sem nota"))

            elif opcao == "8":
                curso_id = input("ID do curso: ")
                ordem = int(input("Ordem do módulo: "))
                titulo = input("Título do módulo: ")
                aulas = input("Aulas separadas por vírgula: ")

                modulo = {
                    "ordem": ordem,
                    "titulo": titulo,
                    "aulas": [
                        aula.strip()
                        for aula in aulas.split(",")
                        if aula.strip()
                    ]
                }

                if adicionar_modulo(curso_id, modulo):
                    print("Módulo adicionado!")
                else:
                    print("Curso não encontrado!")

            elif opcao == "9":
                aluno_id = input("ID do aluno: ")
                confirmar = input("Confirmar exclusão (s/n)? ")

                if confirmar.lower() == "s":
                    if remover_aluno(aluno_id):
                        print("Aluno e matrículas removidos!")
                    else:
                        print("Aluno não encontrado!")
                else:
                    print("Operação cancelada.")

            elif opcao == "0":
                print("Encerrando o sistema...")
                break

            else:
                print("Opção inválida!")

        except (ValueError, InvalidId, PyMongoError) as erro:
            print("Erro:", erro)


if __name__ == "__main__":
    menu()
