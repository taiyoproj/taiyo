import random
import string
import time
from pydantic import Field
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrFieldType, SolrField, SolrFieldClass
from taiyo.parsers.dense.knn import KNNQueryParser

SOLR_URL = "http://localhost:8983/solr"
_rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
COLLECTION = f"test_taiyo_knn_{_rand}"


class Movie(SolrDocument):
    """Movie document with semantic embedding vector."""
    title: str
    genre: str
    description: str
    embedding: list[float] = Field(
        default_factory=list, 
        description="Semantic embedding vector for similarity search"
    )


def test_knn():
    """End-to-end test for KNN search with realistic movie recommendations.
    
    This test simulates a movie recommendation system using semantic embeddings.
    The embeddings are simplified 5-dimensional vectors where dimensions roughly represent:
    - action/adventure intensity
    - drama/emotion level  
    - comedy/humor level
    - sci-fi/fantasy elements
    - romance level
    """
    with SolrClient(SOLR_URL) as client:
        # Create collection
        try:
            client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
        except Exception:
            pass  # Collection may already exist

        client.set_collection(COLLECTION)

        # Define and add vector field type with 5 dimensions
        vector_field_type = SolrFieldType(
            name="movie_embedding",
            solr_class=SolrFieldClass.DENSE_VECTOR,
            vectorDimension=5,
            similarityFunction="cosine",  # Better for semantic similarity
            knnAlgorithm="hnsw",
        )

        client.add_field_type(vector_field_type)

        fields = [
            SolrField(name="title", type="string", stored=True),
            SolrField(name="genre", type="string", stored=True),
            SolrField(name="description", type="text_general", stored=True, multi_valued=False),
            SolrField(name="embedding", type="movie_embedding", indexed=True, stored=False),
        ]

        for field in fields:
            client.add_field(field)

        # Embeddings represent: [action, drama, comedy, sci-fi, romance]
        docs = [
            Movie(
                title="The Matrix",
                genre="Sci-Fi Action",
                description="A hacker discovers reality is a simulation",
                embedding=[0.9, 0.3, 0.1, 0.95, 0.2]  # High action & sci-fi
            ),
            Movie(
                title="Inception",
                genre="Sci-Fi Thriller",
                description="Dream thieves perform corporate espionage",
                embedding=[0.8, 0.6, 0.1, 0.85, 0.1]  # Action & sci-fi with drama
            ),
            Movie(
                title="The Notebook",
                genre="Romance Drama",
                description="A love story spanning decades",
                embedding=[0.1, 0.9, 0.1, 0.0, 0.95]  # High drama & romance
            ),
            Movie(
                title="Superbad",
                genre="Comedy",
                description="High school friends have one last adventure",
                embedding=[0.2, 0.3, 0.95, 0.0, 0.4]  # High comedy
            ),
            Movie(
                title="Interstellar",
                genre="Sci-Fi Drama",
                description="Astronauts travel through a wormhole to save humanity",
                embedding=[0.5, 0.8, 0.1, 0.9, 0.3]  # Sci-fi with strong drama
            ),
            Movie(
                title="Die Hard",
                genre="Action Thriller",
                description="A cop battles terrorists in a skyscraper",
                embedding=[0.95, 0.4, 0.3, 0.0, 0.1]  # High action
            ),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Test 1: Find movies similar to The Matrix (action sci-fi)
        # Query vector: high action and sci-fi
        matrix_like = [0.9, 0.3, 0.1, 0.9, 0.2]
        knn = KNNQueryParser(field="embedding", vector=matrix_like, top_k=3)
        try:
            res = client.search(knn, document_model=Movie)
            assert res.status == 0
            assert res.num_found >= 1
            assert all(isinstance(doc, Movie) for doc in res.docs)
            # Should find The Matrix, Inception, or other sci-fi action movies
            titles = [doc.title for doc in res.docs]
            assert any(movie in titles for movie in ["The Matrix", "Inception", "Interstellar"])
        except SolrError as e:
            print("[DEBUG] Solr KNN query error response:", getattr(e, "response", e))
            raise

        # Test 2: Find romantic movies
        # Query vector: high romance and drama
        romance_query = [0.1, 0.8, 0.1, 0.0, 0.9]
        knn2 = KNNQueryParser(field="embedding", vector=romance_query, top_k=2)
        res2 = client.search(knn2, document_model=Movie)
        assert res2.status == 0
        assert res2.num_found >= 1
        # Should find The Notebook as it's the most romantic
        titles2 = [doc.title for doc in res2.docs]
        assert "The Notebook" in titles2
        print(f"Romantic movies found: {titles2}")

        # Test 3: Find comedy movies
        # Query vector: high comedy
        comedy_query = [0.2, 0.2, 0.95, 0.0, 0.3]
        knn3 = KNNQueryParser(field="embedding", vector=comedy_query, top_k=2)
        res3 = client.search(knn3, document_model=Movie)
        assert res3.status == 0
        # Should find Superbad as the top comedy
        titles3 = [doc.title for doc in res3.docs]
        assert "Superbad" in titles3
        print(f"Comedy movies found: {titles3}")

        # Cleanup
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
