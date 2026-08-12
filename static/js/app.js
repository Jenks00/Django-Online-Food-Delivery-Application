/*
 * Site-wide behaviour that has nothing to do with a specific page.
 *
 * Anonymous shoppers are identified by a `device` cookie so their cart
 * survives a page refresh without requiring an account. This used to be
 * duplicated inline in every base template; it now lives in one place.
 */
(function () {
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function ensureDeviceCookie() {
    var device = getCookie('device');
    if (!device) {
      device = uuidv4();
      document.cookie = 'device=' + device + ';path=/;max-age=' + 60 * 60 * 24 * 365;
    }
    return device;
  }

  ensureDeviceCookie();

  // Confirm before removing a cart line item.
  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-confirm]');
    if (target && !window.confirm(target.getAttribute('data-confirm'))) {
      event.preventDefault();
    }
  });

  // --- Add to cart: no page redirect, a Temu-style "flying" item into the
  // cart icon, and a live badge count on the header.
  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function updateCartBadge(count) {
    var cartLink = document.querySelector('.nav-cart');
    if (!cartLink) return;
    var badge = cartLink.querySelector('.cart-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'cart-badge';
      cartLink.appendChild(badge);
    }
    badge.textContent = count;
    badge.hidden = !count;
    cartLink.setAttribute('aria-label', 'View cart, ' + count + ' items');

    cartLink.classList.remove('cart-bump');
    void cartLink.offsetWidth; // restart the animation
    cartLink.classList.add('cart-bump');
  }

  function flyToCart(sourceEl) {
    var cartLink = document.querySelector('.nav-cart');
    if (!cartLink || !sourceEl || prefersReducedMotion) return;

    var startRect = sourceEl.getBoundingClientRect();
    var endRect = cartLink.getBoundingClientRect();

    var flyer = sourceEl.cloneNode(true);
    flyer.removeAttribute('id');
    flyer.style.position = 'fixed';
    flyer.style.left = startRect.left + 'px';
    flyer.style.top = startRect.top + 'px';
    flyer.style.width = startRect.width + 'px';
    flyer.style.height = startRect.height + 'px';
    flyer.style.margin = '0';
    flyer.style.borderRadius = '50%';
    flyer.style.objectFit = 'cover';
    flyer.style.zIndex = '999';
    flyer.style.pointerEvents = 'none';
    flyer.style.boxShadow = '0 8px 24px rgba(28, 23, 18, 0.35)';
    flyer.style.transition = 'transform 0.6s cubic-bezier(.4,0,.2,1), width 0.6s, height 0.6s, opacity 0.6s ease-in';
    document.body.appendChild(flyer);

    var dx = (endRect.left + endRect.width / 2) - (startRect.left + startRect.width / 2);
    var dy = (endRect.top + endRect.height / 2) - (startRect.top + startRect.height / 2);

    requestAnimationFrame(function () {
      flyer.style.transform = 'translate(' + dx + 'px, ' + dy + 'px)';
      flyer.style.width = '18px';
      flyer.style.height = '18px';
      flyer.style.opacity = '0.4';
    });

    flyer.addEventListener('transitionend', function () {
      flyer.remove();
    }, { once: true });
  }

  document.addEventListener('submit', function (event) {
    var form = event.target.closest('form[data-add-to-cart]');
    if (!form) return;
    event.preventDefault();

    var submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;

    var formData = new FormData(form);

    fetch(form.action, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        var flySource = form.getAttribute('data-fly-from');
        var sourceEl = flySource ? document.querySelector(flySource) : null;
        if (sourceEl) flyToCart(sourceEl);
        updateCartBadge(data.cart_count);

        var feedback = form.querySelector('.add-to-cart-feedback');
        if (feedback) {
          feedback.hidden = false;
          setTimeout(function () { feedback.hidden = true; }, 2500);
        }
      })
      .finally(function () {
        if (submitButton) submitButton.disabled = false;
      });
  });
})();
