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
    
    // Add page transition class to main content sections
    const mainContent = document.querySelector('.dashboard-main');
    if (mainContent) {
        mainContent.classList.add('page-transition');
    }
    
    // Add animation to cards
    animateElementsOnScroll();
    
    // Initialize tooltip functionality
    initializeTooltips();
    
    // Initialize smooth scrolling for anchor links
    initializeSmoothScrolling();

    // Add subtle hover effects to result cards
    addCardHoverEffects();
    
    // Add parallax effect to background
    addParallaxBackgroundEffect();
    
    // Add highlight pulsing effect
    addHighlightPulseEffect();
    
    // Add this animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes highlight-pulse {
            0% {
                background: linear-gradient(120deg, rgba(254, 67, 101, 0.15), rgba(254, 67, 101, 0.25));
                box-shadow: 0 0 0 rgba(254, 67, 101, 0);
            }
            100% {
                background: linear-gradient(120deg, rgba(254, 67, 101, 0.25), rgba(254, 67, 101, 0.35));
                box-shadow: 0 3px 8px rgba(254, 67, 101, 0.15);
            }
        }
        
        @keyframes pulse-effect {
            0% {
                box-shadow: 0 0 0 0 rgba(59, 91, 217, 0.4);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(59, 91, 217, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(59, 91, 217, 0);
            }
        }
        
        .pulse-effect {
            animation: pulse-effect 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
        }
        
        .elegant-tooltip {
            position: absolute;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            padding: 0.6rem 1rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            pointer-events: none;
            opacity: 0;
            z-index: 1000;
            box-shadow: 0 5px 15px rgba(59, 91, 217, 0.3);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            white-space: nowrap;
            backdrop-filter: blur(4px);
        }
        
        .elegant-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -6px;
            width: 12px;
            height: 12px;
            background: var(--primary-dark);
            transform: rotate(45deg) translateY(-6px);
            z-index: -1;
        }
        
        .elegant-tooltip.visible {
            display: block;
        }
    `;
    document.head.appendChild(style);
});

// Animate elements as they scroll into view
function animateElementsOnScroll() {
    // Only run if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        const cards = document.querySelectorAll('.stat-card, .document-card, .result-card');
        
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Add a small delay based on index for cascade effect
                    const delay = Array.from(cards).indexOf(entry.target) * 50;
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, delay);
                    
                    // Stop observing after animation
                    observer.unobserve(entry.target);
                }
            });
        }, options);
        
        // Set initial styles and observe each card
        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(card);
        });
    }
}

// Initialize tooltips for action buttons
function initializeTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
        const tooltipText = trigger.getAttribute('data-tooltip');
        
        // Create tooltip element with premium design
        const tooltip = document.createElement('div');
        tooltip.className = 'elegant-tooltip';
        tooltip.textContent = tooltipText;
        document.body.appendChild(tooltip);
        
        // Show tooltip on hover with premium animation
        trigger.addEventListener('mouseenter', () => {
            const rect = trigger.getBoundingClientRect();
            tooltip.style.left = (rect.left + rect.width/2) + 'px';
            tooltip.style.top = rect.top - 10 + 'px';
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(15px) translateX(-50%) scale(0.95)';
            tooltip.classList.add('visible');
            
            // Animate in with a slight delay for a more polished feel
            setTimeout(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(-12px) translateX(-50%) scale(1)';
            }, 20);
        });
        
        // Hide tooltip on mouse leave with elegant animation
        trigger.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(15px) translateX(-50%) scale(0.95)';
            
            setTimeout(() => {
                tooltip.classList.remove('visible');
            }, 300);
        });
    });
}

// Initialize smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                e.preventDefault();
                
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL without page reload
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });
}

// Add subtle hover effects to result cards
function addCardHoverEffects() {
    const cards = document.querySelectorAll('.result-card');
    
    cards.forEach((card, index) => {
        // Add staggered entrance animation
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 80)); // Staggered timing
        
        // Add 3D hover effect
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left; 
            const y = e.clientY - rect.top; 
            
            // Calculate rotation based on mouse position
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Limit the rotation to a subtle amount
            const rotateY = ((x - centerX) / centerX) * 2; 
            const rotateX = -((y - centerY) / centerY) * 1;
            
            // Apply the transform with subtle perspective
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
            
            // Dynamic shadow based on mouse position
            const shadowX = (x - centerX) / 20;
            const shadowY = (y - centerY) / 20;
            this.style.boxShadow = `
                ${shadowX}px ${shadowY + 8}px 20px rgba(59, 91, 217, 0.12),
                0 10px 20px rgba(0, 0, 0, 0.04)
            `;
            
            // Subtle gradient shift on hover
            const headerEl = this.querySelector('.result-header');
            if (headerEl) {
                const gradientX = ((x / rect.width) * 100);
                const gradientY = ((y / rect.height) * 100);
                headerEl.style.background = `
                    linear-gradient(
                        ${135 + (x - centerX) / 10}deg, 
                        var(--primary-lightest) ${gradientX * 0.5}%, 
                        rgba(240, 245, 255, 0.8) ${100 - gradientY * 0.5}%
                    )
                `;
            }
        });
        
        card.addEventListener('mouseleave', function() {
            // Reset transforms with a smooth transition
            this.style.transform = '';
            this.style.boxShadow = '';
            
            const headerEl = this.querySelector('.result-header');
            if (headerEl) {
                headerEl.style.background = '';
            }
        });
        
        // Add focus effect for click/tap
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on a link or button
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || 
                e.target.closest('a') || e.target.closest('button')) {
                return;
            }
            
            // Add pulse effect
            this.classList.add('pulse-effect');
            setTimeout(() => {
                this.classList.remove('pulse-effect');
            }, 800);
        });
    });
}

// Add parallax background effect to search results
function addParallaxBackgroundEffect() {
    const container = document.querySelector('.dashboard-view');
    if (!container) return;
    
    window.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        // Apply subtle background shift based on mouse position
        container.style.backgroundImage = `
            radial-gradient(
                circle at ${mouseX * 100}% ${mouseY * 100}%,
                rgba(240, 245, 255, 0.8) 0%,
                rgba(248, 250, 255, 0.4) 50%,
                rgba(255, 255, 255, 0.2) 100%
            )
        `;
    });
}

// Add pulsing highlight effect for search terms
function addHighlightPulseEffect() {
    const highlights = document.querySelectorAll('.match-highlight');
    
    highlights.forEach(highlight => {
        // Initial subtle pulse animation
        highlight.style.animation = 'highlight-pulse 2.5s infinite alternate ease-in-out';
        
        // Enhanced hover effect
        highlight.addEventListener('mouseenter', function() {
            this.style.animation = 'none';
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 3px 10px rgba(254, 67, 101, 0.2)';
            this.style.background = 'linear-gradient(120deg, rgba(254, 67, 101, 0.3), rgba(254, 67, 101, 0.4))';
        });
        
        highlight.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
            this.style.background = '';
            this.style.animation = 'highlight-pulse 2.5s infinite alternate ease-in-out';
        });
    });
}

// Add depth to glassmorphism elements
function addGlassmorphismEffect() {
    const glassElements = document.querySelectorAll('.search-header');
    
    glassElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 10px 30px rgba(31, 38, 135, 0.2)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// Add the dynamic tooltip style
const tooltipStyle = document.createElement('style');
tooltipStyle.textContent = `
    .elegant-tooltip {
        position: absolute;
        background: linear-gradient(135deg, #4a6cf7, #3955d8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        pointer-events: none;
        opacity: 0;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(74, 108, 247, 0.25);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        white-space: nowrap;
    }
    
    .elegant-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -6px;
        width: 12px;
        height: 12px;
        background: #4a6cf7;
        transform: rotate(45deg) translateY(-6px);
        z-index: -1;
    }
    
    .elegant-tooltip.visible {
        display: block;
    }
`;
document.head.appendChild(tooltipStyle); 