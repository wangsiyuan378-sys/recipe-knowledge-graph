
# 知识图谱课程论文 - PPT内容大纲

---

## 幻灯片1: 封面页

**标题:** 基于Neo4j的豆瓣电影知识图谱查询系统

**副标题:** 知识图谱课程论文项目

**作者:** [你的姓名]

**日期:** 2026年6月

**背景图:** 电影胶片/电影海报风格

---

## 幻灯片2: 目录页

1. 项目背景与意义
2. 技术栈介绍
3. 数据来源与处理
4. 知识图谱构建
5. Cypher查询示例
6. Streamlit界面展示
7. 功能演示
8. 效果对比分析
9. 结论与展望

---

## 幻灯片3: 项目背景与意义

**研究背景:**
- 知识图谱在影视领域的应用
- 豆瓣电影数据的丰富性
- 传统数据库查询的局限性

**项目目标:**
- 构建豆瓣电影知识图谱
- 实现可视化查询系统
- 对比知识图谱与纯大模型问答效果

**应用价值:**
- 电影推荐系统
- 影视数据分析
- 智能问答系统

---

## 幻灯片4: 技术栈介绍

| 层次 | 技术 | 说明 |
|------|------|------|
| 图数据库 | Neo4j Aura | 云端图数据库服务 |
| 前端框架 | Streamlit | 快速构建Web应用 |
| 数据格式 | CSV | 结构化数据导入 |
| 查询语言 | Cypher | Neo4j图查询语言 |
| 部署平台 | Streamlit Cloud | 免费社区部署 |

**架构图:**
```
用户界面 (Streamlit)
     ↓
   Neo4j Aura
     ↓
  知识图谱数据
```

---

## 幻灯片5: 数据来源

**数据来源:** OpenKG开放知识图谱
- 豆瓣电影知识图谱 (douban-movie-kg)
- 包含2.7万+节点，5万+关系

**数据集特点:**
- 包含电影基本信息（标题、评分、年份、类型）
- 包含人物信息（导演、演员）
- 包含人物与电影的关系

**数据预处理:**
- 数据清洗与去重
- 格式转换（JSON → CSV）
- 实体对齐

---

## 幻灯片6: 数据文件结构

**CSV文件清单:**

| 文件 | 内容 | 记录数 |
|------|------|--------|
| movie_nodes.csv | 电影节点 | 30条 |
| person_nodes.csv | 人物节点 | 71条 |
| movie_director_rels.csv | 导演关系 | 25条 |
| movie_actor_rels.csv | 演员关系 | 42条 |

**节点属性:**
- Movie: movie_id, title, rating, year, genre
- Person: person_id, name, label(导演/演员)

**关系类型:**
- DIRECTED: 导演关系
- ACTED_IN: 演员关系

---

## 幻灯片7: 知识图谱模型

**实体类型:**
- 🎬 Movie (电影)
- 👤 Person (人物)

**关系类型:**
- 🎥 DIRECTED (导演)
- 🎭 ACTED_IN (参演)

**示例三元组:**
```
(周星驰) -[:ACTED_IN]-> (大话西游之大圣娶亲)
(克里斯托弗·诺兰) -[:DIRECTED]-> (盗梦空间)
```

**图谱可视化示意图:**
```
        ┌─────────────────┐
        │   肖申克的救赎   │
        └────────┬────────┘
                 │ DIRECTED
        ┌────────▼────────┐
        │ 弗兰克·德拉邦特  │
        └─────────────────┘
                 │ ACTED_IN
        ┌────────▼────────┐
        │   蒂姆·罗宾斯    │
        └─────────────────┘
```

---

## 幻灯片8: 数据导入流程

**步骤1:** 注册Neo4j Aura免费账号
- 访问: https://neo4j.com/aura/
- 创建免费云实例（5GB容量）

**步骤2:** 准备CSV数据文件
- movie_nodes.csv
- person_nodes.csv  
- movie_director_rels.csv
- movie_actor_rels.csv

**步骤3:** 执行数据导入脚本
```python
python import_data.py
```

**步骤4:** 验证导入结果
```cypher
MATCH (m:Movie) RETURN COUNT(m) AS count
MATCH (p:Person) RETURN COUNT(p) AS count
```

---

## 幻灯片9: 10个Cypher查询示例（1-5）

| 编号 | 查询功能 | Cypher语句 |
|------|---------|-----------|
| 1 | 查询电影导演 | `MATCH (m)-[:DIRECTED]-(d) WHERE m.title CONTAINS '肖申克' RETURN m.title, d.name` |
| 2 | 查询演员作品 | `MATCH (p)-[:ACTED_IN]-(m) WHERE p.name CONTAINS '周星驰' RETURN p.name, m.title` |
| 3 | 高评分电影 | `MATCH (m) WHERE m.rating >= 9.0 RETURN m.title, m.rating ORDER BY m.rating DESC` |
| 4 | 按年份查询 | `MATCH (m {year: 1994}) RETURN m.title, m.rating` |
| 5 | 查询导演作品 | `MATCH (d)-[:DIRECTED]-(m) WHERE d.name CONTAINS '诺兰' RETURN d.name, m.title` |

---

## 幻灯片10: 10个Cypher查询示例（6-10）

| 编号 | 查询功能 | Cypher语句 |
|------|---------|-----------|
| 6 | 动画电影 | `MATCH (m) WHERE m.genre CONTAINS '动画' RETURN m.title, m.rating` |
| 7 | TOP10评分 | `MATCH (m) RETURN m.title, m.rating ORDER BY m.rating DESC LIMIT 10` |
| 8 | 电影演职人员 | `MATCH (m)<-[:DIRECTED]-(d) OPTIONAL MATCH (m)<-[:ACTED_IN]-(a) RETURN m.title, d.name, collect(a.name)` |
| 9 | 按类型查询 | `MATCH (m) WHERE m.genre CONTAINS '剧情' RETURN m.title, m.rating` |
| 10 | 实体搜索 | `MATCH (p)-[r]-(m) WHERE p.name CONTAINS '关键词' RETURN p.name, type(r), m.title` |

---

## 幻灯片11: Streamlit界面设计

**界面架构:**
```
┌─────────────────────────────────────┐
│         🎬 标题栏                   │
├─────────────────────────────────────┤
│  [统计卡片] 电影数 | 导演数 | 演员数 │
├─────────────────────────────────────┤
│  🔍 查询类型选择下拉框               │
├─────────────────────────────────────┤
│  [输入框] 搜索关键词                 │
│  [按钮] 查询                        │
├─────────────────────────────────────┤
│  📊 结果表格展示区                  │
├─────────────────────────────────────┤
│  📝 Cypher查询示例展示              │
└─────────────────────────────────────┘
```

**界面特点:**
- 简洁直观的点击式查询
- 实时数据展示
- 支持多种查询方式

---

## 幻灯片12: 查询功能演示（截图说明）

**查询1: 查询电影导演**
- 输入: "肖申克"
- 输出: 《肖申克的救赎》- 弗兰克·德拉邦特

**查询2: 查询演员作品**
- 输入: "周星驰"
- 输出: 《大话西游之大圣娶亲》等

**查询3: 高评分电影**
- 滑块选择: ≥9.0分
- 输出: 按评分降序排列的电影列表

**查询4: TOP10评分电影**
- 自动展示评分最高的10部电影

---

## 幻灯片13: 实体搜索功能

**搜索框设计:**
- 支持输入演员名或电影名
- 自动匹配人物和电影
- 展示相关关系

**搜索结果展示:**
```
👤 人物匹配:
┌────────────┬──────┬──────────────┬──────┐
│    名称    │ 类型 │  相关电影    │ 关系 │
├────────────┼──────┼──────────────┼──────┤
│ 莱昂纳多   │ 演员 │ 泰坦尼克号   │ 演员 │
│ 莱昂纳多   │ 演员 │ 盗梦空间     │ 演员 │
└────────────┴──────┴──────────────┴──────┘

🎬 电影匹配:
┌────────────┬──────┬──────┬──────┐
│    名称    │ 类型 │ 评分 │ 年份 │
├────────────┼──────┼──────┼──────┤
│ 盗梦空间   │ 电影 │ 9.3  │ 2010 │
└────────────┴──────┴──────┴──────┘
```

---

## 幻灯片14: 推理规则实现（加分项）

**推理规则示例:**
```cypher
// 如果导演的电影评分≥9.0，则标记为成功导演
MATCH (d:Person)-[:DIRECTED]->(m:Movie)
WHERE m.rating >= 9.0
WITH d, count(m) AS high_rated_count
WHERE high_rated_count >= 2
SET d.is_successful = true
RETURN d.name, high_rated_count
```

**推理结果:**
| 导演 | 高分作品数 |
|------|-----------|
| 克里斯托弗·诺兰 | 3 |
| 宫崎骏 | 2 |
| 陈凯歌 | 1 |

**推理价值:**
- 发现隐藏知识
- 提供智能分析
- 辅助决策支持

---

## 幻灯片15: 效果对比分析（加分项）

**对比方法:**
- 选取5个代表性问题
- 分别用纯大模型和知识图谱回答
- 对比回答准确性和可追溯性

**对比结果:**

| 问题 | 纯大模型回答 | 知识图谱回答 | 准确性 |
|------|------------|------------|--------|
| 《流浪地球》导演 | 可能回答错误 | 准确返回郭帆 | ✅ KG |
| 周星驰演过的电影 | 可能遗漏或错误 | 准确列出 | ✅ KG |
| 评分最高的电影 | 可能正确 | 准确可验证 | ✅ KG |
| 1994年上映的电影 | 可能不全 | 完整准确 | ✅ KG |
| 诺兰导演的电影 | 可能正确 | 完整准确 | ✅ KG |

---

## 幻灯片16: 纯大模型 vs 知识图谱

**对比维度:**

| 维度 | 纯大模型 | 知识图谱 |
|------|---------|---------|
| 准确性 | 可能幻觉 | 准确可验证 |
| 可追溯性 | 不可追溯 | 可追溯到数据源 |
| 更新频率 | 依赖训练数据 | 实时更新 |
| 复杂关系 | 有限 | 擅长多跳查询 |
| 数据规模 | 固定 | 可扩展 |
| 推理能力 | 强 | 可定制规则 |

**结论:**
- 知识图谱在事实查询方面更准确可靠
- 大模型在自然语言理解和生成方面更强
- 两者可以互补使用

---

## 幻灯片17: 系统部署

**部署步骤:**

1. **代码托管:** 将项目推送到GitHub
2. **连接Streamlit Cloud:** 登录https://streamlit.io/cloud
3. **配置环境变量:**
   - NEO4J_URI
   - NEO4J_USERNAME  
   - NEO4J_PASSWORD
4. **一键部署:** 点击Deploy按钮
5. **获取公开链接:** 生成可访问的URL

**部署注意事项:**
- Neo4j Aura免费实例14天后会休眠
- 需要定期唤醒或升级付费版
- Streamlit社区云有资源限制

---

## 幻灯片18: 项目总结

**完成的工作:**
1. ✅ 注册Neo4j Aura云实例
2. ✅ 下载并预处理OpenKG数据集
3. ✅ 将CSV数据导入Neo4j
4. ✅ 设计10个Cypher查询语句
5. ✅ 创建Streamlit可视化界面
6. ✅ 实现点击式查询功能
7. ✅ 添加实体搜索框
8. ✅ 部署到本地服务器

**成果:**
- 一个可运行的知识图谱查询系统
- 30部电影和71个人物的知识图谱
- 支持多种查询方式的可视化界面

---

## 幻灯片19: 未来展望

**改进方向:**
1. **扩展数据集:** 添加更多电影和人物数据
2. **增加关系类型:** 编剧、制片、获奖等关系
3. **优化界面:** 添加更丰富的可视化展示
4. **增强推理:** 添加更多推理规则
5. **融合大模型:** 将知识图谱与大模型结合

**应用扩展:**
- 电影推荐系统
- 影视数据分析平台
- 智能问答机器人
- 知识图谱可视化展示

---

## 幻灯片20: 致谢与参考文献

**致谢:**
- 感谢OpenKG提供开放数据集
- 感谢Neo4j提供免费云服务
- 感谢Streamlit提供便捷的部署平台

**参考文献:**
1. OpenKG知识图谱开放平台. http://www.openkg.cn
2. Neo4j图数据库官方文档. https://neo4j.com/docs
3. Streamlit官方文档. https://docs.streamlit.io

**联系方式:**
- [你的邮箱]
- [项目GitHub地址]

---

## 附录: 关键代码片段

**数据导入脚本:**
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(uri, auth=(user, password))

def load_movies(filepath):
    with driver.session() as session:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                session.run("""
                    MERGE (m:Movie {movie_id: $movie_id})
                    SET m.title = $title, m.rating = toFloat($rating)
                """, row)
```

**Streamlit应用:**
```python
import streamlit as st
from neo4j import GraphDatabase

def run_query(query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return [dict(record) for record in result]

st.title("🎬 豆瓣电影知识图谱查询系统")
```
