function debugSearchNavigation() {
    console.log('Search Navigation Status:');
    console.log('- Current Path:', window.location.pathname);
    console.log('- Current URL:', window.location.href);
    console.log('- Referrer:', document.referrer);
    console.log('- localStorage.lastSearchUrl:', localStorage.getItem('lastSearchUrl'));
    console.log('- localStorage.lastSearchQuery:', localStorage.getItem('lastSearchQuery'));
}

function saveSearchState() {
    if (window.location.pathname === '/search') {
        // Store the full search URL including all parameters 
        const fullSearchUrl = window.location.href;
        localStorage.setItem('lastSearchUrl', fullSearchUrl);
        console.log('Saved search URL:', fullSearchUrl);
        
        // Also store just the query for fallback
        const params = new URLSearchParams(window.location.search);
        const query = params.get('query');
        if (query) {
            localStorage.setItem('lastSearchQuery', query);
            console.log('Saved search query:', query);
        }
        
        // Debug
        debugSearchNavigation();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Save search state on page load
    saveSearchState();
    
    // Add event listener to search forms
    document.querySelectorAll('form.search-form').forEach(form => {
        form.addEventListener('submit', function() {
            const queryInput = this.querySelector('input[name="query"]');
            if (queryInput && queryInput.value) {
                localStorage.setItem('lastSearchQuery', queryInput.value);
            }
        });
    });
    
    // ===== Handle direct URL navigation and back button =====
    const currentPath = window.location.pathname;
    const searchParams = new URLSearchParams(window.location.search);
    
    // Store original document.referrer for back navigation
    const referrer = document.referrer;
    
    // Set active sidebar item based on URL
    const setActiveSidebarItem = (path) => {
        const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            const isActive = 
                href === path || 
                (path.includes('/search') && link.id === 'nav-search') ||
                (path.includes('/documents') && link.id === 'nav-documents') ||
                (path.includes('/upload') && link.id === 'nav-upload');
            
            link.parentElement.classList.toggle('active', isActive);
        });
    };
    
    // Set initial active state
    setActiveSidebarItem(currentPath);
    
    // Fix back button behavior
    window.addEventListener('popstate', function(event) {
        // Use History API state if available
        const historyPath = event.state?.path || window.location.pathname;
        setActiveSidebarItem(historyPath);
    });
    
    // Update history state when navigation occurs
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't prevent default, allow normal navigation
            // But add state to history
            const path = this.getAttribute('href');
            history.pushState({ path: path }, '', path);
        });
    });
    
    // Set initial history state if needed
    if (!history.state) {
        history.replaceState({ path: currentPath }, '', currentPath);
    }
    
    // Fix for document viewer back button
    if (currentPath.includes('/view/')) {
        // If we're viewing a document, we should remember where we came from
        const fromSearch = referrer && (
            referrer.includes('/search') || 
            localStorage.getItem('lastSearchQuery')
        );
        
        if (fromSearch) {
            // Add a data attribute to the back button
            const backLinks = document.querySelectorAll('.back-to-results');
            backLinks.forEach(link => {
                const lastQuery = localStorage.getItem('lastSearchQuery');
                if (lastQuery) {
                    link.setAttribute('href', `/search?query=${encodeURIComponent(lastQuery)}`);
                    link.addEventListener('click', function(e) {
                        // Don't actually follow the link, use history.back() which is more reliable
                        e.preventDefault();
                        history.back();
                    });
                }
            });
        }
    }
    
    // For search pages, remember the query
    if (currentPath.includes('/search')) {
        const query = searchParams.get('query');
        if (query) {
            localStorage.setItem('lastSearchQuery', query);
        }
    }
    
    // Add this to document viewers
    if (document.querySelector('.pdf-viewer-container')) {
        // Add back button to PDF viewer if it doesn't exist
        if (!document.querySelector('.back-to-results')) {
            const viewerHeader = document.querySelector('.viewer-header');
            if (viewerHeader) {
                const backBtn = document.createElement('a');
                backBtn.className = 'btn-secondary back-to-results';
                backBtn.innerHTML = '<i class="fas fa-arrow-left"></i> Back to Results';
                backBtn.href = '#';
                backBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    history.back();
                });
                viewerHeader.prepend(backBtn);
            }
        }
    }
    
    // ===== Toggle sidebar on mobile =====
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const dashboardContainer = document.querySelector('.dashboard-container');
    
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            dashboardContainer.classList.toggle('sidebar-collapsed');
        });
    }
    
    // ===== Flash Message Close Buttons =====
    const closeMessageBtns = document.querySelectorAll('.close-message');
    closeMessageBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.message').style.display = 'none';
        });
    });
    
    // ===== PDF Document Actions =====
    // Delete buttons (individual)
    const deleteButtons = document.querySelectorAll('.delete-action, .table-action.delete-action');
    const deleteModal = document.getElementById('delete-modal');
    const deleteFilenameInput = document.getElementById('delete-filename');
    
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const filename = this.getAttribute('data-filename');
                
                if (deleteModal && deleteFilenameInput) {
                    deleteFilenameInput.value = filename;
                    
                    // Update modal text
                    const modalText = deleteModal.querySelector('p');
                    if (modalText) {
                        modalText.innerHTML = `Are you sure you want to delete <strong>${filename}</strong>? This action cannot be undone.`;
                    }
                    
                    deleteModal.style.display = 'block';
                }
            });
        });
    }
    
    // Rename buttons
    const renameButtons = document.querySelectorAll('.rename-action, .table-action.rename-action');
    const renameModal = document.getElementById('rename-modal');
    const originalFilenameInput = document.getElementById('original-filename');
    const newFilenameInput = document.getElementById('new-filename');
    
    if (renameButtons.length > 0) {
        renameButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const filename = this.getAttribute('data-filename');
                
                if (renameModal && originalFilenameInput && newFilenameInput) {
                    originalFilenameInput.value = filename;
                    newFilenameInput.value = filename;
                    
                    renameModal.style.display = 'block';
                }
            });
        });
    }
    
    // ===== Modal Controls =====
    // Close buttons for modals
    const closeButtons = document.querySelectorAll('.close, .cancel-action, .cancel-delete');
    const modals = document.querySelectorAll('.modal');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Escape key to close modals
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });
    
    // ===== Document View Switching (Grid/List) =====
    const viewOptions = document.querySelectorAll('.view-option');
    const gridView = document.getElementById('documents-grid-view');
    const listView = document.getElementById('documents-list-view');
    
    if (viewOptions.length > 0 && gridView && listView) {
        viewOptions.forEach(option => {
            option.addEventListener('click', function() {
                viewOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
                
                const viewType = this.getAttribute('data-view');
                if (viewType === 'grid') {
                    gridView.classList.add('active-view');
                    listView.classList.remove('active-view');
                } else {
                    gridView.classList.remove('active-view');
                    listView.classList.add('active-view');
                }
            });
        });
    }
    
    // ===== Checkbox Selection =====
    const selectAllCheckbox = document.getElementById('select-all-pdfs');
    const pdfCheckboxes = document.querySelectorAll('.pdf-select');
    const deleteSelectedBtn = document.getElementById('delete-selected-btn');
    const bulkDeleteModal = document.getElementById('bulk-delete-modal');
    
    // Handle select all
    if (selectAllCheckbox && pdfCheckboxes.length > 0) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            
            pdfCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            
            updateDeleteSelectedButton();
        });
        
        // Individual checkbox changes
        pdfCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateDeleteSelectedButton();
                
                // Update select all checkbox state
                const allChecked = Array.from(pdfCheckboxes).every(cb => cb.checked);
                const someChecked = Array.from(pdfCheckboxes).some(cb => cb.checked);
                
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = someChecked && !allChecked;
            });
        });
    }
    
    // Delete selected button
    if (deleteSelectedBtn && bulkDeleteModal) {
        deleteSelectedBtn.addEventListener('click', function() {
            const checkedBoxes = document.querySelectorAll('.pdf-select:checked');
            const selectedFilesList = document.getElementById('selected-files-list');
            const selectedFilesInputs = document.getElementById('selected-files-inputs');
            
            if (checkedBoxes.length > 0 && selectedFilesList && selectedFilesInputs) {
                // Clear previous list and inputs
                selectedFilesList.innerHTML = '';
                selectedFilesInputs.innerHTML = '';
                
                // Add files to list and hidden inputs
                checkedBoxes.forEach(checkbox => {
                    const filename = checkbox.getAttribute('data-filename');
                    
                    // Create list item
                    const listItem = document.createElement('div');
                    listItem.className = 'selected-file-item';
                    listItem.textContent = filename;
                    selectedFilesList.appendChild(listItem);
                    
                    // Create hidden input
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'filenames[]';
                    input.value = filename;
                    selectedFilesInputs.appendChild(input);
                });
                
                // Update modal title
                const modalTitle = bulkDeleteModal.querySelector('h2');
                if (modalTitle) {
                    modalTitle.textContent = `Delete ${checkedBoxes.length} Selected PDF${checkedBoxes.length > 1 ? 's' : ''}`;
                }
                
                // Show the modal
                bulkDeleteModal.style.display = 'block';
            }
        });
    }
    
    // Update delete selected button state
    function updateDeleteSelectedButton() {
        if (!deleteSelectedBtn) return;
        
        const checkedBoxes = document.querySelectorAll('.pdf-select:checked');
        const count = checkedBoxes.length;
        
        // Update button state
        deleteSelectedBtn.disabled = count === 0;
        
        // Update button text
        if (count > 0) {
            deleteSelectedBtn.textContent = `Delete Selected (${count})`;
        } else {
            deleteSelectedBtn.textContent = 'Delete Selected';
        }
    }
    
    // Initialize button state if needed
    if (deleteSelectedBtn) {
        updateDeleteSelectedButton();
    }
}); 