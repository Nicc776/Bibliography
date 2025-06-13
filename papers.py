import feedparser as fp

class paper:
    def __init__(self, arxiv_id='', title='', url='', keywords=None, abs='', authors=None, year='', journal='', doi=''):
        self.arxiv_id = arxiv_id
        self.title = title
        self.url = url
        self.keywords = keywords if keywords is not None else []
        self.abs = abs
        self.authors = authors if authors is not None else []
        self.year = year
        self.journal = journal
        self.doi = doi

    def get_arxiv_metadata_by_id(self):
        base_url = "http://export.arxiv.org/api/query?"
        query = f"search_query=id:{self.arxiv_id}&start=0&max_results=1"
        feed = fp.parse(base_url + query)
        if feed.entries:
            entry = feed.entries[0]
            self.title = entry.title
            self.abs = entry.summary
            self.url = "https://arxiv.org/abs/" + self.arxiv_id
            self.authors = [author.name for author in entry.authors] if hasattr(entry, "authors") else []
        # Journal reference (may not always be present)
            self.journal = entry.get("arxiv_journal_ref", "")
        # DOI (may not always be present)
            self.doi = entry.get("arxiv_doi", "")
            self.year = entry.published[:4] if hasattr(entry, "published") else ""
            #print(f"arXiv ID: {self.arxiv_id}")
            #print(f"URL: {self.url}")
            #print(f"Title: {self.title}")
            #print(f"Abstract: {self.abs}")
        else:
            print("No entry found for the given arXiv ID.")
    
    def add_keyword(self, keyword):
        if keyword not in self.keywords:
            self.keywords.append(keyword)
    
    def remove_keyword(self, keyword):
        if keyword in self.keywords:
            self.keywords.remove(keyword)
    
    def get_keywords(self):
        return self.keywords
    
    def show_id(self):
        return self.arxiv_id
    def show_title(self):
        return self.title
    def show_url(self):
        return self.url
    def show_abs(self):
        return self.abs
    def show_authors(self):
        return self.authors if self.authors else "No authors listed"
    def show_journal(self):
        return self.journal if self.journal else "No journal reference"
    def show_doi(self):
        return self.doi if self.doi else "No DOI available"
    def show_year(self):
        return self.year if self.year else "No year available"
    

    def to_bibtex(self):
        authors = " and ".join(self.authors)
        bibtex = (
            f"@article{{{self.arxiv_id},\n"
            f"  title={{ {self.title} }},\n"
            f"  author={{ {authors} }},\n"
            f"  journal={{ {self.journal} }},\n"
            f"  year={{ {self.year} }},\n"
            f"  doi={{ {self.doi} }},\n"
            f"  url={{ {self.url} }},\n"
            f"  note={{arXiv:{self.arxiv_id}}}\n"
            f"}}"
        )
        return bibtex


# Example usage:

#RF_TEST = paper("1512.05435")
#RF_TEST.get_arxiv_metadata_by_id()
