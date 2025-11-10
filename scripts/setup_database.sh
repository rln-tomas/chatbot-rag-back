#!/bin/bash

# Script para configurar la base de datos con migraciones y seeders
# Diseñado para trabajar con Docker Compose

set -e  # Exit on error

echo "🗄️  Configurando Base de Datos..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para ejecutar comandos en el contenedor Docker
run_command() {
    local cmd=$1
    local description=$2
    
    echo -e "${YELLOW}▶${NC} $description"
    
    docker compose exec api $cmd
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Completado"
    else
        echo -e "${RED}✗${NC} Error"
        return 1
    fi
    echo ""
}

# Función para verificar si Docker Compose está corriendo
check_docker() {
    echo -e "${YELLOW}▶${NC} Verificando que Docker Compose está corriendo..."
    
    if ! docker compose ps | grep -q "chatbot_api"; then
        echo -e "${RED}✗${NC} El contenedor de API no está corriendo"
        echo ""
        echo "Por favor inicia los servicios con:"
        echo "  docker compose up -d"
        echo ""
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Docker Compose está corriendo"
    echo ""
}

# Función para verificar si la base de datos está lista
check_database() {
    echo -e "${YELLOW}▶${NC} Verificando conexión a la base de datos..."
    
    docker compose exec api python -c "from app.core.database import get_engine; get_engine().connect()" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Base de datos conectada"
        echo ""
        return 0
    else
        echo -e "${RED}✗${NC} No se pudo conectar a la base de datos"
        echo ""
        echo "Verifica que el contenedor de MySQL esté corriendo:"
        echo "  docker compose ps mysql"
        echo ""
        return 1
    fi
}

# Verificar Docker Compose al inicio
check_docker

# Menú principal
echo "¿Qué deseas hacer?"
echo ""
echo "  1. Ejecutar migraciones solamente"
echo "  2. Ejecutar seeders solamente"
echo "  3. Ejecutar migraciones + seeders (Setup completo)"
echo "  4. Crear nueva migración"
echo "  5. Revertir última migración"
echo "  6. Limpiar base de datos y reiniciar"
echo ""
read -p "Selecciona una opción (1-6): " choice
echo ""

case $choice in
    1)
        echo "============================================"
        echo "  Ejecutando Migraciones"
        echo "============================================"
        echo ""
        
        check_database || exit 1
        
        run_command "alembic upgrade head" "Aplicando migraciones..."
        
        echo -e "${GREEN}✓${NC} Migraciones completadas exitosamente!"
        ;;
        
    2)
        echo "============================================"
        echo "  Ejecutando Seeders"
        echo "============================================"
        echo ""
        
        check_database || exit 1
        
        run_command "python scripts/seed.py" "Poblando base de datos con datos de prueba..."
        
        echo -e "${GREEN}✓${NC} Seeders completados exitosamente!"
        ;;
        
    3)
        echo "============================================"
        echo "  Setup Completo: Migraciones + Seeders"
        echo "============================================"
        echo ""
        
        check_database || exit 1
        
        run_command "alembic upgrade head" "1. Aplicando migraciones..."
        run_command "python scripts/seed.py" "2. Poblando base de datos..."
        
        echo "============================================"
        echo -e "${GREEN}✓${NC} Setup completado exitosamente!"
        echo "============================================"
        echo ""
        echo "📝 Usuarios de prueba creados:"
        echo "   admin@example.com -> admin123"
        echo "   test@example.com  -> test123"
        echo "   john@example.com  -> john123"
        echo "   jane@example.com  -> jane123"
        ;;
        
    4)
        echo "============================================"
        echo "  Crear Nueva Migración"
        echo "============================================"
        echo ""
        
        read -p "Describe el cambio (ej: add_user_avatar_field): " migration_name
        echo ""
        
        if [ -z "$migration_name" ]; then
            echo -e "${RED}✗${NC} Debes proporcionar un nombre para la migración"
            exit 1
        fi
        
        run_command "alembic revision --autogenerate -m \"$migration_name\"" "Generando migración..."
        
        echo -e "${GREEN}✓${NC} Migración creada exitosamente!"
        echo ""
        echo "📁 Revisa el archivo generado en: alembic/versions/"
        echo "⚠️  Recuerda aplicar la migración con: $0 (opción 1)"
        ;;
        
    5)
        echo "============================================"
        echo "  Revertir Última Migración"
        echo "============================================"
        echo ""
        
        check_database || exit 1
        
        echo -e "${YELLOW}⚠️  ADVERTENCIA:${NC} Esto revertirá la última migración aplicada"
        read -p "¿Estás seguro? (y/N): " confirm
        
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Operación cancelada"
            exit 0
        fi
        echo ""
        
        run_command "alembic downgrade -1" "Revirtiendo última migración..."
        
        echo -e "${GREEN}✓${NC} Migración revertida exitosamente!"
        ;;
        
    6)
        echo "============================================"
        echo "  Limpiar y Reiniciar Base de Datos"
        echo "============================================"
        echo ""
        
        echo -e "${RED}⚠️  ADVERTENCIA:${NC} Esto eliminará TODOS los datos de la base de datos"
        echo "Esta acción NO se puede deshacer"
        echo ""
        read -p "¿Estás ABSOLUTAMENTE seguro? Escribe 'SI ELIMINAR': " confirm
        
        if [ "$confirm" != "SI ELIMINAR" ]; then
            echo "Operación cancelada"
            exit 0
        fi
        echo ""
        
        check_database || exit 1
        
        run_command "alembic downgrade base" "1. Revirtiendo todas las migraciones..."
        run_command "alembic upgrade head" "2. Aplicando migraciones desde cero..."
        run_command "python scripts/seed.py" "3. Poblando base de datos..."
        
        echo "============================================"
        echo -e "${GREEN}✓${NC} Base de datos reiniciada exitosamente!"
        echo "============================================"
        ;;
        
    *)
        echo -e "${RED}✗${NC} Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo -e "${GREEN}¡Listo!${NC} 🎉"
echo "============================================"
