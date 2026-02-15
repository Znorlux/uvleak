# InternLink — Sistema de Gestión de Pasantías

**InternLink** es un **laboratorio de seguridad web** que simula una plataforma para conectar estudiantes universitarios con empresas que ofrecen pasantías. El sistema está **intencionalmente vulnerable**: contiene múltiples fallos de seguridad encadenados que permiten escalar privilegios desde un usuario estudiante hasta administrador.

El objetivo del laboratorio es identificar y explotar esas vulnerabilidades en orden, usando solo la interfaz y el comportamiento del sistema como guía.

## Requisitos

- Python 3.10+
- Cuenta en Upstash Redis (o instancia de Redis compatible con REST API)

## Instalación

```bash
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Configuración

Cree un archivo `.env` en la raíz del proyecto:

```
UPSTASH_REDIS_REST_URL=https://su-instancia.upstash.io
UPSTASH_REDIS_REST_TOKEN=su_token_aqui
```

## Ejecución

```bash
python app.py
```

La aplicación se ejecuta en `http://localhost:5000`.

## Roles del sistema

| Rol          | Descripción                                |
|--------------|--------------------------------------------|
| Estudiante   | Sube CV, explora ofertas, edita su perfil  |
| Empresa      | Publica ofertas y revisa candidatos        |
| Coordinador  | Gestiona pasantías y exporta reportes     |
| Administrador| Control total del sistema                   |

## Documentación del laboratorio

- **[docs/SOLUCION.md](docs/SOLUCION.md)** — Guía paso a paso con el flujo completo de resolución del lab y ubicación de cada flag.

## Tecnologías

- **Backend:** Flask 3.0
- **Base de datos:** Redis (Upstash Cloud)
- **Autenticación:** Cookies de sesión + JWT
- **Frontend:** HTML5, CSS3, JavaScript vanilla

## Advertencia

Este proyecto es **intencionalmente vulnerable** y está pensado solo para entornos educativos y de práctica. No lo use en producción ni lo exponga a internet sin las debidas medidas de seguridad.
