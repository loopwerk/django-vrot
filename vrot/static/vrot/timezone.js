/**
 * django-vrot timezone support
 * 
 * This script:
 * 1. Sets a cookie with the user's timezone
 * 2. Converts all elements with class 'local-time' to display in the user's local timezone
 */

// Set timezone cookie immediately
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.cookie = "timezone=" + encodeURIComponent(timezone) + "; path=/; SameSite=Lax";

// Convert times to local timezone when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
    };
    
    document.querySelectorAll('.local-time').forEach(function(element) {
        const datetime = element.getAttribute('datetime');
        if (datetime) {
            try {
                const utcDate = new Date(datetime);
                // Check if date is valid
                if (!isNaN(utcDate.getTime())) {
                    // Use 'en-US' locale to ensure consistent formatting
                    element.textContent = utcDate.toLocaleString('en-US', options);
                }
            } catch (e) {
                // If parsing fails, leave the original content
                console.error('django-vrot: Failed to parse date', datetime, e);
            }
        }
    });
});