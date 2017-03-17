var currentUrl = window.location.pathname;

var deletePost = document.getElementsByClassName('delete-post')[0];

if(deletePost) {
	deletePost.addEventListener('click', function() {
		$.ajax(currentUrl, {
			method: 'delete'
		})
		.done(function(res) {
			if(res !== 'error') {
				// redirect to user's blog page
				window.location.href = '/users/' + res
			} else {
				console.log(res)
			}
		})
	})
}

var editPost = document.getElementsByClassName('edit-post')[0];

if(editPost) {
	editPost.addEventListener('click', function() {
		window.location.href = currentUrl + '?' + 'editingTarget=post';
	})
}

var cancelPostEdit = document.getElementsByClassName('cancel-post-edit')[0];

if(cancelPostEdit) {
	cancelPostEdit.addEventListener('click', function() {
		window.location.href = currentUrl.split('?')[0];
	})
}

var updatePost = document.getElementsByClassName('update-post')[0];

if(updatePost) {
	updatePost.addEventListener('click', function() {
		newSubject = document.getElementsByClassName('subject-input')[0].value;
		newContent = document.getElementsByClassName('content-input')[0].value;

		$.ajax(currentUrl, {
			method: 'put',
			headers: {'Content-Type': 'application/json'},
			data: JSON.stringify({
				'subject': newSubject,
				'content': newContent
			})
		})
		.done(function(res) {
			if(res !== 'error') {
				// return to default post view
				window.location.href = currentUrl.split('?')[0];
			} else {
				console.log(res)
			}
		})
	})
}

var likePost = document.getElementsByClassName('like-post')[0];

if(likePost) {
	likePost.addEventListener('click', function() {
		$.ajax(currentUrl + '/like', {
			method: 'put'
		})
		.done(function(res) {
			if(res !== 'error') {
				// reload page on successful transaction
				window.location.reload(true);
			} else {
				console.log(res);
			}
		})
	})
}

var deleteComment = document.getElementsByClassName('delete-comment');

if(deleteComment) {
	for(var i = 0; i < deleteComment.length; i++) {
		deleteComment[i].addEventListener('click', function() {
			var commentMain = this.parentElement.parentElement.parentElement;
			var commentId = commentMain.id;

			$.ajax(currentUrl + '/comment/' + commentId, {
				method: 'delete'
			})
			.done(function(res) {
				if(res !== 'error') {
					// reload page on successful deletion
					window.location.reload(true);
				} else {
					console.log(res);
				}
			})
		})
	}
}

var editComment = document.getElementsByClassName('edit-comment');

if(editComment) {
	for(var i = 0; i < editComment.length; i++) {
		editComment[i].addEventListener('click', function() {
			var commentMain = this.parentElement.parentElement.parentElement;
			var commentId = commentMain.id;
			var commentOld = commentMain.querySelector('.comment-content');
			var commentContent = commentOld.textContent;
			var defaultCommentSettings = commentMain.querySelector('.comment-settings-default');
			var editingCommentSettings = commentMain.querySelector('.comment-settings-editing');

			defaultCommentSettings.classList.add('hide');
			editingCommentSettings.classList.remove('hide');

			// make editing comment interface
			var commentInput = document.createElement('textarea');
			commentInput.classList.add('comment-content');
			commentInput.classList.add('form-control');
			commentInput.appendChild(document.createTextNode(commentContent));
			commentOld.replaceWith(commentInput)
		})
	}
}

var cancelCommentEdit = document.getElementsByClassName('cancel-comment-edit');

if(cancelCommentEdit) {
	for(var i = 0; i < cancelCommentEdit.length; i++) {
		cancelCommentEdit[i].addEventListener('click', function() {
			var commentMain = this.parentElement.parentElement.parentElement;
			var commentId = commentMain.id;
			var commentOld = commentMain.querySelector('.comment-content');
			var commentContent = commentOld.value;
			var defaultCommentSettings = commentMain.querySelector('.comment-settings-default');
			var editingCommentSettings = commentMain.querySelector('.comment-settings-editing');

			defaultCommentSettings.classList.remove('hide');
			editingCommentSettings.classList.add('hide');

			// make default comment interface
			var commentParagraph = document.createElement('p');
			commentParagraph.classList.add('comment-content');
			commentParagraph.appendChild(document.createTextNode(commentContent));
			commentOld.replaceWith(commentParagraph)
		})
	}
}

var updateComment = document.getElementsByClassName('update-comment');

if(updateComment) {
	for(var i = 0; i < updateComment.length; i++) {
		updateComment[i].addEventListener('click', function() {
			var commentMain = this.parentElement.parentElement.parentElement;
			var commentId = commentMain.id;
			var commentOld = commentMain.querySelector('.comment-content');
			var commentContent = commentOld.value;

			$.ajax(currentUrl + '/comment/' + commentId, {
				method: 'put',
				headers: {'Content-Type': 'application/json'},
				data: JSON.stringify({
					'content': commentContent
				})
			})
			.done(function(res) {
				if(res !== 'error') {
					// reload page on successful update
					window.location.reload(true);
				} else {
					console.log(res);
				}
			})
		})
	}
}