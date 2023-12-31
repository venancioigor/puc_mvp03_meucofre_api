from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from database.database import  ClienteModel, ClienteSchema, ContaModel, PorquinhoModel, db
from flasgger import swag_from

clientes = Blueprint("clientes", __name__, url_prefix="/api/clientes")

@clientes.route('/criarCliente', methods=['POST'], endpoint='criar_cliente')
@swag_from('../docs/cliente/criarCliente.yaml')
def criar_cliente():

    nome = request.json['nome']
    cpf = request.json['cpf']

    if ClienteModel.query.filter_by(cpf=cpf).first() is not None:
       return jsonify({'error': 'Esse cliente já foi cadastrado'}, 409)

    novo_cliente = ClienteModel(nome=nome, cpf=cpf)
    db.session.add(novo_cliente)
    db.session.commit()
    return jsonify({
        'id': novo_cliente.id,
        'nome': novo_cliente.nome,
        'cpf': novo_cliente.cpf
    }), 201

@clientes.get('/getCliente')
@swag_from('../docs/cliente/getCliente.yaml')
def get_cliente():
    cpf = request.args.get('cpf')
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    cliente_schema = ClienteSchema()
    cliente_serialize = cliente_schema.dump(cliente)
    return jsonify(cliente_serialize)

@clientes.route('/atualizarCliente/', methods=['PUT'])
@swag_from('../docs/cliente/atualizarCliente.yaml')
def atualizar_cliente():
    try:
        data = request.json

        novo_nome = data['novo_nome']
        cpf = data['cpf_do_cliente_a_alterar']

        cliente = ClienteModel.query.filter_by(cpf=cpf).first()
        if cliente is None:
            return jsonify({'error': 'Cliente não encontrado'}), 404

        cliente.nome = novo_nome
        cliente.cpf = cpf
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar cliente.'}), 500

    return jsonify({'message': 'Cliente atualizado com sucesso.'}), 200


@clientes.route('/excluirCliente/', methods=['DELETE'])
@swag_from('../docs/cliente/excluirCliente.yaml')
def excluir_cliente():
    try:
        data = request.json
        cpf = data['cpf']
        cliente = ClienteModel.query.filter_by(cpf=cpf).first()
        if cliente is None:
            return jsonify({'error': 'Cliente não encontrado'}), 404

        db.session.delete(cliente)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir cliente.'}), 500

    return jsonify({'message': 'Cliente excluído com sucesso.'}), 200


@clientes.route('/getClienteSaldoGeral')
@swag_from('../docs/cliente/getClienteSaldoGeral.yaml')
def saldo_geral():
    cpf = request.args.get('cpf')
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    saldo_porquinhos = db.session.query(func.sum(PorquinhoModel.saldo)).filter_by(id_cliente=cliente.id).scalar()
    saldo_contas = db.session.query(func.sum(ContaModel.saldo)).filter_by(id_cliente=cliente.id).scalar()
    saldo_geral = (saldo_porquinhos or 0) + (saldo_contas or 0)
    
    return jsonify({'saldo_total': saldo_geral}), 200
