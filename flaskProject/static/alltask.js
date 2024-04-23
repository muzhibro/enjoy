// 在页面加载完成后执行
document.addEventListener("DOMContentLoaded", function() {
    // 获取搜索按钮和重置按钮
    var searchButton = document.getElementById("search-button");
    var resetButton = document.getElementById("reset-button");

    // 给搜索按钮添加点击事件监听器
    searchButton.addEventListener("click", function() {
        searchTasks();
    });

    // 给重置按钮添加点击事件监听器
    resetButton.addEventListener("click", function() {
        // 清空搜索框的值
        document.getElementById("search-input").value = "";
        // 显示所有任务
        showAllTasks();
    });

    // 定义搜索任务函数
    function searchTasks() {
        // 获取搜索框的值
        var searchText = document.getElementById("search-input").value.toLowerCase();

        // 获取所有任务列表项
        var taskItems = document.querySelectorAll(".task-item");

        // 遍历每个任务列表项
        taskItems.forEach(function(taskItem) {
            // 获取当前任务的标题、描述、分配给和状态
            var title = taskItem.querySelector("h2").textContent.toLowerCase();
            var description = taskItem.querySelector("p:nth-of-type(2)").textContent.toLowerCase();
            var assignedTo = taskItem.querySelector(".assigned-to").textContent.toLowerCase();
            var status = taskItem.querySelector("select").value.toLowerCase();

            // 如果标题、描述、分配给或状态包含搜索文本，则显示该任务，否则隐藏该任务
            if (title.includes(searchText) || description.includes(searchText) || assignedTo.includes(searchText) || status.includes(searchText)) {
                taskItem.style.display = "block";
            } else {
                taskItem.style.display = "none";
            }
        });
    }

    // 定义显示所有任务函数
    function showAllTasks() {
        // 获取所有任务列表项
        var taskItems = document.querySelectorAll(".task-item");

        // 遍历每个任务列表项，并显示它们
        taskItems.forEach(function(taskItem) {
            taskItem.style.display = "block";
        });
    }
});
