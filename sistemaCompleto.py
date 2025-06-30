from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco: str):
        self._endereco = endereco
        self._contas = []
    
    def realizar_transacao(self, conta, transacao) -> None:
        transacao.registrar(conta)

    def adicionar_conta(self, conta) -> None:
        self._contas.append(conta)
    
    @property
    def contas(self):
        return self._contas

class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, date: datetime, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_de_nascimento = date
    
    @property
    def cpf(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def data_de_nascimento(self):
        return self._data_de_nascimento

class Conta:
    def __init__(self, num: int, cliente: Cliente):
        self._saldo = 0
        self._numero = num
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    

    def sacar(self, valor: float) -> bool:
        if self._saldo < valor or valor < 0:
            print("Erro! Valor informado é inválido ou ultrapassa saldo disponível!")
            return False
        
        self._saldo -= valor
        print("Operação realizada com sucesso!")
        return True
    
    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("Erro! Valor informado é inválido!")
            return False
        
        self._saldo += valor
        print("Operação realizada com sucesso!")
        return True
    
class ContaCorrente(Conta):
    def __init__(self, num, cliente, limite: float=500, limite_saques: int=3):
        super().__init__(num, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self._historico.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_lim = valor > self._limite
        excedeu_saque = numero_saques > self._limite_saques

        if excedeu_lim:
            print("Erro! Valor excede limite de saque!")
        elif excedeu_saque:
            print("Erro! Você excedeu a quantidade de saques diários máxima!")
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""
            Agência:\t{self.agencia}
            C/C:\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao) ->  None:
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @classmethod
    @abstractmethod
    def registrar(conta: Conta):
        pass

class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def menu():
    menu = '''
    ================
        Banco V1
    ================

    Selecione uma opção:
    [d] Depósito
    [s] Saque
    [e] Exibir extrato
    [nc] Novo conta
    [nu] Novo usuário
    [lc] Listar contas
    [f] Finalizar e sair
    ==> '''

    return input(textwrap.dedent(menu))

def depositar(clientes):
    cpf = input("Insira o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não corresponde a nenhum cliente cadastrado!")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Insira o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não corresponde a nenhum cliente cadastrado!")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Insira o CPF do cliente: ")

    cliente = filtrar_clientes(cpf, clientes)
    if not cliente:
        print("CPF não corresponde a nenhum cliente cadastrado!")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n======================EXTRATO======================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não houveram movimentações na conta."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao["tipo"]:}:\n   R$ {transacao["valor"]:.2f}\n"
    
    print(extrato)
    print(f"\n\nSaldo: R$ {conta.saldo:.2f}")
    print("===================================================")

def cadastrar_cliente(clientes):
    cpf = input("Insira o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if cliente:
        print("CPF já corresponde a um cliente cadastrado!")
        return

    nome = input("Insira o nome do cliente: ")
    data = input("Insira a data de nascimento do cliente (dd-mm-aaaa):")
    ende = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla do estado): ")
    cliente = PessoaFisica(nome=nome, date=data, cpf=cpf, endereco=ende)

    clientes.append(cliente)

    print("Cliente cadastrado com sucesso!")

def criar_conta(num_conta, clientes, contas):
    cpf = input("Insira o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não corresponde a nenhum cliente cadastrado!")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=num_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso!")

def filtrar_clientes(cpf, clientes):     
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente inserido não possui conta!")
        return
    
    return cliente.contas[0]

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opc = menu()

        match(opc):
            case "d":
                depositar(clientes)

            case "s":
                sacar(clientes)

            case "e":
                exibir_extrato(clientes)

            case "nu":
                cadastrar_cliente(clientes)
            
            case "nc":
                num_conta = len(contas) + 1
                criar_conta(num_conta, clientes, contas)
            
            case "lc":
                listar_contas(contas)
            
            case "f":
                break

            case _:
                print("Insira uma opção válida")

main()