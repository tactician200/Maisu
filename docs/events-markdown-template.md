# Markdown Ingestion Template Standard (Drive → DB)

Este estándar define el **frontmatter YAML obligatorio** para contenido curado manualmente en Google Drive y su ingestión a SQL.

---

## 1) Formato de archivo

Cada documento debe tener:

1. `frontmatter` YAML al inicio (entre `---`)
2. Cuerpo markdown con contenido narrativo

```markdown
---
# frontmatter aquí
---

# Título visible
Contenido...
```

---

## 2) Esquema estricto de frontmatter

### 2.1 Campos comunes (todos los tipos)

| Campo | Tipo | Req. | Reglas |
|---|---|---:|---|
| `type` | enum | ✅ | `event` \| `place` \| `history` |
| `slug` | string | ✅ | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, único global |
| `title` | string | ✅ | 5–120 caracteres |
| `language` | enum | ✅ | `es` \| `eu` \| `en` |
| `summary` | string | ✅ | 40–400 caracteres |
| `tags` | string[] | ✅ | 1–12 tags, cada tag 2–40 caracteres |
| `source_url` | string(url) | ❌ | URL válida (https recomendado) |
| `source_name` | string | ❌ | 2–120 caracteres |
| `status` | enum | ✅ | `draft` \| `reviewed` \| `published` |
| `updated_at` | datetime ISO8601 | ✅ | UTC recomendado, ej. `2026-02-23T19:30:00Z` |

### 2.2 Campos por tipo

#### A) `type: place`

| Campo | Tipo | Req. | Reglas |
|---|---|---:|---|
| `place.nombre` | string | ✅ | 2–255 |
| `place.tipo` | string | ✅ | 2–100 |
| `place.descripcion_corta` | string | ✅ | 20–500 |
| `place.descripcion` | string | ❌ | 40–4000 |
| `place.direccion` | string | ❌ | 5–255 |
| `place.barrio` | string | ❌ | 2–100 |
| `place.precio_medio` | number | ❌ | `>=0` y `<=9999.99` |
| `place.rango_precio` | enum | ❌ | `€` \| `€€` \| `€€€` \| `€€€€` |
| `place.valoracion_local` | number | ❌ | `0.0–5.0` |
| `place.por_que_es_especial` | string | ❌ | 20–2000 |
| `place.recomendado_por_locales` | boolean | ❌ | `true/false` |
| `place.website` | string(url) | ❌ | URL válida |

#### B) `type: history`

| Campo | Tipo | Req. | Reglas |
|---|---|---:|---|
| `history.tema` | string | ✅ | 3–255 |
| `history.titulo` | string | ✅ | 5–500 |
| `history.contenido` | string | ✅ | 120–20000 |
| `history.contenido_corto` | string | ❌ | 40–1000 |
| `history.epoca` | string | ❌ | 2–100 |
| `history.fecha_inicio` | date | ❌ | `YYYY-MM-DD` |
| `history.fecha_fin` | date | ❌ | `YYYY-MM-DD`, >= `fecha_inicio` |
| `history.personajes_clave` | string[] | ❌ | 0–20 elementos |
| `history.categoria` | string | ❌ | 2–100 |
| `history.nivel_detalle` | enum | ❌ | `resumen` \| `detallado` \| `academico` |
| `history.fuentes` | string[] | ❌ | URLs o citas cortas |

#### C) `type: event`

> Para ingesta en tabla `events` (si aún no existe, crearla antes de publicar lote).

| Campo | Tipo | Req. | Reglas |
|---|---|---:|---|
| `event.name` | string | ✅ | 5–255 |
| `event.description` | string | ✅ | 40–5000 |
| `event.start_at` | datetime ISO8601 | ✅ | Debe incluir zona horaria |
| `event.end_at` | datetime ISO8601 | ❌ | `>= start_at` |
| `event.timezone` | string | ✅ | IANA TZ, ej. `Europe/Madrid` |
| `event.venue_name` | string | ✅ | 2–255 |
| `event.address` | string | ❌ | 5–255 |
| `event.neighborhood` | string | ❌ | 2–100 |
| `event.price_eur` | number | ❌ | `>=0` |
| `event.currency` | enum | ❌ | por defecto `EUR` |
| `event.category` | string | ❌ | 2–100 |
| `event.organizer` | string | ❌ | 2–255 |
| `event.ticket_url` | string(url) | ❌ | URL válida |
| `event.image_url` | string(url) | ❌ | URL válida |

---

## 3) Reglas de validación (ingesta)

1. Frontmatter inválido ⇒ **rechazar archivo**.
2. `type`, `slug`, `title`, `summary`, `language`, `status`, `updated_at` siempre obligatorios.
3. Debe existir el bloque específico según `type` (`place`, `history` o `event`).
4. `tags` no puede ir vacío.
5. `status=published` requiere:
   - Sin errores de formato
   - Campos obligatorios completos
   - `summary` no genérico (mín. 40 chars)
6. `slug` duplicado en lote o en DB ⇒ **rechazar/merge manual**.
7. Fechas inválidas o `end_at < start_at` / `fecha_fin < fecha_inicio` ⇒ **rechazar**.
8. URLs con esquema distinto de `http/https` ⇒ **rechazar**.

---

## 4) Ejemplos concretos

### 4.1 Ejemplo `event`

```markdown
---
type: event
slug: aste-nagusia-fuegos-2026
title: Aste Nagusia 2026 - Fuegos Artificiales
language: es
summary: Exhibición nocturna de fuegos artificiales durante Aste Nagusia, con alta afluencia local y ambiente festivo en la ría.
tags: [fiestas, fuegos, verano, bilbao]
source_url: https://www.bilbao.eus/agenda
source_name: Ayuntamiento de Bilbao
status: reviewed
updated_at: 2026-02-23T19:30:00Z
event:
  name: Aste Nagusia 2026 - Fuegos Artificiales
  description: Sesión principal de fuegos artificiales junto a la ría con música y zonas de observación recomendadas.
  start_at: 2026-08-22T22:30:00+02:00
  end_at: 2026-08-22T23:15:00+02:00
  timezone: Europe/Madrid
  venue_name: Paseo de Uribitarte
  address: P.º Uribitarte, Bilbao
  neighborhood: Abando
  price_eur: 0
  currency: EUR
  category: fiesta_popular
  organizer: Comisión de Fiestas de Bilbao
  ticket_url: https://www.bilbao.eus/agenda
---

# Aste Nagusia 2026 - Fuegos Artificiales
Detalles logísticos y recomendaciones locales...
```

### 4.2 Ejemplo `place`

```markdown
---
type: place
slug: mercado-ribera-bilbao
title: Mercado de la Ribera
language: es
summary: Mercado histórico junto a la ría, ideal para gastronomía local, pintxos y producto fresco.
tags: [gastronomia, mercado, casco-viejo]
source_url: https://www.bilbaoturismo.net/
source_name: Bilbao Turismo
status: published
updated_at: 2026-02-23T19:30:00Z
place:
  nombre: Mercado de la Ribera
  tipo: mercado
  descripcion_corta: Mercado emblemático de Bilbao con puestos de producto local y zona gastronómica.
  descripcion: Espacio de referencia para conocer la despensa vasca y comer pintxos en ambiente local.
  direccion: Erribera Kalea, s/n, 48005 Bilbao
  barrio: Casco Viejo
  precio_medio: 18
  rango_precio: €€
  valoracion_local: 4.6
  por_que_es_especial: Combina tradición, arquitectura histórica y oferta gastronómica diaria.
  recomendado_por_locales: true
  website: https://www.mercadodelaribera.biz/
---

# Mercado de la Ribera
Notas curatoriales...
```

### 4.3 Ejemplo `history`

```markdown
---
type: history
slug: industrializacion-ria-bilbao
title: La industrialización de la ría de Bilbao
language: es
summary: Panorama de la transformación industrial de Bilbao en los siglos XIX y XX y su impacto urbano y social.
tags: [historia, industria, ria]
source_url: https://www.euskadi.eus/
source_name: Gobierno Vasco
status: reviewed
updated_at: 2026-02-23T19:30:00Z
history:
  tema: Industrialización de Bilbao
  titulo: La industrialización de la ría de Bilbao
  contenido: A partir de finales del siglo XIX, la ría se consolidó como eje productivo...
  contenido_corto: Resumen del auge industrial, migraciones internas y reconversión posterior.
  epoca: Siglos XIX-XX
  fecha_inicio: 1876-01-01
  fecha_fin: 1995-12-31
  personajes_clave: [Ramón de la Sota, Víctor Chávarri]
  categoria: historia
  nivel_detalle: detallado
  fuentes:
    - https://www.euskadi.eus/
    - "Archivo histórico local de Bilbao"
---

# La industrialización de la ría de Bilbao
Contexto ampliado...
```

---

## 5) Mapeo frontmatter → SQL

### 5.1 `type: place` → tabla `places`

| Frontmatter | SQL (`places`) |
|---|---|
| `place.nombre` | `nombre` |
| `place.tipo` | `tipo` |
| `place.descripcion` | `descripcion` |
| `place.descripcion_corta` | `descripcion_corta` |
| `place.direccion` | `direccion` |
| `place.barrio` | `barrio` |
| `place.precio_medio` | `precio_medio` |
| `place.rango_precio` | `rango_precio` |
| `place.valoracion_local` | `valoracion_local` |
| `tags` | `tags` |
| `place.por_que_es_especial` | `por_que_es_especial` |
| `place.recomendado_por_locales` | `recomendado_por_locales` |
| `place.website` | `website` |
| `updated_at` | `updated_at` |

### 5.2 `type: history` → tabla `historia_vasca`

| Frontmatter | SQL (`historia_vasca`) |
|---|---|
| `history.tema` | `tema` |
| `history.titulo` | `titulo` |
| `history.contenido` | `contenido` |
| `history.contenido_corto` | `contenido_corto` |
| `history.epoca` | `epoca` |
| `history.fecha_inicio` | `fecha_inicio` |
| `history.fecha_fin` | `fecha_fin` |
| `history.personajes_clave` | `personajes_clave` |
| `tags` | `tags` |
| `history.categoria` | `categoria` |
| `history.nivel_detalle` | `nivel_detalle` |
| `history.fuentes` | `fuentes` |
| `language` | `idioma` |
| `updated_at` | `updated_at` |

### 5.3 `type: event` → tabla `events`

| Frontmatter | SQL (`events`) |
|---|---|
| `slug` | `slug` |
| `event.name` | `name` |
| `event.description` | `description` |
| `event.start_at` | `start_at` |
| `event.end_at` | `end_at` |
| `event.timezone` | `timezone` |
| `event.venue_name` | `venue_name` |
| `event.address` | `address` |
| `event.neighborhood` | `neighborhood` |
| `event.price_eur` | `price_eur` |
| `event.currency` | `currency` |
| `event.category` | `category` |
| `event.organizer` | `organizer` |
| `event.ticket_url` | `ticket_url` |
| `event.image_url` | `image_url` |
| `language` | `language` |
| `tags` | `tags` |
| `status` | `status` |
| `updated_at` | `updated_at` |

---

## 6) Checklist de calidad antes de publicar

- [ ] Frontmatter YAML parsea sin errores.
- [ ] `type` correcto y bloque específico presente.
- [ ] Todos los campos obligatorios completos.
- [ ] Fechas válidas y consistentes (`fin >= inicio`).
- [ ] `slug` único (en lote + DB).
- [ ] `summary` útil (no placeholder, 40+ chars).
- [ ] `tags` relevantes (1–12, sin duplicados).
- [ ] URLs funcionales (`https` preferido).
- [ ] `status` actualizado (`draft` → `reviewed` → `published`).
- [ ] Revisión humana final completada.
