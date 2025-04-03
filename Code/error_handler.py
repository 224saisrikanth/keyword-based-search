from flask import jsonify, render_template, flash
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles application errors with appropriate responses"""
    
    @staticmethod
    def handle_error(error, is_ajax=False):
        """
        Handle errors with appropriate responses based on request type
        
        Args:
            error: The exception that occurred
            is_ajax: Whether the request is an AJAX request
        
        Returns:
            Appropriate response based on request type
        """
        error_message = str(error)
        logger.error(f"Error occurred: {error_message}")
        logger.error(traceback.format_exc())
        
        if is_ajax:
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
        else:
            flash(f"An error occurred: {error_message}", "error")
            return render_template(
                'error.html',
                error_message=error_message,
                error_trace=traceback.format_exc() if logger.level == logging.DEBUG else None
            ), 500
    
    @staticmethod
    def not_found_error(resource_type="Page", resource_id=None):
        """Handle 404 not found errors"""
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        
        logger.warning(message)
        return render_template('error.html', error_message=message), 404
    
    @staticmethod
    def validation_error(message, is_ajax=False):
        """Handle validation errors"""
        logger.warning(f"Validation error: {message}")
        
        if is_ajax:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        else:
            flash(f"Validation error: {message}", "error")
            return render_template('error.html', error_message=message), 400 