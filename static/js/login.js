document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const errorToast = document.getElementById('error-toast');
    const errorToastBody = document.getElementById('error-toast-body');
    const errorToastInstance = bootstrap.Toast.getOrCreateInstance(errorToast);

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const response = await fetch('/auth/jwt/login', {
            method: 'POST',
            body: new URLSearchParams(formData),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        if (response.ok) {
            window.location.href = '/';
        } else {
            const error = await response.json();
            errorToastBody.textContent = `Erreur: ${error.detail}`;
            errorToastInstance.show();
        }
    });
});