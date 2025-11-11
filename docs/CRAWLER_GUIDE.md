# 🕷️ Guía del Web Crawler

## 📋 Descripción

El sistema de scraping ahora incluye un **crawler recursivo** que descubre y extrae contenido de todas las páginas dentro del mismo dominio.

## ✨ Características

### ✅ Lo que hace el crawler:

1. **Descubrimiento automático de páginas**: Comienza desde una URL y descubre todos los enlaces
2. **Respeta el dominio**: Solo visita páginas del mismo dominio (no sale del sitio)
3. **Navegación recursiva**: Sigue enlaces de forma inteligente
4. **Filtrado inteligente**: Ignora archivos descargables (PDFs, imágenes, videos, etc.)
5. **Límite de seguridad**: Por defecto, máximo 50 páginas (configurable)
6. **Normalización de URLs**: Evita duplicados por URLs similares
7. **Manejo de errores**: Continúa aunque falle alguna página

### ❌ Lo que NO hace:

- No sale del dominio especificado
- No descarga archivos binarios (PDFs, imágenes, etc.)
- No ejecuta JavaScript (solo extrae HTML estático)
- No sigue enlaces externos

## 🚀 Uso

### Opción 1: A través de la API (Recomendado)

```bash
# 1. Crear una configuración con la URL
curl -X POST "http://localhost:8000/api/v1/config/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-sitio-web.com",
    "name": "Mi Sitio Web"
  }'

# 2. Iniciar el scraping (automáticamente crawlea todo el sitio)
curl -X POST "http://localhost:8000/api/v1/scraping/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": 1
  }'
```

### Opción 2: Script de prueba

Para probar el crawler sin la API completa:

```bash
# Probar con una URL específica
python scripts/test_crawler.py https://tu-sitio-web.com
```

El script mostrará:

- URLs descubiertas
- Páginas scrapeadas
- Chunks generados
- Estadísticas de contenido

## ⚙️ Configuración

Puedes ajustar el comportamiento del crawler en `app/scraping/tasks.py`:

```python
scraper = WebScraper(
    chunk_size=2000,        # Tamaño de cada chunk de texto (aumentado)
    chunk_overlap=400,      # Solapamiento entre chunks (aumentado)
    max_pages=50,           # Máximo de páginas a crawlear
    timeout=10             # Timeout por request en segundos
)
```

## 📊 Ejemplo de Salida

Cuando ejecutas un scraping, verás algo como:

```
Starting crawl of example.com from https://example.com
Crawling [1/50]: https://example.com
Crawling [2/50]: https://example.com/about
Crawling [3/50]: https://example.com/products
...
Crawl completed. Discovered 15 pages.

Starting scraping of 15 discovered pages...
Scraping [1/15]: https://example.com
  ✓ Extracted 8 chunks
Scraping [2/15]: https://example.com/about
  ✓ Extracted 4 chunks
...
Scraping completed. Total chunks: 145

Embedding 145 chunks into Pinecone...
Embedded batch 1 of 2
Embedded batch 2 of 2
```

## 🔍 Cómo Funciona

### 1. **Fase de Descubrimiento**

```
URL inicial → Extrae todos los enlaces → Filtra por dominio → Cola de URLs
     ↓                                                              ↓
  Visita ←─────────────────────────────────────────────────────────┘
```

### 2. **Fase de Scraping**

```
Lista de URLs → Scrape cada página → Divide en chunks → Guarda en Pinecone
```

### 3. **Normalización de URLs**

El crawler normaliza URLs para evitar duplicados:

- `https://example.com/page`
- `https://example.com/page/` ← Se trata como la misma
- `https://example.com/page#section` ← Se ignora el fragmento

## 🛡️ Límites de Seguridad

### Límite de Páginas

Por defecto: **50 páginas máximo**

Esto previene:

- Crawling infinito en sitios muy grandes
- Uso excesivo de recursos
- Costos elevados en Pinecone

Para sitios más grandes, aumenta `max_pages`, pero considera:

- Tiempo de ejecución (más páginas = más tiempo)
- Límites de embeddings de Pinecone
- Costos de almacenamiento

### Timeout

Por defecto: **10 segundos por página**

Si una página tarda más, se salta y continúa con las demás.

## 🐛 Solución de Problemas

### "No content could be extracted"

- Verifica que el sitio sea accesible públicamente
- Algunos sitios bloquean scrapers (User-Agent)
- El sitio puede requerir JavaScript (no soportado)

### "Too many pages discovered"

- Aumenta `max_pages` en la configuración
- O divide el scraping en múltiples ejecuciones con URLs más específicas

### "Timeout errors"

- Aumenta el `timeout` si el sitio es lento
- Verifica tu conexión a internet

## 📝 Diferencias con el Sistema Anterior

| Característica       | Antes      | Ahora                     |
| -------------------- | ---------- | ------------------------- |
| Páginas scrapeadas   | Solo 1 URL | Todo el dominio           |
| Descubrimiento       | Manual     | Automático                |
| Enlaces internos     | Ignorados  | Seguidos recursivamente   |
| Límite               | N/A        | 50 páginas (configurable) |
| Tamaño de chunks     | 1000 chars | 2000 chars (duplicado)    |
| Filtrado de archivos | No         | Sí (PDFs, imágenes, etc.) |

## 🎯 Casos de Uso

### Blog o Documentación

```python
# Scraperá todos los artículos del blog
start_url = "https://mi-blog.com"
```

### Sitio de Productos

```python
# Scraperá todas las páginas de productos
start_url = "https://mi-tienda.com/productos"
```

### Documentación Técnica

```python
# Scraperá toda la documentación
start_url = "https://docs.mi-proyecto.com"
```

## ⚠️ Consideraciones Legales

- **Respeta el robots.txt** del sitio
- **Solo scrapea sitios que tienes permiso** para usar
- **Considera la carga** en el servidor objetivo
- **Verifica los términos de servicio** del sitio

## 🔧 Mejoras Futuras Posibles

- [ ] Soporte para robots.txt
- [ ] Rate limiting configurable
- [ ] Soporte para autenticación
- [ ] Renderizado de JavaScript (Playwright/Selenium)
- [ ] Sitemap.xml parsing
- [ ] Priorización de URLs
- [ ] Caché de páginas visitadas

---

**Última actualización**: 8 de noviembre de 2025
