// Main JavaScript file

// CSRF Token Setup
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// AJAX Setup
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Add to Cart
function addToCart(productId, quantity = 1, variantId = null) {
    const data = {
        product_id: productId,
        quantity: quantity,
        variant_id: variantId
    };
    
    $.ajax({
        url: '/cart/add/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            // Update cart count
            $('.cart-count').text(response.cart_count);
            
            // Show success message
            showToast('success', response.message);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to add to cart';
            showToast('error', error);
        }
    });
}

// Update Cart Item
function updateCartItem(itemId, quantity) {
    const data = {
        quantity: quantity
    };
    
    $.ajax({
        url: `/cart/update/${itemId}/`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            // Update UI
            $(`#item-total-${itemId}`).text(`₹${response.item_total}`);
            $('#cart-subtotal').text(`₹${response.cart_total}`);
            $('#cart-gst').text(`₹${response.cart_gst}`);
            $('#cart-grand-total').text(`₹${response.cart_grand_total}`);
            $('.cart-count').text(response.cart_count);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to update cart';
            showToast('error', error);
        }
    });
}

// Remove Cart Item
function removeCartItem(itemId) {
    if (!confirm('Are you sure you want to remove this item?')) {
        return;
    }
    
    $.ajax({
        url: `/cart/remove/${itemId}/`,
        method: 'POST',
        success: function(response) {
            // Remove item from DOM
            $(`#cart-item-${itemId}`).fadeOut(300, function() {
                $(this).remove();
            });
            
            // Update cart totals
            $('#cart-subtotal').text(`₹${response.cart_total}`);
            $('#cart-gst').text(`₹${response.cart_gst}`);
            $('#cart-grand-total').text(`₹${response.cart_grand_total}`);
            $('.cart-count').text(response.cart_count);
            
            showToast('success', response.message);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to remove item';
            showToast('error', error);
        }
    });
}

// Apply Coupon
function applyCoupon() {
    const couponCode = $('#coupon-code').val().trim();
    if (!couponCode) {
        showToast('error', 'Please enter a coupon code');
        return;
    }
    
    const data = {
        coupon_code: couponCode
    };
    
    $.ajax({
        url: '/cart/apply-coupon/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            $('#coupon-discount').text(`-₹${response.discount}`);
            $('#cart-grand-total').text(`₹${response.new_total}`);
            showToast('success', response.message);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to apply coupon';
            showToast('error', error);
        }
    });
}

// Toast Notification
function showToast(type, message) {
    const toastHtml = `
        <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1050;">
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(toastHtml);
    const toastEl = $('.toast').last();
    const toast = new bootstrap.Toast(toastEl[0], { delay: 3000 });
    toast.show();
    
    toastEl.on('hidden.bs.toast', function() {
        $(this).closest('.toast-container').remove();
    });
}

// Product Image Gallery
function changeMainImage(imageUrl, thumbnailElement) {
    $('#main-product-image').attr('src', imageUrl);
    $('.product-thumbnail').removeClass('active');
    $(thumbnailElement).addClass('active');
}

// Quantity Selector
function updateQuantity(change, inputId, maxQuantity = 10) {
    const input = $(`#${inputId}`);
    let currentValue = parseInt(input.val()) || 1;
    let newValue = currentValue + change;
    
    if (newValue < 1) {
        newValue = 1;
    }
    
    if (newValue > maxQuantity) {
        showToast('error', `Maximum quantity is ${maxQuantity}`);
        newValue = maxQuantity;
    }
    
    input.val(newValue);
    return newValue;
}

// Rating Stars
function initRatingStars() {
    $('.rating-stars').each(function() {
        const rating = $(this).data('rating');
        const starContainer = $(this);
        
        starContainer.empty();
        
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                starContainer.append('<i class="fas fa-star text-warning"></i>');
            } else if (i - 0.5 <= rating) {
                starContainer.append('<i class="fas fa-star-half-alt text-warning"></i>');
            } else {
                starContainer.append('<i class="far fa-star text-warning"></i>');
            }
        }
    });
}

// Wishlist Toggle
function toggleWishlist(productId) {
    $.ajax({
        url: `/wishlist/toggle/${productId}/`,
        method: 'POST',
        success: function(response) {
            if (response.in_wishlist) {
                $(`#wishlist-btn-${productId}`).html('<i class="fas fa-heart text-danger"></i>');
                showToast('success', 'Added to wishlist');
            } else {
                $(`#wishlist-btn-${productId}`).html('<i class="far fa-heart"></i>');
                showToast('success', 'Removed from wishlist');
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to update wishlist';
            showToast('error', error);
        }
    });
}

// Initialize on document ready
$(document).ready(function() {
    // Initialize rating stars
    initRatingStars();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
});

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Phone Number Formatting
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 10) {
        value = value.substring(0, 10);
    }
    input.value = value;
}

// Pincode Validation
function validatePincode(input) {
    const pincode = input.value;
    const pincodeRegex = /^[1-9][0-9]{5}$/;
    
    if (!pincodeRegex.test(pincode)) {
        input.classList.add('is-invalid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        return true;
    }
}

// GST Number Validation
function validateGST(input) {
    const gst = input.value.toUpperCase();
    const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    
    if (!gstRegex.test(gst)) {
        input.classList.add('is-invalid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        return true;
    }
}