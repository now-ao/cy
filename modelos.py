
# Importações necessárias
from aplicacao import db
from datetime import datetime
import uuid

# Modelo para histórico de buscas
class HistoricoBusca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_telefone = db.Column(db.String(20), nullable=False)
    codigo_pais = db.Column(db.String(50), nullable=False)
    operadora = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    endereco = db.Column(db.String(255))
    hora_busca = db.Column(db.DateTime, default=datetime.utcnow)

[... continua com o resto dos modelos com comentários em português ...]
