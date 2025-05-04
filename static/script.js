// Display initial AI message when page loads
document.addEventListener('DOMContentLoaded', function() {
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML = `<p><strong>AI:</strong> Hi, How can I help you today?</p>`;
});

async function sendMessage() {
  const input = document.getElementById("user-input").value;
  if (!input.trim()) return; // Prevent empty messages
  
  const chatBox = document.getElementById("chat-box");

  // Add user message to chat
  chatBox.innerHTML += `<p><strong>You:</strong> ${input}</p>`;
  
  // Clear input field
  document.getElementById("user-input").value = "";

  // Show loading indicator
  const loadingId = "loading-" + Date.now();
  chatBox.innerHTML += `<p id="${loadingId}"><strong>AI:</strong> Thinking...</p>`;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    if (!res.ok) {
      throw new Error("Failed to get response");
    }

    const response = await res.json();
    
    // Remove loading indicator
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
      loadingElement.remove();
    }
    
    // Handle different response types
    if (response.type === "study_plan") {
      displayStudyPlan(response.content);
    } else {
      // Regular chat response
      chatBox.innerHTML += `<p><strong>AI:</strong> ${response.content}</p>`;
    }
  } catch (error) {
    console.error("Error:", error);
    // Update loading message with error
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
      loadingElement.innerHTML = `<strong>AI:</strong> Sorry, I encountered an error. Please try again.`;
    }
  }
  
  // Scroll to bottom of chat
  chatBox.scrollTop = chatBox.scrollHeight;
}

function displayStudyPlan(data) {
  const chatBox = document.getElementById("chat-box");
  
  // Display the summary message
  let responseHTML = `<p><strong>AI:</strong> ${data.summary}</p>`;
  
  if (data.schedule && Array.isArray(data.schedule)) {
    responseHTML += `<div class="schedule">
      <h3>Your Study Plan:</h3>
      <ul>`;
    
    data.schedule.forEach(item => {
      responseHTML += `
        <li class="schedule-item">
          <div><strong>${item.day}</strong> (${item.start}-${item.end}): <span class="topic">${item.title}</span></div>
          <div class="description">${item.description || ""}</div>
        </li>`;
    });
    
    responseHTML += `</ul>
      <div class="schedule-actions">
        <button onclick="addToCalendar()" class="calendar-btn">Add to Calendar</button>
      </div>
    </div>`;
  }
  
  // Add a "Would you like to add this to your calendar?" message
  responseHTML += `<p><strong>AI:</strong> Would you like to add this study plan to your calendar? Click the "Add to Calendar" button above.</p>`;
  
  chatBox.innerHTML += responseHTML;
}

function addToCalendar() {
  // This is a placeholder function
  // In a real application, you would integrate with a calendar API
  // For now, we'll just show a message
  
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<p><strong>AI:</strong> Great! In a real application, this would add these events to your calendar. Since this is a demo, consider your plan saved!</p>`;
  
  // Disable the button after clicking
  const buttons = document.querySelectorAll('.calendar-btn');
  buttons.forEach(button => {
    button.disabled = true;
    button.textContent = "Added to Calendar";
    button.classList.add("added");
  });
  
  // Scroll to bottom of chat
  chatBox.scrollTop = chatBox.scrollHeight;
}
 
function addToCalendar() {
  // Backend'e gönderme
  fetch("/add-to-calendar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(response => response.json())
    .then(data => {
      // Başarılı geri dönüş sonrası kullanıcıya bildirim yapalım
      const chatBox = document.getElementById("chat-box");
      chatBox.innerHTML += `<p><strong>AI:</strong> The study plan has been successfully added to your calendar!</p>`;
      
      // Takvim butonunu devre dışı bırak
      const buttons = document.querySelectorAll('.calendar-btn');
      buttons.forEach(button => {
        button.disabled = true;
        button.textContent = "Added to Calendar";
        button.classList.add("added");
      });

      // Scroll'u en alta kaydır
      chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
      console.error("Error:", error);
      const chatBox = document.getElementById("chat-box");
      chatBox.innerHTML += `<p><strong>AI:</strong> Sorry, I encountered an error while adding the plan to your calendar. Please try again later.</p>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    });
} 