# Configuración de Cloudinary para Vercel

Para desplegar en Vercel (serverless), los archivos deben almacenarse en Cloudinary ya que Vercel no tiene sistema de archivos persistente.

## Variables de entorno necesarias

Añade estas variables en Vercel (Settings → Environment Variables) o en tu `.env` local:

```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

O usa la variable única (recomendado):
```
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## Configuración en Cloudinary

1. Crea una cuenta en [cloudinary.com](https://cloudinary.com)
2. En el Dashboard, copia:
   - Cloud name
   - API Key
   - API Secret
3. **IMPORTANTE**: Ve a Settings → Security y habilita **"Allow delivery of PDF and ZIP files"** para que los PDFs sean accesibles públicamente. Si no lo haces, el código usará URLs firmadas automáticamente para bypassear esta restricción.

## URLs Firmadas (Signed URLs)

El código genera automáticamente URLs firmadas para bypassear las restricciones de cuentas gratuitas de Cloudinary (PDFs bloqueados por defecto). Las URLs firmadas:
- Funcionan perfectamente en entornos serverless (Vercel)
- Solo requieren que las variables de entorno estén configuradas correctamente
- Permiten acceso a archivos incluso si la cuenta tiene restricciones activadas
- Son generadas server-side usando el API secret (nunca se expone al cliente)

## Importante para el XSS

El código usa `resource_type="raw"` al subir archivos. Esto es **crítico** porque:
- Preserva el contenido exacto del archivo sin transformaciones
- Permite que los archivos HTML maliciosos se ejecuten correctamente
- No sanitiza ni modifica el contenido

Si cambias a `resource_type="auto"` o `resource_type="image"`, Cloudinary podría transformar el HTML y romper el XSS del Acto 2.

## Compatibilidad con Vercel Serverless

✅ **Funciona correctamente en Vercel:**
- Subida de archivos a Cloudinary
- Generación de URLs firmadas
- Descarga de archivos desde Cloudinary usando `urlopen()` (timeouts de 10s están dentro de los límites de Vercel)
- Variables de entorno se leen correctamente al inicio del módulo

⚠️ **Limitaciones conocidas:**
- Los logs (`logs/debug.log`) se escriben a archivo local, lo cual no persiste en Vercel entre invocaciones. Para producción, considera guardar logs en Redis o usar un servicio de logging externo.
- El archivo `/logs/debug.log` del Acto 8 puede no estar disponible en Vercel a menos que se implemente una solución alternativa (guardar en Redis y servir desde ahí).

## Fallback para desarrollo local

Si Cloudinary no está configurado, el código intentará guardar localmente en `static/uploads/` (solo funciona en desarrollo con sistema de archivos).
