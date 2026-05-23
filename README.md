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


vector_search = {
    "$vectorSearch": {
        "index":          "vectorPlotIndex",
        "path":           "plot_embedding",
        "queryVector":    embedding,
        "numCandidates":  num_candidates,
        "limit":          limit
    }
}

make_array = {
    "$group": { "_id": None, "docs": {"$push": "$$ROOT"} }
}

add_rank = {
    "$unwind": { "path": "$docs", "includeArrayIndex": "rank" }
}

def make_compute_score_doc(priority, score_field_name):
    return {
        "$addFields": {
            score_field_name: {
                "$divide": [
                    1.0,
                    { "$add": ["$rank", priority, 1] }
                ]
            }
        }
    }

def make_projection_doc(score_field_name):
    return  {
        "$project": {
            score_field_name:  1,
            "_id":             "$docs._id",
            "title":           "$docs.title",
            "plot":            "$docs.plot",
            "year":            "$docs.year",
        }
    }


text_search = {
    "$search": {
        "index":  "plotIndex",
        "text":   { "query": query, "path": "plot" },
    }
}

limit_results = {
    "$limit" : limit
}

combine_search_results = {
    "$group": {
        "_id":        "$_id",
        "vs_score":   {"$max":    "$vs_score"},
        "ts_score":   {"$max":    "$ts_score"},
        "title":      {"$first":  "$title"},
        "plot":       {"$first":  "$plot"},
        "year":       {"$first":  "$year"}
    }
}

project_combined_results = {
    "$project": {
        "_id":        1,
        "title":      1,
        "plot":       1,
        "year":       1,
        "score": {
            "$let": {
                "vars": {
                    "vs_score":  { "$ifNull":  ["$vs_score", 0] },
                    "ts_score":  { "$ifNull":  ["$ts_score", 0] }
                },
                "in": { "$add": ["$$vs_score", "$$ts_score"] }
            }
        }
    }
}

sort_results = {
    "$sort": { "score": -1}
}

pipeline = [
    vector_search,
    make_array,
    add_rank,
    make_compute_score_doc(vector_priority, "vs_score"),
    make_projection_doc("vs_score"),
    {
        "$unionWith": { "coll": "movies",
            "pipeline": [
                text_search,
                limit_results,
                make_array,
                add_rank,
                make_compute_score_doc(text_priority, "ts_score"),
                make_projection_doc("ts_score")
            ]
        }
    },
    combine_search_results,
    project_combined_results,
    sort_results,
    limit_results
]

x = collection.aggregate(pipeline)
