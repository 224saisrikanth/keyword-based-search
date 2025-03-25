# Keyword-Based Search Engine for PDF Documents

A sophisticated document search application that enables users to search through large collections of PDF documents using keyword-based queries. This application extracts text from PDFs, indexes the content, and provides a modern, high-end user interface for searching and displaying results with premium animations and interactions.

## 🌟 Key Features

### Document Management
- **PDF Upload**: Upload and manage multiple PDF documents
- **Automatic Text Extraction**: Efficiently extracts text from PDFs using PyMuPDF
- **Batch Processing**: Process multiple documents at once
- **Document Organization**: Manage your document collection with rename and delete operations

### Advanced Search Capabilities
- **Keyword-Based Search**: Find exact matches or semantically similar content
- **Context-Aware Results**: View text before and after matches for better context
- **Result Highlighting**: Clearly highlights matched terms in search results
- **Search Ranking**: Results are ranked by relevance using BM25 algorithm
- **Result Grouping**: Group results by document or view all matches
- **Pagination**: Navigate through large result sets easily

### Document Viewer
- **Interactive PDF Viewer**: View PDFs directly in the application
- **Match Navigation**: Jump between search matches within documents
- **Page Navigation**: Easily navigate between pages
- **Filtered View**: View only pages with matches
- **Keyboard Shortcuts**: Efficient navigation with keyboard shortcuts

### Export & Sharing
- **Multiple Export Formats**: Export search results in PDF, CSV, or JSON format
- **Comprehensive Reports**: Generate detailed reports of search findings
- **Result Filtering**: Export only relevant matches
- **Customizable Output**: Control what information is included in exports

### Premium UI/UX
- **Modern Interface**: Clean, intuitive design with responsive layouts
- **Glassmorphism Effects**: Elegant semi-transparent cards with blur effects
- **Micro-interactions**: Subtle animations and transitions for better user experience
- **3D Hover Effects**: Dynamic perspective shifts on hover for depth
- **Real-time Feedback**: Visual indicators for all user actions

## 🏗️ Technical Architecture

The application is built with a modular architecture consisting of:

### Core Components
- **Flask Web Application**: Handles HTTP requests and renders HTML templates
- **PDF Extractor**: Extracts and processes text from PDF documents
- **Search Engine**: Indexes and searches document content efficiently
- **Data Storage**: Manages data persistence for extracted content
- **Export Manager**: Handles exporting search results in various formats

### Technology Stack
- **Backend**: Python with Flask web framework
- **PDF Processing**: PyMuPDF (Fitz) for high-performance text extraction
- **Search Indexing**: Whoosh for full-text indexing with BM25 ranking
- **Data Storage**: JSON-based document storage with efficient organization
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Export Generation**: ReportLab and FPDF for PDF generation

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Web browser with JavaScript enabled

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/keyword-based-search.git
cd keyword-based-search
```

2. Create a virtual environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize required directories (first run only)
```bash
mkdir -p pdfs data index static/temp
```

### Running the Application

Start the application server:
```bash
python app.py
```

Navigate to `http://localhost:5000` in your browser to access the application.

## 📖 Usage Guide

### Adding Documents

1. **Upload Documents**: Click the "Upload" tab or button on the dashboard
2. **Select Files**: Choose PDF files to upload (multiple files supported)
3. **Process**: Files are automatically uploaded, indexed and made searchable

### Searching Documents

1. **Basic Search**: Enter keywords in the search bar and press Enter
2. **View Results**: Browse through the search results with highlighted matches
3. **Filter Results**: Use the grouping options to organize results by document
4. **Navigate**: Click on results to view the original document with highlighted matches

### Viewing Documents

1. **Document View**: Click on a search result to open the document viewer
2. **Navigate Matches**: Use the navigation buttons to move between matches
3. **Page Navigation**: Use the page controls to move between document pages
4. **Keyboard Shortcuts**: Use arrow keys for navigation, ESC to return to results

### Exporting Results

1. **Export Results**: Click the "Export" button on the search results page
2. **Choose Format**: Select PDF, CSV, or JSON as the export format
3. **Download**: The export will be generated and downloaded automatically

## 📚 Directory Structure

```
keyword-based-search/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── modules/                # Core functionality modules
│   ├── pdf_extractor.py    # PDF text extraction
│   ├── search.py           # Search engine implementation
│   ├── storage.py          # Data storage functionality
│   ├── export.py           # Export generation
│   └── error_handler.py    # Error handling utilities
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── favicon/            # Favicon assets
│   └── temp/               # Temporary files for exports
├── templates/              # HTML templates
│   ├── base.html           # Base template layout
│   ├── index.html          # Dashboard template
│   ├── results.html        # Search results template
│   ├── viewer.html         # PDF viewer template
│   └── ...                 # Other templates
├── pdfs/                   # Storage for uploaded PDFs
├── data/                   # Extracted text data storage
├── index/                  # Search index storage
└── requirements.txt        # Python dependencies
```

## ⚙️ Technical Details

### Search Implementation

The search functionality is implemented using Whoosh, an efficient pure-Python full-text indexing and search library. The search engine:

1. Creates an inverted index mapping words to document locations
2. Uses a schema with document ID, filename, page number, and content fields
3. Implements BM25 ranking algorithm for improved result relevance
4. Extracts and highlights matching content with surrounding context
5. Provides pagination and result grouping features

### PDF Processing

PDF processing is handled by PyMuPDF (Fitz):

1. Extracts text content from PDF documents page by page
2. Preserves page structure for accurate context retrieval
3. Stores extracted text in JSON format for efficient retrieval
4. Maps document metadata to search index for result generation

### UI Implementation

The user interface features modern design elements:

1. Responsive layout using custom CSS
2. Premium animations and transitions using CSS and JavaScript
3. Glassmorphism effects with semi-transparent backgrounds and blur
4. Dynamic 3D hover effects with perspective transformations
5. Micro-interactions for enhanced user experience

## 🔍 Advanced Usage

### Query Syntax

The search engine supports complex query operators:

- **Term searching**: `keyword`
- **Phrase searching**: `"exact phrase"`
- **Field-specific searching**: `filename:document.pdf content:keyword`
- **Boolean operators**: `term1 AND term2`, `term1 OR term2`, `NOT term`
- **Wildcard searching**: `key*` (prefix search)

### Batch Processing

For large document collections:

1. Place PDF files in the `pdfs/` directory
2. Use the "Process All Documents" function on the dashboard
3. All documents will be extracted and indexed in batch

## 🛠️ Maintenance and Troubleshooting

### Common Issues

1. **PDF Not Searchable**: Some PDFs contain scanned images instead of text. These require OCR processing before they can be searched.

2. **Search Index Corruption**: If search results become inconsistent, you may need to rebuild the index:
   - Navigate to Dashboard > Process All Documents to rebuild the index

3. **Large File Handling**: For extremely large PDFs (>50MB), processing may take longer. The application will continue to function during processing.

### Data Management

The application stores data in several locations:

- **PDF Files**: Original PDF documents in `/pdfs` directory
- **Extracted Text**: Text content in `/data` directory as JSON files
- **Search Index**: Whoosh index in `/index` directory
- **Temporary Files**: Temporary exports in `/static/temp` directory

To clear data and start fresh:
1. Stop the application
2. Delete contents of the `data/`, `index/`, and `static/temp/` directories
3. Restart the application and reprocess documents

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions, feature requests, or support, please open an issue in the GitHub repository. 
