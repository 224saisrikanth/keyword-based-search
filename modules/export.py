import csv
import json
import io
from datetime import datetime
from fpdf import FPDF
from flask import make_response, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import re
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import Counter

class ExportManager:
    """Handles exporting search results in different formats"""
    
    @staticmethod
    def export_to_csv(results, query):
        """Export search results to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Filename', 'Page Number', 'Score', 'Excerpt'])
        
        # Write data
        for result in results:
            writer.writerow([
                result['filename'],
                result['page_num'] + 1,  # Make page number 1-based for user
                round(result['score'], 2),
                result['excerpt'].replace('<mark>', '').replace('</mark>', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=search-results-{query.replace(' ', '_')}-{datetime.now().strftime('%Y%m%d')}.csv"
        response.headers["Content-type"] = "text/csv"
        
        return response
    
    @staticmethod
    def export_to_json(results, query):
        """Export search results to JSON format"""
        # Clean up results for export (remove HTML tags, etc.)
        export_results = []
        for result in results:
            export_results.append({
                'filename': result['filename'],
                'page_number': result['page_num'] + 1,
                'score': round(result['score'], 2),
                'excerpt': result['excerpt'].replace('<mark>', '').replace('</mark>', '')
            })
        
        # Create response
        response = make_response(json.dumps(export_results, indent=2))
        response.headers["Content-Disposition"] = f"attachment; filename=search-results-{query.replace(' ', '_')}-{datetime.now().strftime('%Y%m%d')}.json"
        response.headers["Content-type"] = "application/json"
        
        return response
    
    @staticmethod
    def export_to_pdf(results, query):
        """Generate a comprehensive, professional PDF report of search results"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        from flask import send_file
        import re
        from datetime import datetime
        import os
        
        # Create buffer and document
        buffer = BytesIO()
        
        # Document with proper margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f"Search Results for '{query}'",
            author="PDF Search Engine"
        )
        
        # Define professional color scheme
        primary_color = colors.HexColor('#2c3e50')    # Dark blue-gray
        secondary_color = colors.HexColor('#3498db')   # Blue
        highlight_color = colors.HexColor('#f39c12')   # Orange-yellow
        accent_color = colors.HexColor('#27ae60')      # Green
        bg_light = colors.HexColor('#f8f9fa')          # Light gray
        border_color = colors.HexColor('#dfe4ea')      # Light blue-gray
        
        # Get basic styles
        styles = getSampleStyleSheet()
        
        # Define professional styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles["Title"],
            fontSize=24,
            alignment=1,  # Center
            textColor=primary_color,
            spaceAfter=24,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles["Title"],
            fontSize=18,
            alignment=1,  # Center
            textColor=secondary_color,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        heading1_style = ParagraphStyle(
            'Heading1',
            parent=styles["Heading1"],
            fontSize=16,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'Heading2',
            parent=styles["Heading2"],
            fontSize=14,
            textColor=secondary_color,
            spaceBefore=10,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        heading3_style = ParagraphStyle(
            'Heading3',
            parent=styles["Heading3"],
            fontSize=12,
            textColor=accent_color,
            spaceBefore=8,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            fontName='Helvetica'
        )
        
        # Special style for methodology items to ensure line breaks
        methodology_item_style = ParagraphStyle(
            'MethodologyItem',
            parent=normal_style,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20,
            leading=16  # Increased leading for better line spacing
        )
        
        # Define TOC style
        toc_style = ParagraphStyle(
            'TOCStyle',
            parent=styles["Normal"],
            fontSize=12,
            textColor=primary_color,
            spaceAfter=6,
            leftIndent=20,
            bulletFontName='Helvetica',
            bulletFontSize=10,
            bulletColor=primary_color,
            bulletIndent=10,
        )
        
        # Define metadata style
        metadata_style = ParagraphStyle(
            'MetadataStyle',
            parent=styles["Normal"],
            fontSize=10,
            textColor=secondary_color,
            spaceAfter=6,
            leftIndent=20,
            rightIndent=20,
            leading=12
        )
        
        # Custom separator flowable
        class Separator(Flowable):
            def __init__(self, width, thickness=1, color=colors.grey):
                Flowable.__init__(self)
                self.width = width
                self.thickness = thickness
                self.color = color
                
            def draw(self):
                self.canv.setStrokeColor(self.color)
                self.canv.setLineWidth(self.thickness)
                self.canv.line(0, 0, self.width, 0)
        
        # Create document elements
        elements = []
        
        # Get current date/time for the report
        current_date = datetime.now().strftime('%B %d, %Y')
        current_time = datetime.now().strftime('%I:%M %p')
        
        # --- COVER PAGE ---
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph("SEARCH RESULTS REPORT", title_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Report metadata table
        report_data = [["Search Query:", query], ["Results Found:", str(len(results))], ["Documents:", str(len(set(r['filename'] for r in results)))],["Date Generated:", current_date],["Time Generated:", current_time]]
        
        report_table = Table(report_data, colWidths=[2*inch, 3.5*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), bg_light),
            ('TEXTCOLOR', (0, 0), (0, -1), primary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ]))
        
        elements.append(report_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Description of report
        report_desc = f"""
        This report contains the results of a search for "<b>{query}</b>" across the PDF document collection. 
        Each result includes the matching content and its surrounding context to provide a comprehensive view of 
        how the search terms appear within the documents.
        """
        elements.append(Paragraph(report_desc, normal_style))
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("PDF Search Engine", subtitle_style))
        elements.append(PageBreak())
        
        # --- TABLE OF CONTENTS ---
        elements.append(Paragraph("TABLE OF CONTENTS", heading1_style))
        elements.append(Separator(6.5*inch, 1, primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        toc_items = ["1. Overview","2. Methodology","3. Search Results",]
        
        # Add result entries to TOC
        for i, result in enumerate(results, 1):
            filename = result['filename']
            if len(filename) > 40:
                filename = filename[:37] + "..."
            toc_items.append(f"   3.{i} {filename} (Page {result['page'] + 1})")
        
        toc_items.append("4. Conclusion")
        
        for item in toc_items:
            elements.append(Paragraph(item, toc_style))
            elements.append(Spacer(1, 0.05*inch))
        
        elements.append(PageBreak())
        
        # --- OVERVIEW SECTION ---
        elements.append(Paragraph("1. OVERVIEW", heading1_style))
        elements.append(Separator(6.5*inch, 1, primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        overview_text = f"""
        This report presents the results of a search for "<b>{query}</b>" performed on {current_date}.
        The search engine examined all indexed PDF documents in the collection and identified 
        {len(results)} relevant matches across {len(set(r['filename'] for r in results))} documents.
        
        The search was performed using a text-based search algorithm that identifies matches based on keyword relevance
        and textual similarity. Each result shown includes the document information, page number, and excerpts
        showing how the search terms appear in context.
        """
        
        elements.append(Paragraph(overview_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # --- METHODOLOGY SECTION ---
        elements.append(Paragraph("2. METHODOLOGY", heading1_style))
        elements.append(Separator(6.5*inch, 1, primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        methodology_intro = """
        The search process utilized the following methodology to identify and extract relevant content:
        """
        elements.append(Paragraph(methodology_intro, normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Each methodology item as a separate paragraph with its own style for proper line breaks
        elements.append(Paragraph("1. Query Analysis: The search terms were processed to identify keywords and phrases.", methodology_item_style))
        elements.append(Paragraph("2. Document Scanning: All indexed PDF documents were scanned for matches to the search terms.", methodology_item_style))
        elements.append(Paragraph("3. Text Extraction: Relevant sections of text containing the search terms were extracted.", methodology_item_style))
        elements.append(Paragraph("4. Context Retrieval: Additional text before and after the matches was captured to provide context.", methodology_item_style))
        elements.append(Paragraph("5. Report Generation: The results were compiled into this structured report format.", methodology_item_style))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # --- RESULTS SECTION ---
        elements.append(Paragraph("3. SEARCH RESULTS", heading1_style))
        elements.append(Separator(6.5*inch, 1, primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        results_intro = f"""
        The following section presents the {len(results)} results found for the search query "<b>{query}</b>".
        Each result includes the document information, page number, and the extracted content showing
        the search term in context.
        """
        elements.append(Paragraph(results_intro, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Process each result
        for i, result in enumerate(results):
            # Change this line to avoid using 'section' key which doesn't exist
            section_label = f"Section {i + 1}: Document - {result['filename']}"
            section_number = i + 1
            elements.append(Paragraph(f"3.{section_number} {section_label}", heading2_style))
            elements.append(Separator(6.5*inch, 1, secondary_color))
            elements.append(Spacer(1, 0.2*inch))
            
            # Document info metadata
            meta_data = [
                ["Document:", result['filename']],
                ["Page:", f"Page {result['page'] + 1}"],
                ["Section:", f"Document Content"],  # Use a generic section label instead
            ]
            
            # Create a narrower table for better display
            meta_table = Table(meta_data, colWidths=[1.25*inch, 4.75*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), bg_light),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ]))
            
            elements.append(meta_table)
            elements.append(Spacer(1, 0.2*inch))
            
            try:
                # Process the result content safely - strip HTML
                clean_text = re.sub(r'<[^>]+>', '', result.get('highlight', ''))
                clean_text = ExportManager._sanitize_for_pdf(clean_text)
                
                # Break text into smaller chunks (reduced to 200 chars for better display)
                chunks = []
                max_chunk_size = 200
                
                # Process text in smaller chunks
                for start in range(0, len(clean_text), max_chunk_size):
                    end = min(start + max_chunk_size, len(clean_text))
                    # Try to break at a space to avoid cutting words
                    if end < len(clean_text) and clean_text[end] != ' ':
                        # Find the last space before the cutoff
                        last_space = clean_text.rfind(' ', start, end)
                        if last_space > start:
                            end = last_space
                    chunks.append(clean_text[start:end])
                
                # If no chunks were created, use the original text
                if not chunks:
                    chunks = [clean_text]
                
                elements.append(Paragraph(f"{section_number}.1 Matched Content", heading3_style))
                
                # Create content boxes for each chunk to prevent overflow
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_label = f"Extract {chunk_idx+1}/{len(chunks)}" if len(chunks) > 1 else "Extract"
                    elements.append(Paragraph(chunk_label, metadata_style))
                    
                    # Use a more limited width for content to ensure it fits well
                    content_box = Table([[chunk]], colWidths=[5.5*inch])
                    content_box.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.darkgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('PADDING', (0, 0), (-1, -1), 10),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),  # Increased padding
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),  # Increased padding
                    ]))
                    
                    elements.append(content_box)
                    elements.append(Spacer(1, 0.1*inch))
                
                # Add context sections if available
                if result.get('context_before'):
                    context_before = re.sub(r'<[^>]+>', '', result['context_before'])
                    context_before = ExportManager._sanitize_for_pdf(context_before)
                    
                    # Break into smaller chunks (200 chars)
                    before_chunks = []
                    for start in range(0, len(context_before), max_chunk_size):
                        end = min(start + max_chunk_size, len(context_before))
                        if end < len(context_before) and context_before[end] != ' ':
                            last_space = context_before.rfind(' ', start, end)
                            if last_space > start:
                                end = last_space
                        before_chunks.append(context_before[start:end])
                    
                    if not before_chunks:
                        before_chunks = [context_before]
                    
                    elements.append(Paragraph(f"{section_number}.2 Context Before", heading3_style))
                    
                    # Create content boxes for each chunk
                    for chunk_idx, chunk in enumerate(before_chunks):
                        if len(before_chunks) > 1:
                            elements.append(Paragraph(f"Part {chunk_idx+1}/{len(before_chunks)}", metadata_style))
                        
                        context_box = Table([[chunk]], colWidths=[5.5*inch])
                        context_box.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
                            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('PADDING', (0, 0), (-1, -1), 10),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('WORDWRAP', (0, 0), (-1, -1), True),
                            ('LEFTPADDING', (0, 0), (-1, -1), 12),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ]))
                        
                        elements.append(context_box)
                        elements.append(Spacer(1, 0.1*inch))
                
                if result.get('context_after'):
                    context_after = re.sub(r'<[^>]+>', '', result['context_after'])
                    context_after = ExportManager._sanitize_for_pdf(context_after)
                    
                    # Break into smaller chunks (200 chars)
                    after_chunks = []
                    for start in range(0, len(context_after), max_chunk_size):
                        end = min(start + max_chunk_size, len(context_after))
                        if end < len(context_after) and context_after[end] != ' ':
                            last_space = context_after.rfind(' ', start, end)
                            if last_space > start:
                                end = last_space
                        after_chunks.append(context_after[start:end])
                    
                    if not after_chunks:
                        after_chunks = [context_after]
                    
                    elements.append(Paragraph(f"{section_number}.3 Context After", heading3_style))
                    
                    # Create content boxes for each chunk
                    for chunk_idx, chunk in enumerate(after_chunks):
                        if len(after_chunks) > 1:
                            elements.append(Paragraph(f"Part {chunk_idx+1}/{len(after_chunks)}", metadata_style))
                        
                        context_box = Table([[chunk]], colWidths=[5.5*inch])
                        context_box.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
                            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('PADDING', (0, 0), (-1, -1), 10),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('WORDWRAP', (0, 0), (-1, -1), True),
                            ('LEFTPADDING', (0, 0), (-1, -1), 12),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ]))
                        
                        elements.append(context_box)
                        elements.append(Spacer(1, 0.1*inch))
                
            except Exception as e:
                elements.append(Paragraph("Error displaying content: " + str(e)[:100], normal_style))
            
            # Add result separator with enhanced styling
            elements.append(Spacer(1, 0.3*inch))
            if i < len(results):
                elements.append(Separator(6.5*inch, 2, colors.lightgrey))
                elements.append(Spacer(1, 0.3*inch))
                
                # Add page break for each result for better readability
                elements.append(PageBreak())
        
        # --- CONCLUSION SECTION ---
        elements.append(Paragraph("4. CONCLUSION", heading1_style))
        elements.append(Separator(6.5*inch, 1, primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        conclusion_text = f"""
        This report presents search results for the query "<b>{query}</b>". 
        The search process identified {len(results)} relevant matches across {len(set(r['filename'] for r in results))} 
        documents in the document library.
        
        Each result includes the matched content along with contextual information to provide a comprehensive 
        understanding of how the search terms appear within the documents.
        
        For further analysis or to view the complete documents, please access the original files through 
        the PDF Search Engine application.
        """
        
        elements.append(Paragraph(conclusion_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add professional footer with dynamic page numbers
        def add_page_numbers(canvas, doc):
            """Add header and footer to each page"""
            canvas.saveState()
            
            # Header with gradient effect
            canvas.setFillColor(primary_color)
            canvas.rect(doc.leftMargin, letter[1] - 0.4*inch, letter[0] - 1.5*inch, 0.2*inch, fill=1)
            canvas.setFillColor(colors.white)
            canvas.setFont('Helvetica-Bold', 9)
            canvas.drawString(doc.leftMargin + 0.1*inch, letter[1] - 0.3*inch, "PDF SEARCH ENGINE")
            
            # Different header for first page (cover page)
            if canvas.getPageNumber() > 1:
                canvas.setFillColor(colors.black)
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(letter[0] - doc.rightMargin, letter[1] - 0.3*inch, f"Search Query: \"{query}\"")
            
            # Footer
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            
            # Footer line
            canvas.setStrokeColor(colors.grey)
            canvas.line(doc.leftMargin, 0.7*inch, letter[0]-doc.rightMargin, 0.7*inch)
            
            canvas.setFillColor(colors.darkgrey)
            canvas.drawString(doc.leftMargin, 0.5*inch, f"Generated on {current_date}")
            canvas.setFillColor(primary_color)
            canvas.drawRightString(letter[0] - doc.rightMargin, 0.5*inch, f"Page {page_num}")
            
            canvas.restoreState()
        
        # Build the PDF with professional headers and footers
        doc.build(elements, onFirstPage=add_page_numbers, onLaterPages=add_page_numbers)
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"SearchResults_{query.replace(' ', '_')}_{timestamp}.pdf",
            mimetype='application/pdf'
        )
    
    @staticmethod
    def _sanitize_for_pdf(text):
        """Sanitize text for PDF output - much simpler version"""
        if not text:
            return ""
        
        # Replace common problematic characters
        replacements = {
            '\u2013': '-',    # en dash
            '\u2014': '--',   # em dash
            '\u2018': "'",    # left single quotation
            '\u2019': "'",    # right single quotation
            '\u201c': '"',    # left double quotation
            '\u201d': '"',    # right double quotation
            '\u2022': '*',    # bullet
            '\u2026': '...',  # ellipsis
            '\u00a0': ' ',    # non-breaking space
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Replace any other potentially problematic characters
        text = ''.join(c if ord(c) < 128 else '?' for c in text)
        
        return text 