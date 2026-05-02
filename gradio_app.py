import gradio as gr
import requests
from app.data_loader import DATA_DIR, _clean_filename_label

API_URL = "http://localhost:8000/ask"


def _source_examples() -> list[str]:
    return [
        f"Разкажи ми за {_clean_filename_label(f.name)}"
        for f in sorted(DATA_DIR.glob("*.pdf"))
    ]


def chat(message: str, history: list) -> str:
    response = requests.post(API_URL, json={"query": message})
    response.raise_for_status()
    data = response.json()
    answer = data["answer"]
    if data["sources"]:
        answer += f"\n\n*Източници: {', '.join(data['sources'])}*"
    return answer


demo = gr.ChatInterface(
    fn=chat,
    title="Yettel AI Асистент",
    description="Задайте въпрос относно продуктите и услугите на Yettel.",
    examples=_source_examples(),
    submit_btn="Изпрати",
    stop_btn="Спри",
    textbox=gr.Textbox(placeholder="Напишете вашия въпрос тук...", label="Въпрос"),
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
