# 豆瓣电影知识图谱查询系统

基于 Neo4j Aura + Streamlit 构建的知识图谱课程论文项目

## 项目结构

```
knp/
├── data/                           # 数据文件
│   ├── movies.csv                  # 原始电影数据
│   ├── movie_nodes.csv             # Neo4j 电影节点导入文件
│   ├── person_nodes.csv           # Neo4j 人物节点导入文件
│   ├── movie_director_rels.csv    # 导演关系导入文件
│   └── movie_actor_rels.csv       # 演员关系导入文件
├── queries/                        # Cypher 查询语句
│   └── cypher_queries.cql         # 10个查询示例
├── app/                            # Streamlit 应用
│   ├── app.py                     # 主应用
│   ├── import_data.py             # 数据导入脚本
│   └── requirements.txt           # Python 依赖
└── images/                         # 系统截图
```

## 快速开始

### 1. 数据导入

#### 方式一: 使用导入脚本 (推荐)

```bash
cd app
pip install -r requirements.txt
python import_data.py
```

#### 方式二: Neo4j Browser 导入

1. 登录 Neo4j Aura 控制台: https://console.neo4j.io
2. 打开 Neo4j Browser
3. 执行以下命令导入数据:

```cypher
// 导入电影节点
LOAD CSV WITH HEADERS FROM 'file:///movie_nodes.csv' AS row
MERGE (m:Movie {movie_id: row.movie_id})
SET m.title = row.title,
    m.rating = toFloat(row.rating),
    m.year = totoInteger(row.year),
    m.genre = row.genre;

// 导入人物节点
LOAD CSV WITH HEADERS FROM 'file:///person_nodes.csv' AS row
MERGE (p:Person {person_id: row.person_id})
SET p.name = row.name, p.label = row.label;

// 导入导演关系
LOAD CSV WITH HEADERS FROM 'file:///movie_director_rels.csv' AS row
MATCH (d:Person {person_id: row.start_id})
MATCH (m:Movie {movie_id: row.end_id})
MERGE (d)-[:DIRECTED]->(m);

// 导入演员关系
LOAD CSV WITH HEADERS FROM 'file:///movie_actor_rels.csv' AS row
MATCH (a:Person {person_id: row.start_id})
MATCH (m:Movie {movie_id: row.end_id})
MERGE (a)-[:ACTED_IN]->(m);
```

### 2. 启动 Streamlit 应用

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

### 3. 部署到 Streamlit Community Cloud

1. 将代码推送到 GitHub
2. 访问 https://streamlit.io/cloud
3. 连接 GitHub 仓库
4. 设置环境变量:
   - `NEO4J_URI`: neo4j+s://xxxx.databases.neo4j.io
   - `NEO4J_USERNAME`: xxxx
   - `NEO4J_PASSWORD`: xxxx
5. 点击 Deploy

## 10个 Cypher 查询示例

| 编号 | 查询功能 | Cypher 语句 |
|------|---------|-------------|
| 1 | 查询电影导演 | `MATCH (m:Movie)-[:DIRECTED]-(d:Person) WHERE m.title CONTAINS '电影名' RETURN m.title, d.name` |
| 2 | 查询演员参演电影 | `MATCH (p:Person)-[:ACTED_IN]-(m:Movie) WHERE p.name CONTAINS '演员名' RETURN m.title, m.rating` |
| 3 | 高评分电影 | `MATCH (m:Movie) WHERE m.rating >= 9.0 RETURN m.title, m.rating ORDER BY m.rating DESC` |
| 4 | 按年份查询 | `MATCH (m:Movie {year: 1994}) RETURN m.title, m.rating` |
| 5 | 查询导演作品 | `MATCH (d:Person)-[:DIRECTED]-(m:Movie) WHERE d.name CONTAINS '导演名' RETURN m.title` |
| 6 | 动画电影 | `MATCH (m:Movie) WHERE m.genre CONTAINS '动画' RETURN m.title, m.rating` |
| 7 | TOP10评分 | `MATCH (m:Movie) RETURN m.title, m.rating ORDER BY m.rating DESC LIMIT 10` |
| 8 | 电影演职人员 | `MATCH (m:Movie)<-[:DIRECTED]-(d) OPTIONAL MATCH (m)<-[:ACTED_IN]-(a) WHERE m.title CONTAINS '电影名' RETURN m.title, d.name, collect(a.name)` |
| 9 | 按类型查询 | `MATCH (m:Movie) WHERE m.genre CONTAINS '类型' RETURN m.title, m.rating` |
| 10 | 实体搜索 | `MATCH (p:Person)-[r]-(m:Movie) WHERE p.name CONTAINS '关键词' RETURN p.name, type(r), m.title` |

## 技术栈

- **图数据库**: Neo4j Aura (免费版 5GB)
- **后端框架**: Python + Neo4j Driver
- **前端框架**: Streamlit
- **数据来源**: OpenKG 豆瓣电影知识图谱

## 课程论文加分项

### 可选任务1: 推理规则
```cypher
// 如果 A 导演了 B，B 获得了高评分，则 A 是成功的导演
MATCH (d:Person)-[:DIRECTED]->(m:Movie)
WHERE m.rating >= 9.0
RETURN d.name AS 导演, count(m) AS 高分作品数
ORDER BY 高分作品数 DESC
```

### 可选任务2: 实体搜索框
系统已实现 - 见查询10

### 可选任务3: 对比分析
建议在论文中对比:
- 纯大模型问答 (如 ChatGPT)
- 知识图谱问答 (本系统)

展示差异:
| 问题类型 | 大模型回答 | 知识图谱回答 |
|---------|-----------|-------------|
| 事实查询 | 可能 hallucinate | 准确可追溯 |
| 复杂关系 | 笼统 | 精确多跳 |
| 实时性 | 依赖训练数据 | 可更新 |

## Neo4j Aura 连接信息

```
NEO4J_URI=neo4j+s://425d541a.databases.neo4j.io
NEO4J_USERNAME=425d541a
NEO4J_PASSWORD=iBtUIhRNaWygge7ZLIV8NtiUiMdn-vGh_Gt5S4rIwMk
NEO4J_DATABASE=425d541a
```

## 注意事项

1. Neo4j Aura 免费实例会在 14 天后休眠，唤醒需要访问控制台
2. 部署到 Streamlit Cloud 时需要设置环境变量
3. 建议使用 Chrome 浏览器访问 Streamlit 应用
