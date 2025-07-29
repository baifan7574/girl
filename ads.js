// PopCash 弹窗广告代码（自动尝试主/备用CDN）
var uid = '492091';  // 你的 PopCash UID
var wid = '743249';  // 你的 PopCash WID

var pop_tag = document.createElement('script');
pop_tag.src = '//cdn.popcash.net/show.js';
document.body.appendChild(pop_tag);

pop_tag.onerror = function () {
  pop_tag = document.createElement('script');
  pop_tag.src = '//cdn2.popcash.net/show.js';
  document.body.appendChild(pop_tag);
};
