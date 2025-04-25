/**
 * Módulo avançado de obtenção de dados geográficos e do dispositivo
 * Baseado na solução fornecida pelo usuário que demonstrou funcionar corretamente
 */

/**
 * Função principal para obter todos os dados do dispositivo e localização 
 * @returns {Promise} Promise contendo os dados completos
 */
async function obterDadosAvancados() {
    console.log("Iniciando coleta de dados avançada...");
    
    // Preparar objeto de resultado
    let dadosColetados = {
        geolocalizacao: {
            latitude: null,
            longitude: null,
            precisao: null,
            altitude: null,
            altitudePrecisao: null,
            direcao: null,
            velocidade: null
        },
        rede: {
            ip: "Desconhecido",
            isp: "Desconhecido"
        },
        localizacao: {
            pais: "Desconhecido",
            codigoPais: "",
            moeda: "Desconhecida",
            cidade: "Desconhecida",
            regiao: "Desconhecida",
            endereco: "Desconhecido"
        },
        dispositivo: {
            nome: "Desconhecido",
            modelo: "Desconhecido",
            fabricante: "Desconhecido",
            userAgent: navigator.userAgent,
            plataforma: navigator.platform,
            linguagem: navigator.language,
            sistema: "Desconhecido",
            versaoSistema: "Desconhecida",
            navegador: "Desconhecido",
            versaoNavegador: "Desconhecida",
            tela: {
                largura: window.screen.width,
                altura: window.screen.height,
                profundidadeCor: window.screen.colorDepth,
                orientacao: window.screen.orientation ? window.screen.orientation.type : 'desconhecida'
            }
        },
        tempoLocal: new Date().toISOString(),
        fingerprint: {}
    };

    // 1. Obter IP público
    try {
        const ipRes = await fetch('https://api.ipify.org?format=json');
        const ipData = await ipRes.json();
        dadosColetados.rede.ip = ipData.ip;
        console.log("IP público obtido:", dadosColetados.rede.ip);
    } catch (e) {
        console.error("Erro ao obter IP:", e);
    }

    // 2. Obter dados avançados do dispositivo (UserAgentData API)
    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
        try {
            const data = await navigator.userAgentData.getHighEntropyValues([
                'model', 
                'platform', 
                'platformVersion', 
                'architecture', 
                'bitness', 
                'fullVersionList',
                'mobile'
            ]);
            
            dadosColetados.dispositivo.modelo = data.model || "Desconhecido";
            dadosColetados.dispositivo.fabricante = data.platform || "Desconhecido";
            dadosColetados.dispositivo.sistema = data.platform || "Desconhecido";
            dadosColetados.dispositivo.versaoSistema = data.platformVersion || "Desconhecida";
            dadosColetados.dispositivo.nome = data.model || navigator.userAgent;
            
            // Tentar identificar navegador a partir de fullVersionList
            if (data.fullVersionList && data.fullVersionList.length > 0) {
                for (const browser of data.fullVersionList) {
                    if (['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'].includes(browser.brand)) {
                        dadosColetados.dispositivo.navegador = browser.brand;
                        dadosColetados.dispositivo.versaoNavegador = browser.version;
                        break;
                    }
                }
            }
            
            console.log("UserAgentData obtido com sucesso");
        } catch (e) {
            console.error("Erro ao obter dados UserAgentData:", e);
        }
    } else {
        console.log("UserAgentData API não disponível, usando fallbacks");
        // Extract data from user agent as fallback
        dadosColetados.dispositivo.nome = navigator.userAgent;
        
        // Detect browser
        if (navigator.userAgent.indexOf("Chrome") != -1) {
            dadosColetados.dispositivo.navegador = "Chrome";
        } else if (navigator.userAgent.indexOf("Firefox") != -1) {
            dadosColetados.dispositivo.navegador = "Firefox";
        } else if (navigator.userAgent.indexOf("Safari") != -1) {
            dadosColetados.dispositivo.navegador = "Safari";
        } else if (navigator.userAgent.indexOf("Edge") != -1) {
            dadosColetados.dispositivo.navegador = "Edge";
        } else if (navigator.userAgent.indexOf("Opera") != -1) {
            dadosColetados.dispositivo.navegador = "Opera";
        }
        
        // Detect OS
        if (navigator.userAgent.indexOf("Win") != -1) {
            dadosColetados.dispositivo.sistema = "Windows";
        } else if (navigator.userAgent.indexOf("Mac") != -1) {
            dadosColetados.dispositivo.sistema = "MacOS";
        } else if (navigator.userAgent.indexOf("Android") != -1) {
            dadosColetados.dispositivo.sistema = "Android";
        } else if (navigator.userAgent.indexOf("iOS") != -1 || navigator.userAgent.indexOf("iPhone") != -1) {
            dadosColetados.dispositivo.sistema = "iOS";
        } else if (navigator.userAgent.indexOf("Linux") != -1) {
            dadosColetados.dispositivo.sistema = "Linux";
        }
    }

    // 3. Obter informações de conexão se disponível
    if (navigator.connection) {
        dadosColetados.rede.tipoConexao = navigator.connection.effectiveType;
        dadosColetados.rede.velocidade = navigator.connection.downlink;
        dadosColetados.rede.rtt = navigator.connection.rtt;
        dadosColetados.rede.economizaDados = navigator.connection.saveData;
    }

    // 4. Obter geolocalização
    try {
        const posicao = await new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error("Geolocalização não suportada pelo navegador"));
                return;
            }
            
            // Definir um timeout manual
            const timeoutId = setTimeout(() => {
                reject(new Error("Timeout de geolocalização"));
            }, 12000);
            
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    clearTimeout(timeoutId);
                    resolve(pos);
                },
                (error) => {
                    clearTimeout(timeoutId);
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );
        });
        
        // Preencher dados de geolocalização
        dadosColetados.geolocalizacao.latitude = posicao.coords.latitude;
        dadosColetados.geolocalizacao.longitude = posicao.coords.longitude;
        dadosColetados.geolocalizacao.precisao = posicao.coords.accuracy;
        dadosColetados.geolocalizacao.altitude = posicao.coords.altitude;
        dadosColetados.geolocalizacao.altitudePrecisao = posicao.coords.altitudeAccuracy;
        dadosColetados.geolocalizacao.direcao = posicao.coords.heading;
        dadosColetados.geolocalizacao.velocidade = posicao.coords.speed;
        
        console.log("Geolocalização obtida:", 
            dadosColetados.geolocalizacao.latitude.toFixed(6), 
            dadosColetados.geolocalizacao.longitude.toFixed(6));
        
        // 5. Com a localização, obter dados geográficos
        try {
            const geoRes = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${dadosColetados.geolocalizacao.latitude}&longitude=${dadosColetados.geolocalizacao.longitude}&localityLanguage=pt`);
            const geoData = await geoRes.json();
            
            dadosColetados.localizacao.pais = geoData.countryName || "Desconhecido";
            dadosColetados.localizacao.codigoPais = geoData.countryCode || "";
            dadosColetados.localizacao.cidade = geoData.city || geoData.locality || "Desconhecida";
            dadosColetados.localizacao.regiao = geoData.principalSubdivision || "Desconhecida";
            dadosColetados.localizacao.endereco = `${dadosColetados.localizacao.cidade}, ${dadosColetados.localizacao.regiao}, ${dadosColetados.localizacao.pais}`;
            
            // Tentar obter moeda
            if (dadosColetados.localizacao.codigoPais) {
                try {
                    const countryRes = await fetch(`https://restcountries.com/v3.1/alpha/${dadosColetados.localizacao.codigoPais}`);
                    const countryData = await countryRes.json();
                    
                    if (countryData && countryData[0] && countryData[0].currencies) {
                        const currencies = countryData[0].currencies;
                        const keys = Object.keys(currencies);
                        
                        if (keys.length > 0) {
                            dadosColetados.localizacao.moeda = `${currencies[keys[0]].name} (${keys[0]})`;
                        }
                    }
                } catch (err) {
                    console.error("Erro ao obter dados de moeda:", err);
                }
            }
            
            console.log("Dados geográficos obtidos");
        } catch (err) {
            console.error("Erro ao obter dados geográficos:", err);
        }
    } catch (error) {
        console.error("Erro de geolocalização:", error.message);
    }
    
    // Fingerprinting avançado se disponível
    if (typeof getDeviceFingerprint === 'function') {
        try {
            dadosColetados.fingerprint = getDeviceFingerprint();
            console.log("Fingerprint obtido");
        } catch (e) {
            console.error("Erro ao obter fingerprint:", e);
        }
    }
    
    console.log("Coleta de dados completa");
    return dadosColetados;
}

/**
 * Função auxiliar para obter endereço formatado a partir de coordenadas
 * @param {Number} lat - Latitude  
 * @param {Number} lon - Longitude
 * @returns {Promise<String>} - Promise com o endereço formatado
 */
async function obterEndereco(lat, lon) {
    try {
        const resposta = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=pt`);
        const dados = await resposta.json();
        
        // Construir endereço formatado
        const partes = [
            dados.locality,
            dados.city,
            dados.principalSubdivision,
            dados.countryName
        ].filter(Boolean); // Remove valores vazios
        
        return partes.join(", ");
    } catch (err) {
        console.error("Erro ao obter endereço:", err);
        return "Endereço desconhecido";
    }
}