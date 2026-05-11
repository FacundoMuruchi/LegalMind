# 🏛️ LegalMind — Plataforma de Inteligencia Regulatoria y Análisis Contractual

> Plataforma asistida por IA para búsqueda normativa, trazabilidad regulatoria y análisis de cumplimiento contractual. Enfocada inicialmente en Uruguay y Argentina.

---

## 📋 Descripción del Proyecto

**LegalMind** es una plataforma que permite:

- Recolectar y mantener actualizada normativa pública de Uruguay y Argentina desde fuentes oficiales.
- Modelar trazabilidad normativa: derogaciones, sustituciones, modificaciones y vigencias.
- Consultar la base mediante búsqueda tradicional, semántica y preguntas en lenguaje natural (Q&A).
- Analizar contratos o borradores contractuales contra normativa vigente, con hallazgos explicables y auditables.
- Integrar el análisis dentro de Microsoft Word mediante un add-in autenticado (React).

---

## 🏗️ Arquitectura General

El sistema se organiza en tres módulos principales dentro de la **capa lógica**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CAPA LÓGICA                                │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐    │
│  │ Ingesta y       │  │ Análisis de      │  │ Motor de        │    │
│  │ Normativa       │  │ Contratos        │  │ Inferencia      │    │
│  │                 │  │                  │  │ Jurídica        │    │
│  │ - Background    │  │ - Segmentador    │  │                 │    │
│  │   jobs (cron /  │  │   de cláusulas   │  │ - Orquestador   │    │
│  │   EventBridge)  │  │ - Selección      │  │   RAG           │    │
│  │ - Crawler de    │  │   normativa      │  │ - Recuperador   │    │
│  │   fuentes       │  │ - Cumplimiento   │  │   híbrido       │    │
│  │ - Normalizador  │  │   + hallazgos    │  │   (BM25 +       │    │
│  │ - Vigencia y    │  │ - Recomendaciones│  │   vectorial)    │    │
│  │   relaciones    │  │   de remediación │  │ - Trazabilidad  │    │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬─────────┘    │
│           │                   │                     │              │
│      IRepoNormativo      IRepoNormativo        IRepoVectorial      │
└───────────┼───────────────────┼─────────────────────┼──────────────┘
            │                   │                     │
┌───────────▼───────────────────▼─────────────────────▼──────────────┐
│                      CAPA DE ACCESO A DATOS                         │
│                                                                     │
│   ┌──────────────────────────┐   ┌──────────────────────────────┐   │
│   │  «Manejador BD»          │   │  «Manejador BD»              │   │
│   │  Repositorio Normativo   │   │  Repositorio Vectorial       │   │
│   │                          │   │                              │   │
│   │  - Normas + metadatos    │   │  - Embeddings matryoshka     │   │
│   │  - Versiones y vigencias │   │  - Índice BM25               │   │
│   │  - Relaciones normativas │   │  - Chunks de documentos      │   │
│   │  - Config store          │   │  - Campos float por tabla    │   │
│   └────────────┬─────────────┘   └──────────────┬───────────────┘   │
│                └──────────────────┬──────────────┘                  │
│                              IDBAccess                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  «db»  SQLite                   │
              │  tablas normativas + metadatos  │
              │  relaciones + embeddings        │
              │  vectoriales (campo float)      │
              └─────────────────────────────────┘
```

### Interfaces entre capas (Clean Architecture)

| Controlador              | Interfaz provista       | Descripción                                    |
|--------------------------|-------------------------|------------------------------------------------|
| `AuthController`         | `IIdentityManager`      | Valida credenciales y retorna JWT + Tenant     |
| `ContractController`     | `IContractProcessor`    | Recibe texto + jurisdicción, devuelve hallazgos|
| `RagController`          | `IQAOrchestrator`       | Recibe pregunta, ejecuta RAG y retorna citas   |
| `AdminController`        | `IIngestionManager`     | Controla sincronización de fuentes normativas  |

---

## 🛠️ Stack Tecnológico

| Componente       | Tecnología                                      |
|------------------|-------------------------------------------------|
| **Backend**      | Python (frameworks livianos, sin LangChain pesado) |
| **Add-in Word**  | React                                           |
| **Repo Normativo**| SQLite — tablas de normas, metadatos, versiones, vigencias y relaciones |
| **Repo Vectorial**| SQLite — embeddings matryoshka como campos `float` por tabla + índice BM25 |
| **Scheduling**   | AWS EventBridge (cron jobs, no autoejecución)   |
| **Auth**         | Bearer token (ID Token + Access Token), caché LRU ~60s |
| **LLMs**         | OpenAI API (producción) + modelos locales (desarrollo/testing) |
| **Observabilidad**| LangSmith (trazas, tiempos, fuentes utilizadas) |
| **Logs**         | JSON estructurado → stdout → AWS CloudWatch     |
| **Contenedor**   | Docker (imagen liviana, sin exceder ~500MB)     |
| **Entornos**     | Local → Dev → Staging → Producción              |

---

## 📁 Estructura de Carpetas Sugerida

```
legalmind/
├── backend/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── contract_controller.py
│   │   ├── rag_controller.py
│   │   └── admin_controller.py
│   ├── modules/
│   │   ├── ingestion/
│   │   │   ├── crawler.py
│   │   │   ├── normalizer.py
│   │   │   ├── vigency_tracker.py
│   │   │   └── sources_config.json
│   │   ├── contract_analysis/
│   │   │   ├── clause_segmenter.py
│   │   │   ├── norm_selector.py
│   │   │   ├── compliance_engine.py
│   │   │   └── report_generator.py
│   │   └── inference_engine/
│   │       ├── rag_orchestrator.py
│   │       ├── hybrid_retriever.py      # BM25 + vectorial
│   │       ├── traceability.py
│   │       └── prompt_manager.py        # prompts versionados en Git
│   ├── data/
│   │   ├── normative_repository.py      # Manejador BD — normas, metadatos, versiones, relaciones
│   │   └── vector_repository.py         # Manejador BD — embeddings matryoshka + BM25
│   ├── pipelines/
│   │   └── pipeline_config.py           # activa/desactiva pipelines sin redeploy
│   ├── tests/                           # cobertura mínima 90%
│   └── Dockerfile
├── word-addin/                          # React
│   ├── src/
│   │   ├── components/
│   │   │   ├── FindingsPanel.jsx
│   │   │   └── AuthFlow.jsx
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 🗄️ Capa de Acceso a Datos

Ambos repositorios son **Manejadores de BD** que se exponen mediante interfaces (`IRepoNormativo` e `IRepoVectorial`) hacia la capa lógica. Internamente, los dos residen sobre una **única base SQLite**.

### Repositorio Normativo (`IRepoNormativo`)
Responsable de toda la información estructural de las normas:
- Documentos normativos con metadatos (país, organismo, tipo, número, fecha, URL de origen, hash)
- Historial de versiones y estados de vigencia (vigente, derogado, modificado, sustituido)
- Relaciones entre normas: modifica, deroga, reglamenta, complementa, remite a
- Config store: fuentes registradas por jurisdicción con estado activo/inactivo

### Repositorio Vectorial (`IRepoVectorial`)
Responsable de la búsqueda semántica e híbrida:
- Chunks de documentos normalizados listos para RAG
- Embeddings **matryoshka** almacenados como campos `float` en las tablas SQLite
- Índice BM25 para búsqueda léxica complementaria
- Recuperación híbrida: BM25 + vectorial para el motor de inferencia

> **Nota de diseño:** En producción escalable se usaría AWS Aurora + PGVector. Para el MVP y desarrollo local, SQLite embebido es la decisión correcta (liviano, sin dependencias externas, un solo archivo).

---

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- Node.js 18+ (para el add-in)
- API key de OpenAI (para producción)
- Modelo local configurado (para desarrollo, ej. Ollama)

### Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd legalmind

# Backend
cd backend
pip install -r requirements.txt

# Levantar con Docker
docker compose up --build
```

### Variables de entorno

```env
OPENAI_API_KEY=sk-...
AUTH_SERVICE_URL=https://...
AUTH_ENDPOINT_ME=/me
AUTH_ENDPOINT_AUTHORIZED=/authorized
ENV=local   # local | dev | staging | production
USE_LOCAL_MODEL=true   # true para desarrollo (ahorra tokens)
```

### Correr tests

```bash
cd backend
pytest --cov=. --cov-report=term-missing
# Cobertura mínima requerida: 90%
```

---

## 🔄 Roadmap de Etapas

### Etapa 0 — Descubrimiento y Diseño ✅
- Mapa de fuentes oficiales UY + AR
- Taxonomía documental
- Modelo de datos normativo
- Arquitectura inicial definida
- Backlog priorizado

### Etapa 1 — MVP: Corpus Normativo Vivo
- Ingesta de fuentes priorizadas
- Parsing y normalización básica
- Indexación full-text + semántica
- Búsqueda por metadatos y texto
- Visualización de documento y vigencia simple

**Criterio de salida:** usuarios internos pueden encontrar normas vigentes y navegar relaciones básicas.

### Etapa 2 — Trazabilidad Normativa y Q&A Explicable
- Extracción de relaciones entre normas
- Versionado/vigencia robusta
- Q&A con citas y evidencia
- Evaluación de groundedness
- Panel de revisión interna

**Criterio de salida:** el sistema responde preguntas con soporte normativo verificable y baja tasa de alucinación.

### Etapa 3 — Análisis Contractual Backend
- Carga de DOCX/PDF
- Extracción de cláusulas
- Matching cláusula-norma
- Hallazgos con severidad
- Reportes de cumplimiento y faltantes

**Criterio de salida:** analiza contratos acotados contra normativa bien definida.

### Etapa 4 — Add-in de Word
- Autenticación desde Word
- Análisis del documento abierto
- Panel de hallazgos con navegación
- Posibilidad de reanálisis

**Criterio de salida:** abogados pueden correr el análisis sin salir de Word.

### Etapa 5 — Hardening Productivo
- Multi-tenant completo
- Observabilidad
- Administración de organizaciones
- Seguridad/compliance
- Nuevas jurisdicciones y dominios regulatorios

---

## 🔐 Autenticación

El sistema usa **Bearer tokens** (ID Token + Access Token). El `AuthController` es un componente simple y desacoplado que delega toda la lógica al servicio de autenticación externo.

```
Login → obtener tokens → enviar token en cada request → validar con servicio auth
```

**Permisos** (RFC a enviar al equipo de infraestructura):
```
regulations:read
regulations:write
contracts:analyze
admin:sources
```

---

## ⚙️ Pipeline Config

Cada análisis registra en el log qué pipeline y qué versión de prompt usó. Se puede activar/desactivar un pipeline desde configuración sin hacer nuevo deploy.

```json
{
  "contract_analysis": "pipeline_v2_self_rag",
  "qa_engine": "pipeline_v1_naive_rag",
  "active_env": "staging"
}
```

---

## 📊 Métricas de Calidad

| Capa              | Métrica clave                                  |
|-------------------|------------------------------------------------|
| Ingesta           | Cobertura de fuentes, tasa de normalización    |
| Búsqueda          | Precision@k, Recall@k, MRR                    |
| Q&A / RAG         | Groundedness, hallucination rate, citation accuracy |
| Análisis contrac. | Clause detection recall, compliance precision  |
| Producto          | Tiempo hasta primer valor, uso recurrente      |

---

## ⚠️ Consideraciones Importantes

- **El container no puede superar ~500MB** (impacta cold start y UX).
- **No usar LangChain de forma pesada** — preferir OpenAI SDK o Anthropic SDK directamente.
- **Los background jobs no se autoejecutan** — son invocados por AWS EventBridge vía endpoint interno (no público).
- **No almacenar contratos** ni logs en la base de datos. Los logs van a stdout → CloudWatch.
- **Usar modelos locales en desarrollo** para no consumir tokens de OpenAI innecesariamente.
- Los permisos los crea el equipo de infraestructura; el equipo solo envía RFC con el nombre del servicio y la acción.

---

## 👥 Equipo

- **Lucía Olivera** — Diseño y arquitectura
- **Facundo Muruchi** — Desarrollo
- *(Tutor técnico: Federico Gil)*

---

## 📄 Licencia

Proyecto académico — Seminario de Integración Profesional I.
