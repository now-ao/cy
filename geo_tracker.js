/**
 * Sistema avançado de rastreamento GPS - MTelus
 * Obtém a localização GPS precisa dos dispositivos
 */

// Armazena informações do dispositivo
let deviceInfo = {
    browser: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    connection: null,
    screen: {
        width: window.screen.width,
        height: window.screen.height,
        colorDepth: window.screen.colorDepth,
        orientation: window.screen.orientation ? window.screen.orientation.type : 'unknown'
    },
    device: {
        model: '',
        vendor: '',
        memory: navigator.deviceMemory || 'unknown'
    }
};

// Tenta obter mais informações sobre o dispositivo
if (navigator.userAgentData) {
    navigator.userAgentData.getHighEntropyValues([
        "architecture",
        "model",
        "platform",
        "platformVersion",
        "fullVersionList"
    ]).then(data => {
        deviceInfo.device.model = data.model;
        deviceInfo.platform = `${data.platform} ${data.platformVersion}`;
        deviceInfo.architecture = data.architecture;
    }).catch(err => {
        console.log("Não foi possível obter detalhes avançados:", err);
    });
}

// Informações de conexão
if (navigator.connection) {
    deviceInfo.connection = {
        type: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt,
        saveData: navigator.connection.saveData
    };
}

/**
 * Obtém a localização geográfica precisa usando GPS
 */
function getExactGeolocation(options = {}) {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('A geolocalização não é suportada por este navegador'));
            return;
        }

        // Opções de alta precisão para o GPS
        const geoOptions = {
            enableHighAccuracy: true, // Usa GPS de alta precisão quando disponível
            timeout: 10000,          // Timeout de 10 segundos
            maximumAge: 0,           // Sempre obter posição atual
            ...options
        };

        navigator.geolocation.getCurrentPosition(
            position => {
                const locationData = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude,
                    altitudeAccuracy: position.coords.altitudeAccuracy,
                    heading: position.coords.heading,
                    speed: position.coords.speed,
                    timestamp: position.timestamp,
                    deviceInfo: deviceInfo
                };
                resolve(locationData);
            },
            error => {
                console.error('Erro ao obter localização:', error.message);
                reject(error);
            },
            geoOptions
        );
    });
}

/**
 * Envia a localização para o servidor
 */
function trackLocation(trackingId) {
    // Mostra um indicador de carregamento
    const statusElement = document.getElementById('tracking-status');
    if (statusElement) {
        statusElement.innerHTML = `
            <div class="d-flex align-items-center justify-content-center">
                <div class="spinner-border text-primary me-2" role="status"></div>
                <span>Obtendo localização GPS precisa...</span>
            </div>
        `;
    }

    // Obtém a localização exata
    getExactGeolocation()
        .then(locationData => {
            // Mostra resultado
            if (statusElement) {
                statusElement.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i>
                        Localização obtida com sucesso!
                    </div>
                `;
            }

            // Envia para o servidor
            return fetch('/submit_location/' + trackingId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(locationData)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao enviar localização');
            }
            return response.json();
        })
        .then(data => {
            console.log('Sucesso:', data);
            
            // Atualiza a página com os dados de localização
            updateLocationDisplay(data);
        })
        .catch(error => {
            console.error('Erro:', error);
            if (statusElement) {
                statusElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erro ao obter localização: ${error.message}
                    </div>
                `;
            }
        });
}

/**
 * Atualiza a exibição com os dados de localização
 */
function updateLocationDisplay(data) {
    const locationDetailsElement = document.getElementById('location-details');
    const mapElement = document.getElementById('map-container');
    
    if (locationDetailsElement) {
        // Formatar coordenadas para melhor legibilidade
        const formatCoord = (coord) => {
            if (coord === null || coord === undefined) return 'N/A';
            return coord.toFixed(6);
        };
        
        // Construir HTML para informações de localização
        let locationHTML = `
            <div class="location-card">
                <div class="location-header">
                    <i class="fas fa-satellite fa-lg me-2"></i>
                    <h4>Localização GPS Exata</h4>
                </div>
                <div class="location-body">
                    <table class="table table-sm table-bordered">
                        <tr>
                            <th>Latitude:</th>
                            <td>${formatCoord(data.latitude)}</td>
                        </tr>
                        <tr>
                            <th>Longitude:</th>
                            <td>${formatCoord(data.longitude)}</td>
                        </tr>`;
        
        // Adicionar altitude se disponível
        if (data.altitude) {
            locationHTML += `
                        <tr>
                            <th>Altitude:</th>
                            <td>${formatCoord(data.altitude)} metros</td>
                        </tr>`;
        }
        
        // Adicionar precisão se disponível
        if (data.accuracy) {
            locationHTML += `
                        <tr>
                            <th>Precisão:</th>
                            <td>${Math.round(data.accuracy)} metros</td>
                        </tr>`;
        }
        
        // Adicionar endereço se disponível
        if (data.address) {
            locationHTML += `
                        <tr>
                            <th>Endereço:</th>
                            <td>${data.address}</td>
                        </tr>`;
        }
        
        // Adicionar IP se disponível
        if (data.ip) {
            locationHTML += `
                        <tr>
                            <th>Endereço IP:</th>
                            <td>${data.ip}</td>
                        </tr>`;
        }
        
        // Fechar a tabela e adicionar detalhes avançados do dispositivo
        locationHTML += `
                    </table>
                    
                    <div class="device-info-section mt-4">
                        <h5><i class="fas fa-mobile-alt me-2"></i>Informações do Dispositivo</h5>
                        <table class="table table-sm table-bordered">`;
        
        // Verificar se estamos usando o sistema de fingerprinting avançado
        if (data.deviceInfo.fingerprint) {
            // Usando o sistema de fingerprinting avançado
            const fp = data.deviceInfo;
            
            // Sistema operacional e navegador (das informações avançadas)
            locationHTML += `
                            <tr>
                                <th>Sistema:</th>
                                <td>${fp.device?.os || 'Desconhecido'} ${fp.device?.os_version || ''}</td>
                            </tr>
                            <tr>
                                <th>Navegador:</th>
                                <td>${fp.device?.browser || 'Desconhecido'} ${fp.device?.browser_version || ''}</td>
                            </tr>`;
            
            // Informações do dispositivo
            if (fp.device?.model || fp.device?.device_type) {
                locationHTML += `
                            <tr>
                                <th>Dispositivo:</th>
                                <td>${fp.device?.device_type || 'Desconhecido'}${fp.device?.model ? ' - ' + fp.device.model : ''}</td>
                            </tr>`;
            }
            
            // Informações de tela
            if (fp.screen) {
                locationHTML += `
                            <tr>
                                <th>Tela:</th>
                                <td>${fp.screen.width}x${fp.screen.height} (${fp.screen.colorDepth}bit)</td>
                            </tr>`;
            }
            
            // Conexão de rede
            if (fp.connection) {
                locationHTML += `
                            <tr>
                                <th>Conexão:</th>
                                <td>${fp.connection.type || 'Desconhecido'} ${fp.connection.downlink ? '(' + fp.connection.downlink + ' Mbps)' : ''}</td>
                            </tr>`;
            }
            
            // Bateria
            if (fp.battery) {
                const batteryLevel = Math.round(fp.battery.level * 100);
                const batteryStatus = fp.battery.charging ? 'Carregando' : 'Descarregando';
                locationHTML += `
                            <tr>
                                <th>Bateria:</th>
                                <td>${batteryLevel}% (${batteryStatus})</td>
                            </tr>`;
            }
            
            // Fuso horário
            if (fp.time && fp.time.timezone) {
                locationHTML += `
                            <tr>
                                <th>Fuso Horário:</th>
                                <td>${fp.time.timezone}</td>
                            </tr>`;
            }
            
            // Recursos do dispositivo
            const hasWebGL = fp.webgl && fp.webgl.supported;
            const touchSupport = fp.capabilities && fp.capabilities.touch_support;
            
            let capabilities = [];
            if (hasWebGL) capabilities.push('WebGL');
            if (touchSupport) capabilities.push('Touch Screen');
            if (fp.capabilities && fp.capabilities.hardware_concurrency) 
                capabilities.push(`${fp.capabilities.hardware_concurrency} CPU Cores`);
            if (fp.capabilities && fp.capabilities.device_memory) 
                capabilities.push(`${fp.capabilities.device_memory}GB RAM`);
            
            if (capabilities.length > 0) {
                locationHTML += `
                            <tr>
                                <th>Recursos:</th>
                                <td>${capabilities.join(', ')}</td>
                            </tr>`;
            }
            
            // Canvas fingerprint
            if (fp.canvas_fingerprint) {
                locationHTML += `
                            <tr>
                                <th>ID Único:</th>
                                <td>${fp.canvas_fingerprint.substring(0, 8)}...</td>
                            </tr>`;
            }
            
            // Dados de câmera e microfone
            if (fp.media && (fp.media.audio_inputs !== null || fp.media.video_inputs !== null)) {
                const mediaDevices = [];
                if (fp.media.video_inputs) mediaDevices.push(`${fp.media.video_inputs} câmera(s)`);
                if (fp.media.audio_inputs) mediaDevices.push(`${fp.media.audio_inputs} microfone(s)`);
                
                if (mediaDevices.length > 0) {
                    locationHTML += `
                            <tr>
                                <th>Dispositivos:</th>
                                <td>${mediaDevices.join(', ')}</td>
                            </tr>`;
                }
            }
            
        } else {
            // Sistema básico de informações do dispositivo (compatibilidade)
            locationHTML += `
                            <tr>
                                <th>Dispositivo:</th>
                                <td>${data.deviceInfo.platform || 'Desconhecido'}</td>
                            </tr>
                            <tr>
                                <th>Navegador:</th>
                                <td>${data.deviceInfo.browser ? (data.deviceInfo.browser.split(') ')[0].split(' (')[0]) : 'Desconhecido'}</td>
                            </tr>`;
            
            // Adicionar modelo se disponível
            if (data.deviceInfo.device && data.deviceInfo.device.model) {
                locationHTML += `
                            <tr>
                                <th>Modelo:</th>
                                <td>${data.deviceInfo.device.model}</td>
                            </tr>`;
            }
            
            // Adicionar informações de conexão
            if (data.deviceInfo.connection) {
                locationHTML += `
                            <tr>
                                <th>Conexão:</th>
                                <td>${data.deviceInfo.connection.type || 'Desconhecido'}</td>
                            </tr>`;
            }
            
            // Adicionar informações de tela
            if (data.deviceInfo.screen) {
                locationHTML += `
                            <tr>
                                <th>Tela:</th>
                                <td>${data.deviceInfo.screen.width}x${data.deviceInfo.screen.height}</td>
                            </tr>`;
            }
        }
        
        // Fechar a tabela e finalizar o card
        locationHTML += `
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        locationDetailsElement.innerHTML = locationHTML;
        locationDetailsElement.classList.remove('d-none');
    }
    
    // Atualizar o mapa se houver um mapa disponível
    if (data.mapHtml && mapElement) {
        mapElement.innerHTML = data.mapHtml;
        mapElement.classList.remove('d-none');
    }
}