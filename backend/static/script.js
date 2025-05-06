let calendar;
let planCount = 0;

// Modal close events
document.getElementById('modal-close').onclick = closeModal;
document.getElementById('modal-ok').onclick = closeModal;

// Add Event Button
document.getElementById('add-event-btn').onclick = () => {
  openModal("Add Custom Event", `
    <label>Title: <input id="evt-title" type="text" /></label><br/>
    <label>Description: <textarea id="evt-desc"></textarea></label><br/>
    <label>Date: <input id="evt-date" type="date" /></label><br/>
    <label>Start Time: <input id="evt-start" type="time" /></label><br/>
    <label>End Time: <input id="evt-end" type="time" /></label><br/>
    <label>Repeat: 
      <select id="evt-repeat">
        <option value="once">Once</option>
        <option value="weekly">Weekly</option>
      </select>
    </label><br/>
    <button onclick="saveCustomEvent()">Save</button>
  `);
};

// DOM ready
document.addEventListener('DOMContentLoaded', () => {
  calendar = new FullCalendar.Calendar(document.getElementById('calendar-view'), {
    initialView: 'timeGridWeek',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    slotMinTime: '00:00:00',
    slotMaxTime: '24:00:00',
    nowIndicator: true,
    editable: true,
    eventDidMount: info => {
      info.el.addEventListener('contextmenu', e => {
        e.preventDefault();
        openModal(
          'Delete Event?',
          `<p>Do you want to remove <strong>${info.event.title}</strong>?</p>
           <button onclick="calendar.getEventById('${info.event.id}').remove(); closeModal();">Yes, Delete</button>`
        );
      });
    },
    eventClick: info => {
      const e = info.event;
      openModal(
        e.title,
        `<p><strong>When:</strong> ${e.start.toLocaleString()} → ${e.end.toLocaleString()}</p>
         <p><strong>Description:</strong><br>${e.extendedProps.description || '(none)'}</p>`
      );
    },
    events: []
  });

  calendar.render();

  document.getElementById('chat-box').innerHTML = `<p><strong>AI:</strong> Hi, how can I help you today?</p>`;
  document.getElementById('user-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });
  document.getElementById('send-btn').addEventListener('click', sendMessage);
});

// Modal Functions
function openModal(title, html) {
  document.getElementById('modal-title').innerText = title;
  document.getElementById('modal-body').innerHTML = html;
  document.getElementById('modal').style.display = 'block';
}

function closeModal() {
  document.getElementById('modal').style.display = 'none';
}

// Chat Functionality
async function sendMessage() {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  const chatBox = document.getElementById('chat-box');
  chatBox.innerHTML += `<p><strong>You:</strong> ${escapeHtml(text)}</p>`;

  let resp;
  try {
    const r = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    resp = await r.json();
  } catch {
    return openModal('Error', '<p>Cannot reach server.</p>');
  }

  if (resp.type === 'study_plan' && Array.isArray(resp.content.schedule)) {
    showStudyPlan(resp.content);
  } else {
    chatBox.innerHTML += `<p><strong>AI:</strong> ${escapeHtml(resp.content)}</p>`;
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

// Study Plan Display
function showStudyPlan(plan) {
  const chatBox = document.getElementById('chat-box');
  chatBox.innerHTML += `<p><strong>AI:</strong> ${escapeHtml(plan.summary)}</p>`;

  const id = ++planCount;
  const days = new Set(plan.schedule.map(i => i.day)).size;

  if (days === 1) calendar.changeView('timeGridDay');
  else if (days <= 7) calendar.changeView('timeGridWeek');
  else calendar.changeView('dayGridMonth');

  chatBox.innerHTML += `
    <div class="schedule"><h3>Your Study Plan:</h3>
      <ul>${plan.schedule.map(item =>
        `<li><strong>${escapeHtml(item.day)}</strong> (${item.start}-${item.end}): ${escapeHtml(item.title)}</li>`
      ).join('')}</ul>
      <button class="add-plan-btn" data-plan="${id}">Add to Timeline</button>
    </div>
  `;

  document.querySelector(`.add-plan-btn[data-plan="${id}"]`).onclick = () =>
    addToTimeline(plan.schedule, id);
}

// Add Plan to Timeline with Conflict Handling
function addToTimeline(schedule, planId) {
  let index = 0;

  function processNext() {
    if (index >= schedule.length) {
      document.getElementById('chat-box').innerHTML +=
        `<p><strong>AI:</strong> Plan #${planId} added. Left-click → details, Right-click → remove block.</p>`;
      return;
    }

    const item = schedule[index++];
    const newEvent = toEvent(item, planId);
    const conflictEvent = calendar.getEvents().find(evt =>
      (newEvent.start < evt.end && newEvent.end > evt.start)
    );

    if (conflictEvent) {
      openModal("Conflict Detected", `
        <p>Conflict with <strong>${conflictEvent.title}</strong></p>
        <button id="add-anyway-btn">Add Anyway</button>
        <button id="set-schedule-btn">Set Schedule</button>
        <button onclick="processNext()">Skip</button>
      `);

      document.getElementById("add-anyway-btn").onclick = () => {
        calendar.addEvent(newEvent);
        closeModal();
        processNext();
      };

      document.getElementById("set-schedule-btn").onclick = () => {
        adjustConflict(planId, item, processNext);
      };
    } else {
      calendar.addEvent(newEvent);
      processNext();
    }
  }

  processNext();
}

function adjustConflict(planId, item, callback) {
  document.getElementById('modal-body').innerHTML = `
    <p>Adjust time for <strong>${item.title}</strong>:</p>
    <label>New Start: <input id="adjust-start" type="time" /></label><br/>
    <label>New End: <input id="adjust-end" type="time" /></label><br/>
    <button id="save-adjustment-btn">Save</button>
  `;

  document.getElementById("save-adjustment-btn").onclick = () => {
    confirmAdjustment(planId, item, callback);
  };
}

function confirmAdjustment(planId, item, callback) {
  const newStart = document.getElementById('adjust-start').value;
  const newEnd = document.getElementById('adjust-end').value;

  if (!newStart || !newEnd) {
    alert("Please enter both start and end times.");
    return;
  }

  item.start = newStart;
  item.end = newEnd;

  calendar.addEvent(toEvent(item, planId));
  closeModal();
  callback();
}

// Create Calendar Event Object
function toEvent(item, planId) {
  const wd = {
    Sunday: 0, Monday: 1, Tuesday: 2,
    Wednesday: 3, Thursday: 4, Friday: 5, Saturday: 6
  };

  const today = new Date();
  const date = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate() + ((wd[item.day] - today.getDay() + 7) % 7)
  );

  const [sh, sm] = item.start.split(':').map(Number);
  const [eh, em] = item.end.split(':').map(Number);

  const start = new Date(date); start.setHours(sh, sm);
  const end = new Date(date); end.setHours(eh, em);

  const colors = [
    { bg: "#F7C600", border: "#d4af37", text: "#000000" },
    { bg: "#FFB347", border: "#e0962b", text: "#000000" },
    { bg: "#FFF5B7", border: "#f2cd00", text: "#000000" },
    { bg: "#50C878", border: "#419e65", text: "#000000" },
    { bg: "#6CA0DC", border: "#548ec9", text: "#000000" },
    { bg: "#E0FFFF", border: "#AFEEEE", text: "#000000" },
    { bg: "#004953", border: "#006064", text: "#FFFFFF" },
    { bg: "#002B5B", border: "#002B5B", text: "#FFFFFF" },
    { bg: "#1A1A40", border: "#333366", text: "#FFFFFF" },
    { bg: "#0F172A", border: "#1E293B", text: "#FFFFFF" }
  ];

  const color = colors[(planId - 1) % colors.length];

  return {
    id: `p${planId}-${item.day}-${item.start}`,
    title: item.title,
    start,
    end,
    extendedProps: { description: item.description },
    backgroundColor: color.bg,
    borderColor: color.border,
    textColor: color.text,
    editable: true
  };
}

// Utility
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

// Save Custom Event
function saveCustomEvent() {
  const title = document.getElementById('evt-title').value.trim();
  const desc = document.getElementById('evt-desc').value.trim();
  const date = document.getElementById('evt-date').value;
  const start = document.getElementById('evt-start').value;
  const end = document.getElementById('evt-end').value;
  const repeat = document.getElementById('evt-repeat').value;

  if (!title || !date || !start || !end) {
    return openModal('Error', '<p>Please fill in all required fields.</p>');
  }

  const startTime = new Date(`${date}T${start}`);
  const endTime = new Date(`${date}T${end}`);

  const customColor = {
    backgroundColor: "#6A0DAD",
    borderColor: "#5A0C9E",
    textColor: "#FFFFFF"
  };

  calendar.addEvent({
    id: `custom-${Date.now()}`,
    title,
    start: startTime,
    end: endTime,
    extendedProps: { description: desc },
    editable: true,
    ...customColor
  });

  if (repeat === 'weekly') {
    for (let i = 1; i <= 3; i++) {
      const nextStart = new Date(startTime);
      const nextEnd = new Date(endTime);
      nextStart.setDate(nextStart.getDate() + i * 7);
      nextEnd.setDate(nextEnd.getDate() + i * 7);
      calendar.addEvent({
        id: `custom-${Date.now()}-${i}`,
        title,
        start: nextStart,
        end: nextEnd,
        extendedProps: { description: desc },
        editable: true,
        ...customColor
      });
    }
  }

  closeModal();
}

// Export and Import
function downloadSchedule() {
  const events = calendar.getEvents().map(e => ({
    title: e.title,
    start: e.start.toISOString(),
    end: e.end.toISOString(),
    description: e.extendedProps.description || "",
    backgroundColor: e.backgroundColor,
    borderColor: e.borderColor,
    textColor: e.textColor
  }));

  const blob = new Blob([JSON.stringify(events, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "my_schedule.json";
  a.click();

  URL.revokeObjectURL(url);
}

function uploadSchedule(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const events = JSON.parse(e.target.result);
      events.forEach(evt => {
        calendar.addEvent({
          title: evt.title,
          start: evt.start,
          end: evt.end,
          extendedProps: { description: evt.description },
          backgroundColor: evt.backgroundColor,
          borderColor: evt.borderColor,
          textColor: evt.textColor
        });
      });
      alert("Plan uploaded!");
    } catch {
      alert("Invalid file.");
    }
  };
  reader.readAsText(file);
}
