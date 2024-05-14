function action (wixhAction) {
  const signInConatiner = document.querySelector('#signIn');
  const signUpConatiner = document.querySelector('#signUp');
  if (wixhAction === 'in') {
    signUpConatiner.style.display = 'none';
    signInConatiner.style.display = 'flex';
  } else {
    signInConatiner.style.display = 'none';
    signUpConatiner.style.display = 'flex';
  }
}

document.querySelector('#signinBtn').addEventListener('click', function (event) {
  action('in');
});

document.querySelector('#signupBtn').addEventListener('click', function (event) {
  action('up');
});
