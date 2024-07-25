
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

        document.addEventListener('DOMContentLoaded', (event) => {
            const approveButtons = document.querySelectorAll('button[data-action="approve"]');
            approveButtons.forEach(button => {
                button.addEventListener('click', function() {
                    approveUser(this.getAttribute('data-user-id'));
                });
            });
        
            const rejectButtons = document.querySelectorAll('button[data-action="reject"]');
            rejectButtons.forEach(button => {
                button.addEventListener('click', function() {
                    rejectUser(this.getAttribute('data-user-id'), this.getAttribute('data-user-email'));
                });
            });
        });
        

        function approveUser(userId) {
            const csrftoken = getCookie('csrftoken');
            fetch(`approve-user/${userId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ user_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                document.getElementById(`user-row-${userId}`).remove();
        
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        
        function rejectUser(userId, userEmail) {
            const csrftoken = getCookie('csrftoken');
            fetch(`reject-user/${userId}/${userEmail}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ user_id: userId, user_email: userEmail })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                document.getElementById(`user-row-${userId}`).remove();
        
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }