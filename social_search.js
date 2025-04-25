
/**
 * Função que realiza a busca de perfis sociais para um dado nome
 * @param {string} nome - O nome da pessoa a ser buscada
 * @returns {Promise<Object>} - Promessa que retorna os resultados agrupados por rede social
 */
async function buscarPerfilSocial(nome) {
  try {
    // Enviar solicitação para o backend que fará a verificação real dos perfis
    const response = await fetch('/buscar_perfil', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `nome=${encodeURIComponent(nome)}`
    });
    
    if (!response.ok) {
      throw new Error(`Erro na requisição: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Erro ao buscar perfis sociais:', error);
    return {
      facebook: [],
      instagram: [],
      linkedin: [],
      twitter: [],
      erro: error.message
    };
  }
}

/**
 * Renderiza os resultados na interface do usuário
 * @param {Object} resultados - Os resultados da busca agrupados por rede social
 * @param {HTMLElement} container - O container onde serão exibidos os resultados
 */
function renderizarResultados(resultados, container) {
  container.innerHTML = '';
  
  // Ícones para cada rede social
  const icones = {
    facebook: 'fa-facebook',
    instagram: 'fa-instagram',
    linkedin: 'fa-linkedin',
    twitter: 'fa-twitter'
  };
  
  // Cores para cada rede social
  const cores = {
    facebook: 'primary',
    instagram: 'danger',
    linkedin: 'info',
    twitter: 'info'
  };
  
  // Processar cada rede social
  for (const [rede, perfis] of Object.entries(resultados)) {
    if (perfis.length > 0) {
      const redeDiv = document.createElement('div');
      redeDiv.className = 'mb-4';
      
      // Cabeçalho da rede social
      const header = document.createElement('h5');
      header.innerHTML = `<i class="fab ${icones[rede]} me-2"></i>${rede.charAt(0).toUpperCase() + rede.slice(1)}`;
      redeDiv.appendChild(header);
      
      // Lista de perfis encontrados
      const lista = document.createElement('div');
      lista.className = 'list-group';
      
      perfis.forEach(perfil => {
        const perfilItem = document.createElement('div');
        perfilItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Status de verificação
        const verificadoIcon = perfil.verificado 
          ? '<span class="badge bg-success"><i class="fas fa-check"></i> Verificado</span>'
          : '<span class="badge bg-warning text-dark"><i class="fas fa-question"></i> Não verificado</span>';
        
        perfilItem.innerHTML = `
          <div>
            <strong>${perfil.nome}</strong>
            ${verificadoIcon}
          </div>
          <a href="${perfil.url}" target="_blank" class="btn btn-${cores[rede]} btn-sm">
            <i class="fas fa-external-link-alt me-1"></i> Ver
          </a>
        `;
        
        lista.appendChild(perfilItem);
      });
      
      redeDiv.appendChild(lista);
      container.appendChild(redeDiv);
    }
  }
  
  // Se não houver resultados
  if (container.children.length === 0) {
    container.innerHTML = '<div class="alert alert-info">Nenhum perfil social encontrado para este nome.</div>';
  }
}
