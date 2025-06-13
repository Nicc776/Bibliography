import os
import papers
import json

# Always use the Bibliography folder for the JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIB_PATH = os.path.join(BASE_DIR, "bibliography.json")

def save_papers(paper_list, filename=None):
    if filename is None:
        filename = BIB_PATH
    # Ensure all authors fields are lists
    for p in paper_list:
        if isinstance(p.authors, str):
            # Split on commas and strip whitespace
            p.authors = [a.strip() for a in p.authors.split(",") if a.strip()]

    data = [
        {
            "arxiv_id": p.show_id(),
            "title": p.show_title(),
            "url": p.show_url(),
            "keywords": p.get_keywords(),
            "abs": p.show_abs(),
            "authors": p.show_authors(),
            "journal": p.show_journal(),
            "doi": p.show_doi(),
            "year": p.show_year()
        }
        for p in paper_list
    ]

    # Clean newlines before saving
    for entry in data:
        if "title" in entry and entry["title"]:
            entry["title"] = entry["title"].replace('\n  ', ' ')
            
        if "abs" in entry and entry["abs"]:
            entry["abs"] = entry["abs"].replace('\n', ' ')

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_papers(filename=None):
    if filename is None:
        filename = BIB_PATH
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    return [papers.paper(
        entry["arxiv_id"],
        title=entry.get("title").replace('\n  ', ' '),
        url=entry.get("url"),
        keywords=entry.get("keywords"),
        abs=entry.get("abs").replace('\n', ' '),
        authors=entry.get("authors", []),
        year=entry.get("year", ""),
        journal=entry.get("journal", ""),
        doi=entry.get("doi", "")
    ) for entry in data]

# Example usage:
#paper1 = papers.paper("1512.05435")
#paper1.get_arxiv_metadata_by_id()
#paper1.add_keyword("machine learning")
#paper2 = papers.paper("1606.03657")
#paper2.get_arxiv_metadata_by_id()
#paper2.add_keyword("deep learning")
#paper_list = [paper1, paper2]
#save_papers(paper_list)
#loaded_papers = load_papers()
#for p in loaded_papers:
#    print(f"ID: {p.show_id()}, Title: {p.show_title()}, Keywords: {p.get_keywords()}")
