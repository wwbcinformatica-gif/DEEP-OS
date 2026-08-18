@echo off
echo ===========================================
echo Instalador de Dependencias DEEP-AUREA
echo ===========================================

echo Verificando Python e Pip...
pip --version
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Python ou Pip nao instalados. Instale Python 3.10+ e tente novamente.
    goto end
)

echo Instalando dependencias do Backend (Python)...
cd backend
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Aviso: Nao foi possivel instalar dependencias do backend automaticamente. Verifique o requirements.txt.
)
cd ..

echo Verificando Node.js e NPM...
npm --version
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Node.js ou NPM nao instalados. Instale Node.js e tente novamente.
    goto end
)

echo Instalando dependencias do Frontend (Node/NPM)...
cd frontend
npm install
if %ERRORLEVEL% NEQ 0 (
    echo Aviso: Nao foi possivel instalar dependencias do frontend automaticamente.
)
cd ..

echo ===========================================
echo Instalacao de dependencias concluida.
echo Lembre-se de instalar o Ollama localmente, se necessario.
echo ===========================================
:end
pause