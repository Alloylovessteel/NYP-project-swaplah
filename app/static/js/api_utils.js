/**
 * Display error message safely without exposing internals.
 */
function displayError(container, statusCode, errorData) {
    let message = 'An error occurred. Please try again.';
    
    if (statusCode === 400) {
        message = errorData?.error || 'Invalid input. Please check your data.';
    } else if (statusCode === 401) {
        message = 'Please log in to continue.';
    } else if (statusCode === 403) {
        message = 'You do not have permission to perform this action.';
    } else if (statusCode === 404) {
        message = 'The requested resource was not found.';
    } else if (statusCode >= 500) {
        message = 'Server error. Please try again later.';
    }
    
    if (container) {
        container.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
    }
}

/**
 * Display success message.
 */
function displaySuccess(container, message) {
    if (container) {
        container.innerHTML = `<div class="alert alert-success" role="alert">${message}</div>`;
        window.scrollTo(0, 0);
    }
}