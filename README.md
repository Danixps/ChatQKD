# ChatQKD 🔒💬

**ChatQKD** es un simulador de protocolos de *Distribución Cuántica de Claves* (**QKD**) que modela los roles de **Alice**, **Bob** y un posible atacante **Eve**, utilizando protocolos cuánticos clásicos:

- **BB84**
- **BBM92**
- **E91**
- **SARG04**

Con **ChatQKD** puedes experimentar cómo se genera una clave secreta segura incluso en presencia de un atacante.

---

## 📂 Estructura del proyecto

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| `Alice.py` | Implementación de Alice (emisor) |
| `Bob.py` | Implementación de Bob (receptor) |
| `Eve.py` | Implementación de Eve (atacante/interceptor) |
| `BB84/`, `BBM92/`, `E91/`, `SARG04/` | Implementaciones específicas de cada protocolo |
| `Recursos/src_final/` | Recursos y utilidades adicionales |
| `install.sh` | Script de instalación automática de dependencias |
| `requirements.txt` | Lista de librerías necesarias |
| `README.md` | Documentación del proyecto |

---

## ⚙️ Instalación

### Clonar el repositorio

```bash
git clone https://github.com/Danixps/KDChat.git
cd KDChat
```

```bash
chmod +x install.sh
./install.sh

```
Instalar dependencias automáticamente
```bash
chmod +x install.sh
./install.sh
```
O instalar manualmente
```bash
pip install -r requirements.txt
```
🚀 Ejecución

Cada agente tiene su propio script.

Ejemplo:

```bash
# Ejecutar Alice
python3 Alice.py

# Para simular un ataque con Eve:
python3 BBM92/Eve.py

# Ejecutar Bob
python3 BBM92/Bob.py

```
## Documentación

[Ver Documentación](https://danixps.github.io/ChatQKD/)