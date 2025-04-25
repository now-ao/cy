
# Importa a aplicação Flask do arquivo app.py
from aplicacao import app  # noqa: F401

# Verifica se este é o arquivo principal sendo executado
if __name__ == "__main__":
    # Inicia o servidor Flask na porta 5000 com modo debug ativo
    app.run(host="0.0.0.0", port=5000, debug=True)
