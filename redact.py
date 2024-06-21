import logging
import re
from ctypes import string_at

SENSITIVE_PATTERNS = [
    r"\d{3}-\d{2}-\d{4}",  # Social Security Number (SSN) pattern
    r"\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}",  # Credit card number pattern
    r"\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}",  # Phone number
    r"(0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01])[-/.](19|20)\d\d",  # date of birth
    r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",  # IP address
    r"[a-zA-Z0-9]{32}"  # API key
]

ATTRIBUTE_PATTERNS = [
    "nome",
    "cpf",
    "teste",
    "valor",
    "original"
]

Messages = [
    "Erro na validação do schema: None is not of type 'object' Failed validating 'type' in schema: {'properties': {'calendario': {'$ref': '#/components/schemas/CalendarioCob', 'x-scope': ['']}, 'chave': {'description': 'Obrigat\\xf3rio - Determina a ' 'chave Pix registrada no DICT ' 'que ser\\xe1 utilizada para a ' 'cobran\\xe7a.', 'example': '7d9f0335-8dcc-4054-9bf9-0dbd61d36906', 'maxLength': 77, 'type': 'string'}, 'devedor': {'$ref': '#/components/schemas/IPessoaCob', 'x-scope': ['']}, 'infoAdicionais': {'description': 'Cada respectiva ' 'informa\\xe7\\xe3o ' 'adicional contida ' 'na lista (nome e ' 'valor) ser\\xe1 ' 'apresentada ao ' 'pagador.', 'items': {'$ref': '#/components/schemas/InformacaoAdicional', 'x-scope': ['']}, 'maxLength': 50, 'type': 'array'}, 'loc': {'$ref': '#/components/schemas/LocationPayloadID', 'x-scope': ['']}, 'solicitacaoPagador': {'description': 'Determina um ' 'texto a ser ' 'apresentado ao ' 'pagador para ' 'que ele possa ' 'digitar uma ' 'informa\\xe7\\xe3o ' 'correlata.', 'example': 'Servi\\xe7o realizado.', 'maxLength': 140, 'type': 'string'}, 'valor': {'$ref': '#/components/schemas/ValorCob', 'x-scope': ['']}}, 'required': ['calendario', 'chave', 'valor'], 'type': 'object'} On instance: None",
    "Mensagem de erro: 'valor' is a required property Failed validating 'required' in schema: {'properties': {'calendario': {'$ref': '#/components/schemas/CalendarioCob', 'x-scope': ['']}, 'chave': {'description': 'Obrigat\\xf3rio - Determina a ' 'chave Pix registrada no DICT ' 'que ser\\xe1 utilizada para a ' 'cobran\\xe7a.', 'example': '7d9f0335-8dcc-4054-9bf9-0dbd61d36906', 'maxLength': 77, 'type': 'string'}, 'devedor': {'$ref': '#/components/schemas/IPessoaCob', 'x-scope': ['']}, 'infoAdicionais': {'description': 'Cada respectiva ' 'informa\\xe7\\xe3o ' 'adicional contida ' 'na lista (nome e ' 'valor) ser\\xe1 ' 'apresentada ao ' 'pagador.', 'items': {'$ref': '#/components/schemas/InformacaoAdicional', 'x-scope': ['']}, 'maxLength': 50, 'type': 'array'}, 'loc': {'$ref': '#/components/schemas/LocationPayloadID', 'x-scope': ['']}, 'solicitacaoPagador': {'description': 'Determina um ' 'texto a ser ' 'apresentado ao ' 'pagador para ' 'que ele possa ' 'digitar uma ' 'informa\\xe7\\xe3o ' 'correlata.', 'example': 'Servi\\xe7o realizado.', 'maxLength': 140, 'type': 'string'}, 'valor': {'$ref': '#/components/schemas/ValorCob', 'x-scope': ['']}}, 'required': ['calendario', 'chave', 'valor'], 'type': 'object'} On instance: {'calendario': {'expiracao': 3600}, 'chave': '1eeeb615-93af-4923-a40f-16d057f9e23d', 'devedor': {'cpf': '12345678900', 'nome': 'teste'}, 'solicitacaoPagador': 'Servi\\xe7o realizado.', 'teste': 'teste'}",
    "Mensagem de erro: 'chave' is a required property Failed validating 'required' in schema: {'properties': {'calendario': {'$ref': '#/components/schemas/CalendarioCob', 'x-scope': ['']}, 'chave': {'description': 'Obrigat\\xf3rio - Determina a ' 'chave Pix registrada no DICT ' 'que ser\\xe1 utilizada para a ' 'cobran\\xe7a.', 'example': '7d9f0335-8dcc-4054-9bf9-0dbd61d36906', 'maxLength': 77, 'type': 'string'}, 'devedor': {'$ref': '#/components/schemas/IPessoaCob', 'x-scope': ['']}, 'infoAdicionais': {'description': 'Cada respectiva ' 'informa\\xe7\\xe3o ' 'adicional contida ' 'na lista (nome e ' 'valor) ser\\xe1 ' 'apresentada ao ' 'pagador.', 'items': {'$ref': '#/components/schemas/InformacaoAdicional', 'x-scope': ['']}, 'maxLength': 50, 'type': 'array'}, 'loc': {'$ref': '#/components/schemas/LocationPayloadID', 'x-scope': ['']}, 'solicitacaoPagador': {'description': 'Determina um ' 'texto a ser ' 'apresentado ao ' 'pagador para ' 'que ele possa ' 'digitar uma ' 'informa\\xe7\\xe3o ' 'correlata.', 'example': 'Servi\\xe7o realizado.', 'maxLength': 140, 'type': 'string'}, 'valor': {'$ref': '#/components/schemas/ValorCob', 'x-scope': ['']}}, 'required': ['calendario', 'chave', 'valor'], 'type': 'object'} On instance: {'calendario': {'expiracao': 3600}, 'devedor': {'cpf': '12345678900', 'nome': 'teste'}, 'solicitacaoPagador': 'Servi\\xe7o realizado.', 'teste': 'teste', 'valor': {'original': '2.44'}}",
    "Mensagem de erro:{'cpf': '123455968767', 'nome': 'Manoel da Silva'} is not valid under any of the given schemas Failed validating 'oneOf' in schema['properties']['devedor']: {'description': 'Identifica o devedor, ou seja, a pessoa ou a ' 'institui\\xe7\\xe3o a quem a cobran\\xe7a est\\xe1 endere\\xe7ada.', 'oneOf': [{'$ref': '#/components/schemas/PessoaFisicaCob', 'x-scope': ['', '#/components/schemas/IPessoaCob']}, {'$ref': '#/components/schemas/PessoaJuridicaCob', 'x-scope': ['', '#/components/schemas/IPessoaCob']}], 'properties': {'nome': {'type': 'string'}}, 'type': 'object'} On instance['devedor']: {'cpf': '12312312322', 'nome': 'Cristiano'}"
]

def redact(sensitive_pattern, attribute_pattern, message):
    message = repl(attribute_pattern, message)
    message = change(sensitive_pattern, message)
    return message

def repl(attribute_pattern, message):
    msg_return = []
    for pattern in attribute_pattern:
        x = re.finditer(pattern, message)
        for y in x:
            msg_aux1 = []
            for reg in y.regs:
                for r in reg:
                    message =  repl_value(message, pattern, r)
    return message

def repl_value(message, pattern, r):
    flag_aspas = False
    flag_attribute = False
    # flag_vezes = 0
    flag_dois_pontos = False
    i = 0
    z = pattern
    str_acc = ""
    while (i < len(message)):
        try:
            if (message[i:i + len(z)] == z):
                flag_attribute = True
        except:
            print("except")
        if (message[i] == ":" and not flag_aspas and flag_attribute):
            flag_dois_pontos = True
        if (flag_aspas and message[i] != "'" and message[i] != "\"" and flag_attribute and flag_dois_pontos):
            str_acc = str_acc + message[i]
            message = message[0:i] + "*" + message[i + 1:len(message) + i]
        if (message[i] == "{" and flag_dois_pontos):
            flag_attribute = False
            flag_dois_pontos = False
            flag_aspas = False
        if ((message[i] == "'" or message[i] == "\"")):
            flag_aspas = not flag_aspas
        if (flag_aspas == False and flag_attribute == True and flag_dois_pontos and len(str_acc) > 0):
            flag_attribute = False
            flag_dois_pontos = False
            str_acc = ""
        i = i + 1
    return message

def change(sensitive_pattern, message):
    for pattern in sensitive_pattern:
        return re.sub(pattern, "<REDACTED>", message)

if __name__ == "__main__":
    # logger.info("User's SSN: 123-45-6789")
    # logger.info("User's Credit Card: 1234 5678 9012 3456")
    # logger.info("User's phone number: (123) 456-7890")
    # logger.info("User's date of birth: 04/29/1990")
    # logger.info("User's IP address: 192.168.1.1")
    # logger.info("User's API key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")

    #print(change(SENSITIVE_PATTERNS, "User's SSN: 123-45-6789"))
    for message in Messages:
        message = redact(sensitive_pattern=SENSITIVE_PATTERNS, attribute_pattern=ATTRIBUTE_PATTERNS, message=message)
        print(message)

    # message = "Mensagem de erro:{'cpf': '123455968767', 'nome': 'Manoel da Silva'} is not valid under any of the given schemas Failed validating 'oneOf' in schema['properties']['devedor']: {'description': 'Identifica o devedor, ou seja, a pessoa ou a ' 'institui\xe7\xe3o a quem a cobran\xe7a est\xe1 endere\xe7ada.', 'oneOf': [{'$ref': '#/components/schemas/PessoaFisicaCob', 'x-scope': ['', '#/components/schemas/IPessoaCob']}, {'$ref': '#/components/schemas/PessoaJuridicaCob', 'x-scope': ['', '#/components/schemas/IPessoaCob']}], 'properties': {'nome': {'type': 'string'}}, 'type': 'object'} On instance['devedor']: {'cpf': '12312312322', 'nome': 'Cristiano'}"
    # message = redact(sensitive_pattern=SENSITIVE_PATTERNS, attribute_pattern=ATTRIBUTE_PATTERNS, message=message)
    # print(message)
