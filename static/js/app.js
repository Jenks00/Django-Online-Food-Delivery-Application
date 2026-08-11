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
})();
