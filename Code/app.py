import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort, session, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import whoosh.qparser
import time

from config import PDF_DIR, DATA_DIR, INDEX_DIR
from modules.pdf_extractor import PDFExtractor
from modules.storage import DataStorage
from modules.search import SearchEngine
from modules.export import ExportManager

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = PDF_DIR
app.config['MAX_CONTENT_LENGTH'] = 10000 * 1024 * 1024  # Increase to 10000MB max upload

# Initialize modules
pdf_extractor = PDFExtractor(PDF_DIR)
data_storage = DataStorage(DATA_DIR)
search_engine = SearchEngine(INDEX_DIR)

# Add this template filter to convert timestamps to readable dates
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convert Unix timestamp to readable date"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M')

@app.template_filter('pluralize')
def pluralize(count, singular, plural=None):
    """Returns singular or plural form of word based on count."""
    if count == 1:
        return singular
    if plural is None:
        return singular + 's'
    return plural

@app.route('/')
def index():
    # List PDFs in the directory with file sizes
    pdf_files = []
    for f in os.listdir(PDF_DIR):
        if f.lower().endswith('.pdf'):
            file_path = os.path.join(PDF_DIR, f)
            try:
                file_size = os.path.getsize(file_path)
                pdf_files.append({
                    'name': f,
                    'size': file_size,
                    'date_modified': os.path.getmtime(file_path)
                })
            except (FileNotFoundError, PermissionError):
                # Skip files with permission issues
                continue
    
    return render_template('index.html', 
                          pdfs=pdf_files,
                          active_page='dashboard')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload PDF files and automatically process them for search"""
    if 'pdf_file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    files = request.files.getlist('pdf_file')
    
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(request.url)
    
    uploaded_count = 0
    skipped_count = 0
    indexed_count = 0
    
    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                skipped_count += 1
                continue
                
            file.save(file_path)
            uploaded_count += 1
            
            # Automatically process the uploaded file for search
            data = pdf_extractor.extract_text_from_pdf(file_path)
            if data:
                data_storage.save_to_json([data], f"{filename}.json")
                search_engine.index_documents([data])
                indexed_count += 1
        else:
            skipped_count += 1
    
    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s), indexed {indexed_count} file(s)', 'success')
    
    if skipped_count > 0:
        flash(f'Skipped {skipped_count} file(s) (invalid type or already exists)', 'warning')
    
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process_pdfs():
    """Re-extract text from all PDFs and rebuild the search index (for recovery or updates)"""
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        flash('No PDF files found to process', 'warning')
        return redirect(url_for('index'))
    
    # Clear existing index to rebuild it
    if os.path.exists(INDEX_DIR):
        import shutil
        shutil.rmtree(INDEX_DIR)
        os.makedirs(INDEX_DIR, exist_ok=True)
    
    # Import Whoosh index properly to avoid name clash with the 'index' route
    import whoosh.index as whoosh_index
    
    # Recreate the index
    search_engine.index = whoosh_index.create_in(INDEX_DIR, search_engine.schema)
    
    # Process each PDF
    processed_count = 0
    error_count = 0
    
    for filename in pdf_files:
        try:
            # Extract text
            pdf_path = os.path.join(PDF_DIR, filename)
            data = pdf_extractor.extract_text_from_pdf(pdf_path)
            
            if data:
                # Save extracted data
                data_storage.save_to_json([data], f"{filename}.json")
                
                # Add to search index
                search_engine.index_documents([data])
                processed_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            error_count += 1
            print(f"Error processing {filename}: {e}")
    
    if processed_count > 0:
        flash(f'Successfully processed {processed_count} PDF files', 'success')
    
    if error_count > 0:
        flash(f'Failed to process {error_count} PDF files', 'error')
    
    return redirect(url_for('index'))

@app.route('/documents')
def documents():
    """Show all documents with management options"""
    # Get documents with sizes
    pdf_files = []
    for f in os.listdir(PDF_DIR):
        if f.lower().endswith('.pdf'):
            file_path = os.path.join(PDF_DIR, f)
            try:
                file_size = os.path.getsize(file_path)
                pdf_files.append({
                    'name': f,
                    'size': file_size,
                    'date_modified': os.path.getmtime(file_path)
                })
            except (FileNotFoundError, PermissionError):
                # Skip files with permission issues
                continue
    
    return render_template('documents.html', 
                          pdfs=pdf_files, 
                          active_page='documents')

@app.route('/search_page')
def search_page():
    """Show the dedicated search page with advanced options"""
    return render_template('search_page.html', 
                          active_page='search')

@app.route('/upload_page')
def upload_page():
    """Show the dedicated upload page"""
    return render_template('upload_page.html',
                          active_page='upload')

@app.route('/search')
def search():
    """Search for content in indexed PDFs"""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    group = request.args.get('group', 'true')
    group_by_file = group.lower() == 'true'
    
    if not query:
        return render_template('search_page.html', active_page='search_page')
    
    # Search for the query in the index
    results = search_engine.search(
        query, 
        page=page, 
        page_size=10,
        group_by_file=group_by_file
    )
    
    # Add search index directory for debugging
    search_index_dir = INDEX_DIR
    
    # Store the search query in session for later use
    session['last_search_query'] = query
    
    # Log some debug info
    print(f"Search for '{query}' returned {results['total']} results")
    
    return render_template('results.html',
                          query=query,
                          results=results,
                          active_page='search_page',
                          search_index_dir=search_index_dir,
                          request=request)

@app.route('/api/search')
def api_search():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    
    results = search_engine.search(query)
    return jsonify(results)

@app.route('/view/<path:filename>')
def view_pdf(filename):
    """View a PDF file in the browser with highlighting for search terms"""
    page = request.args.get('page', 0, type=int)
    
    # Get the search query from the request or session if available
    query = request.args.get('query', '')
    if not query and 'last_search_query' in session:
        query = session['last_search_query']
    
    if not os.path.exists(os.path.join(PDF_DIR, filename)):
        flash('PDF file not found', 'error')
        return redirect(url_for('index'))
    
    # Store query in session to make it available for highlighting
    if query:
        session['current_query'] = query
        
    # Find pages with matches if we have a query
    matching_pages = []
    if query:
        try:
            # Use the search engine to find which pages match the query
            parser = whoosh.qparser.QueryParser("content", schema=search_engine.index.schema)
            q = parser.parse(query)
            
            with search_engine.index.searcher() as searcher:
                # Get all matches for this specific file
                file_query = f'filename:"{filename}" AND {query}'
                file_parser = whoosh.qparser.MultifieldParser(["content", "filename"], schema=search_engine.index.schema)
                results = searcher.search(file_parser.parse(file_query), limit=100)
                
                # Extract the page numbers from matching results
                for hit in results:
                    if hit['filename'] == filename and 'page_num' in hit:
                        matching_pages.append(hit['page_num'])
                
                # Sort the pages
                matching_pages = sorted(set(matching_pages))
        except Exception as e:
            app.logger.error(f"Error finding matching pages: {str(e)}")
    
    return render_template('viewer.html', 
                          filename=filename, 
                          page=page,
                          query=query,
                          matching_pages=matching_pages,
                          active_page='documents')

@app.route('/pdf/<path:filename>')
def serve_pdf(filename):
    """Serve the PDF file directly for the viewer"""
    try:
        return send_from_directory(PDF_DIR, filename)
    except FileNotFoundError:
        abort(404)

@app.route('/rename_pdf', methods=['POST'])
def rename_pdf():
    """Rename a PDF file"""
    original_filename = request.form.get('original_filename')
    new_filename = request.form.get('new_filename')
    
    if not original_filename or not new_filename:
        flash('Missing filename information', 'error')
        return redirect(url_for('index'))
    
    # Secure the new filename
    new_filename = secure_filename(new_filename)
    
    # Ensure new filename ends with .pdf
    if not new_filename.lower().endswith('.pdf'):
        new_filename += '.pdf'
    
    # Check if original file exists
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    if not os.path.exists(original_path):
        flash(f'File not found: {original_filename}', 'error')
        return redirect(url_for('index'))
    
    # Check if new filename already exists
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    if os.path.exists(new_path) and original_filename != new_filename:
        flash(f'A file with the name {new_filename} already exists', 'error')
        return redirect(url_for('index'))
    
    try:
        # Rename the file
        os.rename(original_path, new_path)
        
        # Update the index if needed
        # This depends on how your indexing system works
        
        flash(f'Successfully renamed {original_filename} to {new_filename}', 'success')
    except Exception as e:
        flash(f'Error renaming file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_pdf', methods=['POST'])
def delete_pdf():
    """Delete a PDF file and remove it from search index"""
    filename = request.form.get('filename')
    
    if not filename:
        flash('No filename specified', 'error')
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'File {filename} not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Delete the file
        os.remove(file_path)
        
        # Remove from search index
        search_engine.remove_document(filename)
        
        flash(f'Successfully deleted {filename}', 'success')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_multiple_pdfs', methods=['POST'])
def delete_multiple_pdfs():
    """Delete multiple PDF files and remove them from search index"""
    filenames = request.form.getlist('filenames[]')
    
    if not filenames:
        flash('No files specified for deletion', 'error')
        return redirect(url_for('index'))
    
    success_count = 0
    error_count = 0
    
    for filename in filenames:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            error_count += 1
            continue
        
        try:
            # Delete the file
            os.remove(file_path)
            
            # Remove from search index
            search_engine.remove_document(filename)
            
            success_count += 1
        except Exception:
            error_count += 1
    
    if success_count > 0:
        flash(f'Successfully deleted {success_count} file(s)', 'success')
    
    if error_count > 0:
        flash(f'Failed to delete {error_count} file(s)', 'error')
    
    return redirect(url_for('index'))

@app.route('/export-results')
def export_results():
    """Export search results as PDF report"""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        flash('No search query specified for export', 'error')
        return redirect(url_for('index'))
    
    # Get search results without pagination to export all results
    search_results = search_engine.search(query, page=1, page_size=1000)  # Get up to 1000 results
    
    # Check if we have results to export
    if not search_results or len(search_results.get('results', [])) == 0:
        flash('No results to export', 'error')
        return redirect(url_for('search', query=query))
    
    # Export to PDF only
    try:
        return ExportManager.export_to_pdf(search_results['results'], query)
    except Exception as e:
        import traceback
        app.logger.error(f"Export error: {str(e)}")
        app.logger.error(traceback.format_exc())
        flash(f'Error exporting results: {str(e)}', 'error')
        return redirect(url_for('search', query=query))

@app.route('/cleanup_temp', methods=['POST'])
def cleanup_temp():
    """Clean up temporary extraction and filtered PDF files"""
    try:
        # Clean up extraction directory
        extraction_dir = os.path.join(DATA_DIR, 'extractions')
        if os.path.exists(extraction_dir):
            for filename in os.listdir(extraction_dir):
                file_path = os.path.join(extraction_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
        # Clean up filtered PDFs
        filtered_dir = os.path.join(app.static_folder, 'temp')
        if os.path.exists(filtered_dir):
            for filename in os.listdir(filtered_dir):
                if filename.startswith('filtered_'):
                    file_path = os.path.join(filtered_dir, filename)
                    try:
                        if os.path.isfile(file_path) and os.path.getmtime(file_path) < time.time() - 3600:  # Older than 1 hour
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        flash('Temporary files cleaned successfully', 'success')
    except Exception as e:
        flash(f'Error cleaning temporary files: {e}', 'error')
    
    return redirect(url_for('upload_page'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'favicon'),
        'favicon.ico', 
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/view_matches/<path:filename>')
def view_matches(filename):
    """View only the pages of a PDF file that contain search matches"""
    # Automatically clean up old filtered PDFs (older than 1 hour)
    try:
        filtered_dir = os.path.join(app.static_folder, 'temp')
        if os.path.exists(filtered_dir):
            current_time = time.time()
            for temp_file in os.listdir(filtered_dir):
                if temp_file.startswith('filtered_'):
                    file_path = os.path.join(filtered_dir, temp_file)
                    if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > 3600:  # Older than 1 hour
                        try:
                            os.unlink(file_path)
                        except Exception as e:
                            app.logger.warning(f"Could not delete old filtered PDF {temp_file}: {e}")
    except Exception as e:
        app.logger.warning(f"Error during filtered PDF cleanup: {e}")
    
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('view_pdf', filename=filename))
    
    # Find pages with matches
    matching_pages = []
    try:
        # Use the search engine to find which pages match the query
        parser = whoosh.qparser.QueryParser("content", schema=search_engine.index.schema)
        q = parser.parse(query)
        
        with search_engine.index.searcher() as searcher:
            # Get all matches for this specific file
            file_query = f'filename:"{filename}" AND {query}'
            file_parser = whoosh.qparser.MultifieldParser(["content", "filename"], schema=search_engine.index.schema)
            results = searcher.search(file_parser.parse(file_query), limit=100)
            
            # Extract the page numbers from matching results
            for hit in results:
                if hit['filename'] == filename and 'page_num' in hit:
                    matching_pages.append(hit['page_num'])
            
            # Sort the pages
            matching_pages = sorted(set(matching_pages))
    except Exception as e:
        app.logger.error(f"Error finding matching pages: {str(e)}")
    
    if not matching_pages:
        flash('No matches found for the search term', 'warning')
        return redirect(url_for('view_pdf', filename=filename))
    
    # Create temporary PDF with only matching pages
    try:
        import PyPDF2
        from io import BytesIO
        import uuid
        
        # Create a unique ID for this filtered document
        filtered_id = str(uuid.uuid4())
        filtered_filename = f"filtered_{filtered_id}.pdf"
        filtered_path = os.path.join(app.static_folder, 'temp', filtered_filename)
        
        # Make sure the temp directory exists
        os.makedirs(os.path.join(app.static_folder, 'temp'), exist_ok=True)
        
        # Create a new PDF writer
        pdf_writer = PyPDF2.PdfWriter()
        
        # Open the original PDF
        with open(os.path.join(PDF_DIR, filename), 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Add only matching pages to the new PDF
            for page_num in matching_pages:
                if page_num < len(pdf_reader.pages):  # Ensure page exists
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
        
        # Write to a file
        with open(filtered_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        # Store information in session
        session['original_filename'] = filename
        session['matching_pages'] = matching_pages
        session['filtered_filename'] = filtered_filename
        session['query'] = query
        session['filtered_id'] = filtered_id
        
        # Render the viewer template with the filtered PDF
        return render_template('viewer.html',
                             filename=filtered_filename,
                             is_filtered=True,
                             query=query,
                             matching_pages=list(range(len(matching_pages))),  # New page numbers are sequential
                             original_page_map=matching_pages,  # Map of new pages to original pages
                             active_page='documents')
        
    except Exception as e:
        app.logger.error(f"Error creating PDF with matching pages: {str(e)}")
        flash('Error extracting matching pages', 'error')
        return redirect(url_for('view_pdf', filename=filename))

@app.route('/filtered_pdf/<path:filename>')
def serve_filtered_pdf(filename):
    """Serve a filtered PDF file"""
    try:
        # Check if the filename follows our filtered_uuid.pdf pattern
        if not filename.startswith('filtered_') or not filename.endswith('.pdf'):
            abort(403)  # Forbidden
        
        # We'll attempt to serve the file if it exists in the temp directory
        # This approach doesn't rely on the session which can expire
        temp_path = os.path.join(app.static_folder, 'temp')
        file_path = os.path.join(temp_path, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(temp_path, filename)
        else:
            abort(404)  # Not Found
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    # Create required directories
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app.run(host="0.0.0.0",debug=True,port=5000) 