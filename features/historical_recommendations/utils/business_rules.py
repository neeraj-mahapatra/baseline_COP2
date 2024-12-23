# src/models/business_rules.py

"""
Module containing business rule scoring functions.
"""

import random

def category_score(product, bundle):
    """
    Returns 1 if product's category is in the current bundle, else 0.
    """
    return 1 if product['category'] in [b['category'] for b in bundle] else 0

def business_score(product):
    """
    Placeholder for any advanced logic; returns a random score for now.
    """
    return random.random()
