// 搜索功能
(function() {
    let searchIndex = [];
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

        // 加载搜索索引
        loadSearchIndex();
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

    // 加载搜索索引
    function loadSearchIndex() {
        fetch('/assets/search-index.json')
            .then(response => response.json())
            .then(data => {
                searchIndex = data;
                console.log(`搜索索引加载完成: ${searchIndex.length} 条记录`);
            })
            .catch(error => {
                console.error('搜索索引加载失败:', error);
            });
    }

    // 处理搜索
    function handleSearch(e) {
        const query = e.target.value.trim().toLowerCase();

        if (!query) {
            searchResults.innerHTML = '';
            return;
        }

        const results = search(query);
        displayResults(results, query);
    }

    // 搜索函数
    function search(query) {
        const results = [];
        const maxResults = 20;

        for (let i = 0; i < searchIndex.length && results.length < maxResults; i++) {
            const item = searchIndex[i];
            const content = item.content.toLowerCase();

            if (content.includes(query)) {
                // 计算相关度分数
                const score = calculateScore(content, query);
                results.push({
                    ...item,
                    score: score
                });
            }
        }

        // 按分数排序
        results.sort((a, b) => b.score - a.score);
        return results;
    }

    // 计算相关度分数
    function calculateScore(content, query) {
        let score = 0;

        // 完全匹配加分
        if (content.includes(query)) {
            score += 10;
        }

        // 开头匹配加分
        if (content.startsWith(query)) {
            score += 5;
        }

        // 出现次数
        const matches = content.match(new RegExp(escapeRegex(query), 'g'));
        if (matches) {
            score += matches.length;
        }

        return score;
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
                <div class="search-result-item" onclick="location.href='/posts/${result.id}.html'">
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
