import pandas as pd
from neo4j import GraphDatabase
import os

# Neo4j连接配置
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://3ab79b4e.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "brZN7uVswltX_DwXFPAedISccdewSvj6jLuJKVaXCXo")

def clear_existing_data(driver):
    """清除现有数据"""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("已清除所有现有数据")

def import_recipes(driver, csv_path):
    """导入食谱数据"""
    recipes = pd.read_csv(os.path.join(csv_path, 'recipes.csv'))
    with driver.session() as session:
        for _, row in recipes.iterrows():
            session.run("""
                CREATE (r:Recipe {
                    recipe_id: $recipe_id,
                    name: $name,
                    difficulty: $difficulty,
                    cook_time: $cook_time,
                    category: $category,
                    description: $description
                })
            """, {
                'recipe_id': row['recipe_id'],
                'name': row['name'],
                'difficulty': row['difficulty'],
                'cook_time': row['cook_time'],
                'category': row['category'],
                'description': row['description']
            })
    print(f"已导入 {len(recipes)} 个食谱")

def import_ingredients(driver, csv_path):
    """导入原材料数据"""
    ingredients = pd.read_csv(os.path.join(csv_path, 'ingredients.csv'))
    with driver.session() as session:
        for _, row in ingredients.iterrows():
            session.run("""
                CREATE (i:Ingredient {
                    ingredient_id: $ingredient_id,
                    name: $name,
                    category: $category,
                    unit: $unit,
                    calories_per_100g: $calories_per_100g
                })
            """, {
                'ingredient_id': row['ingredient_id'],
                'name': row['name'],
                'category': row['category'],
                'unit': row['unit'],
                'calories_per_100g': row['calories_per_100g']
            })
    print(f"已导入 {len(ingredients)} 种原材料")

def import_recipe_ingredients(driver, csv_path):
    """导入食谱-原材料关系"""
    recipe_ingredients = pd.read_csv(os.path.join(csv_path, 'recipe_ingredients.csv'))
    with driver.session() as session:
        for _, row in recipe_ingredients.iterrows():
            session.run("""
                MATCH (r:Recipe {recipe_id: $recipe_id})
                MATCH (i:Ingredient {name: $ingredient_name})
                CREATE (r)-[:NEEDS {quantity: $quantity, note: $note}]->(i)
            """, {
                'recipe_id': row['recipe_id'],
                'ingredient_name': row['ingredient_name'],
                'quantity': row['quantity'],
                'note': row['note'] if pd.notna(row['note']) else ''
            })
    print(f"已导入 {len(recipe_ingredients)} 个原材料关系")

def import_recipe_steps(driver, csv_path):
    """导入制作步骤"""
    steps = pd.read_csv(os.path.join(csv_path, 'recipe_steps.csv'))
    with driver.session() as session:
        for _, row in steps.iterrows():
            session.run("""
                MATCH (r:Recipe {recipe_id: $recipe_id})
                CREATE (s:Step {step_number: $step_number, description: $description})
                CREATE (r)-[:HAS_STEP]->(s)
            """, {
                'recipe_id': row['recipe_id'],
                'step_number': row['step_number'],
                'description': row['description']
            })
    print(f"已导入 {len(steps)} 个制作步骤")

def import_recommendations(driver, csv_path):
    """导入推荐关系"""
    recommendations = pd.read_csv(os.path.join(csv_path, 'recipe_recommendations.csv'))
    with driver.session() as session:
        for _, row in recommendations.iterrows():
            session.run("""
                MATCH (r1:Recipe {recipe_id: $recipe_id})
                MATCH (r2:Recipe {recipe_id: $recommended_recipe_id})
                CREATE (r1)-[:RECOMMENDS {reason: $reason}]->(r2)
            """, {
                'recipe_id': row['recipe_id'],
                'recommended_recipe_id': row['recommended_recipe_id'],
                'reason': row['reason']
            })
    print(f"已导入 {len(recommendations)} 个推荐关系")

def create_indexes(driver):
    """创建索引"""
    with driver.session() as session:
        session.run("CREATE INDEX idx_recipe_name IF NOT EXISTS FOR (r:Recipe) ON (r.name)")
        session.run("CREATE INDEX idx_ingredient_name IF NOT EXISTS FOR (i:Ingredient) ON (i.name)")
        session.run("CREATE INDEX idx_recipe_id IF NOT EXISTS FOR (r:Recipe) ON (r.recipe_id)")
        session.run("CREATE INDEX idx_ingredient_id IF NOT EXISTS FOR (i:Ingredient) ON (i.ingredient_id)")
    print("已创建索引")

def main():
    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print("[OK] Connected to Neo4j successfully")
        
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        clear_existing_data(driver)
        import_recipes(driver, csv_path)
        import_ingredients(driver, csv_path)
        import_recipe_ingredients(driver, csv_path)
        import_recipe_steps(driver, csv_path)
        import_recommendations(driver, csv_path)
        create_indexes(driver)
        
        print("\n[DONE] Recipe knowledge graph import completed!")
        
    except Exception as e:
        print("[ERROR] Import failed:", str(e))
    finally:
        if driver:
            driver.close()

if __name__ == "__main__":
    main()