let sessionId = null;
let useVoice = false;
let profile = { role_type: "General", competencies: [] };

let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;

const $ = (id) => document.getElementById(id);

$("analyzeBtn").onclick = async () => {
  const form = new FormData();
  form.append("resume_text", $("resumeText").value);
  form.append("job_description", $("jobDescription").value);
  const res = await fetch("/api/parse-profile", { method: "POST", body: form });
  profile = await res.json();
  $("analyzeResult").textContent =
    `Detected role: ${profile.role_type} | Competencies: ${profile.competencies.join(", ")}`;
};

$("startBtn").onclick = async () => {
  useVoice = $("voiceToggle").checked;
  const form = new FormData();
  form.append("role_type", profile.role_type || "General");
  form.append("competencies", (profile.competencies || []).join(","));
  form.append("num_questions", $("numQuestions").value);
  form.append("voice", useVoice);

  const res = await fetch("/api/session/start", { method: "POST", body: form });
  const data = await res.json();
  sessionId = data.session_id;

  $("setup").classList.add("hidden");
  $("interview").classList.remove("hidden");
  $("voiceAnswerArea").classList.toggle("hidden", !useVoice);
  $("textAnswerArea").classList.toggle("hidden", useVoice);

  renderQuestion(data);
};

function renderQuestion(data) {
  $("questionCounter").textContent = `Question ${data.question_number} of ${data.total_questions}`;
  $("questionText").textContent = data.question;
  $("feedbackBox").classList.add("hidden");
  $("answerText").value = "";
  recordedBlob = null;
  $("recordStatus").textContent = "";

  if (data.question_audio) {
    $("questionAudio").src = `/api/audio/${data.question_audio}`;
    $("questionAudio").classList.remove("hidden");
    $("questionAudio").play();
  } else {
    $("questionAudio").classList.add("hidden");
  }
}

$("recordBtn").onclick = async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    $("recordBtn").textContent = "Start recording";
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (e) => recordedChunks.push(e.data);
  mediaRecorder.onstop = () => {
    recordedBlob = new Blob(recordedChunks, { type: "audio/webm" });
    $("recordStatus").textContent = "Recording captured. Submit when ready.";
  };
  mediaRecorder.start();
  $("recordBtn").textContent = "Stop recording";
  $("recordStatus").textContent = "Recording...";
};

$("submitAnswerBtn").onclick = async () => {
  const form = new FormData();
  if (useVoice && recordedBlob) {
    form.append("audio", recordedBlob, "answer.webm");
  } else {
    form.append("answer_text", $("answerText").value);
  }

  const res = await fetch(`/api/session/${sessionId}/answer`, { method: "POST", body: form });
  const data = await res.json();

  $("feedbackBox").classList.remove("hidden");
  $("scoresText").textContent = JSON.stringify(data.scores, null, 2);
  $("feedbackText").textContent = data.feedback;
  if (data.transcript) {
    $("questionText").textContent += `\n\nYou said: "${data.transcript}"`;
  }

  if (data.feedback_audio) {
    $("feedbackAudio").src = `/api/audio/${data.feedback_audio}`;
    $("feedbackAudio").classList.remove("hidden");
    $("feedbackAudio").play();
  }

  window._nextQuestion = data.next;
  $("nextBtn").classList.remove("hidden");
};

$("nextBtn").onclick = async () => {
  const next = window._nextQuestion;
  if (next.done) {
    $("interview").classList.add("hidden");
    $("summary").classList.remove("hidden");
    await loadHistory();
  } else {
    renderQuestion(next);
  }
};

async function loadHistory() {
  const res = await fetch("/api/history");
  const rows = await res.json();
  if (rows.length === 0) {
    $("historyTable").textContent = "No history yet.";
    return;
  }
  let html = "<table><tr><th>When</th><th>Role</th><th>Competency</th><th>Avg score</th></tr>";
  for (const r of rows) {
    const avg = ((r.structure + r.specificity + r.technical_accuracy + r.communication) / 4).toFixed(1);
    html += `<tr><td>${r.created_at.slice(0, 16)}</td><td>${r.role_type}</td><td>${r.competency}</td><td>${avg}</td></tr>`;
  }
  html += "</table>";
  $("historyTable").innerHTML = html;
}
