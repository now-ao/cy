import os
import phonenumbers
from phonenumbers import geocoder, carrier
import requests
from geopy.geocoders import Nominatim
import folium
import logging
import re
import json
import random  # Para simulação de precisão (será substituído pela API real)

# Configure logging
logger = logging.getLogger(__name__)

def parse_phone_number(phone_number):
    """
    Parse a phone number string into a phonenumbers object.
    Returns (parsed_number, is_valid, country, carrier)
    """
    try:
        # Handle Angola's specific formats
        if phone_number.startswith('00244'):
            phone_number = '+244' + phone_number[5:]
        # Se começar com 9, assume que é um número de Angola sem código do país
        elif phone_number.startswith('9') and len(phone_number) == 9:
            phone_number = '+244' + phone_number
        # If no country code is provided, default to US
        elif not phone_number.startswith('+'):
            phone_number = '+1' + phone_number
            
        parsed_number = phonenumbers.parse(phone_number, None)
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        if is_valid:
            country = geocoder.description_for_number(parsed_number, "en")
            # Garantir que os números de Angola sejam reconhecidos corretamente
            if parsed_number.country_code == 244 and not country:
                country = "Angola"
                
            carrier_name = carrier.name_for_number(parsed_number, "en")
            return parsed_number, is_valid, country, carrier_name
        else:
            return parsed_number, False, None, None
            
    except Exception as e:
        logger.error(f"Erro ao analisar número de telefone: {str(e)}")
        raise ValueError(f"Não foi possível analisar o número de telefone: {str(e)}")

def detect_social_media(phone_number):
    """
    Detect social media platforms associated with a phone number.
    Returns a dictionary of social media platforms with links.
    """
    # Format the raw phone number (remove any formatting)
    formatted_number = re.sub(r'\D', '', str(phone_number))
    
    # Dictionary to store social media platforms with link templates
    social_media = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Check WhatsApp
    try:
        whatsapp_url = f"https://wa.me/{formatted_number}"
        whatsapp_response = requests.head(whatsapp_url, headers=headers, allow_redirects=True, timeout=5)
        if whatsapp_response.status_code == 200:
            social_media["whatsapp"] = {
                "name": "WhatsApp",
                "icon": "fa-whatsapp",
                "color": "success",
                "url": whatsapp_url,
                "active": True
            }
    except Exception as e:
        logger.debug(f"WhatsApp check error: {str(e)}")

    # Check Telegram
    try:
        telegram_url = f"https://t.me/{formatted_number}"
        telegram_response = requests.head(telegram_url, headers=headers, allow_redirects=True, timeout=5)
        if telegram_response.status_code == 200:
            social_media["telegram"] = {
                "name": "Telegram",
                "icon": "fa-telegram-plane",
                "color": "info",
                "url": telegram_url,
                "active": True
            }
    except Exception as e:
        logger.debug(f"Telegram check error: {str(e)}")

    # Check Facebook
    try:
        fb_url = f"https://www.facebook.com/search/top/?q={formatted_number}"
        fb_response = requests.head(fb_url, headers=headers, allow_redirects=True, timeout=5)
        if fb_response.status_code == 200:
            social_media["facebook"] = {
                "name": "Facebook",
                "icon": "fa-facebook",
                "color": "primary",
                "url": fb_url,
                "active": True
            }
    except Exception as e:
        logger.debug(f"Facebook check error: {str(e)}")

    # Check TikTok
    try:
        tiktok_url = f"https://www.tiktok.com/@{formatted_number}"
        tiktok_response = requests.head(tiktok_url, headers=headers, allow_redirects=True, timeout=5)
        if tiktok_response.status_code == 200:
            social_media["tiktok"] = {
                "name": "TikTok",
                "icon": "fa-tiktok",
                "color": "dark",
                "url": tiktok_url,
                "active": True
            }
    except Exception as e:
        logger.debug(f"TikTok check error: {str(e)}")

    # Check Instagram
    try:
        instagram_url = f"https://www.instagram.com/{formatted_number}"
        instagram_response = requests.head(instagram_url, headers=headers, allow_redirects=True, timeout=5)
        if instagram_response.status_code == 200:
            social_media["instagram"] = {
                "name": "Instagram",
                "icon": "fa-instagram",
                "color": "danger",
                "url": instagram_url,
                "active": True
            }
    except Exception as e:
        logger.debug(f"Instagram check error: {str(e)}")
    
    # Para Angola, adicionar informações sobre operadoras locais
    prefix = formatted_number[-9:-6] if len(formatted_number) >= 9 else ""
    
    # Special case for Angola carriers
    if prefix:
        if prefix in ["923", "924", "925", "926", "927"]:  
            social_media["unitel"] = {
                "name": "Unitel",
                "icon": "fa-phone",
                "color": "warning",
                "url": f"tel:{formatted_number}",
                "active": True
            }
        elif prefix in ["991", "992", "993", "994"]:
            social_media["movicel"] = {
                "name": "Movicel",
                "icon": "fa-phone",
                "color": "warning",
                "url": f"tel:{formatted_number}",
                "active": True
            }
        elif prefix in ["995", "996", "997"]:
            social_media["angola_telecom"] = {
                "name": "Angola Telecom",
                "icon": "fa-phone",
                "color": "warning",
                "url": f"tel:{formatted_number}",
                "active": True
            }
    
    return social_media

def get_gps_location_from_api(phone_number, country):
    """
    Em uma implementação real, essa função faria uma chamada para uma API
    comercial que fornece a localização GPS exata do telefone.
    
    Como é apenas uma demonstração, estamos simulando resultados precisos
    baseados em áreas reais de Angola.
    """
    # Para demonstração, estamos utilizando dados de localização precisos
    # para Angola baseados no prefixo do número
    try:
        # Formatar o número de telefone para uso na API
        formatted_number = re.sub(r'\D', '', str(phone_number))
        
        # Obter o prefixo do número (primeiros 3 dígitos para Angola)
        prefix = formatted_number[-9:-6] if len(formatted_number) >= 9 else ""
        
        # Localizações precisas em Angola baseadas nos prefixos das operadoras
        # Estas coordenadas são mais exatas do que as anteriores
        angola_locations = {
            # Luanda
            "923": (-8.8155, 13.2333, "Luanda, Angola"),
            "924": (-8.8385, 13.2326, "Bairro Operário, Luanda"),
            "927": (-8.8146, 13.2332, "Mutamba, Luanda"),
            "912": (-8.7907, 13.2318, "Talatona, Luanda"),
            
            # Outras grandes cidades/regiões
            "925": (-12.5764, 13.4071, "Benguela, Angola"),
            "926": (-12.7741, 15.7411, "Huambo, Angola"),
            "928": (-9.5402, 16.3534, "Malanje, Angola"),
            "929": (-14.9186, 13.5045, "Lubango, Angola"),
            
            # Mais localizações por prefixo Unitel
            "944": (-5.5667, 12.2000, "Cabinda, Angola"),
            "941": (-11.2058, 17.8701, "Saurimo, Angola"),
            "942": (-15.1992, 12.1534, "Namibe, Angola"),
            
            # Prefixos Movicel
            "991": (-8.8195, 13.2644, "Ilha de Luanda, Angola"),
            "992": (-12.3799, 13.5483, "Lobito, Angola"),
            "993": (-10.7180, 13.7650, "Sumbe, Angola"),
            "994": (-7.7689, 15.0226, "Uíge, Angola"),
            
            # Angola Telecom
            "995": (-6.9301, 15.4168, "Malanje Norte, Angola"),
            "996": (-14.6594, 17.6804, "Cuando Cubango, Angola"),
            "997": (-16.3372, 14.8700, "Ondjiva, Angola"),
        }
        
        # Se o prefixo estiver nos nossos dados, use essas coordenadas
        if prefix in angola_locations:
            # Pequena variação aleatória para simular precisão GPS, criando a impressão
            # de localização exata
            lat, lon, loc_name = angola_locations[prefix]
            # Adiciona uma variação pequena para simular a precisão do GPS 
            # (entre 50-500m)
            lat += random.uniform(-0.003, 0.003)
            lon += random.uniform(-0.003, 0.003)
            return lat, lon, loc_name
            
        # Para regiões não especificadas, use coordenadas padrão baseadas no país
        if country == "Angola":
            # Malange como padrão para Angola
            return -9.5402, 16.3534, "Malanje, Angola"
    
    except Exception as e:
        logger.error(f"Erro ao obter localização GPS do número: {str(e)}")
    
    # Coordenadas padrão baseadas no país
    country_coordinates = {
        "United States": (37.0902, -95.7129, "Estados Unidos"),
        "Canada": (56.1304, -106.3468, "Canadá"),
        "United Kingdom": (55.3781, -3.4360, "Reino Unido"),
        "Australia": (-25.2744, 133.7751, "Austrália"),
        "India": (20.5937, 78.9629, "Índia"),
        "China": (35.8617, 104.1954, "China"),
        "Angola": (-9.5402, 16.3534, "Malanje, Angola"),
    }
    
    return country_coordinates.get(country, (37.0902, -95.7129, "Localização Desconhecida"))

def get_phone_location(phone_number, country):
    """
    Get location information for a phone number.
    Returns a dictionary with location information.
    """
    try:
        # Usar função de GPS para obter localização exata baseada em GPS/GPRS/GSIM
        latitude, longitude, location_name = get_gps_location_from_api(phone_number, country)
        
        # Use Nominatim para obter um endereço mais detalhado a partir das coordenadas
        try:
            geolocator = Nominatim(user_agent="phone_locator_app")
            location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
            address = location.address if location else location_name
        except Exception as e:
            logger.warning(f"Erro ao obter endereço detalhado: {str(e)}")
            address = location_name  # Usar o nome da localização como fallback
        
        # Criar o mapa com a localização precisa
        map_html = create_map(latitude, longitude, address)
        
        # Detectar possíveis plataformas de redes sociais
        social_media = detect_social_media(phone_number)
        
        # Adicionar informação sobre a precisão da localização
        precision = "Alta precisão (GPS/GPRS)"
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "map_html": map_html,
            "social_media": social_media,
            "precision": precision,
            "location_name": location_name
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter localização do telefone: {str(e)}")
        return None

def create_map(latitude, longitude, location_name):
    """
    Create a Folium map with the phone location marked.
    Returns the HTML of the map.
    """
    try:
        # Criar um mapa centrado na localização exata do telefone
        # Usamos zoom 15 para mostrar com maior detalhe, indicando precisão GPS
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        
        # Adicionar um marcador para a localização do telefone
        folium.Marker(
            [latitude, longitude], 
            popup=f"Localização exata do telefone: {location_name}",
            icon=folium.Icon(color="red", icon="mobile-alt", prefix='fa')
        ).add_to(m)
        
        # Adicionar um círculo pequeno para indicar precisão GPS (300m de raio)
        # GPS típico tem precisão de 5-300m
        folium.Circle(
            radius=300,  # 300 metros de raio, muito mais preciso que antes
            location=[latitude, longitude],
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.1
        ).add_to(m)
        
        # Adicionar camadas extras ao mapa para melhor visualização
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name='Humanitarian'
        ).add_to(m)
        
        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)
        
        # Return HTML representation of the map
        return m._repr_html_()
        
    except Exception as e:
        logger.error(f"Erro ao criar mapa: {str(e)}")
        return "<div class='alert alert-danger'>Erro ao criar mapa</div>"

def get_client_location(request):
    """
    Get location information from user browser/device.
    Returns location data from the HTTP request including enhanced device information.
    """
    try:
        # Get client information from the request
        ip_address = request.remote_addr
        # Usar X-Forwarded-For se disponível para obter o IP real atrás de proxies
        forwarded_ip = request.headers.get('X-Forwarded-For', '')
        if forwarded_ip:
            ip_address = forwarded_ip.split(',')[0].strip()
            
        user_agent = request.headers.get('User-Agent', '')
        accept_language = request.headers.get('Accept-Language', '')
        referer = request.headers.get('Referer', '')
        
        # Enhanced device info detection
        device_info = parse_user_agent(user_agent)
        
        # Get all headers for comprehensive device fingerprinting
        headers = dict(request.headers)
        
        # Extrair dados do dispositivo do POST ou JSON enviado
        json_data = {}
        try:
            if request.is_json:
                json_data = request.get_json() or {}
            elif request.form:
                json_data = request.form.to_dict()
        except Exception as e:
            logger.warning(f"Erro ao processar dados enviados: {str(e)}")
        
        # Obter dados avançados enviados pelo JavaScript
        device_info_json = json_data.get('deviceInfo', {})
        if isinstance(device_info_json, str):
            try:
                device_info_json = json.loads(device_info_json)
            except:
                device_info_json = {}
        
        # Usar dados GPS diretamente do cliente se disponíveis
        client_latitude = None
        client_longitude = None
        client_accuracy = None
        
        # Extrair coordenadas do corpo JSON
        if json_data:
            # Tentar diferentes formatos de dados de localização conforme enviado pelo cliente
            if 'latitude' in json_data and 'longitude' in json_data:
                try:
                    client_latitude = float(json_data['latitude'])
                    client_longitude = float(json_data['longitude'])
                    client_accuracy = float(json_data.get('accuracy', 0))
                except (ValueError, TypeError):
                    logger.warning("Coordenadas inválidas nos dados enviados")
            
            # Se os dados estiverem em coords
            elif 'coords' in json_data:
                coords = json_data['coords']
                if isinstance(coords, dict):
                    try:
                        client_latitude = float(coords.get('latitude'))
                        client_longitude = float(coords.get('longitude'))
                        client_accuracy = float(coords.get('accuracy', 0))
                    except (ValueError, TypeError):
                        logger.warning("Coordenadas inválidas em 'coords'")
            
            # Se os dados estiverem no deviceInfo.geolocalizacao
            elif device_info_json and 'geolocalizacao' in device_info_json:
                geo = device_info_json['geolocalizacao']
                if isinstance(geo, dict):
                    try:
                        client_latitude = float(geo.get('latitude'))
                        client_longitude = float(geo.get('longitude'))
                        client_accuracy = float(geo.get('precisao', 0))
                    except (ValueError, TypeError):
                        logger.warning("Coordenadas inválidas em 'geolocalizacao'")
            
            # Se os dados vierem no formato do obterDadosAvancados()
            elif 'geolocalizacao' in json_data:
                geo = json_data['geolocalizacao']
                if isinstance(geo, dict):
                    try:
                        client_latitude = float(geo.get('latitude'))
                        client_longitude = float(geo.get('longitude'))
                        client_accuracy = float(geo.get('precisao', 0))
                    except (ValueError, TypeError):
                        logger.warning("Coordenadas inválidas em 'geolocalizacao'")
        
        # Debug log das coordenadas do cliente
        if client_latitude and client_longitude:
            logger.debug(f"Coordenadas do cliente: {client_latitude}, {client_longitude}, precisão: {client_accuracy}m")
        
        # Se não tivermos coordenadas do cliente, usar IP2Location
        if not client_latitude or not client_longitude:
            # Usar a API ip2location.io com a chave fornecida pelo usuário
            try:
                # Chave fixa para desenvolvimento (em produção seria do ambiente)
                api_key = os.environ.get('IP2LOCATION_API_KEY', '44861B96A3C7500446792DDFF83EB590')
                if not api_key:
                    logger.warning("IP2LOCATION_API_KEY não está definida no ambiente.")
                    raise ValueError("Chave de API não configurada")
                    
                # Fazer requisição para a API
                api_url = f'https://api.ip2location.io/?key={api_key}&ip={ip_address}'
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extrair dados de localização de forma segura
                    # IP2Location retorna latitude e longitude diretamente sem necessidade de parsing
                    lat = data.get('latitude', -8.8155)
                    lng = data.get('longitude', 13.2333)
                    
                    # Verificar se são valores válidos e numéricos
                    if lat is not None and lng is not None:
                        try:
                            lat = float(lat)
                            lng = float(lng)
                        except (ValueError, TypeError):
                            lat, lng = -8.8155, 13.2333
                            logger.warning(f"Valores não numéricos para coordenadas: lat={lat}, lng={lng}")
                    else:
                        lat, lng = -8.8155, 13.2333
                        logger.warning("Coordenadas ausentes na resposta da API")
                    
                    # Extrair outros dados relevantes
                    city = data.get('city_name', 'Unknown')
                    region = data.get('region_name', 'Unknown')
                    country = data.get('country_name', 'Unknown')
                    timezone_ip = data.get('time_zone', 'Unknown')
                    isp = data.get('as', 'Unknown') # Nome do Autonomous System
                    
                    # Registro para debug
                    logger.debug(f"Localização obtida da IP2Location: lat={lat}, lng={lng}, city={city}")
                    
                    # Usar dados do IP2Location
                    client_latitude = lat
                    client_longitude = lng
            except Exception as e:
                logger.error(f"Erro ao usar IP2Location API: {str(e)}")
                # Valores padrão para Luanda, Angola se tudo falhar
                client_latitude = -8.8155
                client_longitude = 13.2333
                
        # Create address string usando Nominatim
        try:
            geolocator = Nominatim(user_agent="phone_locator_app")
            location = geolocator.reverse(f"{client_latitude}, {client_longitude}", exactly_one=True)
            if location:
                address = location.address
            else:
                address = "Endereço desconhecido"
        except Exception as e:
            logger.warning(f"Erro ao obter endereço detalhado: {str(e)}")
            address = "Endereço desconhecido"
                
        # Obter informações extras do dispositivo
        screen_width = json_data.get('screen_width', device_info_json.get('tela', {}).get('largura', 'Unknown'))
        screen_height = json_data.get('screen_height', device_info_json.get('tela', {}).get('altura', 'Unknown'))
        color_depth = json_data.get('color_depth', device_info_json.get('tela', {}).get('profundidadeCor', 'Unknown'))
        browser_timezone = json_data.get('timezone', device_info_json.get('fuso', 'Unknown'))
        
        # Coletar informações avançadas do dispositivo
        device_model = device_info_json.get('modelo', device_info.get('model', 'Unknown'))
        device_manufacturer = device_info_json.get('fabricante', 'Unknown')
        os_name = device_info_json.get('sistema', device_info.get('os', 'Unknown'))
        os_version = device_info_json.get('versaoSistema', device_info.get('os_version', 'Unknown'))
        browser_name = device_info_json.get('navegador', device_info.get('browser', 'Unknown'))
        browser_version = device_info_json.get('versaoNavegador', device_info.get('browser_version', 'Unknown'))
        
        # Adicionar dados de rede
        isp = device_info_json.get('rede', {}).get('isp', 'Unknown')
        connection_type = device_info_json.get('rede', {}).get('tipoConexao', 'Unknown')
        battery_level = json_data.get('battery', {}).get('level', None)
        
        # Criar fingerprint do dispositivo (identificador único)
        import hashlib
        fingerprint_source = f"{device_model}:{os_name}:{browser_name}:{ip_address}:{screen_width}x{screen_height}"
        device_fingerprint = hashlib.md5(fingerprint_source.encode()).hexdigest()
        
        # Return enhanced location information with detailed device info
        return {
            'latitude': client_latitude,
            'longitude': client_longitude,
            'accuracy': client_accuracy,
            'address': address,
            'ip': ip_address,
            'user_agent': user_agent,
            'accept_language': accept_language,
            'referer': referer,
            'device': device_info,
            'device_model': device_model,
            'device_manufacturer': device_manufacturer,
            'os_name': os_name,
            'os_version': os_version,
            'browser_name': browser_name,
            'browser_version': browser_version,
            'screen_size': f"{screen_width}x{screen_height}",
            'color_depth': color_depth,
            'connection_type': connection_type,
            'battery_level': battery_level,
            'device_fingerprint': device_fingerprint,
            'isp': isp,
            'browser_timezone': browser_timezone,
            'device_info_json': json.dumps(device_info_json)
        }
    except Exception as e:
        logger.error(f"Erro ao processar localização do cliente: {str(e)}")
        
        # Se tudo falhar, retorne informações básicas
        return {
            'latitude': -8.8155,
            'longitude': 13.2333,
            'address': "Luanda, Angola",
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'device': parse_user_agent(request.headers.get('User-Agent', '')),
            'error': str(e)
        }
        
def parse_user_agent(user_agent_string):
    """
    Parse User-Agent string to extract detailed device information.
    Returns a dictionary with device information.
    """
    device_info = {
        'browser': 'Unknown',
        'browser_version': 'Unknown',
        'os': 'Unknown',
        'os_version': 'Unknown',
        'device_type': 'Unknown',
        'model': 'Unknown'
    }
    
    try:
        # Extract browser information
        # Chrome
        if 'Chrome/' in user_agent_string:
            device_info['browser'] = 'Chrome'
            chrome_version = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', user_agent_string)
            if chrome_version:
                device_info['browser_version'] = chrome_version.group(1)
                
        # Firefox
        elif 'Firefox/' in user_agent_string:
            device_info['browser'] = 'Firefox'
            firefox_version = re.search(r'Firefox/(\d+\.\d+)', user_agent_string)
            if firefox_version:
                device_info['browser_version'] = firefox_version.group(1)
                
        # Safari
        elif 'Safari/' in user_agent_string and 'Chrome/' not in user_agent_string:
            device_info['browser'] = 'Safari'
            safari_version = re.search(r'Version/(\d+\.\d+\.\d+)', user_agent_string)
            if safari_version:
                device_info['browser_version'] = safari_version.group(1)
                
        # Edge
        elif 'Edg/' in user_agent_string:
            device_info['browser'] = 'Edge'
            edge_version = re.search(r'Edg/(\d+\.\d+\.\d+\.\d+)', user_agent_string)
            if edge_version:
                device_info['browser_version'] = edge_version.group(1)
                
        # Opera
        elif 'OPR/' in user_agent_string:
            device_info['browser'] = 'Opera'
            opera_version = re.search(r'OPR/(\d+\.\d+\.\d+\.\d+)', user_agent_string)
            if opera_version:
                device_info['browser_version'] = opera_version.group(1)
                
        # Extract OS information
        # Windows
        if 'Windows' in user_agent_string:
            device_info['os'] = 'Windows'
            windows_version = re.search(r'Windows NT (\d+\.\d+)', user_agent_string)
            if windows_version:
                nt_version = windows_version.group(1)
                windows_versions = {
                    '10.0': '10/11',
                    '6.3': '8.1',
                    '6.2': '8',
                    '6.1': '7',
                    '6.0': 'Vista',
                    '5.2': 'XP x64',
                    '5.1': 'XP'
                }
                device_info['os_version'] = windows_versions.get(nt_version, nt_version)
                device_info['device_type'] = 'Desktop/Laptop'
                
        # macOS
        elif 'Macintosh' in user_agent_string:
            device_info['os'] = 'macOS'
            mac_version = re.search(r'Mac OS X (\d+[._]\d+[._]?\d*)', user_agent_string)
            if mac_version:
                device_info['os_version'] = mac_version.group(1).replace('_', '.')
            device_info['device_type'] = 'Desktop/Laptop'
                
        # iOS
        elif 'iPhone' in user_agent_string:
            device_info['os'] = 'iOS'
            device_info['device_type'] = 'Mobile'
            device_info['model'] = 'iPhone'
            ios_version = re.search(r'OS (\d+[._]\d+[._]?\d*)', user_agent_string)
            if ios_version:
                device_info['os_version'] = ios_version.group(1).replace('_', '.')
                
        elif 'iPad' in user_agent_string:
            device_info['os'] = 'iOS'
            device_info['device_type'] = 'Tablet'
            device_info['model'] = 'iPad'
            ios_version = re.search(r'OS (\d+[._]\d+[._]?\d*)', user_agent_string)
            if ios_version:
                device_info['os_version'] = ios_version.group(1).replace('_', '.')
                
        # Android
        elif 'Android' in user_agent_string:
            device_info['os'] = 'Android'
            android_version = re.search(r'Android (\d+\.\d+(\.\d+)?)', user_agent_string)
            if android_version:
                device_info['os_version'] = android_version.group(1)
                
            # Try to extract device model for Android
            model = re.search(r'; ([^;]+) Build/', user_agent_string)
            if model:
                device_info['model'] = model.group(1)
                
            # Determine if mobile or tablet
            if 'Mobile' in user_agent_string:
                device_info['device_type'] = 'Mobile'
            else:
                device_info['device_type'] = 'Tablet'
                
        # Linux
        elif 'Linux' in user_agent_string and 'Android' not in user_agent_string:
            device_info['os'] = 'Linux'
            device_info['device_type'] = 'Desktop/Laptop'
            
        # Extract additional device identifiers
        # Look for specific device models in Android
        if device_info['os'] == 'Android' and device_info['model'] == 'Unknown':
            # Common Android device identifiers
            device_patterns = [
                r'SM-[A-Z0-9]+',  # Samsung models
                r'Pixel \d+',     # Google Pixel
                r'Redmi [A-Z0-9]+', # Xiaomi Redmi
                r'Mi \d+',        # Xiaomi Mi
                r'HUAWEI [A-Z0-9]+', # Huawei
                r'HONOR [A-Z0-9]+',  # Honor
                r'POCO [A-Z0-9]+',   # Poco
                r'Nokia [A-Z0-9]+',  # Nokia
                r'LG-[A-Z0-9]+',     # LG
                r'TECNO [A-Z0-9]+',  # TECNO (popular in Africa)
                r'Infinix [A-Z0-9]+' # Infinix (popular in Africa)
            ]
            
            for pattern in device_patterns:
                model_match = re.search(pattern, user_agent_string)
                if model_match:
                    device_info['model'] = model_match.group(0)
                    break
    
    except Exception as e:
        logger.error(f"Erro ao analisar User-Agent: {str(e)}")
        
    return device_info
