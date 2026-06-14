import streamlit as st
import pandas as pd
from neo4j import GraphDatabase
import os

# 配置信息
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://3ab79b4e.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "brZN7uVswltX_DwXFPAedISccdewSvj6jLuJKVaXCXo")

# 页面配置
st.set_page_config(
    page_title="🍳 美食食谱知识图谱",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    .stButton>button {
        background: linear-gradient(90deg, #e94560, #ff6b6b);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #3498db;
        padding: 10px;
    }
    .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #3498db;
    }
    .recipe-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # 测试连接
        driver.verify_connectivity()
        return driver
    except Exception as e:
        st.error(f"数据库连接失败: {str(e)}")
        return None

def run_query(driver, query, params=None):
    results = []
    try:
        with driver.session() as session:
            result = session.run(query, params or {})
            for record in result:
                results.append(dict(record))
    except Exception as e:
        st.error(f"查询错误: {str(e)}")
    return results

def get_stats(driver):
    stats = {}
    try:
        stats['recipes'] = run_query(driver, "MATCH (r:Recipe) RETURN COUNT(r) AS count")[0]['count']
        stats['ingredients'] = run_query(driver, "MATCH (i:Ingredient) RETURN COUNT(i) AS count")[0]['count']
        stats['relations'] = run_query(driver, "MATCH ()-[r]->() RETURN COUNT(r) AS count")[0]['count']
    except:
        stats = {'recipes': 0, 'ingredients': 0, 'relations': 0}
    return stats

def search_recipes(driver, keyword):
    query = """
        MATCH (r:Recipe)
        WHERE r.name CONTAINS $keyword OR r.description CONTAINS $keyword
        RETURN r.name AS 菜名, r.category AS 菜系, r.difficulty AS 难度, r.cook_time AS 烹饪时间, r.description AS 描述
        ORDER BY r.name
    """
    return run_query(driver, query, {'keyword': keyword})

def get_recipe_details(driver, recipe_name):
    # 获取食谱基本信息
    recipe_query = """
        MATCH (r:Recipe {name: $name})
        RETURN r.name AS 菜名, r.category AS 菜系, r.difficulty AS 难度, r.cook_time AS 烹饪时间, r.description AS 描述
    """
    recipe = run_query(driver, recipe_query, {'name': recipe_name})
    
    # 获取原材料（使用 CONTAINS 以支持部分匹配）
    ingredients_query = """
        MATCH (r:Recipe {name: $name})-[rel]->(i:Ingredient)
        RETURN i.name AS 原材料, rel.quantity AS 用量, rel.note AS 备注
        ORDER BY i.name
    """
    ingredients = run_query(driver, ingredients_query, {'name': recipe_name})
    
    # 获取制作步骤
    steps_query = """
        MATCH (r:Recipe {name: $name})-[:HAS_STEP]->(s:Step)
        RETURN s.step_number AS 步骤, s.description AS 说明
        ORDER BY s.step_number
    """
    steps = run_query(driver, steps_query, {'name': recipe_name})
    
    # 获取推荐菜品
    recommend_query = """
        MATCH (r:Recipe {name: $name})-[rel:RECOMMENDS]->(r2:Recipe)
        RETURN r2.name AS 推荐菜品, rel.reason AS 推荐理由
    """
    recommendations = run_query(driver, recommend_query, {'name': recipe_name})
    
    return recipe[0] if recipe else None, ingredients, steps, recommendations

def search_by_ingredient(driver, ingredient_name):
    query = """
        MATCH (r:Recipe)-[rel]->(i:Ingredient)
        WHERE i.name CONTAINS $ingredient
        RETURN DISTINCT r.name AS 菜名, r.category AS 菜系, r.difficulty AS 难度, r.cook_time AS 烹饪时间
        ORDER BY r.name
    """
    return run_query(driver, query, {'ingredient': ingredient_name})

def get_ingredient_info(driver, ingredient_name):
    query = """
        MATCH (i:Ingredient {name: $name})
        RETURN i.name AS 名称, i.category AS 类别, i.unit AS 单位, i.calories_per_100g AS 热量
    """
    return run_query(driver, query, {'name': ingredient_name})

def get_recommendations(driver, recipe_name=None):
    if recipe_name:
        query = """
            MATCH (r:Recipe {name: $name})-[rel:RECOMMENDS]->(r2:Recipe)
            RETURN r2.name AS 推荐菜品, r2.category AS 菜系, r2.difficulty AS 难度, rel.reason AS 推荐理由
            ORDER BY r2.name
        """
        return run_query(driver, query, {'name': recipe_name})
    else:
        # 随机推荐家常菜
        query = """
            MATCH (r:Recipe)
            WHERE r.category = '家常菜' OR r.difficulty = '简单'
            RETURN r.name AS 推荐菜品, r.category AS 菜系, r.difficulty AS 难度, r.cook_time AS 烹饪时间
            ORDER BY rand()
            LIMIT 8
        """
        return run_query(driver, query)

def get_all_ingredients(driver):
    query = "MATCH (i:Ingredient) RETURN i.name AS name ORDER BY i.name"
    results = run_query(driver, query)
    return [r['name'] for r in results]

def get_all_recipes(driver):
    query = "MATCH (r:Recipe) RETURN r.name AS name ORDER BY r.name"
    results = run_query(driver, query)
    return [r['name'] for r in results]

def get_categories(driver):
    query = "MATCH (r:Recipe) RETURN DISTINCT r.category AS category ORDER BY category"
    results = run_query(driver, query)
    return [r['category'] for r in results]

def get_recipe_full_details(driver, recipe_name):
    """获取菜品的完整详细信息，包括所有制作步骤"""
    recipe_query = """
        MATCH (r:Recipe {name: $name})
        RETURN r.name AS 菜名, r.category AS 菜系, r.difficulty AS 难度, 
               r.cook_time AS 烹饪时间, r.description AS 描述, r.taste AS 口味
    """
    recipe = run_query(driver, recipe_query, {'name': recipe_name})
    
    if not recipe:
        return None
    
    # 获取所有原材料（使用通用的关系类型匹配）
    ingredients_query = """
        MATCH (r:Recipe {name: $name})-[rel]->(i:Ingredient)
        RETURN i.name AS 名称, i.category AS 类别, rel.quantity AS 用量, rel.note AS 备注
        ORDER BY i.category, i.name
    """
    ingredients = run_query(driver, ingredients_query, {'name': recipe_name})
    
    # 获取制作步骤
    steps_query = """
        MATCH (r:Recipe {name: $name})-[:HAS_STEP]->(s:Step)
        RETURN s.step_number AS 步骤编号, s.description AS 详细步骤, s.duration AS 预计时间
        ORDER BY s.step_number
    """
    steps = run_query(driver, steps_query, {'name': recipe_name})
    
    # 获取技巧提示
    tips_query = """
        MATCH (r:Recipe {name: $name})-[:HAS_TIP]->(t:Tip)
        RETURN t.content AS 技巧内容, t.category AS 类型
    """
    tips = run_query(driver, tips_query, {'name': recipe_name})
    
    return {
        'basic': recipe[0] if recipe else None,
        'ingredients': ingredients,
        'steps': steps,
        'tips': tips
    }

# 主程序
driver = get_neo4j_driver()

st.title("🍳 美食食谱知识图谱")

if driver:
    stats = get_stats(driver)
    
    # 统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🍲 菜品数量", stats['recipes'])
    with col2:
        st.metric("🥬 原材料种类", stats['ingredients'])
    with col3:
        st.metric("🔗 关系数量", stats['relations'])
    
    st.markdown("---")
    
    # 搜索功能
    search_tab, recipe_tab, ingredient_tab, recommend_tab = st.tabs([
        "🔍 菜品搜索", 
        "📋 菜品详情", 
        "🥬 原材料查询", 
        "✨ 智能推荐"
    ])
    
    with search_tab:
        st.subheader("🔍 搜索菜品")
        search_keyword = st.text_input("输入菜名或关键词:", placeholder="例如：宫保鸡丁、川菜")
        
        if st.button("搜索", use_container_width=True):
            if search_keyword:
                results = search_recipes(driver, search_keyword)
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                else:
                    st.warning("未找到相关菜品")
            else:
                st.warning("请输入搜索关键词")
        
        # 按菜系筛选
        st.markdown("---")
        st.subheader("📁 按菜系浏览")
        categories = get_categories(driver)
        selected_category = st.selectbox("选择菜系:", ["全部"] + categories)
        
        if selected_category != "全部":
            query = """
                MATCH (r:Recipe)
                WHERE r.category = $category
                RETURN r.name AS 菜名, r.difficulty AS 难度, r.cook_time AS 烹饪时间, r.description AS 描述
                ORDER BY r.name
            """
            results = run_query(driver, query, {'category': selected_category})
            st.dataframe(pd.DataFrame(results), use_container_width=True)
    
    with recipe_tab:
        st.subheader("📋 菜品详情")
        all_recipes = get_all_recipes(driver)
        selected_recipe = st.selectbox("选择菜品:", all_recipes)
        
        if selected_recipe:
            recipe_info, ingredients, steps, recommendations = get_recipe_details(driver, selected_recipe)
            
            if recipe_info:
                st.markdown(f"## 🍳 {recipe_info['菜名']}")
                
                # 基本信息卡片
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("菜系", recipe_info.get('菜系', '未知'))
                with col2:
                    st.metric("难度", recipe_info.get('难度', '未知'))
                with col3:
                    st.metric("烹饪时间", recipe_info.get('烹饪时间', '未知'))
                with col4:
                    if recipe_info.get('描述'):
                        st.info(f"**描述**: {recipe_info['描述']}")
                
                # 原材料
                st.markdown("---")
                st.subheader("🛒 所需原材料")
                
                if ingredients:
                    # 按类别分组显示
                    df_ingredients = pd.DataFrame(ingredients)
                    st.dataframe(df_ingredients, use_container_width=True)
                    
                    # 显示原材料列表（用于采购）
                    st.markdown("**采购清单:**")
                    ingredients_list = [f"{row['原材料']} - {row.get('用量', '')} {row.get('备注', '')}" 
                                      for _, row in df_ingredients.iterrows()]
                    for item in ingredients_list:
                        st.write(f"• {item}")
                else:
                    st.info("暂无原材料信息")
                
                # 制作步骤
                st.markdown("---")
                st.subheader("📝 详细制作步骤")
                
                if steps:
                    for idx, step in enumerate(steps, 1):
                        with st.container():
                            col_left, col_right = st.columns([1, 5])
                            with col_left:
                                st.markdown(f"### {step['步骤']}")
                            with col_right:
                                st.write(step['说明'])
                    st.markdown("---")
                    
                    # 步骤概览
                    st.markdown("**步骤概览:**")
                    for step in steps:
                        st.write(f"**步骤 {step['步骤']}**: {step['说明'][:50]}...")
                else:
                    st.info("暂无制作步骤")
                
                # 推荐菜品
                st.markdown("---")
                st.subheader("✨ 推荐搭配")
                if recommendations:
                    st.dataframe(pd.DataFrame(recommendations), use_container_width=True)
                else:
                    st.info("暂无推荐")
    
    with ingredient_tab:
        st.subheader("🥬 原材料查询")
        all_ingredients = get_all_ingredients(driver)
        
        # 搜索原材料
        search_ingredient = st.text_input("搜索原材料:", placeholder="例如：鸡肉、土豆")
        
        if st.button("搜索原材料", use_container_width=True):
            if search_ingredient:
                # 显示原材料信息
                info = get_ingredient_info(driver, search_ingredient)
                if info:
                    st.markdown("**原材料信息:**")
                    st.dataframe(pd.DataFrame(info), use_container_width=True)
                else:
                    st.info("未找到该原材料的详细信息")
                
                # 显示用该原材料的菜品
                st.markdown("---")
                st.subheader(f"🍳 使用 {search_ingredient} 的菜品")
                recipes = search_by_ingredient(driver, search_ingredient)
                if recipes:
                    st.dataframe(pd.DataFrame(recipes), use_container_width=True)
                else:
                    st.info("暂无使用该原材料的菜品")
        
        # 显示所有原材料
        st.markdown("---")
        st.subheader("📦 全部原材料列表")
        if all_ingredients:
            # 每行显示4个
            cols = st.columns(4)
            for idx, ingredient in enumerate(all_ingredients):
                with cols[idx % 4]:
                    st.write(f"• {ingredient}")
    
    with recommend_tab:
        st.subheader("✨ 智能推荐")
        
        # 家常菜推荐
        st.markdown("### 🏠 推荐家常菜")
        st.write("随机推荐简单易做的家常菜：")
        
        home_recipes = get_recommendations(driver)
        if home_recipes:
            st.dataframe(pd.DataFrame(home_recipes), use_container_width=True)
        else:
            st.info("暂无推荐")
        
        # 按口味推荐
        st.markdown("---")
        st.subheader("🍽️ 根据现有食材推荐")
        available_ingredients = st.text_input("输入你现有的食材（用逗号分隔）:", 
                                             placeholder="例如：鸡蛋,西红柿,葱")
        
        if st.button("推荐菜品", use_container_width=True):
            if available_ingredients:
                ingredients_list = [i.strip() for i in available_ingredients.split(',')]
                
                # 查找包含这些食材的菜品
                all_recipes_list = get_all_recipes(driver)
                matching_recipes = []
                
                for recipe in all_recipes_list:
                    recipe_details = get_recipe_details(driver, recipe)
                    if recipe_details[1]:  # ingredients
                        recipe_ingredients = [ing['原材料'].lower() for ing in recipe_details[1]]
                        # 检查有多少匹配
                        matches = sum(1 for item in ingredients_list if any(item.lower() in ri for ri in recipe_ingredients))
                        if matches > 0:
                            matching_recipes.append({
                                '菜名': recipe,
                                '匹配食材数': matches,
                                '总食材数': len(recipe_ingredients),
                                '匹配度': f"{matches}/{len(recipe_ingredients)}"
                            })
                
                if matching_recipes:
                    # 按匹配度排序
                    matching_recipes.sort(key=lambda x: x['匹配食材数'], reverse=True)
                    st.markdown(f"**找到 {len(matching_recipes)} 道可以做的菜！**")
                    st.dataframe(pd.DataFrame(matching_recipes), use_container_width=True)
                else:
                    st.warning("没有找到匹配的菜品")
    
    # 页脚
    st.markdown("---")
    st.markdown("🍳 美食食谱知识图谱 - 基于 Neo4j & Streamlit")
else:
    st.error("❌ 无法连接到数据库，请检查连接配置")
