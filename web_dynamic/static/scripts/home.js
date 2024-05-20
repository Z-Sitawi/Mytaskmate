document.addEventListener('DOMContentLoaded', async function () {
  const createBtn = document.querySelector('#createMission');
  const deleteBtn = document.querySelector('#deleteMission');

  try {
    const missionData = await fetchMissionStatus();
    if (missionData.active === true && missionData.user_id === userId) {
      handleActiveMission(createBtn, deleteBtn, missionData);
    } else {
      handleInactiveMission(createBtn, deleteBtn);
    }
  } catch (error) {
    console.error('Error fetching mission status:', error);
  }
});

async function fetchMissionStatus () {
  const response = await fetch('/active');
  if (!response.ok) {
    throw new Error('Failed to fetch mission status');
  }
  return response.json();
}

function handleActiveMission (createBtn, deleteBtn, data) {
  createBtn.style.display = 'none';
  deleteBtn.style.display = 'flex';
  document.querySelector('#missionDate h2').innerHTML = Today();
  document.querySelector('section#mission').style.minHeight = '500px';
  document.querySelector('#addTaskBtn').style.display = 'block';
}

function handleInactiveMission (createBtn, deleteBtn) {
  deleteBtn.style.display = 'none';
  createBtn.style.display = 'flex';
  document.querySelector('#noTasks').classList.remove('d-none');
  document.querySelector('section#mission').style.minHeight = '0px';
  document.querySelector('#addTaskBtn').style.display = 'none';
}

async function action (whichAction) {
  const createBtn = document.querySelector('#createMission');
  const deleteBtn = document.querySelector('#deleteMission');
  const missionData = await fetchMissionStatus();

  if (whichAction === 'delete') {
    if (missionData.active === true && missionData.user_id === userId) {
      $('#confirmationModal').modal('show');
      document.getElementById('confirmDeleteButton').addEventListener('click', async function () {
        await makeRequest('DELETE', '/missions');
        deleteBtn.style.display = 'none';
        createBtn.style.display = 'flex';
        document.querySelector('section#mission').style.minHeight = '0px';
        document.querySelector('#addTaskBtn').style.display = 'none';
        document.querySelector('#missionDate h2').innerHTML = 'Just Deleted A Mission';
        deleteAllTasks();
        $('#confirmationModal').modal('hide');
        $('.modal-backdrop').remove();
        reloadPageAfterSeconds(1.5);
      });
      document.querySelector('#confirmationModal button.btn-light').addEventListener('click', function () {
        $('#confirmationModal').modal('hide');
      });
    } else {
      location.reload();
    }
  } else {
    if (missionData.active === false) {
      await makeRequest('POST', '/missions');
      document.getElementById('addTaskBtn').style.display = 'block';
      createBtn.style.display = 'none';
      deleteBtn.style.display = 'flex';
      document.querySelector('#noTasks').style.display = 'none';
      document.querySelector('#missionDate h2').innerHTML = Today();
      document.querySelector('section#mission').style.minHeight = '500px';
    } else {
      location.reload();
    }
  }
}

function Today () {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  return `<strong>{</strong> ${day} / ${month} / ${year} <strong>} </strong>`;
}

function createTask () {
  const addTaskBtn = document.querySelector('#addTaskBtn');
  addTaskBtn.style.display = 'none';

  const listOfTasks = document.querySelector('#taskList');
  const task = '<li><i id="trash" class="fas fa-trash"></i><input type="text" placeholder="your task here"><a id="done">&#x2610;</a><button class="btn btn-success m-1 px-1 py-0" id="save-btn" >Save</button><button class="btn btn-danger m-1 px-1 py-0" id="cancel-btn" >Cancel</button></li>';
  listOfTasks.innerHTML += task;
  const newTask = listOfTasks.lastElementChild;
  const inputElement = newTask.querySelector('input');
  const doneButton = newTask.querySelector('#done');
  const trashButton = newTask.querySelector('#trash');
  const saveButton = newTask.querySelector('#save-btn');
  const cancelButton = newTask.querySelector('#cancel-btn');
  inputElement.focus();

  function saveAction () {
    if (inputElement.value) {
      createTaskOnDb(inputElement.value);
      inputElement.placeholder = inputElement.value;
      inputElement.disabled = true;
      saveButton.remove();
      cancelButton.remove();
      doneButton.style.display = 'block';
      trashButton.style.display = 'block';
      addTaskBtn.style.display = 'block';
    }
  }

  saveButton.addEventListener('click', saveAction);
  inputElement.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      saveAction();
      setTimeout(function () {
        reloadPageAfterSeconds(0.2);
      }, 0);
    }
  });

  cancelButton.addEventListener('click', function () {
    newTask.remove();
    addTaskBtn.style.display = 'block';
  });

  listOfTasks.addEventListener('click', function (event) {
    const target = event.target;
    if (target.id === 'done') {
      target.innerHTML = '&#x2705;';
    }
  });
}

async function createTaskOnDb (taskTitle) {
  const missionData = await fetchMissionStatus();
  if (missionData.active === true && missionData.user_id === userId) {
    const response = await fetch(`/tasks/${missionData.id}/${encodeURIComponent(taskTitle)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    if (response.ok) {
      console.log('Task created successfully');
    } else {
      throw new Error('Failed to create task');
    }
  } else {
    console.log('Mission is inactive');
  }
}

async function makeRequest (method, location) {
  const response = await fetch(location, {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  });
  if (!response.ok) {
    throw new Error('Failed to make request');
  }
}

function deleteAllTasks () {
  const allTasks = document.querySelectorAll('#taskList li');
  allTasks.forEach(task => {
    task.remove();
  });
  document.querySelector('#addTaskBtn').remove();
}

function reloadPageAfterSeconds (seconds) {
  const milliseconds = seconds * 1000;
  setTimeout(function () { location.reload(); }, milliseconds);
}

function taskDone (element) {
  const theTaskId = element.parentNode.id;
  if (element.innerHTML === '✅') {
    element.innerHTML = '☐';
    updateTask(theTaskId, 'undone');
  } else {
    element.innerHTML = '✅';
    updateTask(theTaskId, 'done');
  }
}

function taskDel (element) {
  const theTaskId = element.parentNode.id;
  fetch('/tasks/' + theTaskId, {
    method: 'DELETE'
  })
    .then(response => {
      if (response.ok) {
        document.getElementById(element.parentNode.id).remove();
        const alertElement = document.getElementById('alert');
        alertElement.classList.remove('d-none');
        setTimeout(() => {
          alertElement.classList.add('d-none');
        }, 2000);
      } else {
        console.error('Failed to delete task:', response.status);
      }
    })
    .catch(error => {
      console.error('Error deleting task:', error);
    });
}

async function updateTask (t_id, action) {
  const url = `/tasks/${t_id}/${action}`;
  const data = {};
  const options = {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error('Failed to update task');
  }
}
