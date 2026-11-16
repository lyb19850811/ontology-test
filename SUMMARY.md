# 本体构建与推理验证 — 项目总结

> 一句话：从「领域知识文档」出发，用 `owlready2` + HermiT 推理器构建了一个小型医疗 OWL 本体，并程序化验证了 4 类推理能力（继承 / 定义类归属 / 逆属性 / 不一致检测）。

---

## 1. 做了什么

目标链路：**知识文档 → 工具构建本体 → 验证推理能力**，外加前置的「本体」概念深度研究。

最终成果（4 个交付物）：

| 文件 | 作用 |
|---|---|
| `ontology-research.md` | 前置研究：本体的定义/组成/工具/AI 结合 |
| `medical-knowledge.md` | 领域知识文档（自然语言概念化，本体的依据） |
| `build_medical_ontology.py` | 构建本体 + 推理验证脚本（可复现） |
| `medical.owl` | 生成的 OWL 本体（RDF/XML） |

本体的核心内容（医疗领域示例）：

```
Disease ── InfectiousDisease ── BacterialDisease（细菌病）
                             └─ ViralDisease（病毒病）   〔两者互斥〕
Drug    ── Antibiotic（抗生素，定义类）
Symptom
```

- 关系：`hasSymptom`（疾病→症状）、`treats`（药物→疾病）、`treatedBy`（`treats` 的逆）
- 公理：
  - `Antibiotic ≡ Drug ⊓ ∃treats.BacterialDisease`（**定义类**：至少治一种细菌病）
  - `Antibiotic ⊑ ∀treats.BacterialDisease`（**约束**：只治细菌病）

---

## 2. 怎么做的（方法）

### 2.1 流程

```
① 领域知识文档（自然语言事实）
        ↓  形式化
② OWL 本体（owlready2 编程构建）
        ↓  HermiT 推理
③ 验证 4 类推理结论
        ↓
④ 输出 owl + 结论
```

### 2.2 方法论依据

- **本体 = 共享概念化的形式化、显式规格说明**（Gruber/Studer），所以先写知识文档（概念化），再形式化成 OWL。
- **选 OWL 而非普通 RDF/JSON**：OWL 基于描述逻辑，是可判定、可推理的标准语言，"验证推理"必须靠它。
- **用"定义类"而非直接枚举**：`Antibiotic` 不由手写列出，而由语义条件推导——这样"阿莫西林是不是抗生素"是推理结论，能真正证明推理器在工作。
- **`∃`/`∀` 分工**（关键，见 §6 踩坑记录）：
  - `∃`（some）用于**推断归属**——正面事实即可推出；
  - `∀`（only）用于**一致性校验**——只能被"已知反例"违反。

---

## 3. 用了什么工具

| 工具 | 版本/形态 | 用途 | 为什么选它 |
|---|---|---|---|
| **Python** | 3.15（Homebrew） | 脚本语言 | 脚本化、可复现 |
| **owlready2** | Python 库（`.venv` 内安装） | 构建 OWL、调用推理器 | Python 原生 OWL 库，内置 HermiT/Pellet 推理接口 |
| **HermiT** | Java（owlready2 内置 jar） | OWL 2 DL 推理 | 完整描述逻辑推理器，牛津出品 |
| **Java** | OpenJDK 17（Homebrew） | HermiT 运行时 | HermiT 是 JVM 程序 |
| **venv** | Python 虚拟环境 | 隔离依赖 | 规避 macOS PEP 668 系统 Python 保护 |

> 前置研究阶段还调研了（未用于本次实操）：Protégé/WebProtégé（编辑器）、OWLAPI、RDFLib、ROBOT、OntoGPT 等，详见 `ontology-research.md` 第 7 节。本项目选 owlready2 + HermiT 是为了**脚本化、可验证**，而非手动点编辑器。

---

## 4. 有哪些功能

### 4.1 本体（`medical.owl`）具备的能力

- **类层级建模**：疾病 → 传染病 → 细菌/病毒病；药物 → 抗生素。
- **关系建模**：对象属性 + 逆属性（`treats` ↔ `treatedBy`）。
- **公理表达**：互斥（`AllDisjoint`）、定义类（`equivalent_to` + `∃`）、约束（`∀`）。
- **可推理**：由 HermiT 自动推导新结论、检测矛盾。

### 4.2 脚本（`build_medical_ontology.py`）实现的功能

| 功能 | 说明 |
|---|---|
| 构建本体 | 用 Python 类语法程序化定义 TBox + 实例 |
| 推理 | 调用 HermiT（`sync_reasoner`） |
| 验证① 继承 | `isinstance(肺炎, 传染病)` → True |
| 验证② 定义类归属 | 阿莫西林（只断言"药物"）→ 被推断为**抗生素** |
| 验证③ 逆属性 | `肺炎.treatedBy` → 推断出阿莫西林 |
| 验证④ 一致性 | 本体一致；加入矛盾事实后捕获 `OwlReadyInconsistentOntologyError` |
| 持久化 | 保存为 `medical.owl`（RDF/XML） |

关键证据（脚本实际输出）：

```
* Owlready * Reparenting medical.amoxicillin: {medical.Drug} => {medical.Antibiotic}
[1] 继承：肺炎 ∈ 传染病/疾病 → ✓ 成立
[2] 定义类：阿莫西林 ∈ 抗生素 → ✓ 成立
[3] 逆属性：肺炎.treatedBy = ['amoxicillin'] → ✓ 成立
[4] 一致性：不一致的类 = 无 → ✓ 一致
[第 2 轮] 加入"阿莫西林治疗流感" → ✅ 推理器检测到不一致
```

`Reparenting ... => {Antibiotic}` 这行证明：阿莫西林的抗生素身份**是推理器算出来的，不是手写的**。

---

## 5. 用户怎么使用

### 5.1 环境准备（一次性）

```bash
# 1. 需要 Java（HermiT 依赖）
java -version          # 需 8+，本项目用 17

# 2. 创建虚拟环境并安装 owlready2
python3 -m venv .venv
.venv/bin/pip install owlready2
```

### 5.2 复现推理验证

```bash
.venv/bin/python build_medical_ontology.py
```

脚本会自动：构建本体 → 跑 HermiT → 打印 4 类推理结果 → 加入矛盾事实 → 验证不一致检测。

### 5.3 查看生成的本体

```bash
# 看本体文件内容（RDF/XML 或转 Turtle）
cat medical.owl
# 或用 Protégé / WebProtégé 打开 medical.owl 可视化查看
```

### 5.4 扩展成自己的本体

改 `build_medical_ontology.py` 里的 `build_ontology()` 即可，套路固定：

1. **加类**：`class 你的类(父类): pass`
2. **加关系**：`class 你的属性(ObjectProperty): domain/range`
3. **加公理**：`AllDisjoint([...])`、`X.equivalent_to = [...]`、`X.is_a.append(限制)`
4. **加实例**：`某类("名字")` + `实例.属性.append(值)`
5. **加验证**：`isinstance(实例, 类)` 断言 + `sync_reasoner()` 跑推理

⚠️ 注意（本项目踩过的坑）：**"推断归属"用 `∃`，不要用 `∀`**——开放世界假设下，`∀` 推不出"只"。

---

## 6. 踩坑记录（开放世界假设的实战教训）

最初把定义类写成 `Antibiotic ≡ Drug ⊓ ∀treats.BacterialDisease`（"只治细菌病"），结果推理器**不**把阿莫西林判为抗生素。原因是开放世界假设（OWA）：

- `∀`（only）无法靠"没看到反例"确认归属——"阿莫西林只治肺炎"不代表它不治别的未知病；
- `∀` 只能被**已知反例**违反，因此只适合做一致性约束。

修正后（已写入 `medical-knowledge.md` §3 并注明理由）：

```
Antibiotic ≡ Drug ⊓ ∃treats.BacterialDisease   # ∃：推断归属
Antibiotic ⊑ ∀treats.BacterialDisease          # ∀：一致性校验
```

另记录一个工具边界：owlready2 的 HermiT 集成对个体级类型实现只输出**直接类型**，`isinstance()` 的继承判断靠 owlready2 在 Python 层做类层级传递闭包；但**定义类归属（`∃`）确实由 HermiT 真实实现**，非取巧。若需更强的个体实现保证，可改用 `sync_reasoner_pellet`（Pellet 的 `realize` 命令）。

---

## 7. 文件清单

```
ontology-research.md              # 本体概念/工具/AI 结合 深度研究
ontology-vs-knowledge-graph.md    # 本体与知识图谱的关系 深度研究
medical-knowledge.md              # 领域知识文档（本体的自然语言依据）
build_medical_ontology.py         # 构建 + 推理验证脚本
medical.owl                       # 生成的 OWL 本体
.venv/                            # Python 虚拟环境（owlready2）
```
