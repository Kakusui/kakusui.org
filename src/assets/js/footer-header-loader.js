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
  // Determine the correct base path
  let basePath = window.location.pathname.includes('okisouchi') ? '../../' : './';

  // Load Header
  let headerPromise = fetch(basePath + 'assets/html/includes/header.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('header-placeholder').innerHTML = html;
    })
    .catch(err => console.error('Failed to load header:', err));

  // Load Footer
  let footerPromise = fetch(basePath + 'assets/html/includes/footer.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('footer-placeholder').innerHTML = html;
    })
    .catch(err => console.error('Failed to load footer:', err));

  // Call adjustPadding after both header and footer have loaded
  Promise.all([headerPromise, footerPromise]).then(() => adjustPadding());
});

window.addEventListener("resize", adjustPadding);
