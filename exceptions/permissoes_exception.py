class PermissaoNegadaError(Exception):
    def __init__(self, mensagem="Acesso negado para esta operação."):
        super().__init__(mensagem)