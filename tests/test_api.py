import requests
import sys

BASE_URL = "http://localhost:8000"

tests = [
    (
        "Как се добавя дигитален печат без табела?",
        ["100 те обекта_21.01.2025.pdf"],
        "Single source — adding digital stamp without sign"
    ),
    (
        "Какви са трите стълба на Смартфон Вселена?",
        ["Смартфон Вселена_22.01.2025.pdf"],
        "Single source — three pillars of Smartphone Universe"
    ),
    (
        "Как може клиент да смени номер през приложението?",
        ["Приложение Yettel_AI_team_rework.pdf"],
        "Single source — number change via app"
    ),
    (
        "Как се активира услуга в приложението Yettel?",
        None,
        "General query — service activation"
    ),
    (
        "Кои клиенти могат да управляват номера и какви услуги могат да активират?",
        None,
        "Complex query — number management and service activation"
    ),
    (
        "Каква е цената на 5G план на Yettel?",
        None,
        "Out of scope — 5G plan pricing"
    ),
    (
        "На какъв имейл се изпраща наградата от томболата на 100-те обекта?",
        ["100 те обекта_21.01.2025.pdf"],
        "Specific detail — tombola reward email"
    ),
    (
        "Какви са предимствата на услугите на Yettel?",
        None,
        "Ambiguous query — spans multiple documents"
    ),
    (
        "Каква версия на Android се изисква за приложението Yettel?",
        ["Приложение Yettel_AI_team_rework.pdf"],
        "Technical query — Android version requirement"
    ),
    (
        "Ако клиент има физическа книжка на 100-те обекта, какво трябва да направи при регистрация?",
        ["100 те обекта_21.01.2025.pdf"],
        "Multi-step reasoning — physical booklet registration"
    ),
    (
        "Какви услуги предлагате?",
        None,
        "Broad query — what services do you offer"
    ),
]


def run_tests():
    passed = 0
    failed = 0
    sep = "=" * 70

    for i, (query, expected_sources, description) in enumerate(tests, 1):
        r = requests.post(f"{BASE_URL}/ask", json={"query": query})
        data = r.json()
        sources = data["sources"]
        chunks = data.get("chunks", [])

        if expected_sources:
            match = all(s in sources for s in expected_sources)
            status = "PASS" if match else "FAIL"
            if match:
                passed += 1
            else:
                failed += 1
        else:
            status = "INFO"

        print(sep)
        print(f"Test {i} [{status}] — {description}")
        print(f"Q: {query}")
        print(f"Sources: {sources}")
        if chunks:
            print("Chunks used:")
            for c in chunks:
                print(f"  [{c.get('file_name')}] [{c.get('sub_title')}] {(c.get('question') or '')[:80]}")
        print(f"A: {data['answer']}")
        print()

    print(sep)
    print(f"Results: {passed} PASS / {failed} FAIL / {len([t for t in tests if t[1] is None])} INFO")


if __name__ == "__main__":
    run_tests()
