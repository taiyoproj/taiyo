"""Integration tests for authentication with Solr."""

import random
import string
import time
import pytest
from taiyo import SolrClient, BasicAuth, SolrDocument, SolrError
from taiyo.schema import SolrField


SOLR_URL = "http://localhost:8983/solr"
SOLR_AUTH_URL = "http://localhost:8984/solr"

AUTH_USERNAME_TEST = "solr"
AUTH_PASSWORD_TEST = "SolrRocks"

# Configure longer timeout
TIMEOUT = 30.0

class AuthTestDoc(SolrDocument):
    """Simple test document."""

    name: str
    title: str


def test_basic_auth_success():
    """Test successful authentication with BasicAuth."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_auth_success_{_rand}"

    auth = BasicAuth(username=AUTH_USERNAME_TEST, password=AUTH_PASSWORD_TEST)

    # Use longer timeout for auth server (first requests can be slow)
    with SolrClient(SOLR_AUTH_URL, auth=auth, timeout=TIMEOUT) as client:
        # Create collection - should succeed with auth
        client.create_collection(collection, num_shards=1, replication_factor=1)
        time.sleep(1)

        client.set_collection(collection)

        # Add a field
        field = SolrField(name="title", type="text_general", stored=True, indexed=True)
        try:
            client.add_field(field)
        except Exception:
            pass  # Field may already exist

        time.sleep(1)

        # Index a document
        doc = AuthTestDoc(name="1", title="Test Document")
        client.add([doc])
        client.commit()
        time.sleep(1)

        # Search for the document
        results = client.search("*:*")
        assert results.num_found >= 1
        assert any(d.id == "1" for d in results.docs)

        # Cleanup
        client.delete_collection(collection)


def test_basic_auth_failure_wrong_password():
    """Test authentication failure with wrong password."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_auth_fail_{_rand}"

    # Create auth object with wrong password
    auth = BasicAuth(username=AUTH_USERNAME_TEST, password="WrongPassword")

    with pytest.raises(SolrError) as exc_info:
        with SolrClient(SOLR_AUTH_URL, auth=auth) as client:
            # This should fail with 401 Unauthorized
            client.create_collection(collection, num_shards=1, replication_factor=1)

    # Check that we got an authentication error
    assert "401" in str(exc_info.value) or "Unauthorized" in str(exc_info.value)


def test_no_auth_on_auth_server():
    """Test that requests without auth fail on the auth-enabled server."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_no_auth_{_rand}"

    with pytest.raises(SolrError) as exc_info:
        with SolrClient(SOLR_AUTH_URL) as client:
            # This should fail without auth credentials
            client.create_collection(collection, num_shards=1, replication_factor=1)

    # Check that we got an authentication error
    assert "401" in str(exc_info.value) or "Unauthorized" in str(exc_info.value)


def test_auth_on_non_auth_server():
    """Test that auth credentials work fine on non-auth server (should be ignored)."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_auth_ignored_{_rand}"

    # Create auth object (will be ignored by non-auth server)
    auth = BasicAuth(username=AUTH_USERNAME_TEST, password=AUTH_PASSWORD_TEST)

    with SolrClient(SOLR_URL, auth=auth) as client:
        # This should succeed - non-auth server ignores auth headers
        client.create_collection(collection, num_shards=1, replication_factor=1)
        time.sleep(1)

        client.set_collection(collection)

        # Index a document
        doc = AuthTestDoc(name="1", title="Test Document")
        client.add([doc])
        client.commit()
        time.sleep(1)

        # Search
        results = client.search("*:*")
        assert results.num_found >= 1

        # Cleanup
        client.delete_collection(collection)


def test_basic_auth_all_operations():
    """Test that BasicAuth works for all major Solr operations."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_auth_ops_{_rand}"

    auth = BasicAuth(username=AUTH_USERNAME_TEST, password=AUTH_PASSWORD_TEST)

    # Use longer timeout for auth server (first requests can be slow)
    with SolrClient(SOLR_AUTH_URL, auth=auth, timeout=TIMEOUT) as client:
        # Create collection
        client.create_collection(collection, num_shards=1, replication_factor=1)
        time.sleep(1)

        client.set_collection(collection)

        # Add field
        field = SolrField(name="title", type="text_general", stored=True, indexed=True)
        try:
            client.add_field(field)
        except Exception:
            pass

        time.sleep(1)

        # Index documents
        docs = [AuthTestDoc(name=str(i), title=f"Document {i}") for i in range(5)]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Search
        results = client.search("*:*")
        assert results.num_found >= 5

        # Update a document
        update_doc = AuthTestDoc(name="1", title="Updated Document")
        client.add([update_doc])
        client.commit()
        time.sleep(1)

        # Verify update
        results = client.search("title:Updated")
        assert results.num_found >= 1

        # Delete by ID
        client.delete(ids=["1"])
        client.commit()
        time.sleep(1)

        # Verify deletion
        results = client.search("id:1")
        assert results.num_found == 0

        # Delete by query
        client.delete(query="*:*")
        client.commit()
        time.sleep(1)

        # Verify all deleted
        results = client.search("*:*")
        assert results.num_found == 0

        # Cleanup
        client.delete_collection(collection)
