<<<<<<< HEAD
// PopCash 弹窗广告脚本（绑定 UID: 492091，WID: 743249）
window.addEventListener("load", function () {
  var uid = '492091';
  var wid = '743249';
  var pop_tag = document.createElement('script');
  pop_tag.src = '//cdn.popcash.net/show.js';
  pop_tag.async = true;
  document.body.appendChild(pop_tag);

  pop_tag.onerror = function () {
    var fallback = document.createElement('script');
    fallback.src = '//cdn2.popcash.net/show.js';
    fallback.async = true;
    document.body.appendChild(fallback);
  };
});
=======
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
>>>>>>> parent of 62bdce5f ( One.)
