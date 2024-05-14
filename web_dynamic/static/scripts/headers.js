document.addEventListener('DOMContentLoaded', function () {
  const currentUrl = window.location.href;

  // Iterate through each navigation item
  const navItems = document.querySelectorAll('.navbar-nav .nav-item');
  navItems.forEach(function (item) {
    const link = item.querySelector('.nav-link');

    if (link.href === currentUrl) {
      item.classList.add('active');
      item.style.backgroundColor = 'rgb(6, 71, 68)';
      link.style.color = 'white';
    }
  });
});

function logOut () {
  fetch('/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => {
      if (response.ok) {
        window.location.href = '/';
      } else {
        console.error('Logout failed');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function show () {
  element = document.querySelector('#dropdown');
  if (element.style.display == 'block') { element.style.display = 'none'; } else { element.style.display = 'block'; }
}
