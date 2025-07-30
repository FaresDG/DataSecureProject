// Custom JavaScript for the François Mitterrand Middle School intranet

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirmation for delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Animation d'apparition pour les cartes
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });

    // Client-side validation for forms
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Toast notification system
    function showToast(message, type = 'info') {
        var toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        var toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toastElement);
        var toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove element after it is closed
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    // Expose showToast globally
    window.showToast = showToast;

    // Confirmation modal handling
    var confirmModal = document.getElementById('confirmModal');
    if (confirmModal) {
        confirmModal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var action = button.getAttribute('data-action');
            var message = button.getAttribute('data-message') || 'Are you sure you want to perform this action?';
            
            var modalBody = confirmModal.querySelector('.modal-body');
            var confirmButton = confirmModal.querySelector('#confirmAction');
            
            modalBody.textContent = message;
            confirmButton.onclick = function() {
                if (action) {
                    window.location.href = action;
                }
            };
        });
    }

    // Real-time table search
    var searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(function(input) {
        var tableId = input.getAttribute('data-table-search');
        var table = document.getElementById(tableId);
        
        if (table) {
            input.addEventListener('keyup', function() {
                var filter = input.value.toLowerCase();
                var rows = table.getElementsByTagName('tr');
                
                for (var i = 1; i < rows.length; i++) { // Skip header row
                    var row = rows[i];
                    var cells = row.getElementsByTagName('td');
                    var match = false;
                    
                    for (var j = 0; j < cells.length; j++) {
                        if (cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
                            match = true;
                            break;
                        }
                    }
                    
                    row.style.display = match ? '' : 'none';
                }
            });
        }
    });

    // Lazy loading images
    var images = document.querySelectorAll('img[data-src]');
    var imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(function(img) {
        imageObserver.observe(img);
    });

    // Auto-save forms (draft)
    var autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(function(form) {
        var formId = form.id;
        if (formId) {
            // Restore saved data
            var savedData = localStorage.getItem('form_' + formId);
            if (savedData) {
                try {
                    var data = JSON.parse(savedData);
                    Object.keys(data).forEach(function(key) {
                        var field = form.querySelector('[name="' + key + '"]');
                        if (field) {
                            field.value = data[key];
                        }
                    });
                } catch (e) {
                    console.error('Error restoring form data:', e);
                }
            }

            // Save changes
            form.addEventListener('input', function() {
                var formData = new FormData(form);
                var data = {};
                for (var pair of formData.entries()) {
                    data[pair[0]] = pair[1];
                }
                localStorage.setItem('form_' + formId, JSON.stringify(data));
            });

            // Clean saved data after successful submit
            form.addEventListener('submit', function() {
                localStorage.removeItem('form_' + formId);
            });
        }
    });
});

// Global utilities
window.SchoolIntranet = {
    // Format a grade with color
    formatGrade: function(grade, maxGrade = 20) {
        var percentage = (grade / maxGrade) * 100;
        var className = 'text-success';
        
        if (percentage < 50) {
            className = 'text-danger';
        } else if (percentage < 70) {
            className = 'text-warning';
        }
        
        return `<span class="${className}">${grade.toFixed(1)}/${maxGrade}</span>`;
    },

    // Format a date in French
    formatDate: function(dateString) {
        var date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Calculate the average of an array of grades
    calculateAverage: function(grades) {
        if (grades.length === 0) return 0;
        var sum = grades.reduce(function(a, b) { return a + b; }, 0);
        return sum / grades.length;
    },

    // Show a loader
    showLoader: function(element) {
        if (element) {
            element.innerHTML = '<div class="spinner-custom mx-auto"></div>';
        }
    },

    // Hide a loader
    hideLoader: function(element, originalContent) {
        if (element) {
            element.innerHTML = originalContent || '';
        }
    }
};