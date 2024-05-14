function showTasks (mission_id) {
  const xBtn = document.querySelector('#tasksContainer span');
  const taskBox = document.querySelector('#tasksContainer');
  const listOfTasks = document.querySelector('#tasksContainer ul');

  taskBox.style.minHeight = '500px';
  taskBox.style.boxShadow = '0px 3px 5px 2px rgba(0, 0, 0, 0.3)';
  xBtn.classList.remove('d-none');

  xBtn.addEventListener('click', function () {
    // Clear the task list before hiding the container
    listOfTasks.innerHTML = '';
    taskBox.style.minHeight = '0px';
    xBtn.classList.add('d-none');
    taskBox.style.boxShadow = 'none';
  });

  // AJAX request to fetch tasks
  fetch('/tasks/' + mission_id)
    .then(response => response.json())
    .then(tasks => {
      // Process the received tasks here
      listOfTasks.innerHTML = ''; // Clear the task list before adding new tasks
      tasks.forEach(task => {
            const status = (task['completed']) ? '✅' : '🔴';
            const taskHTML = `<li class="col-12 p-3"><p class="d-flex justify-content-between">${task['title']}<a>${status}</a></p></li>`;
            listOfTasks.innerHTML += taskHTML;
        });
    })
    .catch(error => {
      console.error('Error fetching tasks:', error);
    });
}
