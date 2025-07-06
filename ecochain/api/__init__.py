"""
EcoChain API Gateway

This package implements the API gateway for EcoChain Guardian, providing:
- REST API endpoints for third-party integration
- GraphQL support for flexible data querying
- Authentication and rate limiting
"""

from ecochain.api.rest import create_app as create_rest_app
from ecochain.api.graphql import create_app as create_graphql_app

__all__ = ['create_rest_app', 'create_graphql_app'] 