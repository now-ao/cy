# Importações necessárias
import os
import phonenumbers
from phonenumbers import geocoder, carrier
import requests
from geopy.geocoders import Nominatim
import folium
import logging
import re
import json
import random

# Configuração de logging
logger = logging.getLogger(__name__)

# Função para análise do número de telefone
def analisar_numero_telefone(numero_telefone):
    """
    Analisa um número de telefone e retorna informações sobre ele
    """
    try:
        # Tratamento especial para números de Angola
        if numero_telefone.startswith('00244'):
            numero_telefone = '+244' + numero_telefone[5:]

        # Número formatado
        formatted_number = phonenumbers.format_number(phonenumbers.parse(numero_telefone), phonenumbers.PhoneNumberFormat.E164)

        # Informações geográficas
        geocoded_location = geocoder.description_for_number(phonenumbers.parse(numero_telefone), 'pt-BR')

        # Informações da operadora
        operadora = carrier.name_for_number(phonenumbers.parse(numero_telefone), 'pt-BR')

        # Dados para redes sociais
        social_media = {}
        # Para Angola, adicionar informações sobre operadoras locais
        prefix = formatted_number[-9:-6] if len(formatted_number) >= 9 else ""

        # Prefixos atualizados das operadoras de Angola
        if prefix:
            # Unitel (91X, 92X, 93X, 94X, 97X)
            if (prefix.startswith("91") or prefix.startswith("92") or 
                prefix.startswith("93") or prefix.startswith("94") or 
                prefix.startswith("97")):
                social_media["unitel"] = {
                    "name": "Unitel",
                    "icon": "fa-phone",
                    "color": "warning",
                    "url": f"tel:{formatted_number}",
                    "active": True
                }
            # Movicel (96X)
            elif prefix.startswith("96"):
                social_media["movicel"] = {
                    "name": "Movicel",
                    "icon": "fa-phone",
                    "color": "warning",
                    "url": f"tel:{formatted_number}",
                    "active": True
                }
            # Africell (95X)
            elif prefix.startswith("95"):
                social_media["africell"] = {
                    "name": "Africell",
                    "icon": "fa-phone",
                    "color": "warning",
                    "url": f"tel:{formatted_number}",
                    "active": True
                }

        # Retorna as informações coletadas
        return {
            "numero_telefone": formatted_number,
            "localizacao": geocoded_location,
            "operadora": operadora,
            "redes_sociais": social_media
        }

    except Exception as e:
        logger.exception(f"Erro ao analisar número de telefone: {e}")
        return None


# Função para obter localização geográfica
def obter_localizacao_geografica(numero_telefone):
    """
    Obtém a localização geográfica de um número de telefone.
    """
    try:
        num = phonenumbers.parse(numero_telefone)
        geolocator = Nominatim(user_agent="geo_app")
        location = geolocator.reverse(geocoder.description_for_number(num, 'pt-BR'))
        return location.address if location else "Localização desconhecida"

    except Exception as e:
        logger.exception(f"Erro ao obter localização geográfica: {e}")
        return "Erro ao obter localização geográfica"



# Função para criar mapa
def criar_mapa(latitude, longitude, localizacao, numero_telefone):
    """
    Cria um mapa com a localização geográfica do número de telefone.
    """
    try:
        mapa = folium.Map(location=[latitude, longitude], zoom_start=12)
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(f"Número: {numero_telefone}<br> Localização: {localizacao}", max_width=2650),
            tooltip="Clique para ver detalhes",
        ).add_to(mapa)
        return mapa.get_root().render()

    except Exception as e:
        logger.exception(f"Erro ao criar mapa: {e}")
        return "Erro ao criar mapa"

#Função para gerar um código QR
def gerar_codigo_qr(numero_telefone):
    try:
        import qrcode
        img = qrcode.make(numero_telefone)
        img.save("qrcode.png")
        return "qrcode.png"
    except Exception as e:
        logger.exception(f"Erro ao gerar QR Code: {e}")
        return "Erro ao gerar QR Code"

# Função para extrair números de telefone de um texto
def extrair_numeros_telefone(texto):
    """
    Extrai todos os números de telefone de um texto fornecido.
    """
    numeros = re.findall(r'\+?[1-9]\d{1,14}', texto)
    return numeros

#Função para gerar dados para o json
def gerar_dados_json(numero_telefone):
  try:
    dados = analisar_numero_telefone(numero_telefone)
    if dados:
      localizacao = obter_localizacao_geografica(numero_telefone)
      latitude, longitude = obter_coordenadas(localizacao)
      dados["localizacao_detalhada"] = localizacao
      dados["mapa"] = criar_mapa(latitude, longitude, localizacao, numero_telefone)
      dados["qrcode"] = gerar_codigo_qr(numero_telefone)
      return dados
    else:
      return {"erro": "Não foi possível analisar o número de telefone"}
  except Exception as e:
    logger.exception(f"Erro ao gerar dados JSON: {e}")
    return {"erro": "Erro ao gerar dados JSON"}


#Função para obter coordenadas
def obter_coordenadas(localizacao):
    try:
        geolocator = Nominatim(user_agent="geo_app")
        location = geolocator.geocode(localizacao)
        if location:
            return location.latitude, location.longitude
        else:
            return 0, 0 #Retorna coordenadas default se não encontrar
    except Exception as e:
        logger.exception(f"Erro ao obter coordenadas: {e}")
        return 0, 0


#Função para gerar um ficheiro json
def gerar_ficheiro_json(dados, nome_ficheiro="dados_telefone.json"):
    try:
        with open(nome_ficheiro, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return nome_ficheiro
    except Exception as e:
        logger.exception(f"Erro ao gerar ficheiro JSON: {e}")
        return "Erro ao gerar ficheiro JSON"



#Exemplo de uso

numero_telefone = input("Introduza um número de telefone: ")
dados_json = gerar_dados_json(numero_telefone)
ficheiro_json = gerar_ficheiro_json(dados_json)
print(f"Dados do telefone gerados com sucesso em {ficheiro_json}")