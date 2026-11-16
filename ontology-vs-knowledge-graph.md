# 本体与知识图谱的关系 — 深度研究报告

> 生成日期：2026-11-16
> 范围：二者的严格定义与谱系、形式化关系（TBox/ABox）、多维对比、相互依赖机制、语义连续谱、技术栈对应、实践形态与常见误区
> 关联文档：`ontology-research.md`（本体专题）、`medical-knowledge.md`（领域知识）

---

## 目录

1. [为什么这个问题值得厘清](#1-为什么这个问题值得厘清)
2. [各自的严格定义与谱系](#2-各自的严格定义与谱系)
3. [核心关系：一个知识库的两半（TBox / ABox）](#3-核心关系一个知识库的两半tbox--abox)
4. [多维对比](#4-多维对比)
5. [二者如何相互依赖、相互促进](#5-二者如何相互依赖相互促进)
6. [语义强度的连续谱](#6-语义强度的连续谱)
7. [技术栈与标准的对应](#7-技术栈与标准的对应)
8. [实践中的三种典型形态](#8-实践中的三种典型形态)
9. [常见误区澄清](#9-常见误区澄清)
10. [与本项目的关系](#10-与本项目的关系)
11. [参考来源](#11-参考来源)

---

## 1. 为什么这个问题值得厘清

"本体"和"知识图谱"是知识工程领域被**混用最严重**的两个词。根源在于：

- 二者常被当同义词互换（"我们建了个知识图谱" vs "我们建了个本体"）；
- 工业界和学术界的定义不一致（工业界偏"图数据库里的数据"，学术界偏"可推理的知识库"）；
- 语义网学派把本体当作知识图谱的组成部分，而图数据库学派几乎不提本体。

但它们在**层次、逻辑性质、起源、形式化程度**上都有明确差异。不厘清会导致一个实际后果：**建错了东西**——想要可推理、可互操作的语义系统，却只搭了一个无 schema 的属性图；或反之，为一个只需图遍历的应用投入了昂贵的本体建模。

> 一句话结论：**本体是"模式/术语层"（定义有哪些类型与规则），知识图谱是"数据/实例层"（记录具体实体怎么连接）**。二者共同构成一个知识库的两个半区，对应描述逻辑里经典的 TBox（本体）与 ABox（实例图）之分。

---

## 2. 各自的严格定义与谱系

### 2.1 本体（Ontology）：从哲学到语义网

词源上，"Ontology" 来自希腊语 *ὄντος*（ontos，存在者）+ *λόγος*（logos，学说），本是研究"存在本身、有哪些范畴"的形而上学分支。计算机科学在 1990 年代借用了这个词。

定义经过三次精化（这是理解本体的关键）：

| 提出者 | 年份 | 定义 |
|---|---|---|
| Gruber | 1993 | "an **explicit** specification of a **conceptualization**"（对概念化的显式规格说明）<sup>[1]</sup> |
| Borst | 1997 | "a **formal** specification of a **shared** conceptualization"（对共享概念化的形式化规格说明）<sup>[2]</sup> |
| Studer 等 | 1998 | **"a formal, explicit specification of a shared conceptualization"**（共享概念化的形式化、显式规格说明）——把前两者合并，成为最广为引用的标准版<sup>[3]</sup> |

四个关键词的含义：**formal**（机器可读可推理，非自然语言）、**explicit**（概念/约束/公理被显式写出）、**shared**（被共同体一致认可）、**conceptualization**（对领域世界的抽象模型）。

在语义网技术栈中，本体由 **RDFS / OWL（基于描述逻辑 DL）** 书写，内容包括 **类（class）、属性（property）、公理（axiom）、约束（constraint）**。它是**内涵的（intensional）**——讲的是"种类"和"规则"，不涉及具体个体。例如：

```
Movie ⊑ CreativeWork                  (类与层次)
directorOf ⊑ creatorOf                (属性与层次)
Movie ⊑ ∀ director.Person             (公理/约束)
```

### 2.2 知识图谱（Knowledge Graph）：从工业界到学术界

"knowledge graph" 一词最早可追溯到 1972 年（Schneider, 1973）<sup>[4]</sup>，但**现代含义**始于 Google 2012 年发布 Knowledge Graph——其理念 "**things, not strings**"（把检索从"字符串匹配"升级为"对事物的理解"）<sup>[5]</sup>。此后 Facebook、LinkedIn、Microsoft、Airbnb、Amazon、Uber 等相继跟进<sup>[4]</sup>。

目前最权威的定义来自 Hogan 等人 2021 年发表于 **ACM Computing Surveys** 的综述 *Knowledge Graphs*<sup>[4]</sup>：

> "知识图谱是**旨在积累并传递现实世界知识的数据图**，其节点代表所关注的实体，边代表实体间的关系。"
> (*a graph of data intended to accumulate and convey knowledge of the real world, whose nodes represent entities of interest and whose edges represent relations between these entities*)

它是**外延的（extensional）**——记录的是具体实例与事实，例如：

```
(Santiago, capitalOf, Chile)
(Chile, locatedIn, SouthAmerica)
```

该综述同时明确区分了"数据图（data graph）"与承载它的**模式（schema）/本体/规则**，指出：如果要积累"量化陈述"（如"所有首都都是城市"）这类**通用知识**，就必须借助本体或规则这类更富表达力的形式；简单陈述（如"Santiago 是智利首都"）则可直接作为图中的边累积<sup>[4]</sup>。

---

## 3. 核心关系：一个知识库的两半（TBox / ABox）

这是理解二者关系的关键。在描述逻辑知识库（Description Logic Knowledge Base）中，知识被明确分成几个"盒子"<sup>[6]</sup>：

- **TBox（Terminological Box，术语盒）**：关于概念与公理的陈述，如 `Movie ⊑ CreativeWork`。
- **ABox（Assertional Box，断言盒）**：关于个体的断言，如 `Inception : Movie`。
- **RBox（Role Box，角色盒）**：关于属性（角色）的公理，如 `directorOf ⊑ creatorOf`，通常并入模式层讨论。

形式化地，一个知识库 $\mathcal{K} = \langle \mathcal{T}, \mathcal{R}, \mathcal{A} \rangle$，其中 $\mathcal{T}$（TBox）与 $\mathcal{R}$（RBox）构成**术语层/模式层**，$\mathcal{A}$（ABox）构成**实例层/数据层**。

于是对应关系一目了然：

```
             知识库 / 知识图谱  (Knowledge Graph / Knowledge Base)
   ┌─────────────────────────────────────────────────────────────┐
   │                                                             │
   │   模式层 (Schema)        本体  Ontology                      │
   │   ──────────────        ────  TBox + RBox                   │
   │   类 · 属性 · 公理 · 约束 · 规则                              │
   │                          ↑ 定义词汇与语义 (schema/vocabulary) │
   │                          │                                  │
   │   数据层 (Data)          实例图  Data Graph                  │
   │   ──────────────        ────  ABox                           │
   │   实体 · 关系 · 事实 (三元组/边)                              │
   │                          ↓ 实例化 / 填充 (populates)          │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
```

**严格说：本体 ≈ TBox(+RBox)，知识图谱的"数据图"部分 ≈ ABox。** 一个完整、可推理的知识图谱 = **数据图 + 本体 + 推理规则**。

本体与数据图之间有三类作用：

1. **定义（向下）**：本体用类/属性/公理给数据图的节点和边赋予机器可读的语义。
2. **填充（向上）**：数据图用真实实体把本体的类实例化。
3. **推理（横向）**：本体公理在数据图上触发**蕴含（entailment）**，派生图中原本不含的新事实——这是"知识"区别于"数据"的关键能力。

---

## 4. 多维对比

| 维度 | 本体 (Ontology) | 知识图谱 (Knowledge Graph) |
| --- | --- | --- |
| **所处层次** | 术语/模式层（TBox/RBox） | 实例/数据层（ABox） |
| **逻辑性质** | 内涵（intensional），关于"种类" | 外延（extensional），关于"个体" |
| **起源谱系** | 哲学 → AI 知识表示 → 语义网（Gruber 1993） | 工业界 → Web 搜索/数据集成（Google 2012） |
| **形式化程度** | 高：描述逻辑、OWL 2，有严格语义与推理算法 | 常无形式语义；可为 RDF 图或属性图（LPG） |
| **抽象 vs 具体** | 先定"该有什么"，模式先行 | 可先塞数据再补模式（schema-last） |
| **核心目标** | 共享意义、互操作、可推理、消歧 | 集成、查询、图分析、图嵌入/机器学习 |
| **表达单元** | 类、属性、公理、约束 | 三元组 (s, p, o) 或节点–边 |
| **封闭/开放世界** | 开放世界假设（OWA）：未言明 ≠ 假 | 取决于模型；图数据库常按封闭世界处理 |
| **主要标准** | OWL 2、RDFS、SHACL | RDF/SPARQL 或 LPG/Cypher/GQL |

---

## 5. 二者如何相互依赖、相互促进

二者不是静态的"schema↔data"关系，而是**双向、协同演化**的。

### 5.1 本体 → 知识图谱：注入"知识"语义

没有本体的图只是一堆带标签的节点和边——严格说它只能叫**图数据库/数据图**，谈不上"知识"。本体通过三类作用把"数据"变成"知识"：

1. **赋予共享意义**：`city`、`person` 在不同团队间不再歧义，支撑跨系统互操作与术语消歧。
2. **约束数据合法性**：用 SHACL shapes 或 DL 公理校验实例是否符合模式（如"电影的导演必须是 Person"）。
3. **推理（entailment）派生新事实**：从 `Santiago 是 capital` 与公理 `capital ⊑ city`，自动推出 `Santiago 是 city`——这是图本身不含、却可逻辑蕴含的知识。

### 5.2 知识图谱 → 本体：为演化提供证据

1. **本体学习（Ontology Learning）**：从大量实例三元组中归纳出类层次与属性约束（自底向上提炼模式）<sup>[4]</sup>。
2. **本体工程验证**：真实数据分布可暴露本体公理的过度约束或遗漏，驱动版本迭代。
3. **协同演化（co-evolution）**：数据涨出新类型 → 模式修订 → 数据再对齐，二者形成持续循环。

---

## 6. 语义强度的连续谱

本体与知识图谱不是非黑即白，而是落在一个**语义强度从弱到强的连续谱**上<sup>[7]</sup>：

```
受控词表 (Controlled Vocabulary)   —— 术语标准化、无歧义命名
  → 分类法 (Taxonomy)             —— + 层级 is-a
    → 主题词表 (Thesaurus)        —— + 同义、相关关系
      → 本体 (Ontology)           —— + 形式化公理 + 推理
        → 知识图谱 (KG)           —— + 实例数据 + (可选)推理/图分析
```

要点：**知识图谱是连续谱上语义最丰富、覆盖最全的一档**，因为它既含模式（可含本体），又含海量实例，还叠加了图分析/嵌入等数据能力。而本体本身不承载实例数据。

---

## 7. 技术栈与标准的对应

| 层 | 语义网路线（W3C） | 属性图路线（LPG） |
| --- | --- | --- |
| **数据模型** | RDF（三元组：subject–predicate–object） | 属性图（节点+边+属性） |
| **模式/本体层** | RDFS → OWL 2（推理）、SHACL（校验） | 通常无形式化 schema（或由厂商提供约束） |
| **查询语言** | SPARQL | Cypher / GQL（ISO 标准化中） |
| **推理** | 描述逻辑推理器（HermiT、Pellet、ELK） | 一般不提供逻辑推理 |
| **典型系统** | Wikidata、DBpedia、YAGO（RDF 化） | Neo4j、JanusGraph、Amazon Neptune |

关键分歧点：**语义网路线把本体作为知识图谱的一等公民**（RDFS/OWL 内建），而**属性图路线对"本体"没有原生概念**，schema 是松散、可推迟的。这正是两派定义冲突的工程根源<sup>[4][8]</sup>。

---

## 8. 实践中的三种典型形态

企业在落地时，本体与知识图谱的结合强度大致分三档<sup>[4][8][9]</sup>：

| 形态 | 模式层 | 典型技术 | 适用场景 | 推理/互操作能力 |
| --- | --- | --- | --- | --- |
| **无本体（schema-last）** | 无/极松散 | 属性图（Neo4j 等） | 快速图遍历、路径分析、推荐 | 弱 |
| **轻本体** | RDFS / schema.org / 简单词表 | RDF + 轻量 schema | 数据集成、发布、链接开放数据 | 中 |
| **强本体** | OWL 2 DL + 推理器 + SHACL 校验 | RDF/OWL + 推理（如本项目） | 生命科学、医疗、语义互操作、合规 | 强 |

> 选择原则：**需要多少"可推理、可互操作的语义"，就投入多少本体建模**。图遍历应用不必强上 OWL；跨组织语义对齐则必须要有本体层。

---

## 9. 常见误区澄清

1. **"知识图谱 = 本体"** ❌ —— 一个是模式、一个是数据，是分层/互补关系，不是同义词。
2. **"知识图谱必须有本体"** ❌ —— 大量工业知识图谱（尤其属性图路线）没有形式化本体，只有松散 schema 甚至无 schema。此时它仍是"图"，但**推理能力与互操作保证较弱**。
3. **"本体 = 数据库 schema"** ⚠️ —— 本体语义更强：数据库 schema 只约束结构（字段类型）并采用**封闭世界假设（CWA，表中没有即为假）**；OWL 本体默认**开放世界假设（OWA，未言明只是未知）**，且公理承载可判定推理。CWA/OWA 的差异是二者推理行为不同的根源<sup>[4]</sup>。
4. **"有了 RDF 就是有本体了"** ⚠️ —— RDF 只是数据模型（三元组），不等于本体；本体需要 RDFS/OWL 层的公理表达力<sup>[10]</sup>。

---

## 10. 与本项目的关系

本项目（`ontology-test`）目前处于**"强本体、尚无大规模实例层"**的状态，恰好可以用本文框架定位：

| 本项目交付物 | 在 TBox/ABox 框架中的位置 |
| --- | --- |
| `medical-knowledge.md` | 概念化（自然语言，本体的前置依据） |
| `build_medical_ontology.py` + `medical.owl` | **TBox（本体）**：类层级、`treats`/`hasSymptom` 属性、定义类/约束公理 |
| 脚本中的少数个体（阿莫西林、肺炎等） | **ABox（实例层）的雏形**：少数测试实例 |

**若要从"本体"扩展成完整的"知识图谱"**，需要补上的正是 ABox 这一半：

1. 大规模实例化：把真实疾病/药物/症状数据以三元组形式灌入；
2. 以 `medical.owl` 作为 schema 层，用 SPARQL 查询实例，用 HermiT 做全局推理（而非当前的个体级验证）；
3. 用 SHACL 对实例数据做质量校验（模式层的落地约束）。

这印证了本文的核心结论：**本体回答了"这个领域可以有什么"，知识图谱进一步回答了"这个领域现在具体有什么"**——本项目已完成后半句话的"规则"，实例数据的规模化填充即是通往知识图谱的下一步。

---

## 11. 参考来源

1. Gruber, T. R. (1993). *A translation approach to portable ontology specifications*. Knowledge Acquisition, 5(2). https://tomgruber.org/writing/ontology-definition-2007.htm
2. Borst, W. N. (1997). *Construction of Engineering Ontologies for Knowledge Sharing and Reuse*. PhD Thesis, University of Twente.
3. Studer, R., Benjamins, V. R., Fensel, D. (1998). *Knowledge engineering: Principles and methods*. Data & Knowledge Engineering, 25(1–2).
4. Hogan, A., et al. (2021). *Knowledge Graphs*. ACM Computing Surveys, 54(4). doi:10.1145/3447772 · arXiv:2003.02320
5. Singhal, A. (2012). *Introducing the Knowledge Graph: things, not strings*. Google Official Blog. https://blog.google/products/search/introducing-knowledge-graph-things-not/
6. Baader, F., Calvanese, D., McGuinness, D. L., Nardi, D., Patel-Schneider, P. F. (2003). *The Description Logic Handbook*. Cambridge University Press.（TBox/ABox/RBox 术语出处）
7. Neo4j. *Taxonomy vs. ontology vs. knowledge graph: What's the difference?* https://neo4j.com/blog/knowledge-graph/taxonomy-vs-ontology-vs-knowledge-graph/
8. Graphwise (Ontotext). *What Is a Knowledge Graph?* https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/
9. Guarino, N., Oberle, D., Staab, S. (2009). *What is an Ontology?* In: Handbook on Ontologies. Springer. https://iaoa.org/isc2012/docs/Guarino2009_What_is_an_Ontology.pdf
10. W3C. *RDF 1.1 / RDF Schema 1.1 / OWL 2 Web Ontology Language*. https://www.w3.org/TR/owl2-overview/
