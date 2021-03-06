import requests, os, datetime, random

from config import Config, BASE_DIR
from app.models import *
from main import create_app
from app import db
from faker import Faker
from slugify import slugify
from sqlalchemy.exc import IntegrityError

class Permissoes:
    ADMINISTRAR = 64
    MODERAR = 32
    ESCREVER = 16
    EDITAR = 8
    COMENTAR = 4
    POSTAR = 2
    SEGUIR = 1

class Populate_DB():
    def __init__(self):
        self.url_data = 'http://api.myjson.com/bins/jza81'
        self.app = create_app()
        self.arquivos = os.listdir(BASE_DIR)
        self.fake = Faker('pt_BR')

    def load_json(self):
        return requests.get(self.url_data).json()

    def app_config(self):
        self.app.app_context().push()
        self.app.config.from_object(Config)

    def db_config(self):
        db.init_app(self.app)
        db.create_all()

        if 'migrations' not in self.arquivos:
            os.system("""touch data.sqlite &&
export FLASK_APP=main.py && 
flask db init &&
flask db migrate &&
flask db downgrade""")

    def str_to_time(self, minuto, segundo, milissegundo):
        self.minuto = minuto
        self.segundo = segundo
        self.milissegundo = milissegundo

        return datetime.time(hour=0, minute=self.minuto, second=self.segundo,
                             microsecond=self.milissegundo)

    def str_to_date(self, dia, mes, ano):
        self.dia = dia
        self.mes = mes
        self.ano = ano

        return datetime.date(int(ano), int(mes), int(dia))

    def pais(self, **kwargs):
        r = Pais.query.filter_by(nome_pais=kwargs['pais']).first()
        if r is None:
            r = Pais()
            r.nome_pais = kwargs['pais']
            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return r

    def cidade(self, **kwargs):
        r = Cidade.query.filter_by(nome_cidade=kwargs['cidade']).first()
        if r is None:
            r = Cidade()
            r.nome_cidade = kwargs['cidade']
            r.pais = self.pais(**kwargs)
            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return r

    def circuito(self, **kwargs):
        r = Circuito.query.filter_by(nome_circuito=kwargs['nome_circuito']).first()
        if r is None:
            r = Circuito()
            r.nome_circuito = kwargs['nome_circuito']
            r.percurso = kwargs['percurso']
            r.numero_voltas = kwargs['numero_voltas']
            r.distancia_total = kwargs['distancia_total']
            r.primeira_corrida = kwargs['primeira_corrida']
            r.piloto_recorde_pista = kwargs['piloto_recorde']
            r.ano_recorde_pista = kwargs['ano_recorde']
            m, s, ms = int(kwargs['tempo_recorde'][0]), int(kwargs['tempo_recorde'][2:4]), \
                       int(kwargs['tempo_recorde'][5:8])
            r.tempo_recorde_pista = self.str_to_time(m, s, ms)
            r.cidade = self.cidade(**kwargs)
            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return r

    def evento(self, key, **kwargs):
        r = Evento.query.filter_by(local=kwargs[key]).first()
        if r is None:
            r = Evento()
            r.nome_evento = kwargs['nome_oficial_evento']
            r.local = kwargs['local']
            d, M, A = kwargs['data_inicio'][0:2], kwargs['data_inicio'][3:5], \
                      kwargs['data_inicio'][6:]
            r.data_inicio = self.str_to_date(d, M, A)
            d, M, A = kwargs['data_termino'][0:2], kwargs['data_termino'][3:5], \
                      kwargs['data_termino'][6:]
            r.data_termino = self.str_to_date(d, M, A)
            r.url = kwargs['url']
            r.img_evento = kwargs['img_file']
            r.flag_icon = kwargs['flag-icon']

            r.circuito = self.circuito(**kwargs)
            print(r)

        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return r

    def equipe(self, **kwargs):
        r = Equipe.query.filter_by(nome_equipe=kwargs['equipe']).first()
        if r is None:
            r = Equipe()
            r.nome_equipe = kwargs['equipe']
            r.nome_oficial = kwargs['nome_oficial']
            r.numero_titulos = kwargs['titulos_mundiais']
            r.nr_voltas_mais_rapidas = kwargs['voltas_mais_rapidas']
            r.nr_pole_positions = kwargs['pole_positions']
            r.unidade_potencia = kwargs['unidade_potencia']
            r.chassi = kwargs['chassis']
            r.primeiro_campeonato = kwargs['primeiro_campeonato']
            r.posicao_melhor_resultado = kwargs['posicao']
            r.nr_melhor_resultado = kwargs['quantidade']
            r.img = kwargs['img_file']
            r.logo = kwargs['img_logo']
            r.flag_icon = kwargs['flag-icon']
            r.url = kwargs['url']

            r.cidade = self.cidade(**kwargs)

            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return r

    def piloto(self, **kwargs):
        r = Piloto.query.filter_by(nome_piloto=kwargs['nome']).first()
        if r is None:
            r = Piloto()
            r.nome_piloto = kwargs['nome']
            r.slug = slugify(kwargs['nome'])
            r.numero_piloto = kwargs['#']
            r.pontos_ganhos = kwargs['pontos_ganhos']
            dia, mes, ano = kwargs['data_nascimento'][0:2], kwargs['data_nascimento'][3:5], kwargs['data_nascimento'][
                                                                                            6:]
            r.data_nasc = self.str_to_date(dia, mes, ano)
            r.corridas_disputadas = kwargs['gps_disputados']
            r.numero_podios = kwargs['podios']
            r.numero_titulos = kwargs['nr_titulos']
            r.pos_melhor_resultado = kwargs['posicao']
            r.nr_melhor_resultado = kwargs['quantidade']
            r.img = kwargs['img_file']
            r.flag_icon = kwargs['flag-icon']

            r.cidade = self.cidade(**kwargs)
            r.equipe = self.equipe(**kwargs)

            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        return r

    def titulos(self, ano, **kwargs):
        r = Titulo.query.filter_by(ano_titulo=ano).first()
        if r is None:
            r = Titulo()
            r.ano_titulo = ano
            r.piloto = self.piloto(**kwargs)

            print(r)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        return r

    def resultados(self, pos, pontos):
        r = Pontuacao.query.filter_by(posicao=pos).first()
        if r is None:
            r = Pontuacao()
            r.posicao = pos
            r.pontuacao_corrida = pontos

            print(r)

        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        return r

    def resultados_pilotos(self, **kwargs):
        r = Resultado_Piloto()
        r.resultado = self.resultados(kwargs['posicao'], kwargs['pontos_ganhos'])
        r.piloto = self.piloto(**kwargs)
        r.evento = self.evento('grande_premio', **kwargs)
        if 'melhor_volta' in kwargs:
            r.melhor_volta = kwargs['melhor_volta']
        else:
            r.melhor_volta = 0

        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        print(r)
        return r

    def usuarios(self):
        for i in range(150):
            usuario = Usuario.query.filter_by(
                nome_usuario=self.fake.user_name()
            ).first()
            if usuario is None:
                usuario = Usuario(
                    nome=self.fake.name(),
                    nome_usuario=self.fake.user_name(),
                    email=self.fake.email(),
                    data_nasc=self.fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=60),
                    endereco=self.fake.street_name(),
                    numero=self.fake.random_int(min=100, max=9999),
                    complemento=self.fake.neighborhood(),
                    bairro=self.fake.bairro(),
                    cidade=self.fake.city(),
                    estado=self.fake.state(),
                    pais=self.fake.country(),
                    funcao=random.choice(Funcao.query.all()),
                    senha='password',
                )

                print(i, usuario.nome_usuario)
            db.session.add(usuario)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def adicionar_papeis(self):
        papeis = {
            'Usuário': [
                Permissoes.ESCREVER,
                Permissoes.EDITAR,
                Permissoes.COMENTAR,
                Permissoes.POSTAR,
                Permissoes.SEGUIR
            ],
            'Moderador': [
                Permissoes.MODERAR,
                Permissoes.ESCREVER,
                Permissoes.EDITAR,
                Permissoes.COMENTAR,
                Permissoes.POSTAR,
                Permissoes.SEGUIR
            ],
            'Administrador': [
                Permissoes.ADMINISTRAR,
                Permissoes.MODERAR,
                Permissoes.ESCREVER,
                Permissoes.EDITAR,
                Permissoes.COMENTAR,
                Permissoes.POSTAR,
                Permissoes.SEGUIR
            ]
        }

        for (papel, permissoes) in papeis.items():
            p = Funcao.query.filter_by(nome_funcao=papel).first()
            if not p:
                p = Funcao(nome_funcao=papel)
                p.apagar_permissoes()

            for perm in permissoes:
                p.adicionar_permissao(perm)

            db.session.add(p)
            print(papel)
        db.session.commit()

    def posts(self):
        for i in range(100):
            self.titulo = self.fake.sentence(nb_words=random.randint(1, 12))
            self.t = self.fake.paragraphs(nb=random.randint(1, 8))

            texto = ""

            for paragrafo in self.t:
                texto += " " + paragrafo

            p = Post(
                titulo=self.titulo,
                texto=texto,
                slug=slugify(self.titulo),
                data=datetime.datetime.now(),
                autor=random.choice(Usuario.query.all())
            )
            db.session.add(p)
            db.session.commit()
            print(i, p.titulo)

"""

from app.models import *
Funcao.query.all()
f = Funcao.query.get(1)
"""


if __name__ == '__main__':

    os.system("rm -rf migrations/ data.sqlite")

    a = Populate_DB()
    a.app_config()
    a.db_config()
    data = a.load_json()

    corridas = data.get('calendario_temporada')
    equipes = data.get('equipes')
    pilotos = data.get('pilotos')
    pontuacao_corrida = data.get('pontuação')
    resultados = data.get('resultados')

    kwargs = {}

    print("\n\nCorridas")
    for corrida in corridas:
        for i in corrida:
            if type(corrida[i]).__name__ == 'dict':
                for j in corrida[i]:
                    kwargs[j] = corrida[i][j]
            else:
                kwargs[i] = corrida[i]
        a.pais(**kwargs)
        a.cidade(**kwargs)
        a.circuito(**kwargs)
        a.evento('nome_oficial_evento', **kwargs)

    kwargs.clear()

    print("\n\nEquipes")
    for equipe in equipes:
        for i in equipe:
            if type(equipe[i]).__name__ == 'dict':
                for j in equipe[i]:
                    kwargs[j] = equipe[i][j]
            else:
                kwargs[i] = equipe[i]
        a.pais(**kwargs)
        a.cidade(**kwargs)
        a.equipe(**kwargs)

    kwargs.clear()

    print("\n\nPilotos")
    for piloto in pilotos:
        print('\n')
        for (chave, valor) in piloto.items():
            if type(valor).__name__ == 'dict':
                for (c, v) in valor.items():
                    kwargs[c] = v
            else:
                kwargs[chave] = valor
        a.pais(**kwargs)
        a.cidade(**kwargs)
        a.equipe(**kwargs)
        a.piloto(**kwargs)
        for item in kwargs['titulos']:
            a.titulos(item, **kwargs)

    print("\n\nPontuação")
    for (chave, valor) in pontuacao_corrida.items():
        a.resultados(int(chave), valor)

    kwargs.clear()

    print("\n\nResultados")
    for (chave, valor) in resultados.items():
        kwargs['nome'] = chave
        for dict in valor:
            for (k, v) in dict.items():
                kwargs[k] = v
            a.resultados_pilotos(**kwargs)
        kwargs.clear()

    print("\n\nPapéis")
    a.adicionar_papeis()

    print("\n\nUsuários")
    a.usuarios()

    print("\n\nPosts")
    a.posts()