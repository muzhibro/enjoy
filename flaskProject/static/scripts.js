function confirmDelete(taskId) {
    if (confirm("Are you sure you want to delete this task?")) {
        fetch(`/delete_task/${taskId}`, { method: 'POST' })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
    }
}

function confirmDeleteMember(name) {
    if (confirm("Are you sure you want to delete this team member?")) {
        fetch(`/delete_member/${name}`, { method: 'POST' })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
    }
}

function updateTaskStatus(taskId, status) {
    fetch(`/update_task_status/${taskId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => {
        if (response.redirected) {
            // 不执行重定向操作，而是在此处处理返回的数据
            // 在此处处理闪现消息的显示逻辑等
        }
    });
}

function confirmUpdateTaskStatus(taskId) {
    if (confirm("Are you sure you want to update the status of this task?")) {
        var status = document.getElementById('status_' + taskId).value;
        updateTaskStatus(taskId, status);
    }
}
