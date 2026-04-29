from pathlib import Path
import pypdf as pdf
import json
import re

DATA_DIR = Path(__file__).parent.parent / "rag_data_sources"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Check for subtitle
_SUBTITLE_RE = re.compile(r'^[А-ЯA-Z][А-ЯA-Z\s\*\/\:\-\&\(\)0-9]{2,}\s*$')

def _clean_filename_label(name: str) -> str:
    name = name.replace(".pdf", "")
    name = re.sub(r"[_\d\.\-]+$", "", name)
    return name.strip()

# Loading PDF files into a list of dictionaries 
def load_pdf_files(data_dir: Path = DATA_DIR) -> list[dict]:
    doc = []
    for file in sorted(data_dir.glob("*.pdf")):
        # print("Processing file: ", file)
        reader = pdf.PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages]).strip()
        doc.append({
            "file_name": file.name,
            "text": text
        })
    return doc


def chunk_pages(docs:list[dict]) -> list[dict]:

    chunks = []

    for doc in docs:
        current_subtitle = None
        next_subtitle = None
        current_lines = []

        for line in doc["text"].split("\n"):
            strippted_line = line.strip()

            #check if empty row or page header
            if not strippted_line or strippted_line == "Company Internal":
                continue

            # checks for subtitle
            if _SUBTITLE_RE.match(strippted_line):
                next_subtitle = strippted_line

            #if question found
            elif strippted_line.endswith('?'):
                # pypdf wraps long questions across 2 lines. Line 1 has no ? so it lands
                # in current_lines as an answer line. Line 2 ends with ? and triggers here.
                # If line 2 starts lowercase (mid-sentence) or is very short (e.g. "Yettel?"),
                # it is a continuation — pop line 1 from current_lines and merge:
                # "...фактурата си през" + " " + "приложението Yettel?"
                # → "...фактурата си през приложението Yettel?"
                if current_lines and (strippted_line[0].islower() or len(strippted_line) < 12):
                    strippted_line = current_lines.pop() + " " + strippted_line
                if current_lines:
                    chunks.append({
                        "file_name": doc["file_name"],
                        "sub_title": current_subtitle,
                        "question": current_lines[0] if current_lines[0].endswith('?') else None,
                        "text": '\n'.join(current_lines)
                    })
                if next_subtitle:
                    current_subtitle = next_subtitle
                    next_subtitle = None

                current_lines = [strippted_line]
            else:
                current_lines.append(strippted_line)

        if current_lines:
            chunks.append({
                "file_name": doc["file_name"],
                "sub_title": current_subtitle,
                "question": current_lines[0] if current_lines[0].endswith('?') else None,
                "text": "\n".join(current_lines),
            })

    # Add one index chunk per document with service name + all subtitles
    from collections import defaultdict
    subtitles_by_file = defaultdict(list)
    for c in chunks:
        if c["sub_title"] and c["sub_title"] not in subtitles_by_file[c["file_name"]]:
            subtitles_by_file[c["file_name"]].append(c["sub_title"])

    for doc in docs:
        fname = doc["file_name"]
        service_name = _clean_filename_label(fname)
        topics = subtitles_by_file.get(fname, [])
        index_text = f"Услуга: {service_name}\nТеми: {', '.join(topics)}" if topics else f"Услуга: {service_name}"
        chunks.insert(0, {
            "file_name": fname,
            "sub_title": None,
            "question": None,
            "text": index_text,
        })

    return chunks

if __name__ == "__main__":
    pages = load_pdf_files(DATA_DIR)
    chunks = chunk_pages(pages)

    with open("chunks_debug.json", "w", encoding="utf-8") as f:                                                                                                                                                  
        json.dump(chunks, f, ensure_ascii=False, indent=2)                                                                                                                                                       
                                                                                                                                                                                                                   
    print(f"Total chunks: {len(chunks)}")


