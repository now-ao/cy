/**
 * Enhanced Device Fingerprinting Module
 * Collects detailed information about the user's device for tracking purposes
 */

// Store the fingerprint data
let deviceFingerprint = {
    // Basic browser information
    browser: {
        cookies_enabled: navigator.cookieEnabled,
        language: navigator.language,
        languages: navigator.languages ? JSON.stringify(navigator.languages) : null,
        user_agent: navigator.userAgent,
        do_not_track: navigator.doNotTrack,
        online: navigator.onLine,
        platform: navigator.platform,
        product: navigator.product,
        vendor: navigator.vendor
    },
    
    // Screen properties
    screen: {
        width: window.screen.width,
        height: window.screen.height,
        availWidth: window.screen.availWidth,
        availHeight: window.screen.availHeight,
        colorDepth: window.screen.colorDepth,
        pixelDepth: window.screen.pixelDepth,
        orientation: window.screen.orientation ? window.screen.orientation.type : null,
        devicePixelRatio: window.devicePixelRatio
    },
    
    // Time information
    time: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timezone_offset: new Date().getTimezoneOffset(),
        current_time: new Date().toISOString()
    },
    
    // System capabilities
    capabilities: {
        local_storage: !!window.localStorage,
        session_storage: !!window.sessionStorage,
        indexed_db: !!window.indexedDB,
        hardware_concurrency: navigator.hardwareConcurrency || null,
        device_memory: navigator.deviceMemory || null,
        max_touch_points: navigator.maxTouchPoints || 0,
        touch_support: 'ontouchstart' in window
    },
    
    // Connection information
    connection: null,
    
    // Battery information
    battery: null,
    
    // Device orientation support
    motion_support: {
        devicemotion: 'ondevicemotion' in window,
        deviceorientation: 'ondeviceorientation' in window
    },
    
    // Media capabilities
    media: {
        audio_inputs: null,
        video_inputs: null,
        audio_outputs: null
    },
    
    // Canvas fingerprint (a hash of rendered canvas data)
    canvas_fingerprint: null,
    
    // WebGL information
    webgl: {
        supported: false,
        vendor: null,
        renderer: null,
        unmasked_vendor: null,
        unmasked_renderer: null
    },
    
    // Font detection
    available_fonts: []
};

/**
 * Initialize device fingerprinting
 * Collects all available information about the device
 */
function initializeFingerprinting() {
    try {
        // Get network connection info if available
        if (navigator.connection) {
            deviceFingerprint.connection = {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt,
                saveData: navigator.connection.saveData
            };
        }
        
        // Get battery info if available
        if (navigator.getBattery) {
            navigator.getBattery().then(function(battery) {
                deviceFingerprint.battery = {
                    charging: battery.charging,
                    level: battery.level,
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime
                };
            }).catch(err => {
                console.log("Battery API error:", err);
            });
        }
        
        // Get media devices if available
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            navigator.mediaDevices.enumerateDevices()
                .then(function(devices) {
                    let audioInputs = 0;
                    let videoInputs = 0;
                    let audioOutputs = 0;
                    
                    devices.forEach(function(device) {
                        if (device.kind === 'audioinput') audioInputs++;
                        else if (device.kind === 'videoinput') videoInputs++;
                        else if (device.kind === 'audiooutput') audioOutputs++;
                    });
                    
                    deviceFingerprint.media.audio_inputs = audioInputs;
                    deviceFingerprint.media.video_inputs = videoInputs;
                    deviceFingerprint.media.audio_outputs = audioOutputs;
                })
                .catch(err => {
                    console.log("Media Devices API error:", err);
                });
        }
        
        // WebGL detection
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            
            if (gl) {
                deviceFingerprint.webgl.supported = true;
                deviceFingerprint.webgl.vendor = gl.getParameter(gl.VENDOR);
                deviceFingerprint.webgl.renderer = gl.getParameter(gl.RENDERER);
                
                // Try to get unmasked info (may not be available in all browsers)
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    deviceFingerprint.webgl.unmasked_vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    deviceFingerprint.webgl.unmasked_renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                }
            }
        } catch (e) {
            console.log("WebGL detection error:", e);
        }
        
        // Canvas fingerprinting
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 200;
            canvas.height = 100;
            const ctx = canvas.getContext('2d');
            
            // Draw a complex shape
            ctx.textBaseline = 'alphabetic';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.font = '11pt "Times New Roman"';
            ctx.fillText('MTelus Tracker', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.font = '18pt Arial';
            ctx.fillText('Fingerprint', 4, 45);
            
            // Generate a simple hash of the canvas data
            const dataURL = canvas.toDataURL();
            let hash = 0;
            for (let i = 0; i < dataURL.length; i++) {
                hash = ((hash << 5) - hash) + dataURL.charCodeAt(i);
                hash = hash & hash; // Convert to 32bit integer
            }
            deviceFingerprint.canvas_fingerprint = hash.toString(16);
        } catch (e) {
            console.log("Canvas fingerprinting error:", e);
        }
        
        // Font detection
        const fontList = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria', 
            'Candara', 'Comic Sans MS', 'Courier New', 'Georgia', 'Impact', 
            'Tahoma', 'Times New Roman', 'Trebuchet MS', 'Verdana',
            // Add common fonts in Angola/Africa
            'Ubuntu', 'Roboto', 'Open Sans', 'Lato', 'DejaVu Sans'
        ];
        
        // Basic font detection by measuring text width with different fonts
        const detectFont = (font) => {
            const baseFonts = ['monospace', 'sans-serif', 'serif'];
            const testString = "mmmmmmmmmmlli";
            
            const testSize = '80px';
            let detected = false;
            
            for (let baseFontIndex = 0; baseFontIndex < baseFonts.length; baseFontIndex++) {
                const span = document.createElement('span');
                span.style.fontFamily = baseFonts[baseFontIndex];
                span.style.fontSize = testSize;
                span.style.position = 'absolute';
                span.style.left = '-10000px';
                span.style.top = '-10000px';
                span.innerHTML = testString;
                document.body.appendChild(span);
                
                const baseWidth = span.offsetWidth;
                
                // Change to test font
                span.style.fontFamily = `'${font}', ${baseFonts[baseFontIndex]}`;
                
                // Check if width changed
                if (span.offsetWidth !== baseWidth) {
                    detected = true;
                }
                
                document.body.removeChild(span);
                
                if (detected) {
                    break;
                }
            }
            
            return detected;
        };
        
        // Only run font detection if document is fully loaded
        if (document.readyState === 'complete') {
            fontList.forEach(font => {
                if (detectFont(font)) {
                    deviceFingerprint.available_fonts.push(font);
                }
            });
        } else {
            window.addEventListener('load', () => {
                fontList.forEach(font => {
                    if (detectFont(font)) {
                        deviceFingerprint.available_fonts.push(font);
                    }
                });
            });
        }
        
    } catch (error) {
        console.error("Error in device fingerprinting:", error);
    }
    
    return deviceFingerprint;
}

/**
 * Get the complete device fingerprint
 * @returns {Object} Device fingerprint object
 */
function getDeviceFingerprint() {
    // Ensure initialization
    if (!deviceFingerprint.initialized) {
        initializeFingerprinting();
        deviceFingerprint.initialized = true;
    }
    
    return deviceFingerprint;
}

/**
 * Include device fingerprint data with the location when tracking
 * @param {Object} locationData - Location data object
 * @returns {Object} Enhanced location data with device fingerprint
 */
function enhanceLocationWithFingerprint(locationData) {
    if (!locationData) return null;
    
    const enhancedData = { ...locationData };
    enhancedData.fingerprint = getDeviceFingerprint();
    
    return enhancedData;
}

// Initialize fingerprinting on script load
initializeFingerprinting();