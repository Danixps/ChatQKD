#!/bin/bash

# Detectar el sistema operativo
OS=$(uname)

if [[ "$OS" == "Linux" ]]; then
    echo "🔹 Detectado Linux: Instalando dependencias..."
    
    # Actualizar repositorios e instalar Python y pip si no están instalados
    sudo apt update
    sudo apt install -y python3 python3-pip python3-tk
    
    # Verificar que pip esté instalado
    if ! command -v pip3 &> /dev/null; then
        echo "⚠️ pip3 no se pudo instalar. Intenta instalarlo manualmente."
        exit 1
    fi
    
    # Instalar los paquetes de requirements.txt
    pip3 install -r requirements.txt
    
    echo "✅ Instalación completada en Linux."

elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    echo "🔹 Detectado Windows: Instalando dependencias..."
    
    # Instalar Python y pip en Windows
    powershell -Command "& {Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py; python get-pip.py}"
    
    # Instalar tkinter (ya viene con Python en Windows)
    echo "✅ Tkinter ya está instalado en Windows."
    
    # Instalar los paquetes de requirements.txt
    pip install -r requirements.txt
    
    echo "✅ Instalación completada en Windows."

else
    echo "⚠️ Sistema operativo no compatible. Instala las dependencias manualmente."
    exit 1
fi