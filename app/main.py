"""一个简单的终端成语学习程序。"""

import json
import random
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "idioms.json"


def examples_text(idiom: dict[str, object]) -> str:
    """将一个或多个例句合并为便于检索的文本。"""
    return " ".join(idiom["example"])


def load_idioms() -> list[dict[str, object]]:
    """读取并检查成语数据。"""
    try:
        with DATA_PATH.open(encoding="utf-8") as file:
            idioms = json.load(file)
    except FileNotFoundError:
        print(f"找不到数据文件：{DATA_PATH}")
        return []
    except json.JSONDecodeError:
        print("成语数据不是有效的 JSON，请检查 data/idioms.json。")
        return []

    if not isinstance(idioms, list):
        print("成语数据格式错误：最外层应是列表。")
        return []

    valid_idioms = []
    seen_words = set()
    skipped_invalid = 0
    skipped_duplicates = 0
    for idiom in idioms:
        if not isinstance(idiom, dict):
            skipped_invalid += 1
            continue

        text_fields = ("word", "pinyin", "meaning", "mistake")
        examples = idiom.get("example")
        has_valid_examples = (
            isinstance(examples, list)
            and bool(examples)
            and all(isinstance(example, str) and example.strip() for example in examples)
        )
        if not all(isinstance(idiom.get(field), str) and idiom[field].strip() for field in text_fields):
            skipped_invalid += 1
            continue
        if not has_valid_examples:
            skipped_invalid += 1
            continue

        word = idiom["word"]
        if word in seen_words:
            skipped_duplicates += 1
            continue
        seen_words.add(word)
        valid_idioms.append(idiom)

    if skipped_invalid:
        print("提示：已跳过字段不完整的成语数据。")
    if skipped_duplicates:
        print(f"提示：已跳过 {skipped_duplicates} 条重复成语，保留每个成语首次出现的词条。")

    return valid_idioms


def show_idiom(idiom: dict[str, object]) -> None:
    """显示一个成语的学习卡片。"""
    print(f"\n{idiom['word']}  {idiom['pinyin']}")
    print(f"释义：{idiom['meaning']}")
    print("例句：")
    for number, example in enumerate(idiom["example"], 1):
        print(f"  {number}. {example}")
    if idiom['mistake'].strip():
        print(f"易错提醒：{idiom['mistake']}")


def search_idiom(idioms: list[dict[str, object]]) -> None:
    """根据用户输入查询成语。"""
    word = input("请输入要查询的成语：").strip()
    if not word:
        print("请输入一个成语。")
        return

    idiom = next((item for item in idioms if item['word'] == word), None)
    if idiom is None:
        print(f"未找到“{word}”。")
        return

    show_idiom(idiom)


def find_by_meaning(idioms: list[dict[str, object]]) -> None:
    """根据用户输入的关键词，找出可能合适的成语。"""
    query = input("请输入想表达的意思或关键词：").strip()
    if not query:
        print("请输入想表达的意思或关键词。")
        return

    query_words = [word for word in query.replace("，", " ").replace("。", " ").split() if word]
    if not query_words:
        query_words = [query]

    matches = []
    for idiom in idioms:
        # 易错提醒常包含“不应理解成某意思”之类的否定说明，
        # 不参与按意思搜索，避免把不合适的成语推荐给用户。
        searchable_text = " ".join([idiom["word"], idiom["meaning"], examples_text(idiom)])
        score = sum(word in searchable_text for word in query_words)
        if score:
            matches.append((score, idiom))

    matches.sort(key=lambda item: (-item[0], item[1]["word"]))

    if not matches:
        print(f"没有找到与“{query}”直接匹配的成语。")
        print("可以换成更短的关键词再试，例如“准备”“不同意”或“紧急”。")
        return

    print(f"\n与“{query}”相关的成语：")
    for number, (_, idiom) in enumerate(matches[:5], 1):
        short_meaning = idiom["meaning"].split("。", 1)[0]
        print(f"{number}. {idiom['word']}：{short_meaning}。")

    selection = input("输入序号或成语名称查看详情，直接回车返回：").strip()
    if not selection:
        return

    displayed_matches = [idiom for _, idiom in matches[:5]]
    if selection.isdigit():
        if not 1 <= int(selection) <= len(displayed_matches):
            print("请输入列表中的有效序号，或直接输入成语名称。")
            return
        show_idiom(displayed_matches[int(selection) - 1])
        return

    idiom = next((item for item in displayed_matches if item["word"] == selection), None)
    if idiom is None:
        print("请输入列表中的有效序号或成语名称。")
        return

    show_idiom(idiom)


def compare_idioms(idioms: list[dict[str, object]]) -> None:
    """并排展示两个成语，方便辨析。"""
    first_word = input("请输入第一个成语：").strip()
    second_word = input("请输入第二个成语：").strip()

    if not first_word or not second_word:
        print("请完整输入两个成语。")
        return

    lookup = {idiom["word"]: idiom for idiom in idioms}
    first = lookup.get(first_word)
    second = lookup.get(second_word)
    missing = [word for word, idiom in ((first_word, first), (second_word, second)) if idiom is None]

    if missing:
        print(f"未找到：{'、'.join(missing)}。")
        return

    print(f"\n{first['word']} 和 {second['word']}")
    print(f"\n【{first['word']}】{first['pinyin']}")
    print(f"释义：{first['meaning']}")
    print("例句：")
    for number, example in enumerate(first["example"], 1):
        print(f"  {number}. {example}")
    if first['mistake'].strip():
        print(f"易错提醒：{first['mistake']}")

    print(f"\n【{second['word']}】{second['pinyin']}")
    print(f"释义：{second['meaning']}")
    print("例句：")
    for number, example in enumerate(second["example"], 1):
        print(f"  {number}. {example}")
    if second['mistake'].strip():
        print(f"易错提醒：{second['mistake']}")

    print("\n使用时请根据两者释义和例句中的具体语境选择。")


def option_score(target: dict[str, object], candidate: dict[str, object]) -> int:
    """估计两个成语的关联度，用于优先选择较有迷惑性的选项。"""
    target_text = target["meaning"] + target["mistake"]
    candidate_text = candidate["meaning"] + candidate["mistake"]
    score = 0

    # 易错提醒里直接提到另一个成语时，通常就是值得一起辨析的选项。
    if target["word"] in candidate_text or candidate["word"] in target_text:
        score += 100

    # 用释义中共有的双字短语补充关联度，过滤掉过于通用的表达。
    ignored_terms = {
        "比喻", "形容", "表示", "事情", "不能", "用来", "用于",
        "一种", "这个", "没有", "意思", "情况", "行为", "多指",
        "本义", "成语", "搜索", "结果", "强调", "正确", "使用",
        "常用", "典出", "收录", "很多", "如果", "就是", "一个",
        "容易", "混淆", "时候", "特别", "完全", "反复", "指出",
    }
    target_terms = {target_text[index:index + 2] for index in range(len(target_text) - 1)}
    candidate_terms = {candidate_text[index:index + 2] for index in range(len(candidate_text) - 1)}
    score += len((target_terms & candidate_terms) - ignored_terms)
    return score


def build_options(target: dict[str, object], idioms: list[dict[str, object]]) -> list[dict[str, object]]:
    """为一道题生成一个正确答案和三个优先关联的干扰项。"""
    candidates = [idiom for idiom in idioms if idiom["word"] != target["word"]]
    candidates.sort(key=lambda idiom: option_score(target, idiom), reverse=True)

    # 关联度不足时，用其余词条补足，确保每题都恰好有四个选项。
    distractors = candidates[:3]
    return random.sample([target, *distractors], k=4)


def practice(idioms: list[dict[str, object]]) -> None:
    """随机出一道四选一的释义辨析题。"""
    if len(idioms) < 4:
        print("至少需要 4 条成语数据才能进行四选一练习。")
        return

    target = random.choice(idioms)
    options = build_options(target, idioms)
    labels = "ABCD"

    print("\n请选择与下列释义相符的成语：")
    print(target["meaning"])
    for label, option in zip(labels, options):
        print(f"{label}. {option['word']}")

    answer = input("你的答案（A、B、C 或 D）：").strip().upper()
    if answer not in labels:
        print("请输入 A、B、C 或 D。")
        return

    selected = options[labels.index(answer)]
    correct_label = labels[options.index(target)]
    if selected["word"] == target["word"]:
        print("答对了！")
    else:
        print(f"答错了，正确答案是：{correct_label}. {target['word']}")
        print(f"你选择的“{selected['word']}”：{selected['meaning']}")

    show_idiom(target)


def main() -> None:
    idioms = load_idioms()
    if not idioms:
        print("没有可用的成语数据，程序结束。")
        return

    print(f"欢迎使用成语学习程序，已加载 {len(idioms)} 条成语。")

    while True:
        print("\n1. 查询成语")
        print("2. 按意思找成语")
        print("3. 成语对比")
        print("4. 随机练习")
        print("5. 退出")
        choice = input("请选择功能：").strip()

        if choice == "1":
            search_idiom(idioms)
        elif choice == "2":
            find_by_meaning(idioms)
        elif choice == "3":
            compare_idioms(idioms)
        elif choice == "4":
            practice(idioms)
        elif choice == "5":
            print("下次见！")
            break
        else:
            print("请输入 1、2、3、4 或 5。")


if __name__ == "__main__":
    main()
