"""Routes module for the Kingshot Heroes API.

Exports consolidated routers for all API endpoints.
Each module exports a router with prefix and tags already configured.
"""

# Import from top-level router files (not subdirectories)
from . import exclusive_gear, heroes, skills, stats, talents, troops, vip

__all__ = ["exclusive_gear", "heroes", "skills", "stats", "talents", "troops", "vip"]
