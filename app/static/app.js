  const toggle = document.getElementById("toggle");
  // Check and apply the mode preference before the page loads
  const savedMode = localStorage.getItem('mode');
  if (savedMode === 'dark') {
    document.body.classList.add('dark-mode');
  } else {
    toggle.classList.add("checked");
  }

  // Toggle between dark and light modes and save preference
  function toggleMode() {
    const htmlElement = document.body;
    htmlElement.classList.toggle('dark-mode');
    toggle.classList.toggle("checked");
    const currentMode = htmlElement.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('mode', currentMode);      
  }
  toggle.addEventListener("click", () => {toggleMode()});

  const resultBox = document.getElementById("result");
  const progressArea = document.getElementById("progress-area");

  function createProgressBar(taskId) {
    const wrapper = document.createElement("div");
    wrapper.id = `task-${taskId}`;
    wrapper.innerHTML = `
      <progress id="bar-${taskId}" value="0" max="100"></progress>
      <span id="msg-${taskId}">Starting...</span>
    `;
    progressArea.appendChild(wrapper);
  }

  function pollProgress(taskId) {
    const bar = document.getElementById(`bar-${taskId}`);
    const msg = document.getElementById(`msg-${taskId}`);
    const interval = setInterval(() => {
      fetch(`/progress/${taskId}`)
        .then(res => res.json())
        .then(data => {
          msg.innerText = data.progress + '%' || '';
          let raw = parseFloat(data.progress);
          bar.value = !isNaN(raw) ? raw : 0;
          if (data.status === 'finished' || data.status === 'error') {
            afterProgress();
            clearInterval(interval);
          }
        })
        .catch(() => {
          msg.innerText = "Error polling progress";
          afterProgress();
          clearInterval(interval);
        });
    }, 1000);
    function afterProgress() {
      // remove progress bar after 5 seconds
      setTimeout(() => {
        progressArea.removeChild(document.getElementById(`task-${taskId}`));
      }, 5000);
    }
    
  }

  // Function to handle the download button click
  const downloadShowBtn = document.getElementById("download-show");
  const downloadEpisodeBtn = document.getElementById("download-episode");
  const downloadMovieBtn = document.getElementById("download-movie");
  const urlInput = document.getElementById("url");

  const postUrl = async (path) => {
    let value = document.getElementById("url").value;
    let myBody = {"textfield": document.getElementById("url").value};

    // rest api call
    fetch('/'+path, {
      method: 'POST',
      body: JSON.stringify(myBody), // string or object
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(res => res.json())
    .then(data => {
      if (data.task_id) {
        createProgressBar(data.task_id);
        pollProgress(data.task_id);
      }
      urlInput.value = "";
    })
    .catch(err => {
      resultBox.innerText = "Server error.";
    });
  }

  // add events for button and inputfield
  downloadShowBtn.addEventListener("click", () => {postUrl('download-show')});
  downloadEpisodeBtn.addEventListener("click", () => {postUrl('download-episode')});
  downloadMovieBtn.addEventListener("click", () => {postUrl('download-movie')});

  // add sharehandler function
  const url = new URL(document.location);
  const sharedLink = url.searchParams.get("link");
  let description = url.searchParams.get("description");
  try {
    if(sharedLink !== null){
      new URL(sharedLink);
      document.getElementById("url").value = sharedLink;
    } else if(description !== null){
      const searchString = "https";
      const startIndex = description.indexOf(searchString);

      if (startIndex !== -1) {
        description = description.slice(startIndex);
        new URL(description);
        document.getElementById("url").value = description;
      } else {
        document.getElementById("result").innerText = "Shared Text does not contain https";
      }
    }
  } catch (_) {
    document.getElementById("result").innerText = "Invalid URL";
  }

  window.addEventListener('DOMContentLoaded', () => {
    // Fetch and show all active tasks
    fetch('/active-tasks')
      .then(res => res.json())
      .then(data => {
        (data.tasks || []).forEach(task => {
          createProgressBar(task.task_id);
          pollProgress(task.task_id);
        });
      });
  });