function adjustPadding() {
  let header = document.querySelector('header');
  let footer = document.querySelector('footer');
  let bodyStyle = document.body.style;

  let headerHeight = header.offsetHeight;
  let footerHeight = footer.offsetHeight;

  bodyStyle.paddingTop = `${headerHeight}px`;
  bodyStyle.paddingBottom = `${footerHeight}px`;
}

document.addEventListener("DOMContentLoaded", function() {
  // Load Header
  fetch('assets/html/includes/header.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('header-placeholder').innerHTML = html;
      adjustPadding(); // Adjust padding after header is loaded
    })
    .catch(err => console.error('Failed to load header:', err));

  // Load Footer
  fetch('assets/html/includes/footer.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('footer-placeholder').innerHTML = html;
      adjustPadding(); // Adjust padding after footer is loaded
    })
    .catch(err => console.error('Failed to load footer:', err));
});

window.addEventListener("resize", adjustPadding);