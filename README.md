
![image](https://github.com/user-attachments/assets/77e3ac5f-1439-4ed9-8604-45c79eafaf0e)

# LearnX – Your AI-Powered Study Timeline

🌐 **Live Site**: [https://learnx-sv60.onrender.com](https://learnx-sv60.onrender.com)

**LearnX** is a simple and smart study planner that helps users generate, visualize, and manage personalized study schedules through an intuitive calendar interface.

---

## 🚀 Project Description

**LearnX** is a hackathon-built AI-powered web app designed to improve study productivity. Users describe what they want to study, and the AI instantly returns a customized plan, displayed as draggable and interactive calendar blocks.

---

## 🎯 Hackathon Submission Details

- **Theme:** Next Generation Learning

### 🔗 How It Matches
LearnX empowers learners to structure and own their study journey through AI planning, intuitive scheduling, and full flexibility—perfectly aligning with future-ready education tools.

---

## ✅ Key Strengths

- Clean UX  
- Interactive calendar blocks  
- Simple AI interface  
- Save & reload your timeline anytime  

---

## 🚧 Limitations / Future Work

- AI does not yet ask clarifying questions automatically  
- User input should ideally be detailed (e.g. duration, level, goals)  
- Extended time-based planning (e.g. “3-month plan”) to be added  

---

## ✨ Features

### 🧠 AI Study Plan Generator
- Users can send a single message to describe their study goal (e.g. _"Make me a TOEFL study plan"_).
- The plan is instantly created and displayed in a calendar format.

### 📅 Interactive Calendar Interface
- ⬅️➡️ Navigate by week or day
- 🟨 **Blocks** = Study tasks
- ✅ **Left-click** → View task details  
- ❌ **Right-click** → Delete block  
- 🔄 **Drag-and-drop** to rearrange  

### 📝 Add Event Function
- Manually add custom study events with a title, time, and description

### 💾 Save & Load Plans
- Download timeline with **Save Plan**
- Import timeline with **Load Plan**

---

## 🛠️ Key Modules & Code Highlights

| File              | Description |
|-------------------|-------------|
| `scheduler.py`    | Handles chat logic, session state, and Gemini API prompts |
| `planner.py`      | Stores the AI-generated study plan for calendar rendering |
| `script.js`       | Calendar UI logic, event conflict handling, modal behavior |
| `style.css`       | UI styling with navy, mustard, and light backgrounds |
| `index.html`      | Combines the calendar + chat layout |
| `app.py`          | FastAPI backend – routes, logic dispatcher |

---
