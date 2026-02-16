# Recursos de Diseño - Estilo UDEM

Este proyecto utiliza un diseño inspirado en la Universidad de Medellín. Para que el diseño funcione completamente, necesitas agregar los siguientes archivos:

## Archivos Necesarios

### 1. Background Image (`static/uploads/bg.jpg`)
- **Ubicación**: `static/uploads/bg.jpg`
- **Descripción**: Imagen de fondo que se mostrará con efecto blur y overlay morado/azul
- **Recomendaciones**:
  - Resolución: 1920x1080 o superior
  - Formato: JPG o PNG
  - Contenido: Imagen de oficina, aula, o ambiente profesional/educativo
  - Si no se proporciona, se usará un gradiente morado/azul como fallback

### 2. Logo UDEM (`static/udemlogo.png`)
- **Ubicación**: `static/udemlogo.png`
- **Descripción**: Logo de la Universidad de Medellín
- **Recomendaciones**:
  - Formato: PNG con transparencia
  - Tamaño: 200x200px o similar (se escalará automáticamente)
  - Si no se proporciona, el logo no se mostrará (hay un fallback con `onerror`)

## Estructura de Archivos

```
uvleak/
├── static/
│   ├── uploads/
│   │   └── bg.jpg          ← Imagen de fondo aquí
│   └── udemlogo.png        ← Logo UDEM aquí
├── templates/
│   ├── gate.html           ← Página de verificación
│   └── login.html          ← Página de login
└── static/css/
    └── style.css           ← Estilos del diseño
```

## Características del Diseño

- **Fondo con blur**: La imagen de fondo se muestra con efecto blur y overlay morado/azul
- **Glassmorphism**: Card central semi-transparente con efecto de vidrio esmerilado
- **Header flotante**: Logo y nombre de la Universidad en la parte superior
- **Footer flotante**: Información de contacto en la parte inferior
- **Iconos de ayuda**: Botones flotantes para accesibilidad y soporte
- **Responsive**: Diseño adaptativo para móviles y tablets

## Notas

- Si los archivos no existen, el diseño seguirá funcionando con fallbacks
- El background usa un gradiente como fallback si no hay imagen
- El logo tiene un `onerror` que lo oculta si no existe
- Todos los estilos están en `static/css/style.css`
