// College Mess Feedback Portal - Frontend JavaScript with Backend Integration
// Enhanced with API integration for voting, feedback, and complaints

// Configuration
const API_BASE_URL = window.location.origin + '/api';

// Utility functions
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}

function showLoading(show = true) {
    let loader = document.getElementById('loading-overlay');
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'loading-overlay';
            loader.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    } else {
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

// API functions
async function makeAPICall(endpoint, method = 'GET', data = null) {
    showLoading(true);
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error?.message || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    } finally {
        showLoading(false);
    }
}

// Voting functionality
async function submitVote(day, meal, dish) {
    try {
        const result = await makeAPICall('/vote', 'POST', {
            day: day,
            meal: meal,
            dish: dish
        });
        
        showNotification('Vote submitted successfully!', 'success');
        
        // Store vote in localStorage for UI updates
        const voteKey = `vote_${day}_${meal}`;
        localStorage.setItem(voteKey, dish);
        
        return result;
    } catch (error) {
        if (error.message.includes('already voted')) {
            showNotification('You have already voted for this meal!', 'warning');
        } else {
            showNotification('Failed to submit vote. Please try again.', 'error');
        }
        throw error;
    }
}

async function checkVoteStatus(day, meal) {
    try {
        const result = await makeAPICall('/check-vote', 'POST', {
            day: day,
            meal: meal
        });
        
        return result.has_voted;
    } catch (error) {
        console.error('Error checking vote status:', error);
        return false;
    }
}

// Feedback functionality
async function submitFeedback(feedbackType, message, rating) {
    try {
        const result = await makeAPICall('/feedback', 'POST', {
            feedback_type: feedbackType,
            message: message,
            rating: rating
        });
        
        showNotification('Feedback submitted successfully!', 'success');
        return result;
    } catch (error) {
        showNotification('Failed to submit feedback. Please try again.', 'error');
        throw error;
    }
}

// Complaint functionality
async function submitComplaint(category, message, urgency) {
    try {
        const result = await makeAPICall('/complaint', 'POST', {
            category: category,
            message: message,
            urgency: urgency
        });
        
        showNotification('Complaint submitted successfully!', 'success');
        return result;
    } catch (error) {
        showNotification('Failed to submit complaint. Please try again.', 'error');
        throw error;
    }
}

// Menu suggestion functionality
async function submitMenuSuggestion(dishName, mealType, ingredients, description) {
    try {
        const result = await makeAPICall('/menu-suggestion', 'POST', {
            dish_name: dishName,
            meal_type: mealType,
            ingredients: ingredients,
            description: description
        });
        
        showNotification('Menu suggestion submitted successfully!', 'success');
        return result;
    } catch (error) {
        showNotification('Failed to submit menu suggestion. Please try again.', 'error');
        throw error;
    }
}

// Global variables for modal functionality
let currentVoteDay = '';
let currentVoteMeal = '';
let selectedDish = '';
let currentRating = 0;

// Menu options for different meals
const menuOptions = {
    breakfast: [
        'Idli Sambar',
        'Poha with Chutney',
        'Upma',
        'Bread Butter Jam'
    ],
    lunch: [
        'Dal Rice',
        'Rajma Chawal',
        'Chole Bhature',
        'Biryani'
    ],
    snacks: [
        'Samosa',
        'Pakora',
        'Sandwich',
        'Tea & Biscuits'
    ],
    dinner: [
        'Roti Sabzi',
        'Fried Rice',
        'Pasta',
        'Soup & Bread'
    ]
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeScrollAnimations();
    initializeStarRating();
    initializeFormHandlers();
    loadVotedMeals();
    initializePDFFunctions();
    addNotificationStyles();
});

// Navigation functionality
function initializeNavigation() {
    const navbar = document.getElementById('navbar');
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    // Always show navbar on all pages
    if (navbar) {
        navbar.classList.remove('hidden');
        navbar.classList.add('visible');
    }
    
    // Mobile menu toggle
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
}

// Smooth scroll to about section
function scrollToAbout() {
    const aboutSection = document.getElementById('about');
    if (aboutSection) {
        aboutSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// PDF functionality
function initializePDFFunctions() {
    // This would be implemented with actual PDF generation/download
    // For demo purposes, we'll show notifications
}

function downloadPDF() {
    showNotification('PDF download started!', 'success');
    // In a real application, this would trigger PDF download
    setTimeout(() => {
        showNotification('PDF download completed!', 'success');
    }, 2000);
}

function printPDF() {
    window.print();
}

// Open vote modal
async function openVoteModal(day, meal) {
    currentVoteDay = day;
    currentVoteMeal = meal;
    
    const modal = document.getElementById('voteModal');
    const modalTitle = document.getElementById('modalTitle');
    const dishOptions = document.getElementById('dishOptions');
    
    if (!modal || !modalTitle || !dishOptions) {
        console.error('Modal elements not found');
        return;
    }
    
    // Check if already voted using backend
    const hasVoted = await checkVoteStatus(day, meal);
    if (hasVoted) {
        showNotification('You have already voted for this meal!', 'warning');
        return;
    }
    
    // Set modal title
    modalTitle.textContent = `Vote for ${capitalizeFirst(day)} ${capitalizeFirst(meal)}`;
    
    // Clear previous options
    dishOptions.innerHTML = '';
    
    // Add dish options
    const dishes = menuOptions[meal] || [];
    dishes.forEach((dish, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'dish-option';
        optionDiv.onclick = () => selectDish(dish, optionDiv);
        
        optionDiv.innerHTML = `
            <input type="radio" name="dish" value="${dish}" id="dish_${index}">
            <label for="dish_${index}">${dish}</label>
        `;
        
        dishOptions.appendChild(optionDiv);
    });
    
    // Reset selected dish
    selectedDish = '';
    updateVoteButton();
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close vote modal
function closeVoteModal() {
    const modal = document.getElementById('voteModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        selectedDish = '';
    }
}

// Select dish option
function selectDish(dish, element) {
    // Remove previous selection
    document.querySelectorAll('.dish-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked element
    element.classList.add('selected');
    element.querySelector('input[type="radio"]').checked = true;
    
    selectedDish = dish;
    updateVoteButton();
}

// Update vote button state
function updateVoteButton() {
    const voteBtn = document.getElementById('voteBtn');
    if (voteBtn) {
        if (selectedDish) {
            voteBtn.disabled = false;
            voteBtn.textContent = 'Submit Vote';
        } else {
            voteBtn.disabled = true;
            voteBtn.textContent = 'Select a dish to vote';
        }
    }
}

// Submit vote
async function submitVoteFromModal() {
    if (!selectedDish) {
        showNotification('Please select a dish to vote for!', 'warning');
        return;
    }
    
    try {
        await submitVote(currentVoteDay, currentVoteMeal, selectedDish);
        
        // Update UI to show voted state
        const mealCell = document.querySelector(`[onclick="openVoteModal('${currentVoteDay}', '${currentVoteMeal}')"]`);
        if (mealCell) {
            mealCell.classList.add('voted');
            mealCell.innerHTML = '<span>✓ Voted</span>';
            mealCell.onclick = null;
        }
        
        // Close modal
        closeVoteModal();
    } catch (error) {
        // Error already handled in submitVote function
    }
}

// Load previously voted meals
async function loadVotedMeals() {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const meals = ['breakfast', 'lunch', 'snacks', 'dinner'];
    
    for (const day of days) {
        for (const meal of meals) {
            try {
                const hasVoted = await checkVoteStatus(day, meal);
                if (hasVoted) {
                    const mealCell = document.querySelector(`[onclick="openVoteModal('${day}', '${meal}')"]`);
                    if (mealCell) {
                        mealCell.classList.add('voted');
                        mealCell.innerHTML = '<span>✓ Voted</span>';
                        mealCell.onclick = null;
                    }
                }
            } catch (error) {
                console.error(`Error checking vote status for ${day} ${meal}:`, error);
            }
        }
    }
}

// Initialize star rating system
function initializeStarRating() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating');
    
    if (stars.length === 0) return; // No stars on this page
    
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            currentRating = index + 1;
            if (ratingInput) ratingInput.value = currentRating;
            updateStarDisplay();
        });
        
        star.addEventListener('mouseover', () => {
            highlightStars(index + 1);
        });
    });
    
    const ratingContainer = document.querySelector('.rating-stars');
    if (ratingContainer) {
        ratingContainer.addEventListener('mouseleave', () => {
            updateStarDisplay();
        });
    }
}

// Update star display
function updateStarDisplay() {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < currentRating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// Highlight stars on hover
function highlightStars(rating) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// Initialize form handlers
function initializeFormHandlers() {
    // Feedback form
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', handleFeedbackSubmit);
    }
    
    // Complaint form
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', handleComplaintSubmit);
    }
    
    // Menu suggestion form
    const menuSuggestionForm = document.getElementById('menuSuggestionForm');
    if (menuSuggestionForm) {
        menuSuggestionForm.addEventListener('submit', handleMenuSuggestionSubmit);
    }
}

// Handle feedback form submission
async function handleFeedbackSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const feedbackType = formData.get('feedbackType');
    const message = formData.get('feedbackMessage');
    const rating = formData.get('rating') ? parseInt(formData.get('rating')) : null;
    
    if (!message.trim()) {
        showNotification('Please enter your feedback!', 'warning');
        return;
    }
    
    try {
        await submitFeedback(feedbackType, message, rating);
        
        // Reset form
        e.target.reset();
        currentRating = 0;
        updateStarDisplay();
        
        // Clear rating input
        const ratingInput = document.getElementById('rating');
        if (ratingInput) ratingInput.value = '';
    } catch (error) {
        // Error already handled in submitFeedback function
    }
}

// Handle complaint form submission
async function handleComplaintSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const category = formData.get('complaintCategory');
    const message = formData.get('complaintMessage');
    const urgency = formData.get('urgency');
    
    if (!message.trim()) {
        showNotification('Please describe your complaint!', 'warning');
        return;
    }
    
    try {
        await submitComplaint(category, message, urgency);
        e.target.reset();
    } catch (error) {
        // Error already handled in submitComplaint function
    }
}

// Handle menu suggestion form submission
async function handleMenuSuggestionSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const dishName = formData.get('dishName');
    const mealType = formData.get('mealType');
    const ingredients = formData.get('ingredients') || '';
    const description = formData.get('description') || '';
    
    if (!dishName.trim()) {
        showNotification('Please enter a dish name!', 'warning');
        return;
    }
    
    try {
        await submitMenuSuggestion(dishName, mealType, ingredients, description);
        e.target.reset();
    } catch (error) {
        // Error already handled in submitMenuSuggestion function
    }
}

// Initialize scroll animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Add fade-in class to elements that should animate
    const animateElements = document.querySelectorAll('.feature-card, .form-container, .menu-grid, .instruction-card, .option-card');
    animateElements.forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// Add notification styles
function addNotificationStyles() {
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                padding: 0;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                animation: slideIn 0.3s ease-out;
            }
            
            .notification.success {
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.9), rgba(22, 163, 74, 0.9));
                border: 1px solid rgba(34, 197, 94, 0.3);
            }
            
            .notification.error {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9));
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .notification.warning {
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.9), rgba(217, 119, 6, 0.9));
                border: 1px solid rgba(245, 158, 11, 0.3);
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 16px 20px;
                color: white;
                font-weight: 500;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                margin-left: 12px;
                opacity: 0.8;
                transition: opacity 0.2s;
            }
            
            .notification-close:hover {
                opacity: 1;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            #loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10001;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Utility function to capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    const modal = document.getElementById('voteModal');
    if (modal && e.target === modal) {
        closeVoteModal();
    }
});

// Handle escape key to close modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('voteModal');
        if (modal && modal.style.display === 'block') {
            closeVoteModal();
        }
    }
});

// Health check on page load
window.addEventListener('load', async () => {
    try {
        await fetch(`${API_BASE_URL}/health`);
        console.log('Backend connection established');
    } catch (error) {
        console.warn('Backend not available:', error);
        showNotification('Backend service is not available. Some features may not work.', 'warning');
    }
});

// Update vote button onclick in HTML to use the new function
window.submitVote = submitVoteFromModal;

// Photo upload functionality
function initializePhotoUpload() {
    const photoInput = document.getElementById('complaintPhotos');
    const photoPreview = document.getElementById('photoPreview');
    
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            photoPreview.innerHTML = '';
            
            // Limit to 3 photos
            const maxPhotos = 3;
            const selectedFiles = files.slice(0, maxPhotos);
            
            selectedFiles.forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const photoItem = document.createElement('div');
                        photoItem.className = 'photo-item';
                        photoItem.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <button type="button" class="remove-photo" onclick="removePhoto(${index})">&times;</button>
                        `;
                        photoPreview.appendChild(photoItem);
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }
}

// Remove photo from preview
function removePhoto(index) {
    const photoInput = document.getElementById('complaintPhotos');
    const photoPreview = document.getElementById('photoPreview');
    
    if (photoInput && photoPreview) {
        const dt = new DataTransfer();
        const files = Array.from(photoInput.files);
        
        files.forEach((file, i) => {
            if (i !== index) {
                dt.items.add(file);
            }
        });
        
        photoInput.files = dt.files;
        
        // Re-trigger change event to update preview
        const event = new Event('change');
        photoInput.dispatchEvent(event);
    }
}

// Initialize photo upload when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializePhotoUpload();
});

