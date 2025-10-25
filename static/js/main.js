// Notification
if (!localStorage.getItem('notifDismissed')) {
    document.getElementById('notification').style.display = 'block';
}
function closeNotif() {
    document.getElementById('notification').style.display = 'none';
    localStorage.setItem('notifDismissed', 'true');
}

// Play All (Queue)
function playAll() {
    // Placeholder for queue logic
    console.log('Play All clicked');
    // Add videos to queue array and play sequentially
}