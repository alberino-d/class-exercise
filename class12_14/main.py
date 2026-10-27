#main.py

import logging
from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import FastAPI, Query, File, UploadFile, HTTPException

from src import MovieResponse, MovieInput, CSVInfo, DataStorage, ProcessConfig

from middleware import log_requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

movies = {
    1: {"id": 1, "title": "Movie A", "release_year": 2020},
    2: {"id": 2, "title": "Movie B", "release_year": 2021},
}

storage = DataStorage()

app = FastAPI(title="Movie API")

# After the existing app = FastAPI(...):
app.middleware("http")(log_requests)


@app.get("/health")
def health_check():
    return {"status": "ok"}


#a path parameter identifies a resource (movie) to retrieve
@app.get("/demo/movies/{movie_id}")
def demo_get_movie(movie_id: int): #type annotation: it declares the expected type, int
    return {"requested_id": movie_id}


#a query parameter adjusts a request
@app.get("/demo/movies")
def demo_list_movies(limit: int = Query(default=2, ge=1)):
    #The default is 2 when limit is omitted in the query.
    # ge=1 means greater than or equal to one.
    return {"requested_limit": limit}


@app.post("/demo/movies")
def demo_add_movie(movie: MovieInput):
    return movie.model_dump() #Converts the model to a Python dictionary.


demo_movie_examples = []

@app.post("/demo/movie-examples", response_model=MovieResponse)
def demo_add_movie_example(movie: MovieInput):
    movie_id = len(demo_movie_examples) + 1
    record = movie.model_dump()
    record["id"] = movie_id
    demo_movie_examples.append(record)
    return record


@app.get("/movies", response_model=list[MovieResponse])
def list_movies(limit: int = Query(default=2, ge=1)):
    result = list(movies.values())[:limit]
    logger.info(f"Returned {len(result)} movies")
    return result


@app.post("/movies", response_model=MovieResponse)
def add_movie(movie: MovieInput):
    movie_id = max(movies.keys(), default=0) + 1
    record = movie.model_dump()
    record["id"] = movie_id
    movies[movie_id] = record

    logger.info(f"Added movie: id={movie_id}")
    return record


@app.post("/demo/inspect-csv")
async def demo_inspect_csv(file: UploadFile = File(...)):
    # ... in File(...) means the upload is required.
    contents = await file.read() # reads as bytes e.g. b"title,year\nMovie A,2020\n"
    return {"filename": file.filename,"size_bytes": len(contents)}


@app.get("/demo/movie-lookup/{movie_id}", response_model=MovieResponse)
def demo_lookup_movie(movie_id: int):
    movie = movies.get(movie_id)

    if movie is None:
        logger.warning(f"Movie not found: {movie_id}")
        raise HTTPException( status_code=404, detail="Movie not found")

    return movie


@app.post("/inspect-csv", response_model=CSVInfo)
async def inspect_csv(file: UploadFile = File(...)):
    if Path(file.filename or "").suffix.lower() != ".csv":
        logger.warning(f"Rejected non-CSV file: {file.filename}")
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
    except (pd.errors.EmptyDataError,pd.errors.ParserError,UnicodeDecodeError) as error:
        logger.warning(f"Cannot parse CSV {file.filename}: {error}")
        raise HTTPException(status_code=400, detail="Cannot parse the uploaded CSV")

    dataset_id = storage.save_data(df, file.filename)
    logger.info(f"Stored CSV: id={dataset_id}, filename={file.filename}")

    return CSVInfo(
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=list(df.columns),
        dataset_id=dataset_id
    )


@app.get("/datasets/{dataset_id}/shape")
def get_dataset_shape(dataset_id: int):
    df = storage.get_data(dataset_id)

    if df is None:
        logger.warning(f"Dataset not found: id={dataset_id}")
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    logger.info(f"Retrieved dataset: id={dataset_id}")

    return {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": len(df.columns)
    }


@app.post("/demo/process-config")
def demo_process_config(config: ProcessConfig):
    df = pd.DataFrame({"title": ["Movie A", "Movie A", "Movie B", None]})
    settings = config.model_dump()

    if settings["processing"]["remove_duplicates"]:
        df = df.drop_duplicates()
    if settings["processing"]["drop_missing"]:
        df = df.dropna()
        
    return {"rows": len(df)}
