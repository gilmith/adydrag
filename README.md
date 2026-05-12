db.runCommand({
  "createSearchIndexes": "adyd_hechizos_2",
  "indexes": [
    {
      "name": "vector_hechizos_index_2",
      "type": "vectorSearch",
      "definition": {
        "fields": [
          {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 768,
            "similarity": "cosine"
          },
          {
            "type": "filter",
            "path": "nivel"
          },
          {
            "type": "filter",
            "path": "clases"
          },
          {
            "type": "filter",
            "path": "componentes"
          },
          {
            "type": "filter",
            "path": "salvacion"
          },
          {
            "type": "filter",
            "path": "tiempo_lanzamiento"
          },
          // Para búsqueda híbrida dentro de Vector Search, 
          // usamos 'filter' también para texto o quitamos el 'analyzer'
          {
            "type": "filter", 
            "path": "nombre"
          },
          {
            "type": "filter",
            "path": "keywords"
          }
        ]
      }
    }
  ]
})



## Descargar mongodb-atlas y configurar 

 - Descarga de imagen docker
`docker pull mongodb/mongodb-atlas-local`
- Correr el contenedor
`docker run -d \
  -p 27017:27017 \
  --name vector \
  mongodb/mongodb-atlas-local:latest`
- Configurar el usuario de la aplicacion 
 `use admin`
 `db.createUser({ user: "rag_user", pwd: "pass4rag", roles: [ { role: "readWrite", db: "adyd_rag" }, { role: "dbAdmin", db: "adyd_rag" }, { role: "clusterAdmin", db: "admin" } ] })`

## Crear una coleccion
se crea con el insert no hace falta hacer mas
## Crear un indice vectorial
`db.adyd_rag.createSearchIndex({ name: "vector_hechizos_index", type: "vectorSearch", definition: { "fields": [ { "type": "vector", "path": "embeddings", "numDimensions": 1536, "similarity": "cosine" }, { "type": "filter", "path": "title" } ] } });`
## indice hibrido
db.runCommand({
  "createSearchIndexes": "adyd_hechizos_2",
  "indexes": [
    {
      "name": "vector_hechizos_index_2",
      "type": "vectorSearch",
      "definition": {
        "fields": [
          {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 768,
            "similarity": "cosine"
          },
          {
            "type": "filter",
            "path": "nivel"
          },
          {
            "type": "filter",
            "path": "clases"
          },
          {
            "type": "filter",
            "path": "componentes"
          },
          {
            "type": "filter",
            "path": "salvacion"
          },
          {
            "type": "filter",
            "path": "tiempo_lanzamiento"
          },
          // Para búsqueda híbrida dentro de Vector Search, 
          // usamos 'filter' también para texto o quitamos el 'analyzer'
          {
            "type": "filter", 
            "path": "nombre"
          },
          {
            "type": "filter",
            "path": "keywords"
          }
        ]
      }
    }
  ]
})