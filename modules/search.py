import os
import whoosh.index as index
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh.highlight import ContextFragmenter, HtmlFormatter, Highlighter
import re

class SearchEngine:
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.schema = Schema(
            doc_id=ID(stored=True),
            filename=TEXT(stored=True),
            page_num=STORED,
            content=TEXT(analyzer=StemmingAnalyzer(), stored=True)
        )
        
        # Create or open index
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
            self.index = index.create_in(index_dir, self.schema)
        else:
            try:
                self.index = index.open_dir(index_dir)
            except:
                self.index = index.create_in(index_dir, self.schema)
    
    def index_documents(self, documents):
        """Index the extracted documents."""
        writer = self.index.writer()
        
        for doc in documents:
            filename = doc["filename"]
            for page_num, text in doc["pages"].items():
                doc_id = f"{filename}:{page_num}"
                writer.add_document(
                    doc_id=doc_id,
                    filename=filename,
                    page_num=int(page_num),
                    content=text
                )
        
        writer.commit()
        print(f"Indexed {len(documents)} documents with {sum(len(doc['pages']) for doc in documents)} pages")
    
    def search(self, query_text, page=1, page_size=10, group_by_file=True):
        """Perform a search against the index"""
        if not query_text or not query_text.strip():
            return {"results": [], "total": 0, "file_count": 0, "page": page, "pages": 0, "grouped": group_by_file}
            
        try:
            # Create a query parser for the content field
            parser = MultifieldParser(["content", "filename"], schema=self.index.schema)
            
            # Parse the query string
            query = parser.parse(query_text)
            
            # Set up highlighter with custom HTML formatting
            formatter = HtmlFormatter(tagname="em", classname="", termclass="")
            fragmenter = ContextFragmenter(maxchars=100, surround=50)
            highlighter = Highlighter(formatter=formatter, fragmenter=fragmenter)
            
            # Perform the search
            with self.index.searcher() as searcher:
                results = searcher.search(query, limit=1000)  # Get many results for processing
                
                # Process results
                search_results = []
                for hit in results:
                    # Get content and highlight matches
                    content = hit.get("content", "")
                    highlighted = highlighter.highlight_hit(hit, "content")
                    
                    # Only add if we have a highlighted result
                    if highlighted:
                        # Create result object
                        result = {
                            "filename": hit.get("filename", "Unknown"),
                            "page": hit.get("page_num", 0),
                            "highlight": highlighted,
                            "content": content
                        }
                        
                        # Extract context around the highlight
                        result["context_before"], result["context_after"] = self._extract_context(content, highlighted)
                        
                        search_results.append(result)
                
                # Return formatted results
                if not search_results:
                    return {"results": [], "total": 0, "file_count": 0, "page": page, "pages": 0, "grouped": group_by_file}
                
                return self.format_search_results(search_results, page, page_size, group_by_file)
        
        except Exception as e:
            print(f"Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"results": [], "total": 0, "file_count": 0, "page": page, "pages": 0, "grouped": group_by_file}

    def format_search_results(self, results, page, page_size, grouped=True):
        """Format search results with proper highlighting and context"""
        if not results:
            return {"results": [], "total": 0, "file_count": 0, "page": page, "pages": 0, "grouped": grouped}
            
        formatted_results = []
        
        # Group by filename if needed
        if grouped:
            grouped_results = {}
            for result in results:
                filename = result["filename"]
                if filename not in grouped_results:
                    grouped_results[filename] = result
            formatted_results = list(grouped_results.values())
        else:
            formatted_results = results
        
        # Sort by filename for consistency
        formatted_results.sort(key=lambda x: x["filename"])
        
        # Calculate pagination
        total_results = len(formatted_results)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_results)
        
        # Get results for current page
        page_results = formatted_results[start_idx:end_idx]
        
        # Count unique files
        file_count = len(set(r["filename"] for r in formatted_results))
        
        # Calculate total pages
        total_pages = max(1, (total_results + page_size - 1) // page_size)
        
        return {
            "results": page_results,
            "total": total_results,
            "file_count": file_count,
            "page": page,
            "pages": total_pages,
            "grouped": grouped
        }

    def _extract_context(self, content, highlight):
        """Extract text before and after the highlighted section"""
        # Remove HTML tags from highlight to find in content
        clean_highlight = re.sub(r'<[^>]+>', '', highlight)
        
        try:
            pos = content.find(clean_highlight)
            if pos >= 0:
                # Get context before (up to 150 chars)
                context_before = content[max(0, pos-150):pos].strip()
                if context_before and len(context_before) > 0 and pos > 150:
                    context_before = "..." + context_before
                
                # Get context after (up to 150 chars)
                highlight_end = pos + len(clean_highlight)
                context_after = content[highlight_end:min(len(content), highlight_end+150)].strip()
                if context_after and len(context_after) > 0 and highlight_end + 150 < len(content):
                    context_after = context_after + "..."
                
                return context_before, context_after
        except Exception as e:
            print(f"Context extraction error: {e}")
            pass
        
        return "", ""

    def remove_document(self, filename):
        """Remove all documents related to a specific file from the index"""
        writer = self.index.writer()
        writer.delete_by_term('filename', filename)
        writer.commit()
        print(f"Removed documents for {filename} from search index")

    def _matches_pattern(self, filename, pattern):
        """Check if a filename matches a pattern with wildcards"""
        # Convert the pattern to a regex pattern
        regex_pattern = pattern.replace('.', '\.').replace('*', '.*')
        return re.match(f"^{regex_pattern}$", filename, re.IGNORECASE) is not None 