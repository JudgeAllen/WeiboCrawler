/**
 * 图片灯箱功能
 * 点击图片放大显示，点击背景或关闭按钮关闭
 */

document.addEventListener('DOMContentLoaded', function() {
    const lightbox = document.getElementById('image-lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeBtn = document.querySelector('.lightbox-close');

    // 为所有图片链接添加点击事件
    function initLightbox() {
        const imageLinks = document.querySelectorAll('.weibo-images .image-link');

        imageLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const imgSrc = this.querySelector('img').src;
                openLightbox(imgSrc);
            });
        });
    }

    // 打开灯箱
    function openLightbox(src) {
        lightboxImg.src = src;
        lightbox.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 禁止背景滚动
    }

    // 关闭灯箱
    function closeLightbox() {
        lightbox.style.display = 'none';
        document.body.style.overflow = ''; // 恢复滚动
    }

    // 点击关闭按钮
    closeBtn.addEventListener('click', closeLightbox);

    // 点击背景关闭
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // ESC键关闭
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && lightbox.style.display === 'flex') {
            closeLightbox();
        }
    });

    // 初始化
    initLightbox();
});
