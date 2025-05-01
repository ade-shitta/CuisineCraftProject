#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cuisine_craft_project.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_if_recipes_exist():
    """Check if there are already recipes in the database"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM recipes_recipe")
        count = cursor.fetchone()[0]
    return count > 0

def import_data():
    print("Checking if recipes already exist...")
    if check_if_recipes_exist():
        print("Recipes already exist in the database. Skipping import.")
        return
        
    print("Importing recipes from TheMealDB API...")
    call_command('import_recipes')
    
    print("Adding dietary tags to recipes...")
    call_command('add_dietary_tags')
    
    print("Data import completed successfully!")

if __name__ == "__main__":
    import_data() 