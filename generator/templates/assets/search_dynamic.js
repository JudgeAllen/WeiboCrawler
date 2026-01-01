// 搜索功能 - 动态API版本
(function() {
    let searchPanel = null;
    let searchInput = null;
    let searchResults = null;

    // 初始化
    function init() {
        searchPanel = document.getElementById('search-panel');
        searchInput = document.getElementById('search-input');
        searchResults = document.getElementById('search-results');

        // 搜索按钮
        const searchToggle = document.getElementById('search-toggle');
        if (searchToggle) {
            searchToggle.addEventListener('click', toggleSearch);
        }

        // 搜索输入
        if (searchInput) {
            searchInput.addEventListener('input', debounce(handleSearch, 300));
            searchInput.addEventListener('keydown', handleKeydown);
        }
    }

    // 切换搜索面板
    function toggleSearch(e) {
        e.preventDefault();
        if (searchPanel) {
            searchPanel.classList.toggle('active');
            if (searchPanel.classList.contains('active')) {
                searchInput.focus();
            }
        }
    }

    // 处理搜索
    function handleSearch(e) {
        const query = e.target.value.trim();

        if (!query) {
            searchResults.innerHTML = '';
            return;
        }

        // 调用搜索API
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(results => {
                displayResults(results, query);
            })
            .catch(error => {
                console.error('搜索失败:', error);
                searchResults.innerHTML = '<div class="no-results">搜索出错，请重试</div>';
            });
    }

    // 显示搜索结果
    function displayResults(results, query) {
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="no-results">未找到相关微博</div>';
            return;
        }

        const html = results.map(result => {
            const excerpt = createExcerpt(result.content, query);
            const date = formatDate(result.created_at);

            return `
                <div class="search-result-item" onclick="location.href='/post/${result.id}'">
                    <div>
                        <span class="author">${result.user_name}</span>
                        <span class="time">${date}</span>
                    </div>
                    <div class="content">${excerpt}</div>
                </div>
            `;
        }).join('');

        searchResults.innerHTML = html;
    }

    // 创建摘要并高亮关键词
    function createExcerpt(content, query, maxLength = 150) {
        const lowerContent = content.toLowerCase();
        const lowerQuery = query.toLowerCase();
        const index = lowerContent.indexOf(lowerQuery);

        let start = 0;
        let end = content.length;

        if (index !== -1) {
            // 以匹配位置为中心截取
            start = Math.max(0, index - 50);
            end = Math.min(content.length, index + query.length + 50);
        } else {
            // 截取开头
            end = Math.min(maxLength, content.length);
        }

        let excerpt = content.substring(start, end);

        // 添加省略号
        if (start > 0) excerpt = '...' + excerpt;
        if (end < content.length) excerpt = excerpt + '...';

        // 高亮关键词
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        excerpt = excerpt.replace(regex, '<mark>$1</mark>');

        return excerpt;
    }

    // 格式化日期
    function formatDate(dateStr) {
        if (!dateStr) return '';

        try {
            const date = new Date(dateStr);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        } catch (e) {
            return dateStr;
        }
    }

    // 转义正则表达式特殊字符
    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // 防抖函数
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 处理键盘事件
    function handleKeydown(e) {
        // ESC 关闭搜索
        if (e.key === 'Escape') {
            searchPanel.classList.remove('active');
            searchInput.value = '';
            searchResults.innerHTML = '';
        }
    }

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
