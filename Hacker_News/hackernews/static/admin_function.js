console.log("hahaha")
document.addEventListener("DOMContentLoaded", function() {
    const deleteButtons = document.querySelectorAll("button");

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const userID = button.id;
            deleteUser(userID);
        });
    });
});

function deleteUser(userID) {
	console.log("whaaat" + userID)
    window.location.href = '/delete-user/' + userID;
}

document.addEventListener("DOMContentLoaded", function() {
    const deleteIcons = document.querySelectorAll("[id^='delete-icon-']");
    
    deleteIcons.forEach(icon => {
        icon.addEventListener("click", function() {
            const postId = icon.id.split("-")[2]; // Extract post ID from icon ID
            delete_post(postId);
        });
    });
});

function delete_post(postID) {
    window.location.href = '/delete-post/' + postID;
}

