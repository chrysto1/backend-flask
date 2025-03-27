def add_task(task, name):
    task = {"task": task, "name": name}
    tasks.append(task)
    print(f"Tarefa adicionada: {task}")
    return

tarefas = []

while True:
    print('\nMenu de gerenciador de tarefas:')
    print('1 - Adicionar tarefa')
    print('2 - Listar tarefas')
    print('3 - Sair')
    opcao = input('Escolha uma opção: ')

    if opcao == '1':
        tarefa = input('Digite a tarefa: ')
        nome = input('Digite o nome: ')
        add_task(tarefa, nome)

        