<p align="center">
  <img src="assets/logo.png" alt="Taiyo logo" width="100" />
</p>

<h1 align="center">Taiyo</h1>

<p align="center">
  Modern Python client for Apache Solr with type-safety and async support, built with httpx and Pydantic.
</p>

---

## Features

- Shared sync and async client APIs for consistent developer experience
- Query parsers for standard, dismax, edismax, spatial, and dense vector search with full IDE support. Serializes into standard HTTP query parameters for compatibility with other clients.
- Supports grouping, faceting, highlighting, and more-like-this features defined with a Pythonic syntax either as config objects or in pandas-like method chains
- Schema utilities for defining fields, types, and copy-field rules for indexing
- Authentication support for Basic, Bearer, and OAuth2

---

## Use Cases

- Full-text search applications with faceting and highlighting
- Recommendation systems using vector similarity for semantic search
- Analytics using Solr's grouping and faceting capabilities
- Content management with type-safe document indexing
- Geospatial applications with location-based search and filtering

## Next Steps

- [Getting Started](getting-started.md) - Basic setup and first queries
- [Clients](clients/overview.md) - Client configuration, authentication, and usage patterns
- [Indexing](indexing/overview.md) - Document indexing and batch operations
- [Query Parsers](parsers/overview.md) - Query parser reference and examples
- [Controlling Results](controlling-results/faceting.md) - Faceting, grouping, highlighting, and MoreLikeThis

