(function() {
  function init(root) {
    var items = Array.prototype.slice.call(root.querySelectorAll('.dclb2-item'));
    var thumbs = Array.prototype.slice.call(root.querySelectorAll('.dclb2-thumb'));
    if (!items.length) return;
    var prev = root.querySelector('.dclb2-prev');
    var next = root.querySelector('.dclb2-next');
    var index = 0;
    items.forEach(function(it, i) { if (i !== 0) it.style.display = 'none'; });
    function show(i) {
      items[index].style.display = 'none';
      thumbs[index].classList.remove('active');
      index = (i + items.length) % items.length;
      items[index].style.display = 'block';
      thumbs[index].classList.add('active');
    }
    thumbs.forEach(function(btn, i) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        show(i);
      });
    });
    if (prev) prev.addEventListener('click', function() { show(index - 1); });
    if (next) next.addEventListener('click', function() { show(index + 1); });
  }
  function bind() {
    document.querySelectorAll('.dclb2-carousel').forEach(init);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();