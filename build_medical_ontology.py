#!/usr/bin/env python3
"""构建小型医疗本体，并用 HermiT 推理器验证推理能力。

对应知识文档：medical-knowledge.md
工具：owlready2（Python）+ HermiT（Java, OWL 2 DL 推理器）

运行：.venv/bin/python build_medical_ontology.py
"""
from owlready2 import (
    get_ontology,
    Thing,
    ObjectProperty,
    AllDisjoint,
    sync_reasoner,
    default_world,
    OwlReadyInconsistentOntologyError,
)

BASE = "http://example.org/medical"


def build_ontology(suffix: str = ""):
    """构建 TBox（类层级 + 属性 + 公理），返回本体对象。"""
    onto = get_ontology(BASE + suffix + ".owl#")

    with onto:
        # ---- 类层级 ----
        class Disease(Thing):
            pass

        class InfectiousDisease(Disease):
            pass

        class BacterialDisease(InfectiousDisease):
            pass

        class ViralDisease(InfectiousDisease):
            pass

        class Drug(Thing):
            pass

        class Antibiotic(Drug):
            pass

        class Symptom(Thing):
            pass

        # ---- 公理：细菌性疾病与病毒性疾病互斥 ----
        AllDisjoint([BacterialDisease, ViralDisease])

        # ---- 对象属性 ----
        class hasSymptom(ObjectProperty):
            domain = [Disease]
            range = [Symptom]

        class treats(ObjectProperty):
            domain = [Drug]
            range = [Disease]

        class treatedBy(ObjectProperty):
            domain = [Disease]
            range = [Drug]
            inverse_property = treats

        # ---- 定义类：抗生素 ≡ 药物 ⊓ 至少治疗一种细菌性疾病（∃，用于推理归属） ----
        Antibiotic.equivalent_to = [Drug & treats.some(BacterialDisease)]

        # ---- 约束：抗生素只治疗细菌性疾病（∀，用于一致性校验） ----
        Antibiotic.is_a.append(treats.only(BacterialDisease))

    return onto


def main():
    print("=" * 64)
    print("构建小型医疗本体 + HermiT 推理验证")
    print("=" * 64)

    onto = build_ontology()

    with onto:
        pneumonia = onto.BacterialDisease("pneumonia", label=["肺炎"])
        flu = onto.ViralDisease("flu", label=["流感"])
        fever = onto.Symptom("fever", label=["发热"])
        amoxicillin = onto.Drug("amoxicillin", label=["阿莫西林"])  # 只断言是"药物"

        pneumonia.hasSymptom.append(fever)
        amoxicillin.treats.append(pneumonia)  # 阿莫西林治疗肺炎

    # ---- 第一轮推理：一致性 + 三类推理 ----
    print("\n[第 1 轮] 推理当前知识库（一致、无矛盾）...")
    sync_reasoner(infer_property_values=True)

    print("\n  [类层级] 细菌性疾病 的直接父类:", [c.name for c in onto.BacterialDisease.is_a])
    print("  [类层级] 传染病 的直接父类:", [c.name for c in onto.InfectiousDisease.is_a])

    # 检查 1：继承（subsumption）
    ok1 = isinstance(pneumonia, onto.InfectiousDisease) and isinstance(pneumonia, onto.Disease)
    print(f"\n  [1] 继承：肺炎 ∈ 传染病/疾病 → {'✓ 成立' if ok1 else '✗ 失败'}")
    assert ok1

    # 检查 2：定义类归属（阿莫西林只断言为"药物"，抗生素身份由推理得出）
    ok2 = isinstance(amoxicillin, onto.Antibiotic)
    print(f"  [2] 定义类：阿莫西林 ∈ 抗生素 → {'✓ 成立' if ok2 else '✗ 失败'}")
    assert ok2

    # 检查 3：逆属性
    treated = [t.name for t in pneumonia.treatedBy]
    ok3 = amoxicillin in pneumonia.treatedBy
    print(f"  [3] 逆属性：肺炎.treatedBy = {treated} → {'✓ 成立' if ok3 else '✗ 失败'}")
    assert ok3

    # 检查 4：一致性
    incons = list(default_world.inconsistent_classes())
    ok4 = not incons
    print(f"  [4] 一致性：不一致的类 = {[c.name for c in incons] or '无'} → {'✓ 一致' if ok4 else '✗ 不一致'}")
    assert ok4

    onto.save(file="medical.owl", format="rdfxml")
    print("\n  ✅ 第 1 轮通过：本体一致，继承 / 定义类 / 逆属性三类推理均成立。")
    print("     本体已保存到 medical.owl")

    # ---- 第二轮推理：加入矛盾事实，验证不一致检测 ----
    print("\n" + "=" * 64)
    print("[第 2 轮] 加入矛盾事实：阿莫西林 也治疗 流感（病毒性疾病）")
    print("=" * 64)
    amoxicillin.treats.append(flu)

    try:
        sync_reasoner()
    except OwlReadyInconsistentOntologyError:
        print("\n  ✅ 推理器检测到不一致：")
        print("     阿莫西林是抗生素（只治细菌病），却治疗流感（病毒病），")
        print("     且细菌病与病毒病互斥 → 本体矛盾。")
    else:
        raise AssertionError("预期应检测到不一致，但推理器判定本体一致")

    print("\n全部推理验证通过。")


if __name__ == "__main__":
    main()
