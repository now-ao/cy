/**
 * Auto Geolocation Module
 * Versão automática que aceita a localização sem mostrar diálogos de permissão
 */

// Configuração de preferências para aceitação automática
const GEO_PREF_KEY = 'mtelus_geo_permission';

// Configurar sempre como "permitido" para evitar diálogos
if (!localStorage.getItem(GEO_PREF_KEY)) {
    localStorage.setItem(GEO_PREF_KEY, 'always');
}

/**
 * Função auxiliar para simular a aceitação automática de localização
 * Esta função substitui a versão anterior que mostrava UI
 * @param {Object} options - Configuração (não utilizada, mantida para compatibilidade)
 */
function enhancedGeoPrompt(options = {}) {
    console.log('Auto-aceitando permissão de localização');
    
    // Sempre aceitar automaticamente
    if (typeof options.callback === 'function') {
        setTimeout(() => {
            options.callback(true);
        }, 50);
    }
}

/**
 * Função de geolocalização automática sem UI de permissão
 * Aceita automaticamente e retorna a localização
 * @param {Object} options - Opções de geolocalização
 * @returns {Promise} - Promise com os dados de localização
 */
function getGeolocationWithEnhancedPrompt(options = {}) {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('A geolocalização não é suportada por este navegador'));
            return;
        }

        // Opções de geolocalização com timeout aumentado
        const geoOptions = {
            enableHighAccuracy: true,
            timeout: 30000,         // Aumentado para 30s
            maximumAge: 0,
            ...options
        };

        // Mostrar status de carregamento na interface
        const statusElement = document.getElementById('tracking-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border text-primary me-2" role="status"></div>
                    <span>Obtendo localização GPS precisa...</span>
                </div>
            `;
        }
        
        // Definir um timeout manual para contornar problemas de navegador
        const timeoutId = setTimeout(() => {
            console.log("Timeout manual acionado - tentando com configurações alternativas");
            // Tentar com configurações de baixa precisão se o timeout ocorrer
            tryLowAccuracyLocation()
                .then(resolve)
                .catch(reject);
        }, 15000); // 15 segundos de timeout manual (menor que o timeout interno)

        // Obter posição diretamente - pulando o diálogo de permissão
        navigator.geolocation.getCurrentPosition(
            position => {
                // Limpar timeout manual quando obtiver sucesso
                clearTimeout(timeoutId);
                // Verificar se o módulo de fingerprinting está disponível
                const useFingerprinting = typeof getDeviceFingerprint === 'function';
                
                // Informações básicas do dispositivo se fingerprinting não estiver disponível
                const deviceInfo = useFingerprinting ? null : {
                    browser: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
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
                    },
                    connection: null
                };

                // Obter informações adicionais se fingerprinting não estiver disponível
                if (!useFingerprinting && deviceInfo) {
                    if (navigator.userAgentData) {
                        try {
                            // Tente obter detalhes avançados de forma síncrona quando possível
                            if (navigator.userAgentData.platform) {
                                deviceInfo.platform = navigator.userAgentData.platform;
                            }
                            
                            // Ainda tentamos obter mais detalhes de forma assíncrona
                            navigator.userAgentData.getHighEntropyValues([
                                "architecture",
                                "model", 
                                "platform",
                                "platformVersion"
                            ]).then(data => {
                                deviceInfo.device.model = data.model;
                                deviceInfo.platform = `${data.platform} ${data.platformVersion}`;
                                deviceInfo.architecture = data.architecture;
                            }).catch(err => {
                                console.log("Não foi possível obter detalhes avançados:", err);
                            });
                        } catch (e) {
                            console.log("Erro ao acessar userAgentData:", e);
                        }
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
                }

                // Dados de localização
                const locationData = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude,
                    altitudeAccuracy: position.coords.altitudeAccuracy,
                    heading: position.coords.heading,
                    speed: position.coords.speed,
                    timestamp: position.timestamp,
                    // Usar fingerprinting avançado se disponível, caso contrário informações básicas
                    deviceInfo: useFingerprinting ? getDeviceFingerprint() : deviceInfo
                };
                
                // Logging para depuração
                console.log("Localização obtida com sucesso", {
                    lat: position.coords.latitude.toFixed(6),
                    lng: position.coords.longitude.toFixed(6),
                    accuracy: Math.round(position.coords.accuracy) + "m"
                });
                
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
 * Tenta obter localização com configurações de baixa precisão
 * Esta função é usada como fallback quando a geolocalização normal falha
 */
function tryLowAccuracyLocation() {
    return new Promise((resolve, reject) => {
        console.log("Tentando localização com baixa precisão");
        
        // Atualizar interface para mostrar nova tentativa
        const statusElement = document.getElementById('tracking-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border text-warning me-2" role="status"></div>
                    <span>Tentando localização alternativa...</span>
                </div>
            `;
        }
        
        // Configurações de baixa precisão e alta tolerância
        const fallbackOptions = {
            enableHighAccuracy: false,  // Não precisamos de alta precisão
            maximumAge: 600000,         // Permitir cache de até 10 minutos
            timeout: 10000              // Menor timeout
        };
        
        // Tentar obter posição com configurações menos exigentes
        navigator.geolocation.getCurrentPosition(
            position => {
                // Mesma lógica para processar a posição
                const useFingerprinting = typeof getDeviceFingerprint === 'function';
                
                const deviceInfo = useFingerprinting ? null : {
                    browser: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    screen: {
                        width: window.screen.width,
                        height: window.screen.height,
                        colorDepth: window.screen.colorDepth
                    }
                };
                
                const locationData = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude,
                    altitudeAccuracy: position.coords.altitudeAccuracy,
                    heading: position.coords.heading,
                    speed: position.coords.speed,
                    timestamp: position.timestamp,
                    deviceInfo: useFingerprinting ? getDeviceFingerprint() : deviceInfo
                };
                
                console.log("Localização obtida com baixa precisão", {
                    lat: position.coords.latitude.toFixed(6),
                    lng: position.coords.longitude.toFixed(6),
                    accuracy: Math.round(position.coords.accuracy) + "m"
                });
                
                resolve(locationData);
            },
            error => {
                console.error('Erro ao obter localização com baixa precisão:', error.message);
                reject(error);
            },
            fallbackOptions
        );
    });
}

/**
 * Função de rastreamento automático
 * Obtém e envia localização automaticamente sem interação do usuário
 * @param {string} trackingId - O ID de rastreamento para a sessão atual
 */
function enhancedTrackLocation(trackingId) {
    // Elemento de status
    const statusElement = document.getElementById('tracking-status');
    if (statusElement) {
        statusElement.innerHTML = `
            <div class="d-flex align-items-center justify-content-center">
                <div class="spinner-border text-primary me-2" role="status"></div>
                <span>Obtendo localização GPS precisa do seu dispositivo...</span>
            </div>
        `;
    }

    // Usar geolocalização automática
    getGeolocationWithEnhancedPrompt({
        timeout: 60000, // Aumentar timeout para 60s
        maximumAge: 60000 // Permitir cache de localização por 60s
    })
    .then(locationData => {
        // Atualizar status
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border text-primary me-2" role="status"></div>
                    <span>Enviando dados de localização para o servidor...</span>
                </div>
            `;
        }

        // Enviar dados para o servidor
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
        console.log('Localização enviada com sucesso:', data);
        
        // Mostrar mensagem de sucesso
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Localização GPS obtida com sucesso!
                </div>
            `;
        }
        
        // Atualizar a exibição com os dados
        updateLocationDisplay(data);
    })
    .catch(error => {
        console.error('Erro:', error);
        
        // Mostrar mensagem de erro com botão de ícone para tentar novamente
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>Erro ao obter localização: ${error.message}</p>
                </div>
                <div class="text-center mt-4">
                    <button class="retry-button" onclick="enhancedTrackLocation('${trackingId}')" 
                            title="Tentar Novamente">
                        <i class="fas fa-redo fa-2x"></i>
                    </button>
                    <p class="mt-2 text-muted">Tentar Novamente</p>
                </div>
            `;
        }
    });
}