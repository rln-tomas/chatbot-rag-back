#!/bin/bash

# Script para configurar Ollama con el modelo deseado

echo "🦙 Configurando Ollama..."
echo ""

# Verificar si el contenedor de Ollama está corriendo
if ! docker ps | grep -q chatbot_ollama; then
    echo "❌ Error: El contenedor de Ollama no está corriendo"
    echo "Ejecuta: docker-compose up -d ollama"
    exit 1
fi

echo "✅ Contenedor de Ollama detectado"
echo ""

# Listar modelos disponibles
echo "📋 Modelos actualmente instalados:"
docker exec chatbot_ollama ollama list
echo ""

# Preguntar qué modelo instalar
echo "🤔 ¿Qué modelo deseas instalar?"
echo ""
echo "Modelos populares:"
echo "  1. gpt-oss:20b (el que estás usando)"
echo "  2. llama3.2:1b (muy liviano, ~1GB)"
echo "  3. llama3.2:3b (liviano, ~2GB)"
echo "  4. llama3.2 (estándar, ~8GB)"
echo "  5. mistral (7B, ~4GB)"
echo "  6. codellama (para código, ~4GB)"
echo "  7. Otro (especificar manualmente)"
echo ""

read -p "Selecciona una opción (1-7) o escribe 'skip' para saltar: " choice

case $choice in
    1)
        MODEL="gpt-oss:20b"
        ;;
    2)
        MODEL="llama3.2:1b"
        ;;
    3)
        MODEL="llama3.2:3b"
        ;;
    4)
        MODEL="llama3.2"
        ;;
    5)
        MODEL="mistral"
        ;;
    6)
        MODEL="codellama"
        ;;
    7)
        read -p "Escribe el nombre del modelo: " MODEL
        ;;
    skip)
        echo "⏭️  Saltando instalación de modelo"
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "⬇️  Descargando modelo: $MODEL"
echo "Esto puede tardar varios minutos dependiendo del tamaño..."
echo ""

# Descargar el modelo
docker exec chatbot_ollama ollama pull $MODEL

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Modelo $MODEL instalado correctamente"
    echo ""
    echo "📝 No olvides actualizar tu archivo .env:"
    echo "   OLLAMA_MODEL=$MODEL"
    echo ""
    echo "🔄 Reinicia el servicio API:"
    echo "   docker-compose restart api"
else
    echo ""
    echo "❌ Error al instalar el modelo"
    exit 1
fi
