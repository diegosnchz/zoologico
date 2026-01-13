#!/bin/bash
# Script para desplegar e iniciar la aplicación web del sistema de vigilancia

echo "======================================================================"
echo "🦁 DESPLIEGUE DEL SISTEMA DE VIGILANCIA DISTRIBUIDA"
echo "======================================================================"
echo ""

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python no está instalado"
    exit 1
fi

echo "✓ Python encontrado: $(python --version)"

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt --quiet

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
python web_app.py
