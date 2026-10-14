/* ============================================================
   BHARATKART ADMIN - Custom JavaScript
   ============================================================ */

(function() {
    'use strict';

    // Wait for DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        addLuxuryBranding();
        enhanceSaveButtons();
        addConfirmDialogs();
        enhanceSearchFocus();
        animateCounters();
    });

    // ============ LUXURY BRANDING ============
    function addLuxuryBranding() {
        // Add gold gradient to the brand name
        const brandText = document.querySelector('.brand-text');
        if (brandText && !brandText.querySelector('span')) {
            brandText.innerHTML = brandText.textContent.replace('Kart', '<span>Kart</span>');
        }

        // Update page title with luxury touch
        const pageTitle = document.querySelector('.content-header h1');
        if (pageTitle && !pageTitle.querySelector('.luxury-dot')) {
            pageTitle.innerHTML += '<span class="luxury-dot" style="color: var(--gold); margin-left: 8px;">●</span>';
        }
    }

    // ============ SAVE BUTTON ENHANCEMENT ============
    function enhanceSaveButtons() {
        // Add loading spinner to submit buttons
        document.querySelectorAll('input[type="submit"], button[type="submit"]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (this.type === 'submit' && !this.disabled) {
                    const originalText = this.value || this.innerHTML;
                    if (this.value) {
                        this.value = '⏳ Saving...';
                    } else {
                        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                    }
                }
            });
        });
    }

    // ============ CONFIRM DIALOGS ============
    function addConfirmDialogs() {
        // Confirm on delete actions
        document.querySelectorAll('.deletelink, a[href*="/delete/"]').forEach(function(el) {
            el.addEventListener('click', function(e) {
                if (!confirm('⚠️ Are you sure you want to delete this? This action cannot be undone.')) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    // ============ SEARCH FOCUS ============
    function enhanceSearchFocus() {
        const searchBar = document.getElementById('searchbar');
        if (searchBar) {
            // Add luxury placeholder
            searchBar.placeholder = '🔍 Search ' + (document.querySelector('.content-header h1')?.textContent?.trim() || 'records') + '...';
        }
    }

    // ============ COUNTER ANIMATION ============
    function animateCounters() {
        document.querySelectorAll('.info-box-number, .small-box h3').forEach(function(el) {
            const text = el.textContent.trim();
            const number = parseFloat(text.replace(/[^\d.]/g, ''));
            
            if (isNaN(number) || number === 0) return;
            
            const hasComma = text.includes(',');
            const hasRupee = text.includes('₹');
            const hasPercent = text.includes('%');
            
            let current = 0;
            const increment = number / 30;
            const duration = 800;
            const stepTime = duration / 30;
            
            // Clear original text
            el.textContent = hasRupee ? '₹0' : '0';
            
            const timer = setInterval(function() {
                current += increment;
                if (current >= number) {
                    current = number;
                    clearInterval(timer);
                }
                
                let displayValue = Math.floor(current);
                if (hasComma) displayValue = displayValue.toLocaleString('en-IN');
                
                el.textContent = (hasRupee ? '₹' : '') + displayValue + (hasPercent ? '%' : '');
            }, stepTime);
        });
    }

    // ============ KEYBOARD SHORTCUTS ============
    document.addEventListener('keydown', function(e) {
        // Ctrl+S = Save form (if on change form)
        if (e.ctrlKey && e.key === 's') {
            const saveBtn = document.querySelector('input[name="_save"], button[name="_save"]');
            if (saveBtn) {
                e.preventDefault();
                saveBtn.click();
            }
        }
        
        // Ctrl+Shift+A = Add new item
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            const addBtn = document.querySelector('.object-tools a.addlink');
            if (addBtn) {
                e.preventDefault();
                addBtn.click();
            }
        }
        
        // Escape = Go back
        if (e.key === 'Escape' && !document.querySelector('.modal.show')) {
            const backBtn = document.querySelector('.breadcrumb-item a');
            if (backBtn && window.history.length > 1) {
                // Only navigate back if there's history
            }
        }
    });

    // ============ TOOLTIP HINTS ============
    document.querySelectorAll('[title]').forEach(function(el) {
        el.style.cursor = 'help';
    });

    // ============ TABLE ROW HIGHLIGHT ============
    document.querySelectorAll('table tbody tr').forEach(function(row) {
        row.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.tagName === 'INPUT') return;
            const link = this.querySelector('th a, td a');
            if (link) window.location.href = link.href;
        });
        row.style.cursor = 'pointer';
    });

    // ============ DASHBOARD WELCOME ============
    const contentHeader = document.querySelector('.content-header h1');
    if (contentHeader && contentHeader.textContent.trim() === 'Dashboard') {
        const userName = document.querySelector('.user-panel .info a')?.textContent?.trim() || 'Admin';
        const firstName = userName.split(' ')[0];
        contentHeader.textContent = 'Welcome back, ' + firstName;
        
        // Add subtitle
        const breadcrumb = document.querySelector('.breadcrumb');
        if (breadcrumb) {
            breadcrumb.innerHTML = '<li class="breadcrumb-item">Dashboard</li>';
        }
    }

    // ============ SIDEBAR ACTIVE STATE ============
    document.querySelectorAll('.nav-sidebar .nav-link').forEach(function(link) {
        if (window.location.pathname === link.getAttribute('href')) {
            link.classList.add('active');
        }
    });

    // ============ SCROLL TO TOP ============
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c9a961 0%, #a68a4a 100%);
        color: white;
        border: none;
        box-shadow: 0 10px 30px rgba(201,169,97,0.4);
        cursor: pointer;
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: all 0.3s;
        font-size: 1rem;
    `;
    document.body.appendChild(scrollBtn);
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    scrollBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1) translateY(-4px)';
    });
    
    scrollBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1) translateY(0)';
    });
    
    window.addEventListener('scroll', function() {
        scrollBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
    });

})();