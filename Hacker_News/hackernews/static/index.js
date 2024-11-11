document.addEventListener("DOMContentLoaded", function() {
    const likeButtons = document.querySelectorAll("[id^='like-button-']");
    const dislikeButtons = document.querySelectorAll("[id^='dislike-button-']");

    likeButtons.forEach(button => {
        button.addEventListener("click", function() {
            const postId = button.id.split("-")[2]; // Extract post ID from button ID
            like(postId);
        });
    });

    dislikeButtons.forEach(button => {
        button.addEventListener("click", function() {
            const postId = button.id.split("-")[2]; // Extract post ID from button ID
            dislike(postId);
        });
    });
});

function like(postId) {
	//console.log(sessionData);
	if(!sessionData.hasOwnProperty('user'))
		alert('Please log in to like this post');
	else {
	const likeCount = document.getElementById('likes-count-' + postId);
	const likeButton = document.getElementById('like-button-'+postId);
	const dislikeCount = document.getElementById('dislikes-count-' + postId);
	const dislikeButton = document.getElementById('dislike-button-'+postId);
	//console.log(dislikeButton);
	fetch('/like-post/'+postId, {method:"POST"})
	.then((res) => res.json())
    	.then((data) => {
      		likeCount.innerHTML = data["likes"];
		dislikeCount.innerHTML = data["dislikes"];
		if(data["liked"] === true) {
			likeButton.className = "btn btn-primary active";
			dislikeButton.className = "btn btn-danger";
		}
		else {
			likeButton.className = "btn btn-primary";
		}
	})
	.catch((e) => alert("Could not like post."));
	}
}

function dislike(postId) {
	if(!sessionData.hasOwnProperty('user'))
                alert('Please log in to dislike this post');
        else {
        const dislikeCount = document.getElementById('dislikes-count-' + postId);
        const dislikeButton = document.getElementById('dislike-button-'+postId);
	const likeCount = document.getElementById('likes-count-' + postId);
	const likeButton = document.getElementById('like-button-'+postId);
		//console.log(dislikeButton);
        fetch('/dislike-post/'+postId, {method:"POST"})
        .then((res) => res.json())
        .then((data) => {
                dislikeCount.innerHTML = data["dislikes"];
		likeCount.innerHTML = data["likes"];
		if(data["disliked"] === true) {
			dislikeButton.className = "btn btn-danger active";
			likeButton.className = "btn btn-primary";
		}
		else {
			dislikeButton.className = "btn btn-danger";
		}
        })
        .catch((e) => alert("Could not dislike post."));
	}
}
