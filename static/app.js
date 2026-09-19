let currentLeadId = null;

const form = document.getElementById('lead-form');
const panel = document.getElementById('qualification-panel');
const message = document.getElementById('form-message');
const startCallBtn = document.getElementById('start-call-btn');
const callStatus = document.getElementById('call-status');
const transcriptEl = document.getElementById('transcript');
const callResult = document.getElementById('call-result');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  message.textContent = 'Saving...';
  message.className = 'message';

  const data = new FormData(form);

  try {
    const res = await fetch('/api/leads', {
      method: 'POST',
      body: data,
    });
    const json = await res.json();

    if (json.success) {
      currentLeadId = json.lead.id;
      message.textContent = 'Lead captured. Scroll down to start the AI call.';
      message.className = 'message success';
      panel.classList.remove('hidden');
      panel.scrollIntoView({ behavior: 'smooth' });
      form.querySelector('button').disabled = true;
    } else {
      throw new Error(json.detail || 'Failed to save lead');
    }
  } catch (err) {
    message.textContent = err.message;
    message.className = 'message error';
  }
});

startCallBtn.addEventListener('click', () => {
  if (!currentLeadId) return;

  startCallBtn.disabled = true;
  callStatus.textContent = 'Calling...';
  callStatus.className = 'status calling';
  transcriptEl.innerHTML = '';
  callResult.classList.add('hidden');

  const source = new EventSource(`/api/leads/${currentLeadId}/call-stream`);

  source.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'transcript') {
      const isAI = data.text.startsWith('AI:');
      const turn = document.createElement('div');
      turn.className = `turn ${isAI ? 'ai' : 'lead'}`;
      turn.innerHTML = `<span class="speaker">${isAI ? 'AI' : 'Lead'}</span>${data.text.replace(/^(AI|Lead): /, '')}`;
      transcriptEl.appendChild(turn);
      transcriptEl.scrollTop = transcriptEl.scrollHeight;
    }

    if (data.type === 'done') {
      source.close();
      startCallBtn.disabled = false;
      startCallBtn.textContent = 'Restart AI Call';

      if (data.qualified) {
        callStatus.textContent = 'Qualified ✅';
        callStatus.className = 'status qualified';
        callResult.className = 'call-result';
        callResult.innerHTML = `<strong>Outcome:</strong> ${data.outcome}<br><strong>Summary:</strong> ${data.summary}`;
      } else {
        callStatus.textContent = 'Needs Review';
        callStatus.className = 'status review';
        callResult.className = 'call-result negative';
        callResult.innerHTML = `<strong>Outcome:</strong> ${data.outcome}<br><strong>Summary:</strong> ${data.summary}`;
      }
      callResult.classList.remove('hidden');
    }
  });

  source.addEventListener('error', () => {
    source.close();
    startCallBtn.disabled = false;
    callStatus.textContent = 'Call failed. Try again.';
    callStatus.className = 'status review';
  });
});