document.addEventListener("DOMContentLoaded", function() {
  // Load Header
  fetch('assets/html/header.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('header-placeholder').innerHTML = html;
    })
    .catch(err => console.error('Failed to load header:', err));

  // Load Footer
  fetch('assets/html/footer.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('footer-placeholder').innerHTML = html;
    })
    .catch(err => console.error('Failed to load footer:', err));
});
  
  /* Places the footer and header heights into place */
document.addEventListener("DOMContentLoaded", function() {
  var headerHeight = document.querySelector('header').offsetHeight;
  var footerHeight = document.querySelector('footer').offsetHeight;

  document.body.style.paddingTop = headerHeight + 'px';
  document.body.style.paddingBottom = footerHeight + 'px';
});