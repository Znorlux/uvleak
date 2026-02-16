# Configuración de Cloudinary para Vercel

Para desplegar en Vercel (serverless), los archivos deben almacenarse en Cloudinary ya que Vercel no tiene sistema de archivos persistente.

## Variables de entorno necesarias

Añade estas variables en Vercel (Settings → Environment Variables) o en tu `.env` local:

```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

O usa la variable única:
```
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## Configuración en Cloudinary

1. Crea una cuenta en [cloudinary.com](https://cloudinary.com)
2. En el Dashboard, copia:
   - Cloud name
   - API Key
   - API Secret

## Importante para el XSS

El código usa `resource_type="raw"` al subir archivos. Esto es **crítico** porque:
- Preserva el contenido exacto del archivo sin transformaciones
- Permite que los archivos HTML maliciosos se ejecuten correctamente
- No sanitiza ni modifica el contenido

Si cambias a `resource_type="auto"` o `resource_type="image"`, Cloudinary podría transformar el HTML y romper el XSS del Acto 2.

## Fallback para desarrollo local

Si Cloudinary no está configurado, el código intentará guardar localmente en `static/uploads/` (solo funciona en desarrollo con sistema de archivos).
