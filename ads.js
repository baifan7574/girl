// PopCash 弹窗广告加载脚本（兼容主流浏览器）
(function () {
  var pop_tag = document.createElement('script');
  pop_tag.src = '//cdn.popcash.net/show.js';
  pop_tag.async = true;
  document.body.appendChild(pop_tag);

  // 加载失败自动切换备用CDN
  pop_tag.onerror = function () {
    var fallback = document.createElement('script');
    fallback.src = '//cdn2.popcash.net/show.js';
    fallback.async = true;
    document.body.appendChild(fallback);
  };
})();
