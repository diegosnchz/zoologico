#!/bin/bash
# Script para desplegar e iniciar la aplicación web del sistema de vigilancia

echo "======================================================================"
echo "🦁 DESPLIEGUE DEL SISTEMA DE VIGILANCIA DISTRIBUIDA"
echo "======================================================================"
echo ""

# Verificar Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python no está instalado"
    exit 1
fi

echo "✓ Python encontrado: $($PYTHON_CMD --version)"

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencias instaladas correctamente"
else
    echo "❌ Error al instalar dependencias"
    exit 1
fi

# Iniciar la aplicación web
echo ""
echo "======================================================================"
echo "🚀 INICIANDO APLICACIÓN WEB"
echo "======================================================================"
echo ""
echo "🌐 La aplicación estará disponible en:"
echo "   http://localhost:5000"
echo ""
echo "📊 Dashboard principal:"
echo "   http://localhost:5000"
echo ""
echo "🛑 Para detener la aplicación, presiona Ctrl+C"
echo ""
echo "======================================================================"
echo ""

# Iniciar servidor Flask
$PYTHON_CMD web_app.py
